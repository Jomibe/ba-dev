"""
Diese Datei enthält für das Debugging notwendige Ausgabefunktionen

Quelle: GitHub-Repository von Jonas Berger
https://github.com/Jomibe/wireguard-config-generator/blob/main/src/debugging.py
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken
from datetime import datetime

# Imports von Drittanbietern
from colorama import Fore, Style

# Eigene Imports
import constants
from constants import DEBUG, LOGDIR


def console(*message, end=None, mode, no_space=None, perm=None, quiet=None, secret=None):
    """
    Gibt die Inhalte von message in abwechselnden Farben auf der Konsole aus, wenn DEBUG oder perm aktiv ist. Unabhängig
    vom Status von DEBUG oder perm wird in eine Datei unter LOGDIR geschrieben.
    end gibt das Zeilenende für print() an.
    Wenn quiet=True, dann wird 'Info:', usw. weggelassen.
    Wenn no_space=True, werden keine Leerzeichen zwischen den Parametern ausgegeben
    mode muss beim Aufruf zwingend einen Wert zugewiesen werden
    Wenn secret=True, erfolgt keine Ausgabe in die Datei
    """

    # Unabhängig vom Status von DEBUG oder perm wird in eine Datei unter LOGDIR geschrieben, sobald der Dateiname
    # bekannt ist. Es erfolgt keine Ausgabe, wenn sensible Daten (secret) protokolliert werden.
    if not secret and constants.log_filename is not None:
        with open(f"{LOGDIR}{constants.log_filename}", 'a+') as f:
            f.write("[ " + get_time_stamp(pretty=True) + " ] ")

            if mode == Mode.INFO:
                f.write("Info: ")
            elif mode == Mode.WARN:
                f.write("Warnung: ")
            elif mode == Mode.ERR:
                f.write("Fehler: ")
            elif mode == Mode.SUCC:
                f.write("Erfolg: ")

            for part in message:
                if no_space:
                    f.write(part)
                else:
                    f.write(f"{part} ")
            f.write("\n")

    # Konsolenausgabe
    if DEBUG or perm:

        was_colored = False  # Gibt an, ob die letzte Ausgabe farblich markiert war.

        if quiet is not True:
            print("[ " + get_time_stamp(pretty=True) + " ] ", end="")
            print_color_code(mode)

            if mode == Mode.INFO:
                print("Info: ", end="")
            elif mode == Mode.WARN:
                print("Warnung: ", end="")
            elif mode == Mode.ERR:
                print("Fehler: ", end="")
            elif mode == Mode.SUCC:
                print("Erfolg: ", end="")

        for part in message:
            if not was_colored:
                print_color_code(mode)
                was_colored = True
            else:
                print(f"{Style.RESET_ALL}", end="")
                was_colored = False

            if no_space:
                print(part, end="")
            else:
                print(part, end=" ")

        # Zeilenende kann durch den Parameter end beeinflusst werden
        if end is None:
            print(f"{Style.RESET_ALL}")  # Abschließender Zeilenumbruch
        else:
            print(f"{Style.RESET_ALL}", end=end)  # Parameter end wird an print() weitergegeben


def print_color_code(mode):
    """
    Gibt den Steuercode für eine bestimmte Farbe auf der Konsole aus. Die Farbe wird indirekt durch mode bestimmt:
    info -> blau
    warn -> gelb
    err -> rot
    succ -> grün
    Entspricht mode keinem der o.g. Zeichenketten, erfolgt keine Ausgabe. Dadurch bleibt die Farbausgabe unverändert
    und wird nicht zurückgesetzt.
    """

    if mode == Mode.INFO:
        print(Fore.BLUE, end="")
    elif mode == Mode.WARN:
        print(Fore.YELLOW, end="")
    elif mode == Mode.ERR:
        print(Fore.RED, end="")
    elif mode == Mode.SUCC:
        print(Fore.GREEN, end="")


def get_time_stamp(pretty):
    """
    Gibt das derzeitige Datum inkl. Uhrzeit zurück.
    :return: Angabe von Zeit und Datum
    """
    now = datetime.now()
    if pretty:  # für die Ausgabe auf der Konsole
        return now.strftime("%d. %b, %H:%M:%S:%f")
    else:  # für die Verwendung im Dateinamen
        return now.strftime("%y%m%d-%H%M%S")


class Mode:
    INFO = "Info"
    WARN = "Warn"
    ERR = "Err"
    SUCC = "Succ"


INFO = Mode.INFO
WARN = Mode.WARN
ERR = Mode.ERR
SUCC = Mode.SUCC
