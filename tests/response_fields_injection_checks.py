#!/usr/bin/env python3
"""Unit tests for responseFields injection behavior on GET endpoints."""

import unittest
from unittest.mock import patch

from pixxio_client import Client
from pixxio_client.files import File
from pixxio_client.directories import Directory
from pixxio_client.keywords import Keyword
from pixxio_client.synonyms import Synonym
from pixxio_client.portals import PortalPage, PortalUser


def _mock_response(text: str = "{}"):
    """Create a lightweight mock response object compatible with _parseResponse."""
    class Response:
        ok = True
        status_code = 200

        def __init__(self, body: str):
            self.text = body

    return Response(text)


class ResponseFieldsInjectionTests(unittest.TestCase):
    def setUp(self):
        self.client = Client.create_client("test-api-key", "example.test")

    def test_standard_get_injects_response_fields(self):
        files = File(self.client)
        files.set_response_fields(["id", "fileName"])

        with patch.object(self.client.session, "get", return_value=_mock_response()) as mock_get:
            files.get()

        params = mock_get.call_args.kwargs["params"]
        self.assertIn("responseFields", params)
        self.assertEqual(params["responseFields"], ["id", "fileName"])

    def test_context_manager_temporarily_disables_injection(self):
        files = File(self.client)
        files.set_response_fields(["id"])

        with patch.object(self.client.session, "get", return_value=_mock_response()) as mock_get:
            with files._without_response_fields():
                files.get(1)
            files.get(2)

        first_params = mock_get.call_args_list[0].kwargs["params"]
        second_params = mock_get.call_args_list[1].kwargs["params"]

        self.assertNotIn("responseFields", first_params)
        self.assertIn("responseFields", second_params)

    def test_directory_get_tree_never_injects_response_fields(self):
        directories = Directory(self.client)
        directories.set_response_fields(["id", "name"])

        with patch.object(self.client.session, "get", return_value=_mock_response()) as mock_get:
            directories.get_tree()

        params = mock_get.call_args.kwargs["params"]
        self.assertNotIn("responseFields", params)

    def test_keyword_download_never_injects_response_fields(self):
        keywords = Keyword(self.client)
        keywords.set_response_fields(["id", "name"])

        with patch.object(self.client.session, "get", return_value=_mock_response()) as mock_get:
            keywords.download()

        params = mock_get.call_args.kwargs["params"]
        self.assertNotIn("responseFields", params)

    def test_synonym_get_columns_never_injects_response_fields(self):
        synonyms = Synonym(self.client)
        synonyms.set_response_fields(["id"])

        with patch.object(self.client.session, "get", return_value=_mock_response()) as mock_get:
            synonyms.get_columns()

        params = mock_get.call_args.kwargs["params"]
        self.assertNotIn("responseFields", params)

    def test_portal_page_get_never_injects_response_fields(self):
        portal_pages = PortalPage(self.client)
        portal_pages.set_response_fields(["id"])

        with patch.object(self.client.session, "get", return_value=_mock_response()) as mock_get:
            portal_pages.get(1)

        params = mock_get.call_args.kwargs["params"]
        self.assertNotIn("responseFields", params)

    def test_portal_user_get_never_injects_response_fields(self):
        portal_users = PortalUser(self.client)
        portal_users.set_response_fields(["id"])

        with patch.object(self.client.session, "get", return_value=_mock_response()) as mock_get:
            portal_users.get(1)
            portal_users.get(1, user_id=2)

        first_params = mock_get.call_args_list[0].kwargs["params"]
        second_params = mock_get.call_args_list[1].kwargs["params"]

        self.assertNotIn("responseFields", first_params)
        self.assertNotIn("responseFields", second_params)

    def test_file_download_convert_never_injects_response_fields(self):
        files = File(self.client)
        files.set_response_fields(["id", "fileName"])

        with patch.object(self.client.session, "get", return_value=_mock_response()) as mock_get:
            files.download(42)
            files.download()

        first_params = mock_get.call_args_list[0].kwargs["params"]
        second_params = mock_get.call_args_list[1].kwargs["params"]

        self.assertNotIn("responseFields", first_params)
        self.assertNotIn("responseFields", second_params)


if __name__ == "__main__":
    unittest.main()
