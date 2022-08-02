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


def main():
    console("Detaillierte Ausgaben zum Programmablauf sind eingeschaltet.", mode=INFO)
    colorama.init()  # Colorama passt sich an das Betriebssystem an
    env = dotenv_values(".env")  # Variablen aus der .env-Datei übertragen
    console("TELEGRAM_BOT_TOKEN=", env["TELEGRAM_BOT_TOKEN"], mode=INFO, no_space=True)
    prepare()  # Das Programm prüft für den Programmablauf wichtige Funktionen


if __name__ == "__main__":
    sys.exit(main())
