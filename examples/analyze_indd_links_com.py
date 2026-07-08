#!/usr/bin/env python3
"""
Analyze InDesign documents via COM and extract unique linked image filenames.

Workflow:
1. Start Adobe InDesign (2026 if available, fallback to generic app id)
2. Open every .indd file in a folder
3. Read linked assets in each document
4. Keep only image-like link names (configurable)
5. Write unique filenames to an output text file (one filename per line)
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Set, Tuple


IMAGE_EXTENSIONS = {
    ".ai",
    ".bmp",
    ".eps",
    ".gif",
    ".heic",
    ".heif",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".psd",
    ".svg",
    ".tif",
    ".tiff",
    ".webp",
}


def _get_indesign_app(version: str):
    try:
        import win32com.client  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "pywin32 fehlt. Bitte in der venv installieren: pip install pywin32"
        ) from exc

    prog_ids = [f"InDesign.Application.{version}", "InDesign.Application"]
    last_error = None

    for prog_id in prog_ids:
        try:
            app = win32com.client.DispatchEx(prog_id)
            return app
        except Exception as exc:
            last_error = exc

    raise RuntimeError(
        "InDesign COM konnte nicht gestartet werden. "
        f"Versuchte ProgIDs: {prog_ids}. Letzter Fehler: {last_error}"
    )


def _suppress_dialogs(app) -> None:
    """
    Reduce user interaction prompts in InDesign during batch runs.

    We try multiple approaches because available COM constants may differ per
    installation and generated typelibs.
    """
    # InDesign constant for idNeverInteract (fallback integer value).
    NEVER_INTERACT_FALLBACK = 1699640946

    try:
        import win32com.client  # type: ignore
        constants = win32com.client.constants
    except Exception:
        constants = None

    candidates = []
    if constants is not None:
        for attr in ("idNeverInteract", "neverInteract"):
            value = getattr(constants, attr, None)
            if value is not None:
                candidates.append(value)
    candidates.append(NEVER_INTERACT_FALLBACK)

    # Variant 1: app.ScriptPreferences.UserInteractionLevel
    script_prefs = getattr(app, "ScriptPreferences", None)
    if script_prefs is not None:
        for candidate in candidates:
            try:
                script_prefs.UserInteractionLevel = candidate
                break
            except Exception:
                continue

    # Variant 2: direct app-level property (not always available)
    for candidate in candidates:
        try:
            app.UserInteractionLevel = candidate
            break
        except Exception:
            continue


def _iter_indd_files(folder: Path, recursive: bool) -> Iterable[Path]:
    pattern = "**/*.indd" if recursive else "*.indd"
    for path in sorted(folder.glob(pattern)):
        if path.is_file():
            yield path.resolve()


def _is_image_filename(name: str) -> bool:
    suffix = Path(name).suffix.lower()
    return suffix in IMAGE_EXTENSIONS


def _extract_link_names(document) -> List[str]:
    names: List[str] = []
    links = document.Links
    count = int(links.Count)

    # InDesign COM collections are 1-based.
    for idx in range(1, count + 1):
        link = links.Item(idx)
        try:
            link_name = str(link.Name)
        except Exception:
            continue
        names.append(Path(link_name).name)

    return names


def _close_document_without_save(document) -> None:
    try:
        # SaveOptions.no (idNo) integer fallback to avoid dialog prompts.
        document.Close(1852776480)
    except Exception:
        try:
            document.Close()
        except Exception:
            pass


def analyze_documents(
    input_dir: Path,
    output_file: Path,
    version: str,
    recursive: bool,
    include_non_images: bool,
) -> Tuple[int, int, Set[str], List[str]]:
    input_dir = input_dir.resolve()
    output_file = output_file.resolve()

    app = _get_indesign_app(version)
    _suppress_dialogs(app)

    unique_names: Set[str] = set()
    processed = 0
    failed: List[str] = []

    files = list(_iter_indd_files(input_dir, recursive=recursive))
    if not files:
        raise RuntimeError(f"Keine .indd Dateien gefunden in: {input_dir}")

    for indd_path in files:
        document = None
        try:
            print(f"Oeffne: {indd_path.name}")
            document = app.Open(str(indd_path), False)
            link_names = _extract_link_names(document)

            for name in link_names:
                if include_non_images or _is_image_filename(name):
                    unique_names.add(name)

            processed += 1
        except Exception as exc:
            failed.append(f"{indd_path.name}: {exc}")
            print(f"FEHLER bei {indd_path.name}: {exc}")
        finally:
            if document is not None:
                _close_document_without_save(document)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        "\n".join(sorted(unique_names, key=lambda s: s.lower())) + "\n",
        encoding="utf-8",
    )

    try:
        app.Quit()
    except Exception:
        pass

    return len(files), processed, unique_names, failed


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    default_input = script_dir / "data"
    default_output = script_dir / "data" / "used_image_filenames.txt"

    parser = argparse.ArgumentParser(
        description="Analysiere INDD-Dateien via InDesign COM und sammle Bild-Dateinamen."
    )
    parser.add_argument("--input-dir", default=str(default_input))
    parser.add_argument("--output-file", default=str(default_output))
    parser.add_argument("--indesign-version", default="2026")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument(
        "--include-non-images",
        action="store_true",
        help="Wenn gesetzt, werden alle Link-Dateien gesammelt, nicht nur Bilder.",
    )

    args = parser.parse_args()

    total, processed, unique_names, failed = analyze_documents(
        input_dir=Path(args.input_dir),
        output_file=Path(args.output_file),
        version=args.indesign_version,
        recursive=args.recursive,
        include_non_images=args.include_non_images,
    )

    print("\nAnalyse abgeschlossen")
    print(f"Gefundene Dokumente: {total}")
    print(f"Erfolgreich analysiert: {processed}")
    print(f"Unique Dateinamen: {len(unique_names)}")
    print(f"Ausgabe: {Path(args.output_file)}")

    if failed:
        error_file = Path(args.output_file).with_suffix(".errors.txt")
        error_file.write_text("\n".join(failed) + "\n", encoding="utf-8")
        print(f"Fehler in {len(failed)} Dokumenten. Details: {error_file}")


if __name__ == "__main__":
    main()
