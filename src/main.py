"""

Bachelorarbeit

"Entwicklung eines Telegram-Bots zur Abfrage von Informationen aus der Software Graylog per Sprachnachricht"

Jonas Berger
Fachhochschule Südwestfalen
Sommersemester 2022

"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken
import sys

# Imports von Drittanbietern
import colorama
from dotenv import dotenv_values

# Eigene Imports
import constants  # für Zugriff auf globale Variablen
from constants import AUTHORIZED_CHAT_IDS, KEYWORDS_TYPE, KEYWORDS_TIME, KEYWORDS_PROPERTIES
from debugging import console
from debugging import INFO, WARN, ERR, SUCC
from preparing import prepare
from telegram import get_updates, send_hello, send_telegram_message, extract_information
from store import store_cur_update_id


def main():
    console("Detaillierte Ausgaben zum Programmablauf sind eingeschaltet.", mode=INFO)
    colorama.init()  # Colorama passt sich an das Betriebssystem an
    env = dotenv_values(".env")  # Variablen aus der .env-Datei übertragen
    constants.telegram_bot_token = env["TELEGRAM_BOT_TOKEN"]
    constants.graylog_username = env["GRAYLOG_USERNAME"]
    constants.graylog_password = env["GRAYLOG_PASSWORD"]
    console("TELEGRAM_BOT_TOKEN =", constants.telegram_bot_token, mode=INFO)
    console("GRAYLOG_USERNAME =", constants.graylog_username, mode=INFO)
    console("GRAYLOG_PASSWORD =", constants.graylog_password, mode=INFO)
    if not prepare():  # Das Programm prüft für den Programmablauf wichtige Funktionen
        console("Der Programmablauf wird abgebrochen", mode=ERR)
        return 1

    while True:  # long polling
        console("Prüfung auf neue Ereignisse der Telegram-API...", mode=INFO)
        updates = get_updates()
        # Auch wenn hier nicht über die Elemente der Liste iteriert wird, wird jedes Ereignis bearbeitet
        if len(updates["result"]) > 0:
            console("Es liegen neue Ereignisse vor", mode=SUCC)

            message_first_name = updates["result"][0]["message"]["chat"]["first_name"]
            console("Name :", message_first_name, mode=INFO)
            message_chat_id = updates["result"][0]["message"]["chat"]["id"]
            console("Chat_id :", message_chat_id, mode=INFO)
            constants.telegram_update_id = updates["result"][0]["update_id"]
            console("Die aktuelle update_id ist nun", constants.telegram_update_id, mode=INFO)

            # Verarbeitung des Ereignisinhalts
            if message_chat_id not in AUTHORIZED_CHAT_IDS:
                console("Dieser Benutzer ist nicht für Abfragen berechtigt. Breche ab.", mode=INFO)
                send_telegram_message(env["TELEGRAM_BOT_TOKEN"], message_chat_id, "Fehler: Dieser Account wurde noch "
                                                                                  "nicht autorisiert.")
                continue

            if "text" in updates["result"][0]["message"]:
                message_text = updates["result"][0]["message"]["text"]
                console("Textnachricht :", message_text, mode=INFO)
                if message_text == "/start":
                    send_hello(message_chat_id, message_first_name)
                else:
                    result_type = extract_information(message_text, KEYWORDS_TYPE, 1)
                    if result_type is None:
                        send_telegram_message(message_chat_id, "Fehler: Keine valide Eingabe. Es werden Informationen "
                                                               f"zu folgenden Schlüsselwörtern benötigt: {result_type}")

                    result_properties = extract_information(message_text, KEYWORDS_PROPERTIES, 1)
                    if result_properties is None:
                        send_telegram_message(message_chat_id, "Fehler: Keine valide Eingabe. Es werden Informationen "
                                                               "zu folgenden Schlüsselwörtern benötigt: "
                                                               f"{result_properties}")

                    result_time = extract_information(message_text, KEYWORDS_TIME, 2)
                    if result_time is None:
                        send_telegram_message(message_chat_id, "Fehler: Keine valide Eingabe. Es werden Informationen "
                                                               f"zu folgenden Schlüsselwörtern benötigt: {result_time}")

                    if result_type is None or result_properties is None or result_time is None:
                        continue

            store_cur_update_id(constants.telegram_update_id)


if __name__ == "__main__":
    sys.exit(main())
