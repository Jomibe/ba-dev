"""
Diese Datei enthält Funktionen, welche für den ordnungsgemäßen Programmstart benötigt werden.
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken

# Imports von Drittanbietern

# Eigene Imports
from debugging import console
from debugging import INFO, WARN, ERR, SUCC


def prepare():
    console("Starte Vorbereitungen...", mode=INFO)
    console("Vorbereitungen erfolgreich abgeschlossen", mode=SUCC)
