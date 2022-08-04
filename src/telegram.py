"""

Diese Datei enthält alle Funktionen, welche mit der Telegram-API in Verbindung stehen.

"""

# Imports aus Standardbibliotheken
import json

# Imports von Drittanbietern
import requests

# Eigene Imports
import constants  # für den Zugriff auf globale Variablen
from constants import TELEGRAM_LONG_POLL_TIMEOUT
from debugging import console
from debugging import INFO, WARN, ERR, SUCC


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
