"""

Diese Datei enthält Funktionen, welche für das Persistieren von Daten auf dem Dateisystem benötigt werden.

"""

# Imports aus Standardbibliotheken
from pathlib import Path

# Imports von Drittanbietern

# Eigene Imports
import constants
from constants import STOREFILE
from debugging import console
from debugging import INFO, WARN, ERR, SUCC


def store_cur_update_id(cur_update_id):
    """
    Speichert die aktuelle update_id der Telegram API in der dafür vorgesehenen Datei.
    """
    console("Aktuelle update_id", cur_update_id, "speichern...", mode=INFO)

    with open(STOREFILE, "w", encoding='utf-8') as f:
        f.write(str(cur_update_id))
        console("Speichern der aktuellen update_id", cur_update_id, "abgeschlossen.", mode=SUCC)


def restore_cur_update_id():
    """
    Gibt die aktuelle update_id der Telegram API als Ganzzahl zurück.
    """
    console("Wiederherstellen der aktuellen update_id...", mode=INFO)

    console("Prüfe, ob die Datei", STOREFILE, "existiert. Datei wird falls notwendig erstellt.", mode=INFO)
    p = Path(STOREFILE)

    p.touch(exist_ok=True)

    if not p.exists():
        console("Der Pfad", STOREFILE, "existiert nicht.", mode=ERR)
        return False

    if not p.is_file():
        console("Der Pfad", STOREFILE, "ist keine Datei.", mode=ERR)
        return False

    console("Die Datei existiert.", mode=SUCC)

    with open(STOREFILE, encoding='utf-8') as f:
        try:
            cur_update_id = int(f.read())
        except ValueError:
            console("Es ist keine gültige Update-ID in der Datei", STOREFILE, "hinterlegt", mode=WARN)
            cur_update_id = 1
        console("Wiederherstellung der aktuellen update_id", cur_update_id, "abgeschlossen.", mode=SUCC)

    constants.telegram_update_id = cur_update_id

    return True
