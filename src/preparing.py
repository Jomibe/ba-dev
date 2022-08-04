"""

Diese Datei enthält Funktionen, welche für den ordnungsgemäßen Programmstart benötigt werden.

"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken

# Imports von Drittanbietern

# Eigene Imports
from debugging import console
from debugging import INFO, WARN, ERR, SUCC
from telegram import telegram_reachable
from graylog import graylog_reachable
from store import restore_cur_update_id


def prepare():
    console("Starte Vorbereitungen...", mode=INFO)
    if not telegram_reachable():
        return False
    if not graylog_reachable():
        return False
    # Nach einem Programmneustart muss die zuletzt verwendete update_id geladen werden
    if not restore_cur_update_id():
        return False

    console("Vorbereitungen erfolgreich abgeschlossen", mode=SUCC)
    return True
