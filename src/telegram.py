"""

Diese Datei enthält alle Funktionen, welche mit der Telegram-API in Verbindung stehen.

"""

# Imports aus Standardbibliotheken
import json
import re

# Imports von Drittanbietern
import requests

# Eigene Imports
from aws import upload_file_to_s3, speech_to_text, text_to_speech
import constants  # für den Zugriff auf globale Variablen
from constants import TELEGRAM_LONG_POLL_TIMEOUT, AUTHORIZED_CHAT_IDS, SAVEDIR_TELEGRAM_DL_FILES, \
    ENABLE_FAILSAFE_TRANSCRIPTION
from debugging import console, INFO, WARN, ERR, SUCC
from store import store_cur_update_id
from message_processing import process_text_message
from aws import transcribe_realtime


def telegram_reachable():
    """
    Prüft die Verbindung zur Telegram API durch die API-Funktion 'getMe'.
    :return: bool, ob die Aktion erfolgreich war
    """
    console("Prüfung der Verbindung zur Telegram API...", mode=INFO)
    r = requests.get(f'https://api.telegram.org/bot{constants.telegram_bot_token}/getMe', timeout=3)
    if r.status_code == 200:
        console("Telegram API ist in", f"{r.elapsed.microseconds/1000}ms", "erreichbar", mode=SUCC)
        return True
    else:
        console("Telegram API ist nicht erreichbar. Details:", f"{r.status_code} {r.reason} - {r.text}", mode=ERR)
        return False


def get_updates():
    """
    Ruft Aktualisierungen von der Telegram API ab.

    :return: JSON-Objekt mit dem Inhalt der API-Antwort, None im Fehlerfall
    """
    console("Rufe Aktualisierungen von der Telegram API ab", mode=INFO)
    r = requests.get(url=f'https://api.telegram.org/bot{constants.telegram_bot_token}/getUpdates',
                     params={"offset": constants.telegram_update_id + 1,
                             "timeout": f"{TELEGRAM_LONG_POLL_TIMEOUT}",
                             "allowed_updates": '["message"]'
                             })
    if r.status_code == 200:
        console("Antwort in", f"{r.elapsed.microseconds/1000}ms", "erhalten", mode=SUCC)
    else:
        console("Telegram API ist nicht erreichbar. Details:", f"{r.status_code} {r.reason} - {r.text}", mode=ERR)
        return None
    return json.loads(r.text)


def send_hello(message_chat_id, message_first_name):
    """
    Sendet eine Begrüßungsnachricht an einen Telegram-Chat.

    :param message_chat_id: int, entspricht Wert message_chat_id der Telegram API
    :param message_first_name: str, Vorname des Adressaten
    :return: bool, ob die Aktion erfolgreich war
    """
    r = requests.get(url=f'https://api.telegram.org/bot{constants.telegram_bot_token}/sendMessage',
                     params={"chat_id": message_chat_id,
                             "text": f"Hey there {message_first_name}!",
                             })

    if r.status_code == 200:
        console("Nachricht in", f"{r.elapsed.microseconds / 1000}ms", "übermittelt", mode=SUCC)
    else:
        console("Telegram API ist nicht erreichbar. Details:", f"{r.status_code} {r.reason} - {r.text}", mode=ERR)
        return None


def send_telegram_text_message(message_chat_id, message_text):
    """
    Sendet eine Textnachricht per Telegram.

    :param message_chat_id: int, entspricht dem gleichnamigen Parameter der Telegram API.
    :param message_text: str, Text der zu sendenden Nachricht.
    :return: bool, ob die Aktion erfolgreich war.
    """

    r = requests.get(url=f'https://api.telegram.org/bot{constants.telegram_bot_token}/sendMessage',
                     params={"chat_id": f"{message_chat_id}",
                             "text": message_text,
                             })

    if r.status_code == 200:
        console("Nachricht in", f"{r.elapsed.microseconds / 1000}ms", "übermittelt", mode=SUCC)
        return True
    else:
        console("Telegram API ist nicht erreichbar. Details:", f"{r.status_code} {r.reason} - {r.text}", mode=ERR)
        return False


