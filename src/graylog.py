"""

Diese Datei enthält alle Funktionen, welche mit der Graylog-API in Verbindung stehen.

"""

# Imports aus Standardbibliotheken
import json

# Imports von Drittanbietern
import requests
from requests.auth import HTTPBasicAuth

# Eigene Imports
import constants
from constants import GRAYLOG_API_URL
from debugging import console
from debugging import INFO, WARN, ERR, SUCC


def graylog_reachable():
    console("Prüfung der Verbindung zur Graylog API...", mode=INFO)
    r = requests.get(url=f'{GRAYLOG_API_URL}system/processing/status',
                     auth=HTTPBasicAuth(constants.graylog_session_token, "session"))

    if r.status_code == 401:  # Es muss ein neuer Sitzungsschlüssel bezogen werden, danach erneuter Versuch
        get_session_token()
        r = requests.get(url=f'{GRAYLOG_API_URL}system/processing/status',
                         auth=HTTPBasicAuth(constants.graylog_session_token, "session"))

    if r.status_code == 200:
        console("Graylog API ist erreichbar", mode=SUCC)
        return True
    else:
        console("Graylog API ist nicht erreichbar. Details:", f"{r.status_code} - {r.text}", mode=ERR)
        return False


def get_session_token():
    """
    Ruft einen für den Zugriff notwendigen Authentifizierungsschlüssel von der Graylog API ab. Der Token verliert
    nach kurzer Zeit seine Gültigkeit.
    """
    console("Abrufen eines weiteren temporären Authentifizierungsschlüssels für Graylog...", mode=INFO)

    r = requests.post(url=f'{GRAYLOG_API_URL}system/sessions',
                      headers={"X-Requested-By": "cli",
                               "Content-Type": "application/json",
                               "Accept": "application/json"},
                      data=json.dumps({"username": constants.graylog_username,
                             "password": constants.graylog_password,
                             "host": "",
                             }))

    if r.status_code != 200:
        console("Fehler bei der Kommunikation mit der Graylog API. Details:", f"{r.status_code} - {r.text}", mode=ERR)
        return False

    else:
        console("Authentifizierungsschlüssel", json.loads(r.text)["session_id"], "erfolgreich bezogen", mode=SUCC,
                secret=True)
        constants.graylog_session_token = json.loads(r.text)["session_id"]


def execute_query(query, seconds):
    """
    Diese Funktion führt eine ElasticSearch-Abfrage über die Graylog API aus.
    :param query: str, Graylog ElasticSearch-Abfrage
    :param seconds: int, Anzahl der Sekunden des relativen Zeitraums
    :return: Gibt die Anzahl der gezählten Ereignisse zurück
    """

    console("Führe Abfrage", query, "im Zeitraum der letzten", seconds, "Sekunden in Graylog aus", mode=INFO)

    # Mit absoluter Zeitangabe
    # payload = {"streams": ["000000000000000000000001"],
    #           "timerange": ["absolute", {"from": "2022-07-01T00:00:00.000Z", "to": "2022-07-01T15:00:00.000Z"}],
    #           "query_string": { "type": "elasticsearch", "query_string": "http_response_code: 200"}}

    # Mit relativer Zeitangabe
    payload = {"streams": ["000000000000000000000001"],
               "timerange": ["relative", {"range": "86400"}],
               "query_string": {"type": "elasticsearch", "query_string": "http_response_code: 200"}}
    payload["query_string"]["query_string"] = query
    payload["timerange"][1]["range"] = seconds

    r = requests.post(url=f'{GRAYLOG_API_URL}views/search/messages',
                      json=payload,
                      headers={"X-Requested-By": "cli",
                              "Content-Type": "application/json",
                              "Accept": "text/csv",
                              "Cookie": f"authentication={constants.graylog_session_token}"
                              }
                      )

    if r.status_code != 200:
        console("Fehler bei der Kommunikation mit der Graylog API. Details:", f"{r.status_code} {r.reason} - {r.text}",
                mode=ERR)

    # Es werden Daten im CSV-Format mit einer Überschrift zurückgegeben. Diese muss bei der Zählung der Zeilen ignoriert
    # werden.
    console("Ergebnis der Abfrage:", r.text.count('\n')-1, "Ereignisse", mode=SUCC)

    return r.text.count('\n')-1
