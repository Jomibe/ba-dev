"""

Diese Datei enthält alle Funktionen, welche mit der Telegram-API in Verbindung stehen.

"""

# Imports aus Standardbibliotheken
import json

# Imports von Drittanbietern
import requests

# Eigene Imports
from constants import TELEGRAM_LONG_POLL_TIMEOUT
from debugging import console
from debugging import INFO, WARN, ERR, SUCC


def api_reachable(bot_token):
    console("Prüfung der Verbindung zur Telegram API...", mode=INFO)
    r = requests.get(f'https://api.telegram.org/bot{bot_token}/getMe')
    if r.status_code == 200:
        console("API ist erreichbar", mode=SUCC)
        return True
    else:
        return False


def get_updates(bot_token, offset):
    r = requests.get(url=f'https://api.telegram.org/bot{bot_token}/getUpdates',
                     params={"offset": f"{offset}",
                             "timeout": f"{TELEGRAM_LONG_POLL_TIMEOUT}",
                             "allowed_updates": '["message"]'
                             })
    return json.loads(r.text)


def send_hello(bot_token, message_chat_id, message_first_name):
    r = requests.get(url=f'https://api.telegram.org/bot{bot_token}/sendMessage',
                     params={"chat_id": f"{message_chat_id}",
                             "text": f"Hey there {message_first_name}!",
                             })