def send_telegram_message(message_chat_id, message_text):
    """
    Diese Funktion versendet eine kombinierte Sprachnachricht mit dem gesprochenen Text als Wert für 'caption'.
    Die Sprachausgabe wird ausgelassen, wenn der Konfigurationsparameter TTS_ENABLED den Wert False hat.
    :param message_chat_id: int, entspricht dem Parameter chat_id der Telegram API
    :param message_text: str, der Nachrichtentext in Textform
    :return: bool, ob die Ausführung erfolgreich war
    """

    if not constants.TTS_ENABLED:
        send_telegram_text_message(message_chat_id, message_text)
        return True

    console("Sende Text", message_text, "an Chat", message_chat_id, "in einer kombinierten Sprachnachricht.", mode=INFO)
    send_audio_message(message_chat_id,
                       f"{constants.SAVEDIR_TELEGRAM_DL_FILES}{text_to_speech(message_text)}",
                       message_text
                       )


def send_audio_message(message_chat_id, voice_file, caption):
    """
    Sendet eine Sprachnachricht per Telegram.

    :param message_chat_id: int, entspricht dem Parameter chat_id der Telegram API.
    :param voice_file: str, Dateipfad der zu sendenden Sprachnachricht. Die Datei muss im Format OGG (OPUS) vorliegen
    und darf nicht größer als 1 MB sein.
    :param caption: str, in der Sprachnachricht enthaltener Text.
    :return: bool, ob die Aktion erfolgreich war.
    """

    console("Sende Audiodatei", voice_file, "als Sprachnachricht", mode=INFO)

    with open(voice_file, 'rb') as f:
        r = requests.post(url=f"https://api.telegram.org/bot{constants.telegram_bot_token}/sendVoice",
                          data={"chat_id": message_chat_id, "caption": caption},
                          files={"voice": f}
                          )

    if r.status_code == 200:
        console("Nachricht in", f"{r.elapsed.microseconds / 1000}ms", "übermittelt", mode=SUCC)
        return True
    else:
        console("Telegram API ist nicht erreichbar. Details:", f"{r.status_code} {r.reason} - {r.text}", mode=ERR)
        return False


def extract_information(message_text, keywords, wordcount):
    """
    Durchsucht die Nachricht auf die Inhalte der Liste keywords und liefert die darauffolgenden Wörter
    als String zurück.

    :param message_text: str, der Nachrichtentext.
    :param keywords: list mit str, welche die zu prüfenden Schlüsselwörter enthält.
    :param wordcount: int, Anzahl der auf das Schlüsselwort folgenden Wörter, welche zurückgegeben werden.
    :return: str, wenn Wörter gefunden wurden. None, wenn das Schlüsselwort nicht gefunden wurde.
    """

    console("Untersuche Nachricht auf Schlüsselwörter...", mode=INFO)

    for keyword in keywords:
        console("Prüfe auf", keyword, mode=INFO)
        if re.search(f"{keyword}", message_text):
            # value = re.split(f"({keyword})", message_text)[-1].strip().split()
            value = ' '.join(re.split(f"({keyword})", message_text)[-1].strip().split()[0:wordcount])
            # value = value[0:int(wordcount)]
            console("Schlüsselwort", keyword, "erkannt. Folgende", wordcount, "Wörter:", value, mode=SUCC)
            return value
    console("Kein Fund. Es kann keine Abfrage gebildet werden, da Informationen fehlen.", mode=ERR)
    return None


def get_file_path(file_id):
    """
    Diese Funktion bezieht eine relative URL von der Telegram API, unter welcher die mit dem Parameter file_id
    verknüpfte Datei zum Download angeboten wird und gibt diese als Rückgabewert zurück.
    """

    console("Ermittlung des Dateipfads für den Download über die Telegram API", mode=INFO)
    r = requests.get(url=f'https://api.telegram.org/bot{constants.telegram_bot_token}/getFile',
                     params={"file_id": file_id})

    console("Dateipfad bezogen", mode=SUCC)
    return json.loads(r.text)["result"]["file_path"]


