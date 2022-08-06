"""

Diese Datei enthält alle Funktionen, welche mit der Telegram-API in Verbindung stehen.

"""

# Imports aus Standardbibliotheken
import json
import re

# Imports von Drittanbietern
import requests

# Eigene Imports
import constants  # für den Zugriff auf globale Variablen
from constants import TELEGRAM_LONG_POLL_TIMEOUT, AUTHORIZED_CHAT_IDS
from debugging import console, INFO, WARN, ERR, SUCC
from store import store_cur_update_id
from message_processing import process_text_message


def telegram_reachable():
    console("Prüfung der Verbindung zur Telegram API...", mode=INFO)
    r = requests.get(f'https://api.telegram.org/bot{constants.telegram_bot_token}/getMe')
    if r.status_code == 200:
        console("Telegram API ist erreichbar", mode=SUCC)
        return True
    else:
        console("Telegram API ist nicht erreichbar. Details:", f"{r.status_code} - {r.text}", mode=ERR)
        return False


def get_updates():
    r = requests.get(url=f'https://api.telegram.org/bot{constants.telegram_bot_token}/getUpdates',
                     params={"offset": constants.telegram_update_id + 1,
                             "timeout": f"{TELEGRAM_LONG_POLL_TIMEOUT}",
                             "allowed_updates": '["message"]'
                             })
    return json.loads(r.text)


def send_hello(message_chat_id, message_first_name):
    r = requests.get(url=f'https://api.telegram.org/bot{constants.telegram_bot_token}/sendMessage',
                     params={"chat_id": message_chat_id,
                             "text": f"Hey there {message_first_name}!",
                             })


def send_telegram_message(message_chat_id, message_text):
    r = requests.get(url=f'https://api.telegram.org/bot{constants.telegram_bot_token}/sendMessage',
                     params={"chat_id": f"{message_chat_id}",
                             "text": message_text,
                             })


def extract_information(message_text, keywords, wordcount):
    """
    Diese Funktion durchsucht die Nachricht auf die Inhalte der Liste keywords und liefert die darauffolgenden Wörter
    als String zurück. Wieviele Wörter zurückgegeben werden, wird mit wordcount definiert.
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
            send_telegram_message(constants.telegram_bot_token, message_chat_id, "Fehler: Dieser Account wurde noch "
                                                                              "nicht autorisiert.")
            return False

        if "text" in updates["result"][0]["message"]:  # Handelt es sich um eine Textnachricht?
            message_text = updates["result"][0]["message"]["text"]  # Text extrahieren
            console("Textnachricht :", message_text, mode=INFO)
            if message_text == "/start":
                send_hello(message_chat_id, message_first_name)
            else:
                process_text_message(message_text, message_chat_id)

    return True