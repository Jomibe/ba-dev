"""
Diese Datei enthält Funktionen, welche für die Verarbeitung von Sprach- und Textnachrichten notwendig sind.
"""

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

    success = False  # notwendig für den Abbruch der verschachtelden Schleife im Erfolgsfall

    for system_type in constants.config_toml.keys():  # Webserver, Mailserver, Firewall, etc.
        console("Prüfe", result_type, "auf Übereinstimmung mit Typ", system_type, mode=INFO)
        # Wenn der Benutzer ein System erwähnt, prüfe ob die gefragte Eigenschaft existiert
        if compare(result_type, system_type, constants.max_len_type_names):
            console("Typ", system_type, "identifiziert", mode=SUCC)
            for system_property in constants.config_toml[system_type].keys():  # Systemspezifische Eigenschaften
                console("Prüfe", result_properties, "auf Übereinstimmung mit Eigenschaft", system_property, mode=INFO)
                if compare(result_properties, system_property, constants.max_len_property_names):
                    console("Übereinstimmung mit", system_property, mode=SUCC)
                    console("Führe Abfrage", constants.config_toml[system_type][system_property], "aus",
                            mode=INFO)
                    event_count = execute_query(constants.config_toml[system_type][system_property])
                    send_telegram_message(message_chat_id, f"Ergebnis der Anfrage zur Eigenschaft {system_property} "
                                                           f"des Typs {system_type} im Zeitraum der letzten 24 Stunden:"
                                                           f" es wurden {event_count} Ereignisse erfasst.")
                    success = True
                    break

            if not success:
                send_telegram_message(message_chat_id, f"Fehler: Unbekannte Eigenschaft {result_properties}")
                console("Unbekannte Eigenschaft", result_properties, mode=ERR)
            break
        if not success:  # notwendig für den Abbruch der verschachtelden Schleife im Erfolgsfall
            send_telegram_message(message_chat_id, f"Fehler: Unbekanntes System {result_type}")
            console("Unbekanntes System", result_type, mode=ERR)
        break

    return True
