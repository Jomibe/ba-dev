"""
Diese Datei enthält Funktionen, welche für die Verarbeitung von Sprach- und Textnachrichten notwendig sind.
"""
import re

# Imports aus Standardbibliotheken

# Imports von Drittanbietern

# Eigene Imports
import constants
from constants import KEYWORDS_TIME, KEYWORDS_TYPE, KEYWORDS_PROPERTIES
from debugging import console, INFO, WARN, ERR, SUCC
from graylog import execute_query


def compare(actual, target, wordcount):
    """
    Diese Funktion prüft, ob zwei Texte miteinander übereinstimmen. Beide Parameter können aus mehreren Wörtern
    bestehen, jedoch nicht mehr als in wordcount angegeben. Es wird auch geprüft, ob target ("soll") eine Untermenge von
    actual ("ist") ist.
    """

    actual = actual.lower()
    target = target.lower()

    console("Vergleiche", actual, "und", target, "miteinander", mode=INFO)
    if actual == target:
        console("Direkte Übereinstimmung", mode=SUCC)
        return True

    for i in range(1, wordcount):
        console("Vergleiche Untermenge", ' '.join(actual.strip().split()[0:i]), "mit", target, mode=INFO)
        if ' '.join(actual.strip().split()[0:i]) == target:
            console("Übereinstimmung gefunden", mode=SUCC)
            return True

    return False


def extract_timerange(result_time):
    """
    Extrahiert Informationen zum angeforderten relativen Zeitraum aus dem übermittelten Text.
    :param message: str, Ergebnis der Schlüsselwortanalyse. Der String muss aus zwei Wörtern bestehen, wobei das erste
    Wort auch aus Ziffern bestehen kann und das zweite Wort die Zeiteinheit enthält.
    :return: int, angeforderte Zeit in Sekunden; None im Fehlerfall
    """

    console("Extrahiere Informationen zum angeforderten Zeitraum aus", result_time, mode=INFO)
    console("Ermittle Anzahl der Zeiteinheiten aus", result_time.split()[0], mode=INFO)
    count = 0
    if result_time.split()[0].isdigit():  # Prüft, ob eine Ganzzahl vorliegt
        count = int(result_time.split()[0])
    elif re.search("ein", result_time.split()[0]):
        count = 1
    else:
        console("Ermittlung der Anzahl der Zeiteinheiten nicht erfolgreich", mode=ERR)
        return None
    console("Anzahl der Zeiteinheiten wurde bestimmt:", count, mode=SUCC)

    console("Ermittle Zeiteinheit aus", result_time.split()[1], mode=INFO)
    unit = None
    if re.search("Sekunde", result_time.split()[1]):
        unit = "second"
        console("Zeiteinheit", "Sekunde", "wurde bestimmt", mode=SUCC)
        return count
    elif re.search("Minute", result_time.split()[1]):
        unit = "minute"
        console("Zeiteinheit", "Minute", "wurde bestimmt", mode=SUCC)
        return count * 60
    elif re.search("Stunde", result_time.split()[1]):
        unit = "hour"
        console("Zeiteinheit", "Stunde", "wurde bestimmt", mode=SUCC)
        return count * 3600
    elif re.search("Tag", result_time.split()[1]):
        unit = "day"
        console("Zeiteinheit", "Tag", "wurde bestimmt", mode=SUCC)
        return count * 86400
    elif re.search("Woche", result_time.split()[1]):
        unit = "week"
        console("Zeiteinheit", "Woche", "wurde bestimmt", mode=SUCC)
        return count * 604800
    elif re.search("Monat", result_time.split()[1]):
        unit = "month"
        console("Zeiteinheit", "Monat", "wurde bestimmt", mode=SUCC)
        return count * 2592000  # ein Monat besteht aus 30 Tagen
    elif re.search("Jahr", result_time.split()[1]):
        unit = "year"  # ein Jahr besteht aus 365 Tagen
        console("Zeiteinheit", "Jahr", "wurde bestimmt", mode=SUCC)
        return count * 31536000
    else:
        console("Ermittlung der Zeiteinheit nicht erfolgreich", mode=INFO)
        return None


def process_text_message(message_text, message_chat_id):
    from telegram import extract_information, send_telegram_message  # cannot import from partially initialized module

    result_type = extract_information(message_text, KEYWORDS_TYPE, constants.max_len_type_names)
    if result_type is None:
        send_telegram_message(message_chat_id, "Fehler: Keine valide Eingabe. Es werden Informationen "
                                               "zu folgenden Schlüsselwörtern benötigt: "
                                               f"{KEYWORDS_TYPE}")

    result_properties = extract_information(message_text, KEYWORDS_PROPERTIES,
                                            constants.max_len_property_names)
    if result_properties is None:
        send_telegram_message(message_chat_id, "Fehler: Keine valide Eingabe. Es werden Informationen "
                                               "zu folgenden Schlüsselwörtern benötigt: "
                                               f"{KEYWORDS_PROPERTIES}")

    result_time = extract_information(message_text, KEYWORDS_TIME, 2)
    if result_time is None:
        send_telegram_message(message_chat_id, "Fehler: Keine valide Eingabe. Es werden Informationen "
                                               "zu folgenden Schlüsselwörtern benötigt: "
                                               f"{KEYWORDS_TIME}")

    if result_type is None or result_properties is None or result_time is None:
        return False

    # Ermittlung des angeforderten relativen Zeitraums
    seconds = extract_timerange(result_time)
    if seconds is None:
        console("Breche Vorgang ab", mode=ERR)
        return False
    console("Informationen der letzten", seconds, "Sekunden werden ausgewertet", mode=INFO)

    type_found = False
    prop_found = False

    for system_type in constants.config_toml.keys():  # Webserver, Mailserver, Firewall, etc.
        console("Prüfe", result_type, "auf Übereinstimmung mit Typ", system_type, mode=INFO)
        # Wenn der Benutzer ein System erwähnt, prüfe ob die gefragte Eigenschaft existiert
        if compare(result_type, system_type, constants.max_len_type_names):
            type_found = True
            console("Typ", system_type, "identifiziert", mode=SUCC)
            for system_property in constants.config_toml[system_type].keys():  # Systemspezifische Eigenschaften
                console("Prüfe", result_properties, "auf Übereinstimmung mit Eigenschaft", system_property, mode=INFO)
                if compare(result_properties, system_property, constants.max_len_property_names):
                    prop_found = True
                    console("Übereinstimmung mit", system_property, mode=SUCC)
                    console("Führe Abfrage", constants.config_toml[system_type][system_property], "aus",
                            mode=INFO)
                    event_count = execute_query(constants.config_toml[system_type][system_property], seconds)
                    send_telegram_message(message_chat_id, f"Ergebnis der Anfrage zur Eigenschaft {system_property} "
                                                           f"des Typs {system_type} im Zeitraum der letzten "
                                                           f"{result_time}:"
                                                           f" es wurden {event_count} Ereignisse erfasst.")
                    return True
            if not prop_found:
                send_telegram_message(message_chat_id, f"Fehler: Unbekannte Eigenschaft {result_properties}")
                console("Unbekannte Eigenschaft", result_properties, mode=ERR)
            #break
    if not type_found:  # notwendig für den Abbruch der verschachtelden Schleife im Erfolgsfall
        send_telegram_message(message_chat_id, f"Fehler: Unbekanntes System {result_type}")
        console("Unbekanntes System", result_type, mode=ERR)
        # break

    return True
