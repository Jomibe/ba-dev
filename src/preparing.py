"""

Diese Datei enthält Funktionen, welche für den ordnungsgemäßen Programmstart benötigt werden.

"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken

# Imports von Drittanbietern
import toml

# Eigene Imports
import constants
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
    if not load_config_toml():
        return False

    console("Vorbereitungen erfolgreich abgeschlossen", mode=SUCC)
    return True


def load_config_toml():
    """
    Liest die Inhalte der Datei config.toml im Programmverzeichnis ein und speichert diese in der internen Datenstruktur
    constants.config_toml.
    """

    console("Importiere Inhalt der Datei", "config.toml", mode=INFO)
    constants.config_toml = toml.load("./src/config.toml")
    console("Import erfolgreich", mode=SUCC)

    return True
