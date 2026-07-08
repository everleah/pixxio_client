#!/usr/bin/env python3
"""
Download all assets from a PIXXIO collection and create an ID->filename CSV mapping.

Output:
- Files in examples/data
- CSV with header: id;Dateiname
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from typing import Any, Iterable, List, Optional, Tuple

from pixxio_client import Client
from pixxio_client.collections import Collection
from pixxio_client.files import File


DEFAULT_HOST = "https://weru.px.media/"
DEFAULT_API_KEY = "2AoXVLvsT4yJm0Tc5kMuu3Pji12QYNqKV2940RAUG3ojlGp9HVjahwpEjUqZRecy"
DEFAULT_COLLECTION_NAME = "hoerl_InDesign_Dokumente"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "data"


def _to_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _get_attr(obj: Any, *names: str) -> Any:
    for name in names:
        if isinstance(obj, dict) and name in obj:
            return obj.get(name)
        value = getattr(obj, name, None)
        if value is not None:
            return value
    return None


def _as_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_filename(name: str) -> str:
    invalid = '<>:"/\\|?*'
    cleaned = "".join("_" if ch in invalid else ch for ch in name)
    cleaned = cleaned.strip().strip(".")
    return cleaned or "unnamed_asset"


def _extract_collection_id(collections_response: Any, collection_name: str) -> int:
    collections = _to_list(_get_attr(collections_response, "collections"))
    for item in collections:
        name = _get_attr(item, "name")
        if name == collection_name:
            cid = _as_int(_get_attr(item, "id"))
            if cid is not None:
                return cid
    raise RuntimeError(f"Collection '{collection_name}' wurde nicht gefunden.")


def _extract_file_ids_from_collection_detail(collection_detail: Any) -> List[int]:
    collection_obj = _get_attr(collection_detail, "collection") or collection_detail
    ids: List[int] = []

    for key in ("fileIDs", "fileIds", "filesIDs", "filesIds"):
        raw_ids = _to_list(_get_attr(collection_obj, key))
        for raw_id in raw_ids:
            file_id = _as_int(raw_id)
            if file_id is not None:
                ids.append(file_id)

    for key in ("files", "previewFiles"):
        for file_item in _to_list(_get_attr(collection_obj, key)):
            file_id = _as_int(_get_attr(file_item, "id"))
            if file_id is not None:
                ids.append(file_id)

    return sorted(set(ids))


def _extract_preview_file_entries(collection_detail: Any) -> List[Tuple[int, str]]:
    collection_obj = _get_attr(collection_detail, "collection") or collection_detail
    entries: List[Tuple[int, str]] = []
    for item in _to_list(_get_attr(collection_obj, "previewFiles")):
        file_id = _as_int(_get_attr(item, "id"))
        file_name = _get_attr(item, "fileName")
        if file_id is not None and file_name:
            entries.append((file_id, str(file_name)))
    # Keep order, remove duplicates by id.
    dedup: List[Tuple[int, str]] = []
    seen = set()
    for file_id, file_name in entries:
        if file_id in seen:
            continue
        seen.add(file_id)
        dedup.append((file_id, file_name))
    return dedup


def _extract_files_from_files_response(files_response: Any) -> List[Any]:
    return _to_list(_get_attr(files_response, "files"))


def _file_belongs_to_collection(file_item: Any, collection_id: int) -> bool:
    static_collections = _to_list(_get_attr(file_item, "staticCollections"))
    for collection in static_collections:
        current_id = _as_int(_get_attr(collection, "id"))
        if current_id == collection_id:
            return True
    return False


def _extract_download_url(download_response: Any) -> Optional[str]:
    preferred_keys = (
        "url",
        "downloadURL",
        "downloadUrl",
        "directURL",
        "directUrl",
        "originalFileURL",
        "previewFileURL",
        "fileURL",
        "fileUrl",
    )

    def walk(node: Any) -> Optional[str]:
        if node is None:
            return None
        if isinstance(node, str) and node.startswith(("http://", "https://")):
            return node

        for key in preferred_keys:
            value = _get_attr(node, key)
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                return value

        if isinstance(node, dict):
            values: Iterable[Any] = node.values()
        else:
            values = [getattr(node, k) for k in vars(node).keys()] if hasattr(node, "__dict__") else []

        for value in values:
            found = walk(value)
            if found:
                return found
        return None

    return walk(download_response)


def _resolve_collection_assets(client: Client, collection_id: int) -> List[Tuple[int, str]]:
    files = File(client)
    collections = Collection(client)

    # 1) Try collection detail with preview files (works for many setups incl. dynamic collections).
    try:
        detail = collections.get(
            collection_id,
            previewFilesLimit=100000,
            previewFilesResponseFields=["id", "fileName"],
        )
        preview_entries = _extract_preview_file_entries(detail)
        if preview_entries:
            return preview_entries
    except Exception:
        # Continue with additional strategies below.
        detail = collections.get(collection_id)

    # 2) Try extracting explicit file IDs from collection detail response.
    file_ids = _extract_file_ids_from_collection_detail(detail)
    if file_ids:
        files.set_response_fields(["id", "fileName"])
        result: List[Tuple[int, str]] = []
        for file_id in file_ids:
            info = files.get(file_id)
            file_name = _get_attr(_get_attr(info, "file") or info, "fileName")
            if not file_name:
                file_name = f"asset_{file_id}"
            result.append((file_id, str(file_name)))
        return result

    # 3) Fallback: paginate all files and filter membership by staticCollections.
    files.set_response_fields(["id", "fileName", "staticCollections"])
    result: List[Tuple[int, str]] = []
    page = 1
    page_size = 200
    while True:
        response = files.get(page=page, pageSize=page_size)
        batch = _extract_files_from_files_response(response)
        if not batch:
            break

        for item in batch:
            if not _file_belongs_to_collection(item, collection_id):
                continue
            file_id = _as_int(_get_attr(item, "id"))
            file_name = _get_attr(item, "fileName")
            if file_id is not None and file_name:
                result.append((file_id, str(file_name)))

        quantity = _as_int(_get_attr(response, "quantity"))
        if quantity is not None and page * page_size >= quantity:
            break
        page += 1

    if not result:
        raise RuntimeError(
            "Es konnten keine Assets fuer die Collection ermittelt werden. "
            "Bitte pruefe API-Rechte oder passe die Response-Fields an."
        )

    # Keep deterministic output order and avoid duplicates by id.
    ordered: List[Tuple[int, str]] = []
    seen_ids = set()
    for file_id, file_name in sorted(result, key=lambda x: x[0]):
        if file_id in seen_ids:
            continue
        seen_ids.add(file_id)
        ordered.append((file_id, file_name))
    return ordered


def download_collection_assets(host: str, api_key: str, collection_name: str, output_dir: Path) -> None:
    client = Client.create_client(api_key, host)
    collections = Collection(client)
    files = File(client)

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{collection_name}_assets.csv"

    collection_list = collections.get(page=1, pageSize=1000)
    collection_id = _extract_collection_id(collection_list, collection_name)
    assets = _resolve_collection_assets(client, collection_id)

    existing_names = set()
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(["id", "Dateiname"])

        for file_id, original_file_name in assets:
            safe_name = _safe_filename(original_file_name)
            target_path = output_dir / safe_name

            stem = target_path.stem
            suffix = target_path.suffix
            idx = 1
            while target_path.name in existing_names or target_path.exists():
                target_path = output_dir / f"{stem}_{idx}{suffix}"
                idx += 1
            existing_names.add(target_path.name)

            download_response = files.download(file_id)
            download_url = _extract_download_url(download_response)
            if not download_url:
                raise RuntimeError(
                    f"Keine Download-URL fuer Asset {file_id} gefunden. Response: {download_response}"
                )

            with client.session.get(download_url, stream=True, timeout=120) as response:
                response.raise_for_status()
                with target_path.open("wb") as out_file:
                    for chunk in response.iter_content(chunk_size=1024 * 256):
                        if chunk:
                            out_file.write(chunk)

            writer.writerow([file_id, target_path.name])
            print(f"[{file_id}] gespeichert als {target_path.name}")

    print(f"\nFertig. {len(assets)} Dateien gespeichert in: {output_dir}")
    print(f"CSV-Mapping erstellt: {csv_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lade alle Assets einer PIXXIO-Collection und erstelle eine Mapping-CSV."
    )
    parser.add_argument("--host", default=os.getenv("PIXXIO_HOST", DEFAULT_HOST))
    parser.add_argument("--api-key", default=os.getenv("PIXXIO_API_KEY", DEFAULT_API_KEY))
    parser.add_argument("--collection", default=DEFAULT_COLLECTION_NAME)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))

    args = parser.parse_args()
    download_collection_assets(
        host=args.host,
        api_key=args.api_key,
        collection_name=args.collection,
        output_dir=Path(args.output_dir),
    )


if __name__ == "__main__":
    main()