def download_file(file_path, unique_file_id, mime_type):
    """
    Diese Funktion bezieht eine Datei (Audiodatei, Bilddatei, Video) anhand der URL über die Telegram API und
    speichert diese auf dem lokalen Dateisystem. Der Dateiname setzt sich aus der unique_file_id und dem MIME-Typ als
    Dateiendung zusammen. Die Funktion gibt den Dateinamen ohne Dateipfad zurück.
    """

    # Download-URL bilden
    url = f"https://api.telegram.org/file/bot{constants.telegram_bot_token}/{file_path}"
    console("Lade Datei herunter. URL:", url, mode=INFO)

    # Dateinamen bilden
    # TODO mit RegEx aus mime_type exportieren
    filename = f"{unique_file_id}.oga"

    console("Speichere auf dem Dateisystem. Dateipfad:", f"{SAVEDIR_TELEGRAM_DL_FILES}{filename}", mode=INFO)
    r = requests.get(url, allow_redirects=True)
    with open(f"{SAVEDIR_TELEGRAM_DL_FILES}{filename}", 'wb') as file:
        file.write(r.content)
        file.close()
    console("Speichern abgeschlossen", mode=INFO)

    return filename


def check_updates():
    """
    Diese Funktion ruft Aktualisierungen von der Telegram API ab und verarbeitet diese, falls es sich um Text- oder
    Sprachnachrichten handelt.
    """

    console("Prüfung auf neue Ereignisse der Telegram-API...", mode=INFO)
    updates = get_updates()
    # Auch wenn hier nicht über die Elemente der Liste iteriert wird, wird jedes Ereignis bearbeitet, indem die
    # update_id jeweils um 1 inkrementiert wird
    if len(updates["result"]) > 0:
        console("Es liegen neue Ereignisse vor", mode=SUCC)

        message_first_name = updates["result"][0]["message"]["chat"]["first_name"]
        console("Name :", message_first_name, mode=INFO)
        message_chat_id = updates["result"][0]["message"]["chat"]["id"]
        console("Chat_id :", message_chat_id, mode=INFO)
        constants.telegram_update_id = updates["result"][0]["update_id"]
        store_cur_update_id(constants.telegram_update_id)
        console("Die aktuelle update_id ist nun", constants.telegram_update_id, mode=INFO)

        # Verarbeitung des Ereignisinhalts
        if message_chat_id not in AUTHORIZED_CHAT_IDS:
            console("Dieser Benutzer ist nicht für Abfragen berechtigt. Breche ab.", mode=INFO)
            send_telegram_message(message_chat_id, "Fehler: Dieser Account wurde noch nicht autorisiert.")
            return False

        if "text" in updates["result"][0]["message"]:  # Handelt es sich um eine Textnachricht?
            message_text = updates["result"][0]["message"]["text"]  # Text extrahieren
            console("Textnachricht :", message_text, mode=INFO)
            if message_text == "/start":
                send_hello(message_chat_id, message_first_name)
                send_audio_message(message_chat_id, f"files/{text_to_speech('Hallo Welt')}", "Hallo Welt")
            else:
                process_text_message(message_text, message_chat_id)

        if "voice" in updates["result"][0]["message"]:  # Handelt es sich um eine Sprachnachricht?
            console("Sprachnachricht erhalten", mode=INFO)
            voice_file_id = updates["result"][0]["message"]["voice"]["file_id"]  # ID der Audionachricht extrahieren
            console("file_id :", voice_file_id, mode=INFO)
            mime_type = updates["result"][0]["message"]["voice"]["mime_type"]  # Dateityp extrahieren
            console("Dateityp :", mime_type, mode=INFO)
            file_path = get_file_path(voice_file_id)
            filename = download_file(file_path, voice_file_id, mime_type)
            if ENABLE_FAILSAFE_TRANSCRIPTION:
                spoken_text = speech_to_text(filename)
            else:
                spoken_text = transcribe_realtime(f"{constants.SAVEDIR_TELEGRAM_DL_FILES}{filename}")
            send_telegram_message(message_chat_id, f"Die Anfrage \"{spoken_text}\" wird verarbeitet...")
            process_text_message(spoken_text, message_chat_id)

    return True
