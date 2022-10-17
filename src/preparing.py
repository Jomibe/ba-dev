"""

Diese Datei enthält Funktionen, welche für den ordnungsgemäßen Programmstart benötigt werden.

"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken
import copy
from pathlib import Path
import re

# Imports von Drittanbietern
import toml
from dotenv import dotenv_values

# Eigene Imports
from aws import init_s3_api, init_transcribe_api, init_transcribe_rt_api, init_polly_api
import constants
from debugging import console, get_time_stamp
from debugging import INFO, WARN, ERR, SUCC
from telegram import telegram_reachable
from graylog import graylog_reachable
from store import restore_cur_update_id


def prepare():
    console("Starte Vorbereitungen...", mode=INFO)
    if not set_logfile_filename():
        console("Vorbereitungen für die Protokollaufzeichnung in eine Datei fehlgeschlagen", mode=ERR)
        return False
    if not load_env():
        console("Umgebungsvariablen konnten nicht initialisiert werden", mode=ERR)
        return False
    if not telegram_reachable():
        console("Verbindungsaufbau zu Telegram API nicht möglich", mode=ERR)
        return False
    if not graylog_reachable():
        console("Verbindungsaufbau zu Graylog API nicht möglich", mode=ERR)
        return False
    if not init_s3_api():
        console("Verbindungsaufbau zu AWS S3 nicht möglich", mode=ERR)
        return False
    if not init_transcribe_api():
        console("Verbindungsaufbau zu AWS Transcribe nicht möglich", mode=ERR)
        return False
    if not init_transcribe_rt_api():
        console("Verbindungsaufbau zu AWS Transcribe für Echtzeittranskription nicht möglich", mode=ERR)
        return False
    if not init_polly_api():
        console("Verbindungsaufbau zu AWS Polly nicht möglich", mode=ERR)
        return False
    # Nach einem Programmneustart muss die zuletzt verwendete update_id geladen werden
    if not restore_cur_update_id():
        console("Wiederherstellung des Aktualisierungszählers für die Telegram API nicht möglich", mode=ERR)
        return False
    if not load_config_toml():
        console("Laden der Stichwortzuordnungen nicht möglich", mode=ERR)
        return False
    if not determine_max_len_config_toml():
        console("Verarbeitung der Stichwortzuordnungen fehlgeschlagen", mode=ERR)
        return False

    console("Vorbereitungen erfolgreich abgeschlossen", mode=SUCC)
    return True


def load_config_toml():
    """
    Liest die Inhalte der Datei config.toml im Programmverzeichnis ein und speichert diese in der internen Datenstruktur
    constants.config_toml.
    """

    console("Importiere Inhalt der Datei", "config.toml", mode=INFO)

    console("Prüfe, ob die Datei", "config.toml", "existiert. Datei wird falls notwendig erstellt.", mode=INFO)
    p = Path("config.toml")

    p.touch(exist_ok=True)

    if not p.exists():
        console("Der Pfad", "config.toml", "existiert nicht.", mode=ERR)
        return False

    if not p.is_file():
        console("Der Pfad", "config.toml", "ist keine Datei.", mode=ERR)
        return False

    console("Die Datei existiert.", mode=SUCC)

    constants.config_toml = toml.load("config.toml")
    console("Import erfolgreich", mode=SUCC)

    console("Prüfe auf Aliase", mode=INFO)

    for typ in constants.config_toml.keys():
        if "::ALIAS::" in constants.config_toml[typ].keys():  # Erkennung Typ-Alias
            target_typ = constants.config_toml[typ]["::ALIAS::"]
            console("Typ-Alias", typ, "mit Ziel", target_typ, "erkannt", mode=SUCC)
            console("Stelle Verbindung zum Zieltyp", target_typ, "her", mode=INFO)
            constants.config_toml[typ] = copy.deepcopy(constants.config_toml[target_typ])
            console("Der Typ", f"{typ} -> {target_typ}", "wurde verknüpft", mode=INFO)

        for eigenschaft in constants.config_toml[typ].keys():
            console("Prüfe auf Alias bei Wert", constants.config_toml[typ][eigenschaft], "von Eigenschaft",
                    eigenschaft, mode=INFO)
            if re.search(r"^::ALIAS::.*", constants.config_toml[typ][eigenschaft]):  # re.match untersucht nur den Anfang
                target_eigenschaft = re.split("::ALIAS::", constants.config_toml[typ][eigenschaft])[1]
                console("Eigenschafts-Alias", eigenschaft, "mit Ziel", target_eigenschaft, "erkannt", mode=SUCC)
                console("Verbinde Ziel", target_eigenschaft, "mit Quelle", eigenschaft, mode=INFO)
                constants.config_toml[typ][eigenschaft] = constants.config_toml[typ][target_eigenschaft]

    return True


def determine_max_len_config_toml():
    """
    Diese Funktion ermittelt, wie viele Wörter die Bezeichner in den Sektionsbezeichnungen und Schlüsselnamen der
    Konfigurationsdatei config.toml maximal enthalten und schreibt diese Werte in globale Variablen. Die Werte werden
    für die Texterkennung benötigt.
    """

    console("Prüfe maximale Wortanzahl von Typ- und Eigenschaftsbezeichnungen der Konfigurationsdatei", mode=INFO)
    for typ in constants.config_toml.keys():
        console("Prüfe Typ", typ, mode=INFO)
        if len(typ.split()) > constants.max_len_type_names:
            console("Typ", typ, "erhöht die maximale Wortanzahl von Typbezeichnungen auf", len(typ.split()), mode=SUCC)
            constants.max_len_type_names = len(typ.split())

        for eigenschaft in constants.config_toml[typ].keys():
            console("Prüfe Eigenschaft", eigenschaft, mode=INFO)
            if len(eigenschaft.split()) > constants.max_len_property_names:
                console("Eigenschaft", eigenschaft, "erhöht die maximale Wortanzahl von Eigenschaftsbezeichnungen auf",
                        len(eigenschaft.split()), mode=SUCC)
                constants.max_len_property_names = len(eigenschaft.split())

    console("Prüfung erfolgreich. Maximale Wortanzahl Typbezeichnungen:", constants.max_len_type_names,
            ". Maximale Wortanzahl Eigenschaftsbezeichnungen:", constants.max_len_property_names, mode=SUCC)

    return True


def load_env():
    """
    Mit dieser Funktion werden sämtliche Umgebungsvariablen initialisiert. Umgebungsvariablen werden verwendet, um
    sensible Daten zu hinterlegen.
    """

    console("Lese sensible Daten aus der Datei", ".env", mode=INFO)
    env = dotenv_values(".env")  # Variablen aus der .env-Datei übertragen

    try:
        constants.telegram_bot_token = env["TELEGRAM_BOT_TOKEN"]
        constants.graylog_username = env["GRAYLOG_USERNAME"]
        constants.graylog_password = env["GRAYLOG_PASSWORD"]
        constants.aws_access_key_id = env["AWS_ACCESS_KEY_ID"]
        constants.aws_secret_access_key = env["AWS_SECRET_ACCESS_KEY"]
        constants.aws_s3_bucket_name = env["AWS_S3_BUCKET_NAME"]
        constants.aws_s3_bucket_voice_dir = env["AWS_S3_BUCKET_VOICE_DIR"]
        constants.aws_region = env["AWS_REGION"]
    except KeyError:
        console("Die Datei ", ".env ", "enthält nicht alle erforderlichen Angaben. Folgende Parameter müssen definiert "
                                     "sein: ", "TELEGRAM_BOT_TOKEN", ", ", "GRAYLOG_USERNAME", ", ", "GRAYLOG_PASSWORD",
                ", ", "AWS_ACCESS_KEY_ID", ", ", "AWS_SECRET_ACCESS_KEY", ", ", "AWS_S3_BUCKET_NAME", ", ",
                "AWS_S3_BUCKET_VOICE_DIR", ", ", "AWS_REGION", mode=ERR, no_space=True)
        return False

    console("TELEGRAM_BOT_TOKEN =", constants.telegram_bot_token, mode=INFO, secret=True)
    console("GRAYLOG_USERNAME =", constants.graylog_username, mode=INFO, secret=True)
    console("GRAYLOG_PASSWORD =", constants.graylog_password, mode=INFO, secret=True)
    console("AWS_ACCESS_KEY_ID =", constants.aws_access_key_id, mode=INFO, secret=True)
    console("AWS_SECRET_ACCESS_KEY =", constants.aws_secret_access_key, mode=INFO, secret=True)
    console("AWS_S3_BUCKET_NAME =", constants.aws_s3_bucket_name, mode=INFO, secret=True)
    console("AWS_S3_BUCKET_VOICE_DIR =", constants.aws_s3_bucket_voice_dir, mode=INFO, secret=True)
    console("AWS_REGION =", constants.aws_region, mode=INFO, secret=True)

    return True


def set_logfile_filename():
    """
    Diese Funktion bildet den Namen für die aktuelle Logdatei unter LOGDIR
    :return: bool, ob die Aktion erfolgreich war
    """
    console("Bereite die Protokollaufzeichnung in eine Datei vor", mode=INFO)

    console("Prüfe, ob der Ordner", constants.LOGDIR, "existiert. Ordner wird falls notwendig erstellt.", mode=INFO)
    p = Path(constants.LOGDIR)

    p.mkdir(exist_ok=True)

    if not p.exists():
        console("Der Pfad", constants.LOGDIR, "existiert nicht.", mode=ERR)
        return False

    if not p.is_dir():
        console("Der Pfad", constants.LOGDIR, "ist kein Ordner.", mode=ERR)
        return False

    console("Der Ordner existiert.", mode=SUCC)

    constants.log_filename = f"{get_time_stamp(pretty=False)}.log"
    console("Name für die Protolldatei:", f"{constants.LOGDIR}{constants.log_filename}", mode=SUCC)

    return True
