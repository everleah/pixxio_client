#!/usr/bin/env python3
"""
Upload only changed InDesign files back to PIXXIO by replacing existing assets.

Inputs:
- examples/data/apply_pixxio_labels.changed.txt  (one filename per line)
- examples/data/hoerl_InDesign_Dokumente_assets.csv (id;Dateiname)

Behavior:
- Resolve PIXXIO file ID by exact filename match from CSV.
- Upload local file from input directory.
- Replace existing PIXXIO asset using replaceID.
"""

from __future__ import annotations

import argparse
import csv
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pixxio_client import Client
from pixxio_client.files import File


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_DIR = SCRIPT_DIR / "data"
DEFAULT_CHANGED_TXT = DEFAULT_INPUT_DIR / "apply_pixxio_labels.changed.txt"
DEFAULT_ASSETS_CSV = DEFAULT_INPUT_DIR / "hoerl_InDesign_Dokumente_assets.csv"


@dataclass
class UploadResult:
    file_name: str
    file_id: Optional[int]
    status: str
    details: str


def _read_changed_file_names(changed_txt: Path) -> List[str]:
    changed_txt = changed_txt.resolve()
    if not changed_txt.exists():
        raise FileNotFoundError(f"Changed-Datei nicht gefunden: {changed_txt}")

    names: List[str] = []
    for line in changed_txt.read_text(encoding="utf-8").splitlines():
        name = line.strip()
        if not name:
            continue
        names.append(name)

    # Keep order, deduplicate.
    seen = set()
    deduped: List[str] = []
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        deduped.append(name)
    return deduped


def _read_asset_id_by_name(assets_csv: Path) -> Dict[str, int]:
    assets_csv = assets_csv.resolve()
    if not assets_csv.exists():
        raise FileNotFoundError(f"Assets-CSV nicht gefunden: {assets_csv}")

    mapping: Dict[str, int] = {}
    with assets_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        required = {"id", "Dateiname"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise RuntimeError("CSV-Header ungueltig. Erwartet: id;Dateiname")

        for row in reader:
            raw_id = (row.get("id") or "").strip()
            name = (row.get("Dateiname") or "").strip()
            if not raw_id or not name:
                continue
            try:
                mapping[name] = int(raw_id)
            except ValueError:
                continue

    return mapping


def upload_changed_files(
    input_dir: Path,
    changed_txt: Path,
    assets_csv: Path,
    host: str,
    api_key: str,
    dry_run: bool,
    limit: Optional[int],
) -> Tuple[List[UploadResult], int, int, int]:
    input_dir = input_dir.resolve()
    changed_names = _read_changed_file_names(changed_txt)
    id_by_name = _read_asset_id_by_name(assets_csv)

    if limit is not None and limit >= 0:
        changed_names = changed_names[:limit]

    client = Client.create_client(api_key, host)
    files = File(client)

    results: List[UploadResult] = []
    uploaded = 0
    missing_local = 0
    missing_id = 0

    for file_name in changed_names:
        local_path = input_dir / file_name

        if not local_path.exists():
            missing_local += 1
            results.append(
                UploadResult(
                    file_name=file_name,
                    file_id=None,
                    status="missing-local-file",
                    details=f"Nicht gefunden: {local_path}",
                )
            )
            continue

        file_id = id_by_name.get(file_name)
        if file_id is None:
            missing_id += 1
            results.append(
                UploadResult(
                    file_name=file_name,
                    file_id=None,
                    status="missing-id",
                    details="Dateiname nicht in Assets-CSV gefunden",
                )
            )
            continue

        if dry_run:
            uploaded += 1
            results.append(
                UploadResult(
                    file_name=file_name,
                    file_id=file_id,
                    status="dry-run",
                    details="Upload uebersprungen (dry-run)",
                )
            )
            print(f"[DRY-RUN] {file_name} -> replaceID={file_id}")
            continue

        try:
            # Replace existing PIXXIO file by its ID.
            files.upload_and_wait(str(local_path), replaceID=file_id)
            uploaded += 1
            results.append(
                UploadResult(
                    file_name=file_name,
                    file_id=file_id,
                    status="uploaded",
                    details="OK",
                )
            )
            print(f"[OK] {file_name} -> replaceID={file_id}")
        except Exception as exc:
            results.append(
                UploadResult(
                    file_name=file_name,
                    file_id=file_id,
                    status="upload-failed",
                    details=str(exc),
                )
            )
            print(f"[FAIL] {file_name} -> replaceID={file_id}: {exc}")

    return results, uploaded, missing_local, missing_id


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload geaenderte INDD-Dateien zurueck nach PIXXIO (replaceID)."
    )
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--changed-txt", default=str(DEFAULT_CHANGED_TXT))
    parser.add_argument("--assets-csv", default=str(DEFAULT_ASSETS_CSV))
    parser.add_argument("--host", default=os.getenv("PIXXIO_HOST"),
                        help="PIXXIO host; defaults to the PIXXIO_HOST environment variable")
    parser.add_argument("--api-key", default=os.getenv("PIXXIO_API_KEY"),
                        help="PIXXIO API key; defaults to the PIXXIO_API_KEY environment variable")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--error-log",
        default=str(DEFAULT_INPUT_DIR / "upload_changed_indd_files.errors.txt"),
    )

    args = parser.parse_args()
    if not args.host:
        parser.error("--host is required (or set the PIXXIO_HOST environment variable)")
    if not args.api_key:
        parser.error("--api-key is required (or set the PIXXIO_API_KEY environment variable)")

    results, uploaded, missing_local, missing_id = upload_changed_files(
        input_dir=Path(args.input_dir),
        changed_txt=Path(args.changed_txt),
        assets_csv=Path(args.assets_csv),
        host=args.host,
        api_key=args.api_key,
        dry_run=args.dry_run,
        limit=args.limit,
    )

    total = len(results)
    failed = sum(1 for r in results if r.status == "upload-failed")

    print("\nUpload-Statistik")
    print(f"Eintraege verarbeitet: {total}")
    print(f"Erfolgreich (oder dry-run): {uploaded}")
    print(f"Fehlende lokale Datei: {missing_local}")
    print(f"Fehlende PIXXIO-ID: {missing_id}")
    print(f"Upload-Fehler: {failed}")

    if failed > 0 or missing_local > 0 or missing_id > 0:
        error_log = Path(args.error_log).resolve()
        error_log.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"{r.file_name};{r.file_id if r.file_id is not None else ''};{r.status};{r.details}"
            for r in results
            if r.status in {"missing-local-file", "missing-id", "upload-failed"}
        ]
        error_log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Fehlerdetails: {error_log}")


if __name__ == "__main__":
    main()
