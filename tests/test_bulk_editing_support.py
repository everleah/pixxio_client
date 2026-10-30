"""Offline tests for paging, structured parameter encoding, update_and_wait and retries."""

import json
import unittest
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

from requests.adapters import HTTPAdapter

from pixxio_client import Client
from pixxio_client.directories import Directory
from pixxio_client.exceptions import JobFailedException
from pixxio_client.files import File
from pixxio_client.metadata import (
    CustomMetadata,
    CustomMetadataBuilder,
    MetadataValueBuilder,
    StandardMetadata,
)


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.status_code = status_code
        self.text = json.dumps(payload) if payload is not None else ""
        self.ok = 200 <= status_code < 400
        self.headers = {}


class FakeSession:
    """Records requests and answers them via handler(method, url, kwargs)."""

    def __init__(self, handler):
        self.handler = handler
        self.calls = []

    def _request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return FakeResponse(self.handler(method, url, kwargs))

    def get(self, url, **kwargs):
        return self._request("GET", url, **kwargs)

    def put(self, url, **kwargs):
        return self._request("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self._request("DELETE", url, **kwargs)


def make_client(handler):
    client = Client.create_client("dummy-key", "example.pixxio.test")
    client._session = FakeSession(handler)
    return client


def paged_handler(total, list_key="files", **item_fields):
    def handler(method, url, kwargs):
        params = kwargs["params"]
        page, size = params["page"], params["pageSize"]
        start = (page - 1) * size
        ids = range(start + 1, min(start + size, total) + 1)
        items = [{"id": i, **{k: f"{v}{i}" for k, v in item_fields.items()}} for i in ids]
        return {"success": True, "quantity": total, list_key: items}
    return handler


def job_handler(job_success):
    def handler(method, url, kwargs):
        if method == "PUT":
            return {"success": True, "jobID": 42}
        return {"success": True, "job": {"id": 42, "isFinished": True,
                                         "success": job_success, "error": "boom"}}
    return handler


class IterAllTests(unittest.TestCase):
    def test_fetches_all_pages_and_stops_at_quantity(self):
        client = make_client(paged_handler(total=250))
        items = File(client).get_all(page_size=100)
        self.assertEqual([f.id for f in items], list(range(1, 251)))
        self.assertEqual([c[2]["params"]["page"] for c in client.session.calls], [1, 2, 3])

    def test_stops_after_exact_full_page_using_quantity(self):
        client = make_client(paged_handler(total=200))
        self.assertEqual(len(File(client).get_all(page_size=100)), 200)
        self.assertEqual(len(client.session.calls), 2)

    def test_respects_max_items_lazily(self):
        client = make_client(paged_handler(total=1000))
        self.assertEqual(len(File(client).get_all(page_size=100, max_items=150)), 150)
        self.assertEqual(len(client.session.calls), 2)

    def test_stops_when_paging_is_ignored(self):
        client = make_client(lambda m, u, k: {"success": True, "files": [{"id": 1}, {"id": 2}]})
        items = File(client).get_all(page_size=2)
        self.assertEqual([f.id for f in items], [1, 2])
        self.assertEqual(len(client.session.calls), 2)

    def test_non_paged_resource_uses_single_request(self):
        client = make_client(
            lambda m, u, k: {"success": True, "standardMetadata": [{"id": 1}, {"id": 2}]})
        items = StandardMetadata(client).get_all()
        self.assertEqual([i.id for i in items], [1, 2])
        self.assertEqual(len(client.session.calls), 1)
        self.assertNotIn("page", client.session.calls[0][2]["params"])

    def test_custom_metadata_builder_loads_all_pages(self):
        client = make_client(paged_handler(
            total=120, list_key="customMetadata", name="f", editType=""))
        builder = CustomMetadataBuilder(client)
        self.assertTrue(builder.is_valid_field_by_id(120))
        self.assertTrue(builder.is_valid_field_name("f101"))

    def test_custom_metadata_clamps_page_size_to_endpoint_limit(self):
        client = make_client(paged_handler(
            total=120, list_key="customMetadata", name="f", editType=""))
        items = CustomMetadata(client).get_all(page_size=100)
        self.assertEqual(len(items), 120)
        self.assertEqual([c[2]["params"]["pageSize"] for c in client.session.calls],
                         [50, 50, 50])

    def test_files_clamps_page_size_to_endpoint_limit(self):
        client = make_client(paged_handler(total=600))
        items = File(client).get_all(page_size=1000)
        self.assertEqual(len(items), 600)
        self.assertEqual(client.session.calls[0][2]["params"]["pageSize"], 500)

    def test_directories_clamp_page_size_to_endpoint_limit(self):
        client = make_client(paged_handler(total=45, list_key="directories", name="d"))
        items = Directory(client).get_all()
        self.assertEqual(len(items), 45)
        self.assertEqual({c[2]["params"]["pageSize"] for c in client.session.calls}, {20})


class StructuredParamTests(unittest.TestCase):
    def test_get_encodes_filter_as_json(self):
        client = make_client(paged_handler(total=1))
        file_filter = {"filterType": "fileName", "term": "cat", "inverted": False}
        File(client).get_all(filter=file_filter)
        params = client.session.calls[0][2]["params"]
        self.assertEqual(json.loads(params["filter"]), file_filter)
        self.assertIsInstance(params["responseFields"], list)

    def test_delete_encodes_filter_as_json(self):
        client = make_client(lambda m, u, k: {"success": True})
        File(client).delete(filter={"filterType": "rating", "rating": 1})
        params = client.session.calls[0][2]["params"]
        self.assertEqual(json.loads(params["filter"]), {"filterType": "rating", "rating": 1})

    def test_update_encodes_object_fields_and_keeps_ids_list(self):
        client = make_client(lambda m, u, k: {"success": True})
        File(client).update(
            ids=[1, 2],
            description="x",
            metadataCustom=[{"action": "replace", "id": 5, "value": "a"}],
            metadataText={"7": ["t"]},
            metadataStandard='[{"action": "remove", "id": 3}]',
        )
        data = client.session.calls[0][2]["data"]
        self.assertEqual(data["ids"], [1, 2])
        self.assertEqual(data["description"], "x")
        self.assertEqual(json.loads(data["metadataCustom"]),
                         [{"action": "replace", "id": 5, "value": "a"}])
        self.assertEqual(json.loads(data["metadataText"]), {"7": ["t"]})
        self.assertEqual(data["metadataStandard"], '[{"action": "remove", "id": 3}]')


class UpdateAndWaitTests(unittest.TestCase):
    def test_without_job_returns_response(self):
        client = make_client(lambda m, u, k: {"success": True})
        result = File(client).update_and_wait(ids=[1], description="x")
        self.assertIs(result.success, True)
        self.assertEqual(len(client.session.calls), 1)

    def test_waits_for_job(self):
        client = make_client(job_handler(job_success=True))
        job = File(client).update_and_wait(ids=[1, 2], description="x", poll_interval=0)
        self.assertEqual(job.id, 42)
        self.assertTrue(any(c[1].endswith("/jobs/42") for c in client.session.calls))

    def test_raises_on_failed_job(self):
        client = make_client(job_handler(job_success=False))
        with self.assertRaises(JobFailedException):
            File(client).update_and_wait(ids=[1, 2], description="x", poll_interval=0)


class DeleteAndWaitTests(unittest.TestCase):
    def test_without_job_returns_response(self):
        client = make_client(lambda m, u, k: {"success": True})
        result = File(client).delete_and_wait(ids=[1])
        self.assertIs(result.success, True)
        self.assertEqual(len(client.session.calls), 1)

    def test_waits_for_delete_job_and_exposes_deleted_ids(self):
        def handler(method, url, kwargs):
            if method == "DELETE":
                return {"success": True, "jobID": 42}
            return {"success": True, "job": {
                "id": 42, "jobType": "filesDelete", "isFinished": True,
                "success": True, "error": None,
                "finishedJobData": {"deletedFileIDs": [1, 2], "notDeletedFileIDs": []},
            }}

        client = make_client(handler)
        job = File(client).delete_and_wait(ids=[1, 2], poll_interval=0)
        self.assertEqual(job.id, 42)
        self.assertEqual(list(job.finishedJobData.deletedFileIDs), [1, 2])
        self.assertEqual(list(job.finishedJobData.notDeletedFileIDs), [])
        self.assertTrue(any(c[1].endswith("/jobs/42") for c in client.session.calls))

    def test_raises_on_failed_delete_job(self):
        def handler(method, url, kwargs):
            if method == "DELETE":
                return {"success": True, "jobID": 42}
            return {"success": True, "job": {
                "id": 42, "isFinished": True, "success": False, "error": "boom",
            }}

        client = make_client(handler)
        with self.assertRaises(JobFailedException):
            File(client).delete_and_wait(ids=[1, 2], poll_interval=0)

    def test_requires_exactly_one_selector(self):
        client = make_client(lambda m, u, k: {"success": True})
        with self.assertRaises(ValueError):
            File(client).delete_and_wait()
        with self.assertRaises(ValueError):
            File(client).delete_and_wait(ids=[1], filter={"filterType": "files"})


class RetryTests(unittest.TestCase):
    def test_retry_adapter_is_opt_in(self):
        default_adapter = Client.create_client("k", "h.test").session.get_adapter("https://h.test")
        self.assertEqual(default_adapter.max_retries.total, 0)

        adapter = Client.create_client("k", "h.test", max_retries=3).session.get_adapter("https://h.test")
        self.assertIsInstance(adapter, HTTPAdapter)
        self.assertEqual(adapter.max_retries.total, 3)
        self.assertIn(429, adapter.max_retries.status_forcelist)
        self.assertNotIn("POST", adapter.max_retries.allowed_methods)


class MetadataValueTests(unittest.TestCase):
    """Date values must use the only format the API accepts: YYYY-MM-DD HH:MM:SS."""

    def _builder(self, edit_type="date"):
        field = SimpleNamespace(id=7, name="Datum", editType=edit_type, selectionOptions=[])
        return MetadataValueBuilder([field])

    def test_datetime_uses_api_format(self):
        builder = self._builder()
        builder.append("replace", 7, datetime(2026, 12, 31, 23, 45, 0))
        self.assertEqual(builder.build(),
                         [{"action": "replace", "id": 7, "value": "2026-12-31 23:45:00"}])

    def test_aware_datetime_keeps_wall_time(self):
        builder = self._builder()
        builder.append("replace", 7, datetime(2026, 12, 31, 23, 45, tzinfo=timezone(timedelta(hours=2))))
        self.assertEqual(builder.build()[0]["value"], "2026-12-31 23:45:00")

    def test_plain_date_gets_midnight(self):
        builder = self._builder()
        builder.append("replace", 7, date(2026, 12, 31))
        self.assertEqual(builder.build()[0]["value"], "2026-12-31 00:00:00")

    def test_api_string_is_passed_through(self):
        builder = self._builder()
        builder.append("replace", 7, "2026-12-31 23:45:00")
        self.assertEqual(builder.build()[0]["value"], "2026-12-31 23:45:00")

    def test_unknown_field_is_rejected(self):
        builder = self._builder()
        with self.assertRaises(ValueError):
            builder.append("replace", 999, "2026-12-31 23:45:00")

    def test_selection_name_is_mapped_to_id(self):
        field = SimpleNamespace(id=8, name="Kampagne", editType="selection",
                                selectionOptions=[{"id": 11, "name": "Sommer"}])
        builder = MetadataValueBuilder([field])
        builder.append("replace", 8, "Sommer")
        self.assertEqual(builder.build()[0]["value"], 11)


if __name__ == "__main__":
    unittest.main()
