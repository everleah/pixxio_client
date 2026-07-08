#!/usr/bin/env python3
"""
Diagnose: Versuche zu ermitteln, welche Dateien beschädigte Links/Fonts haben.

Diese Dateien öffnen in InDesign, die "Verknüpfungen reparieren" UI starten,
und dann speichern. Danach können wir die Labels anwenden.
"""

from pathlib import Path
import time


def _get_indesign_app():
    try:
        import win32com.client
    except ImportError as exc:
        raise RuntimeError("pywin32 fehlt") from exc
    
    return win32com.client.DispatchEx("InDesign.Application")


def diagnose_failing_files(indd_list_path: Path):
    """
    Öffne die Dateien die beim Speichern fehlschlagen und versuche die Fehler zu beheben.
    """
    indd_list_path = indd_list_path.resolve()
    
    # Lese die Liste der fehlgeschlagenen Dateien
    with open(indd_list_path) as f:
        failing_files = [line.strip() for line in f if line.strip()]
    
    app = _get_indesign_app()
    
    # Deaktiviere Dialoge
    try:
        app.ScriptPreferences.UserInteractionLevel = 1699640946
    except:
        pass
    
    base_dir = Path("examples/data")
    
    for filename in failing_files[:5]:  # Test mit ersten 5
        indd_path = base_dir / filename
        if not indd_path.exists():
            print(f"Nicht gefunden: {filename}")
            continue
        
        print(f"\nÖffne: {filename}")
        try:
            doc = app.Open(str(indd_path.resolve()), False)
            
            # Versuche Links zu reparieren
            print(f"  - Links: {doc.Links.Count}")
            
            # Versuche zu speichern
            doc.Save()
            print(f"  ✓ Gespeichert!")
            
            doc.Close(1852776480)  # SaveOptions.no
            
        except Exception as e:
            print(f"  ✗ Fehler: {e}")
            try:
                if doc:
                    doc.Close(1852776480)
            except:
                pass


if __name__ == "__main__":
    # Nutze die Fehler-Liste von der vorherigen Ausführung
    diagnose_failing_files(Path("examples/data/apply_pixxio_labels.errors.txt"))
