#!/usr/bin/env python3
"""
Apply PIXXIO labels to links and documents in InDesign files via COM.

Reads mapping rows from CSV with columns:
- dateiname;fileID;quality;md5sum;pluginPath

For each linked image in each .indd file, sets link labels when a mapping exists:
- pixxio.fileID
- pixxio.quality
- pixxio.md5sum

For each .indd document, sets a document label when a mapping exists in
hoerl_InDesign_Dokumente_assets.csv:
- pixxio.fileID

Documents are saved after changes.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass
class MappingRow:
    file_id: str
    quality: str
    md5sum: str
    plugin_path: str


def _clean_plugin_path(value: str) -> str:
    text = (value or "").strip().strip('"').strip("'")
    # Defensive cleanup for accidental markdown wrappers like: [C:/path/file.ext]()
    if text.startswith("[") and text.endswith("]()"):
        text = text[1:-3].strip()
    elif text.startswith("[") and text.endswith("]"):
        text = text[1:-1].strip()
    if text.startswith("file:"):
        text = text[5:]
    return text


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
            return win32com.client.DispatchEx(prog_id)
        except Exception as exc:
            last_error = exc

    raise RuntimeError(
        "InDesign COM konnte nicht gestartet werden. "
        f"Versuchte ProgIDs: {prog_ids}. Letzter Fehler: {last_error}"
    )


def _suppress_dialogs(app) -> None:
    """
    Reduce interactive prompts in InDesign during batch processing.
    """
    never_interact_fallback = 1699640946  # idNeverInteract

    try:
        import win32com.client  # type: ignore
        constants = win32com.client.constants
    except Exception:
        constants = None

    candidates: List[int] = []
    if constants is not None:
        for attr in ("idNeverInteract", "neverInteract"):
            value = getattr(constants, attr, None)
            if value is not None:
                candidates.append(int(value))
    candidates.append(never_interact_fallback)

    script_prefs = getattr(app, "ScriptPreferences", None)
    if script_prefs is not None:
        for candidate in candidates:
            try:
                script_prefs.UserInteractionLevel = candidate
                break
            except Exception:
                continue

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


def _disable_resource_checks(app) -> None:
    """
    Deaktiviere Link- und Font-Validierung beim Speichern.
    Ermöglicht Speichern auch wenn Ressourcen fehlen (da wir nur Labels ändern).
    """
    try:
        # Setze LinkUpdateOptions auf "never" (1282 = idNeverUpdateLinks)
        app.LinkUpdateOptions = 1282
    except Exception:
        pass  # Fehler hier sind unkritisch
    
    try:
        # Deaktiviere Preflight-Prüfungen wenn möglich
        prefs = app.Preferences
        if prefs is not None:
            # Versuche PreflightOptions zu setzen
            preflight = getattr(prefs, "PreflightOptions", None)
            if preflight is not None:
                preflight.PreflightOption = 1619  # idPreflightOff
    except Exception:
        pass  # Fehler hier sind unkritisch


def _close_document_without_prompt(document) -> None:
    try:
        # SaveOptions.no
        document.Close(1852776480)
    except Exception:
        try:
            document.Close()
        except Exception:
            pass


def _read_mapping_csv(mapping_csv: Path) -> Dict[str, MappingRow]:
    mapping_csv = mapping_csv.resolve()
    if not mapping_csv.exists():
        raise FileNotFoundError(f"Mapping CSV nicht gefunden: {mapping_csv}")

    lookup: Dict[str, MappingRow] = {}
    with mapping_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        required = {"dateiname", "fileID", "quality", "md5sum", "pluginPath"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise RuntimeError(
                "CSV-Header ungueltig. Erwartet: dateiname;fileID;quality;md5sum;pluginPath"
            )

        for row in reader:
            filename = (row.get("dateiname") or "").strip()
            file_id = (row.get("fileID") or "").strip()
            quality = (row.get("quality") or "").strip()
            md5sum = (row.get("md5sum") or "").strip()
            plugin_path = _clean_plugin_path((row.get("pluginPath") or "").strip())

            if not filename:
                continue
            if not file_id:
                # Not found entries are intentionally skipped.
                continue

            if not quality:
                quality = "original"
            if not md5sum:
                md5sum = filename

            lookup[filename.lower()] = MappingRow(
                file_id=file_id,
                quality=quality,
                md5sum=md5sum,
                plugin_path=plugin_path,
            )

    return lookup


def _read_document_file_ids_csv(assets_csv: Path) -> Dict[str, str]:
    assets_csv = assets_csv.resolve()
    if not assets_csv.exists():
        raise FileNotFoundError(f"Assets CSV nicht gefunden: {assets_csv}")

    lookup: Dict[str, str] = {}
    with assets_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        required = {"id", "Dateiname"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise RuntimeError(
                "Assets CSV-Header ungueltig. Erwartet: id;Dateiname"
            )

        for row in reader:
            file_id = (row.get("id") or "").strip()
            file_name = (row.get("Dateiname") or "").strip()
            if not file_id or not file_name:
                continue
            lookup[file_name.lower()] = file_id

    return lookup


def _resolve_label_target_from_link(link):
    """
    Return the best label target for a link, preferring the link itself.

    The PIXXIO InDesign plugin reads labels from the Link object in IDML,
    so we write there first and only fall back if the COM object does not
    expose InsertLabel directly.
    """
    if hasattr(link, "InsertLabel"):
        return link

    current = getattr(link, "Parent", None)
    chain = []
    for _ in range(6):
        if current is None:
            break
        chain.append(current)
        current = getattr(current, "Parent", None)

    frame_type_names = {
        "rectangle",
        "oval",
        "polygon",
        "textframe",
        "group",
        "splineitem",
    }

    # Prefer known frame-like objects.
    for obj in chain:
        if not hasattr(obj, "InsertLabel"):
            continue
        try:
            constructor = getattr(obj, "Constructor", None)
            type_name = str(getattr(constructor, "Name", "")).lower()
        except Exception:
            type_name = ""
        if type_name in frame_type_names:
            return obj

    # Fallback to first object that supports InsertLabel.
    for obj in chain:
        if hasattr(obj, "InsertLabel"):
            return obj

    return None


def _extract_link_name(link) -> Optional[str]:
    try:
        name = str(link.Name)
    except Exception:
        return None
    if not name:
        return None
    return Path(name).name


def _normalize_path_text(path_text: str) -> str:
    return path_text.replace("\\", "/").strip().lower()


def _extract_link_source_path(link) -> Optional[str]:
    for attr in ("FilePath", "filePath", "LinkResourceURI", "linkResourceURI", "AssetURL", "assetURL"):
        value = getattr(link, attr, None)
        if not value:
            continue
        text = str(value)
        if text.startswith("file:"):
            text = text[5:]
        if text:
            return text
    return None


def _escape_js_string(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", "")
        .replace("\n", "\\n")
    )


def _try_relink_via_js(app: Any, document_name: str, link_index_1_based: int, relink_path: Path) -> Tuple[bool, str]:
    link_index_0_based = link_index_1_based - 1
    file_path = _escape_js_string(str(relink_path.resolve()).replace("\\", "/"))
    doc_name = _escape_js_string(document_name)
    script = (
        f'var d=app.documents.itemByName("{doc_name}");'
        f'var l=d.links[{link_index_0_based}];'
        f'var f=new File("{file_path}");'
        'if(f.exists){l.relink(f);try{l.update();}catch(e){}}'
    )

    # Different COM signatures exist depending on InDesign/pywin32 versions.
    call_variants = [
        lambda: app.DoScript(script),
        lambda: app.DoScript(script, 1246973031),  # likely idJavascript
        lambda: app.DoScript(script, 1246973031, None),
    ]

    last_error: Optional[Exception] = None
    for call in call_variants:
        try:
            call()
            return True, "javascript"
        except Exception as exc:
            last_error = exc

    script_preview = script[:220]
    return False, (
        f"{last_error} | script={script_preview}..."
        if last_error
        else f"DoScript fehlgeschlagen | script={script_preview}..."
    )


def _try_relink_link(
    link: Any,
    app: Any,
    relink_path: Path,
    document_name: str,
    link_index_1_based: int,
) -> Tuple[bool, str]:
    attempts = [
        str(relink_path),
        str(relink_path.resolve()),
        str(relink_path.resolve()).replace("/", "\\"),
    ]

    last_error: Optional[Exception] = None
    for candidate in attempts:
        try:
            link.Relink(candidate)
            try:
                link.Update()
            except Exception:
                pass
            return True, candidate
        except Exception as exc:
            last_error = exc

    # Some InDesign COM installs expect a File spec object.
    try:
        file_spec = app.File(str(relink_path.resolve()))
        link.Relink(file_spec)
        try:
            link.Update()
        except Exception:
            pass
        return True, str(relink_path.resolve())
    except Exception as exc:
        last_error = exc

    # Final fallback: relink via InDesign JavaScript File() object.
    js_ok, js_detail = _try_relink_via_js(app, document_name, link_index_1_based, relink_path)
    if js_ok:
        return True, js_detail

    return False, str(last_error) if last_error else f"unbekannter Fehler / JS: {js_detail}"


def apply_labels_to_documents(
    input_dir: Path,
    mapping_csv: Path,
    assets_csv: Path,
    version: str,
    recursive: bool,
) -> Tuple[int, int, int, int, int, int, int, int, List[str], List[str]]:
    input_dir = input_dir.resolve()
    mapping = _read_mapping_csv(mapping_csv)
    document_file_ids = _read_document_file_ids_csv(assets_csv)

    app = _get_indesign_app(version)
    _suppress_dialogs(app)
    _disable_resource_checks(app)  # Ignoriere fehlende Fonts/Links beim Speichern

    docs_total = 0
    docs_opened = 0
    docs_saved = 0

    links_total = 0
    links_with_mapping = 0
    frames_labeled = 0
    links_skipped_no_mapping = 0
    label_errors = 0

    failures: List[str] = []
    changed_files: List[str] = []

    for indd_path in _iter_indd_files(input_dir, recursive=recursive):
        docs_total += 1
        document = None
        changed = False

        try:
            print(f"Oeffne: {indd_path.name}")
            document = app.Open(str(indd_path), False)
            docs_opened += 1

            # Write document-level PIXXIO label when a file ID is known.
            document_file_id = document_file_ids.get(indd_path.name.lower())
            if document_file_id:
                try:
                    document.InsertLabel("pixxio.fileID", document_file_id)
                    changed = True
                except Exception as exc:
                    label_errors += 1
                    failures.append(f"{indd_path.name} / DocumentLabel: {exc}")

            links = document.Links
            count = int(links.Count)

            for idx in range(1, count + 1):
                links_total += 1
                link = links.Item(idx)
                link_name = _extract_link_name(link)
                if not link_name:
                    links_skipped_no_mapping += 1
                    continue

                mapping_row = mapping.get(link_name.lower())
                if mapping_row is None:
                    links_skipped_no_mapping += 1
                    continue

                links_with_mapping += 1
                # Plugin-Kompatibilitaet: Relink ist best effort.
                relink_path = Path(mapping_row.plugin_path) if mapping_row.plugin_path else None
                relink_done = False
                if relink_path is None or not relink_path.exists():
                    failures.append(
                        f"{indd_path.name} / {link_name}: Relink uebersprungen (Pfad fehlt oder existiert nicht: {mapping_row.plugin_path})"
                    )
                else:
                    before_relink = _extract_link_source_path(link)
                    try:
                        relink_done, detail = _try_relink_link(
                            link,
                            app,
                            relink_path,
                            document.Name,
                            idx,
                        )
                        if relink_done:
                            changed = True
                        else:
                            failures.append(
                                f"{indd_path.name} / {link_name}: Relink fehlgeschlagen: {detail}"
                            )
                    except Exception as exc:
                        failures.append(f"{indd_path.name} / {link_name}: Relink fehlgeschlagen: {exc}")

                # Nach Relink Link erneut holen, da InDesign intern Objekte ersetzen kann.
                if relink_done:
                    try:
                        link = links.Item(idx)
                    except Exception:
                        pass

                    after_relink = _extract_link_source_path(link)
                    if after_relink:
                        expected = _normalize_path_text(str(relink_path.resolve()))
                        current = _normalize_path_text(after_relink)
                        if current != expected:
                            failures.append(
                                f"{indd_path.name} / {link_name}: Relink ohne erwartete Pfadaenderung (vorher={before_relink}, nachher={after_relink}, erwartet={relink_path})"
                            )

                target = _resolve_label_target_from_link(link)
                if target is None:
                    label_errors += 1
                    continue

                try:
                    target.InsertLabel("pixxio.fileID", mapping_row.file_id)
                    target.InsertLabel("pixxio.quality", mapping_row.quality or "original")
                    target.InsertLabel("pixxio.md5sum", mapping_row.md5sum or link_name)
                    frames_labeled += 1
                    changed = True
                except Exception as exc:
                    label_errors += 1
                    failures.append(f"{indd_path.name} / {link_name}: {exc}")

            if changed:
                try:
                    # Versuche Standard Save
                    document.Save()
                    docs_saved += 1
                    changed_files.append(indd_path.name)
                except Exception as save_exc:
                    # Fallback: Versuche SaveAs mit selben Pfad
                    try:
                        file_path = str(indd_path)
                        # SaveAs kann Format-Parameter haben, aber mit selben Pfad sollte es funktionieren
                        document.Save(file_path,False,"pixxio labels added",True)
                        docs_saved += 1
                        changed_files.append(indd_path.name)
                        #print(f"Datei {indd_path.name} mit SaveAs gespeichert (Standard Save fehlgeschlagen)")
                    except Exception as saveas_exc:
                        # SaveAs auch fehlgeschlagen - dokumentieren
                        exc_str = str(save_exc)
                        failures.append(f"{indd_path.name} (Speichern): InDesign Save/SaveAs fehlgeschlagen - Link-/Ressourcen-Problem - {exc_str[:100]}")

        except Exception as exc:
            exc_str = str(exc)
            if "Vorgang vom Benutzer abgebrochen" in exc_str or "user" in exc_str.lower():
                failures.append(f"{indd_path.name}: Link-Problem oder Verarbeitungsabbruch (Bildverknuepfung/Datenzugriff fehlgeschlagen?) - Details: {exc}")
                print(f"Link-Problem bei {indd_path.name}: {exc}")
            else:
                failures.append(f"{indd_path.name}: {exc}")
                print(f"FEHLER bei {indd_path.name}: {exc}")
        finally:
            if document is not None:
                _close_document_without_prompt(document)

    try:
        app.Quit()
    except Exception:
        pass

    return (
        docs_total,
        docs_opened,
        docs_saved,
        links_total,
        links_with_mapping,
        frames_labeled,
        links_skipped_no_mapping,
        label_errors,
        failures,
        changed_files,
    )


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    default_input = script_dir / "data"
    default_mapping = script_dir / "data" / "pixxio_image_asset_mapping.csv"
    default_assets = script_dir / "data" / "hoerl_InDesign_Dokumente_assets.csv"

    parser = argparse.ArgumentParser(
        description="Setzt Pixxio Labels auf Bildrahmen in INDD-Dateien via COM."
    )
    parser.add_argument("--input-dir", default=str(default_input))
    parser.add_argument("--mapping-csv", default=str(default_mapping))
    parser.add_argument("--assets-csv", default=str(default_assets))
    parser.add_argument("--indesign-version", default="2026")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument(
        "--error-log",
        default=str(script_dir / "data" / "apply_pixxio_labels.errors.txt"),
    )

    args = parser.parse_args()

    (
        docs_total,
        docs_opened,
        docs_saved,
        links_total,
        links_with_mapping,
        frames_labeled,
        links_skipped_no_mapping,
        label_errors,
        failures,
        changed_files,
    ) = apply_labels_to_documents(
        input_dir=Path(args.input_dir),
        mapping_csv=Path(args.mapping_csv),
        assets_csv=Path(args.assets_csv),
        version=args.indesign_version,
        recursive=args.recursive,
    )

    print("\nStatistik")
    print(f"Dokumente gefunden: {docs_total}")
    print(f"Dokumente geoeffnet: {docs_opened}")
    print(f"Dokumente gespeichert (geaendert): {docs_saved}")
    print(f"Links gesamt: {links_total}")
    print(f"Links mit Mapping: {links_with_mapping}")
    print(f"Bildrahmen gelabelt: {frames_labeled}")
    print(f"Links ohne Mapping uebersprungen: {links_skipped_no_mapping}")
    print(f"Label-Fehler: {label_errors}")

    if changed_files:
        changed_log = Path(args.error_log).parent / "apply_pixxio_labels.changed.txt"
        changed_log.write_text("\n".join(changed_files) + "\n", encoding="utf-8")
        print(f"\nGeaenderte Dateien ({len(changed_files)}): {changed_log}")

    if failures:
        error_log = Path(args.error_log).resolve()
        error_log.parent.mkdir(parents=True, exist_ok=True)
        error_log.write_text("\n".join(failures) + "\n", encoding="utf-8")
        print(f"Fehlerdetails ({len(failures)}): {error_log}")


if __name__ == "__main__":
    main()
