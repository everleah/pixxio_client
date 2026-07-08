#!/usr/bin/env python3
"""
Build a CSV mapping for image filenames against PIXXIO assets.

Input:
- A text file with one filename per line, e.g. examples/data/used_image_filenames.txt

Output CSV columns:
- dateiname;fileID;quality;md5sum;pluginPath

Rules:
- Match assets by fileName in PIXXIO.
- If no asset is found: fileID/quality/md5sum stay empty.
- If asset is found but quality missing: use "original".
- If asset is found but md5sum missing: use dateiname.
- pluginPath points to the local PIXXIO plugin storage target path based on APPDATA:
    <APPDATA>/Adobe/UXP/PluginsStorage/IDSN/21/External/6d78b396/PluginData/{fileID}_original/{dateiname}
- The pluginPath directory is created and the original asset is downloaded there.
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from pixxio_client import Client
from pixxio_client.files import File


DEFAULT_HOST = "https://weru.px.media/"
DEFAULT_API_KEY = "2AoXVLvsT4yJm0Tc5kMuu3Pji12QYNqKV2940RAUG3ojlGp9HVjahwpEjUqZRecy"
DEFAULT_INPUT = Path(__file__).resolve().parent / "data" / "used_image_filenames.txt"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "data" / "pixxio_image_asset_mapping.csv"


def _get_roaming_appdata_path() -> Path:
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata)

    # Fallback for uncommon shells where APPDATA is missing.
    return Path.home() / "AppData" / "Roaming"


def _build_plugin_path(file_id: str, file_name: str, appdata_roaming: Path) -> str:
    plugin_path = (
        appdata_roaming
        / "Adobe"
        / "UXP"
        / "PluginsStorage"
        / "IDSN"
        / "21"
        / "External"
        / "6d78b396"
        / "PluginData"
        / f"{file_id}_original"
        / file_name
    )
    return str(plugin_path).replace("\\", "/")


def _get_attr(obj: Any, *names: str) -> Any:
    for name in names:
        if isinstance(obj, dict) and name in obj:
            return obj.get(name)
        value = getattr(obj, name, None)
        if value is not None:
            return value
    return None


def _to_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _as_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


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


def _download_asset_to_path(client: Client, files_resource: File, file_id: str, target_path: Path) -> None:
    download_response = files_resource.download(int(file_id))
    download_url = _extract_download_url(download_response)
    if not download_url:
        raise RuntimeError(f"Keine Download-URL fuer Asset {file_id} gefunden")

    target_path.parent.mkdir(parents=True, exist_ok=True)

    with client.session.get(download_url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with target_path.open("wb") as out_file:
            for chunk in response.iter_content(chunk_size=1024 * 256):
                if chunk:
                    out_file.write(chunk)
    
    print(f"Asset {file_id} heruntergeladen nach: {target_path}")


def _read_filenames(input_file: Path) -> List[str]:
    if not input_file.exists():
        raise FileNotFoundError(f"Eingabedatei nicht gefunden: {input_file}")

    lines = [line.strip() for line in input_file.read_text(encoding="utf-8").splitlines()]
    filenames = [line for line in lines if line]
    # Ensure uniqueness while preserving order.
    seen = set()
    ordered_unique = []
    for name in filenames:
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered_unique.append(name)
    return ordered_unique


def _iter_all_files(files_resource: File, page_size: int = 500) -> Iterable[Any]:
    page = 1
    while True:
        response = files_resource.get(page=page, pageSize=page_size)
        batch = _to_list(_get_attr(response, "files"))
        if not batch:
            break

        for item in batch:
            yield item

        quantity = _as_int(_get_attr(response, "quantity"))
        if quantity is not None and page * page_size >= quantity:
            break
        page += 1


def _build_lookup(client: Client) -> Dict[str, List[Dict[str, Any]]]:
    files = File(client)
    files.set_response_fields(["id", "fileName", "md5sum", "uploadDate", "quality"])

    lookup: Dict[str, List[Dict[str, Any]]] = {}
    for item in _iter_all_files(files):
        file_name = _get_attr(item, "fileName")
        file_id = _as_int(_get_attr(item, "id"))
        if not file_name or file_id is None:
            continue

        normalized = str(file_name).lower()
        entry = {
            "fileName": str(file_name),
            "id": file_id,
            "quality": _get_attr(item, "quality"),
            "md5sum": _get_attr(item, "md5sum"),
            "uploadDate": _get_attr(item, "uploadDate"),
        }
        lookup.setdefault(normalized, []).append(entry)

    # Deterministic preference: newest ID first.
    for key in lookup:
        lookup[key].sort(key=lambda x: int(x["id"]), reverse=True)

    return lookup


def _map_filename(name: str, lookup: Dict[str, List[Dict[str, Any]]]) -> Tuple[str, str, str]:
    candidates = lookup.get(name.lower(), [])
    if not candidates:
        return "", "", ""

    asset = candidates[0]
    file_id = str(asset["id"])

    quality = _get_attr(asset, "quality")
    quality_value = str(quality) if quality else "original"

    md5 = _get_attr(asset, "md5sum")
    md5_value = str(md5) if md5 else name

    return file_id, quality_value, md5_value


def build_mapping_csv(host: str, api_key: str, input_file: Path, output_file: Path) -> Tuple[int, int, int, int]:
    input_file = input_file.resolve()
    output_file = output_file.resolve()

    filenames = _read_filenames(input_file)
    if not filenames:
        raise RuntimeError(f"Keine Dateinamen in Eingabedatei: {input_file}")

    client = Client.create_client(api_key, host)
    lookup = _build_lookup(client)
    files = File(client)
    appdata_roaming = _get_roaming_appdata_path()

    output_file.parent.mkdir(parents=True, exist_ok=True)

    found_count = 0
    downloaded_count = 0
    download_failed = 0
    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["dateiname", "fileID", "quality", "md5sum", "pluginPath"])

        for name in filenames:
            file_id, quality, md5sum = _map_filename(name, lookup)
            if file_id:
                found_count += 1
            plugin_path = _build_plugin_path(file_id, name, appdata_roaming) if file_id else ""
            writer.writerow([name, file_id, quality, md5sum, plugin_path])

            if not file_id:
                continue

            try:
                _download_asset_to_path(client, files, file_id, Path(plugin_path))
                downloaded_count += 1
            except Exception as exc:
                download_failed += 1
                print(f"[WARN] Download fehlgeschlagen fuer {name} (ID {file_id}): {exc}")

    return len(filenames), found_count, downloaded_count, download_failed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Erstellt dateiname->Pixxio Asset CSV (fileID, quality, md5sum)."
    )
    parser.add_argument("--host", default=os.getenv("PIXXIO_HOST", DEFAULT_HOST))
    parser.add_argument("--api-key", default=os.getenv("PIXXIO_API_KEY", DEFAULT_API_KEY))
    parser.add_argument("--input-file", default=str(DEFAULT_INPUT))
    parser.add_argument("--output-file", default=str(DEFAULT_OUTPUT))

    args = parser.parse_args()

    total, found, downloaded, download_failed = build_mapping_csv(
        host=args.host,
        api_key=args.api_key,
        input_file=Path(args.input_file),
        output_file=Path(args.output_file),
    )

    print(f"Fertig. Gesamt: {total}, mit Asset gefunden: {found}, ohne Treffer: {total - found}")
    print(f"Downloads erfolgreich: {downloaded}, Download-Fehler: {download_failed}")
    print(f"CSV: {Path(args.output_file)}")


if __name__ == "__main__":
    main()
