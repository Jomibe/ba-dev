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
    if not determine_max_len_config_toml():
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


def determine_max_len_config_toml():
    """
    Diese Funktion ermittelt, wie viele Wörter die Bezeichner in den Sektionsbezeichnungen und Schlüsselnamen der
    Konfigurationsdatei config.toml maximal enthalten und schreibt diese Werte in globale Variablen. Die Werte werden
    für die Texterkennung benötigt.
    """

    console("Prüfe maximale Wortanzahl von Typ- und Eigenschaftsbezeichnungen der Konfigurationsdatei", mode=INFO)
    for typ in constants.config_toml.keys():
        console("Prüfe Typ", typ, mode=INFO)
        if len(typ.split()) > constants.max_len_type_names:
            console("Typ", typ, "erhöht die maximale Wortanzahl von Typbezeichnungen auf", len(typ.split()), mode=SUCC)
            constants.max_len_type_names = len(typ.split())

        for eigenschaft in constants.config_toml[typ].keys():
            console("Prüfe Eigenschaft", eigenschaft, mode=INFO)
            if len(eigenschaft.split()) > constants.max_len_property_names:
                console("Eigenschaft", eigenschaft, "erhöht die maximale Wortanzahl von Eigenschaftsbezeichnungen auf",
                        len(eigenschaft.split()), mode=SUCC)
                constants.max_len_property_names = len(eigenschaft.split())

    console("Prüfung erfolgreich. Maximale Wortanzahl Typbezeichnungen:", constants.max_len_type_names,
            ". Maximale Wortanzahl Eigenschaftsbezeichnungen:", constants.max_len_property_names, mode=SUCC)

    return True
