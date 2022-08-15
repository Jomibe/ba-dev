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


# Eigene Imports
import constants  # für Zugriff auf globale Variablen
from debugging import console, INFO, WARN, ERR, SUCC
from graylog import execute_query
from preparing import prepare
from telegram import check_updates


def main():
    colorama.init()  # Colorama passt sich an das Betriebssystem an
    console("Detaillierte Ausgaben zum Programmablauf sind eingeschaltet.", mode=INFO)
    if not prepare():  # Das Programm prüft für den Programmablauf wichtige Funktionen
        console("Der Programmablauf wird abgebrochen", mode=ERR)
        return 1

    while True:  # long polling
        check_updates()


if __name__ == "__main__":
    sys.exit(main())
