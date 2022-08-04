"""

Diese Datei enthält Funktionen, welche für das Persistieren von Daten auf dem Dateisystem benötigt werden.

"""

# Imports aus Standardbibliotheken

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

    with open(STOREFILE, encoding='utf-8') as f:
        cur_update_id = int(f.read())
        console("Wiederherstellung der aktuellen update_id", cur_update_id, "abgeschlossen.", mode=SUCC)

    constants.telegram_update_id = cur_update_id

    return True
