"""

Enthält vom Programm verwendete statische Veriablen. Die Parameter können auf das eigene System angepasst werden.

"""

# Zusätzliche Ausgaben zum Programmablauf ausgeben
DEBUG = True

# Alle Textnachrichten zusätzlich als Sprachnachricht senden
TTS_ENABLED = True

# Wert in Sekunden, wie lange die "long poll" Vorgänge zum Abruf von Aktualisierungen der Telegram-API dauern sollen
TELEGRAM_LONG_POLL_TIMEOUT = 30

# ASCII-Textdatei, welche Informationen persistent auf dem Dateisystem speichert.
STOREFILE = "store.txt"

# Für Abfragen berechtigte Benutzer (chat_id)
AUTHORIZED_CHAT_IDS = [27055973]

# URL der Graylog-API, mit / am Ende
GRAYLOG_API_URL = "http://10.10.12.1:9000/api/"

# Schlüsselwörter, auf welche die Worterkennung reagiert
KEYWORDS_TYPE = ["Typ", "Kategorie"]
KEYWORDS_PROPERTIES = ["bezüglich", "in Sachen"]
KEYWORDS_TIME = ["Zeitraum", "seit"]

# Relativer Speicherpfad für heruntergeladene Dateien von der Telegram API. Muss mit einem / enden.
SAVEDIR_TELEGRAM_DL_FILES = "files/"

# Ordner für die Ablage der Protokolldateien
LOGDIR = "log/"

# AWS Polly Einstellungen
AWS_POLLY_ENGINE = "neural"  # standard oder neural
AWS_POLLY_VOICE = "Vicki"  # standard: Marlene oder Hans; neural: Vicki

# Einstellungen für die Sprachtranskription
# Die Anbindung der Echtzeittranskription mit Python befindet sich noch in der Testphase. Sollte es zu Problemen kommen,
# kann folgende Option aktiviert werden. Die Daten werden dann nicht per Stream sondern per S3-Bucket an den Dienst
# übermittelt. Dies führt zu einer um wenige Sekunden erhöhten Wartezeit bei der Verarbeitung einer Sprachnachricht.
ENABLE_FAILSAFE_TRANSCRIPTION = False

# Globale Variablen, werden zur Laufzeit überschrieben
telegram_bot_token = None
telegram_update_id = None
graylog_username = None
graylog_password = None
graylog_session_token = None
config_toml = None
log_filename = None  # Dateiname der aktuellen Logdatei unter LOGDIR
max_len_type_names = 0  # Maximale Anzahl von Wörtern, welche in einem Sektionsnamen der config.toml vorkommen
max_len_property_names = 0  # Maximale Anzahl von Wörtern, welche in einem Namen der config.toml vorkommen
aws_access_key_id = None
aws_secret_access_key = None
aws_s3_bucket_name = None
aws_s3_bucket_voice_dir = None
aws_region = None
aws_s3_obj = None  # boto3.resource()-Objekt für den Zugriff auf AWS S3
aws_transcribe_obj = None  # boto3.client()-Objekt für den Zugriff auf Übersetzungsdienst AWS Transcribe
# TranscribeStreamingClient()-Objekt für den Zugriff auf Übersetzungsdienst AWS Transcribe (Echtzeit)
aws_transcribe_rt_obj = None
aws_polly_obj = None  # boto3.client()-Objekt für den Zugriff auf Übersetzungsdienst AWS Polly
