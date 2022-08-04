"""

Enthält vom Programm verwendete statische Veriablen. Die Parameter können auf das eigene System angepasst werden.

"""

# Zusätzliche Ausgaben zum Programmablauf ausgeben
DEBUG = True

# Wert in Sekunden, wie lange die "long poll" Vorgänge zum Abruf von Aktualisierungen der Telegram-API dauern sollen
TELEGRAM_LONG_POLL_TIMEOUT = 30

# ASCII-Textdatei, welche Informationen persistent auf dem Dateisystem speichert.
STOREFILE = "store.txt"

# Für Abfragen berechtigte Benutzer (chat_id)
AUTHORIZED_CHAT_IDS = [27055973]

# URL der Graylog-API, mit / am Ende
GRAYLOG_API_URL = "http://10.10.12.1:9000/api/"

# Globale Variablen, werden zur Laufzeit überschrieben
telegram_bot_token = None
telegram_update_id = None
graylog_username = None
graylog_password = None
graylog_session_token = None
