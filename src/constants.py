"""

Enthält vom Programm verwendete statische Veriablen. Die Parameter können auf das eigene System angepasst werden.

"""

# Zusätzliche Ausgaben zum Programmablauf ausgeben
DEBUG = True

# Wert in Sekunden, wie lange die "long poll" Vorgänge zum Abruf von Aktualisierungen der Telegram-API dauern sollen
TELEGRAM_LONG_POLL_TIMEOUT = 30

# ASCII-Textdatei, welche Informationen persistent auf dem Dateisystem speichert.
STOREFILE = "store.txt"
