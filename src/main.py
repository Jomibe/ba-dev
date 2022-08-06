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
from debugging import console, INFO, WARN, ERR, SUCC
from preparing import prepare
from telegram import check_updates


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
        check_updates()


if __name__ == "__main__":
    sys.exit(main())
