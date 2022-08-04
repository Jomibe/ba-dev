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
from debugging import console
from debugging import INFO, WARN, ERR, SUCC
from preparing import prepare
from telegram import get_updates, send_hello
from store import store_cur_update_id, restore_cur_update_id


def main():
    console("Detaillierte Ausgaben zum Programmablauf sind eingeschaltet.", mode=INFO)
    colorama.init()  # Colorama passt sich an das Betriebssystem an
    env = dotenv_values(".env")  # Variablen aus der .env-Datei übertragen
    console("TELEGRAM_BOT_TOKEN = ", env["TELEGRAM_BOT_TOKEN"], mode=INFO, no_space=True)
    prepare(env["TELEGRAM_BOT_TOKEN"])  # Das Programm prüft für den Programmablauf wichtige Funktionen

    cur_update_id = restore_cur_update_id()

    while True:  # long polling
        console("Prüfung auf neue Ereignisse der Telegram-API...", mode=INFO)
        updates = get_updates(env["TELEGRAM_BOT_TOKEN"], offset=cur_update_id + 1)
        if len(updates["result"]) > 0:
            console("Es liegen neue Ereignisse vor", mode=SUCC)
            message_first_name = updates["result"][0]["message"]["chat"]["first_name"]
            console("Name :", message_first_name, mode=INFO)
            message_chat_id = updates["result"][0]["message"]["chat"]["id"]
            console("Chat_id :", message_chat_id, mode=INFO)
            cur_update_id = updates["result"][0]["update_id"]
            console("Die aktuelle update_id ist nun", cur_update_id, mode=INFO)

            if "text" in updates["result"][0]["message"]:
                message_text = updates["result"][0]["message"]["text"]
                console("Textnachricht :", message_text, mode=INFO)
                if message_text == "/start":
                    send_hello(env["TELEGRAM_BOT_TOKEN"], message_chat_id, message_first_name)

            store_cur_update_id(cur_update_id)


if __name__ == "__main__":
    sys.exit(main())
