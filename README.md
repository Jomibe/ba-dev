# ba-dev
Repository für die Weiterentwicklung einer im Rahmen der Bachelorarbeit implementierten Software.

In diesem Repository findet die aktive Entwicklung der Software statt. Der Stand zum Zeitpunkt der Abgabe der Bachelorarbeit kann in [Jomibe/ba](https://github.com/Jomibe/ba) angesehen werden.

## Setup

Um die Software nutzen zu können, sind einige Vorbereitungen notwendig. Das System, auf welchem die Software ausgeführt wird, muss vorbereitet werden. Außerdem müssen AWS, Graylog und Telegram passend konfiguriert werden. Dies wird im folgenden Abschnitt beschrieben.

### Lokales System

Die Software wurde für den Betrieb auf unix-artigen Systemen ausgelegt. Die Kompatibilität zu Windows wurde nicht geprüft. Die Installation von Python 3 und Pip wird vorausgesetzt. Die Software ist kompatibel zu Python 3.9 und den Modulversionen aus der Datei requirements.txt. Andere Konfigurationen wurden nicht geprüft.

1. Klonen dieses Repositorys
2. Vorbereitung der Umgebung
    1. Mit dem Terminal in das geklonte Verzeichnis wechseln
    2. Erstellung der virtuellen Umgebung für Python im Ordner venv/ `python3 -m venv venv`
    3. Ergänzung der PATH-Umgebungsvariable im venv, sodass das main-Modul gefunden wird ([Quelle](https://stackoverflow.com/a/47184788/237059))
        `echo "../../../../src" > venv/lib/python3.9/site-packages/main.pth`
    4. Virtuelle Umgebung starten `source venv/bin/activate`
    5. Abhängigkeiten laden `pip install -r requirements.txt`
    6. Zur Überprüfung der Anpassungen das main-Modul ausführen, das Programm wird sich nach Ausgabe einer Fehlermeldung beenden `python -m main`

### AWS

AWS stellt die Dienste Polly, S3 und Transcribe zur Verfügung. Um auf die Dienste programmgesteuert zugreifen zu können, muss ein IAM-Benutzer mit passenden Berechtigungen erstellt werden. Hierfür kann die [Vorlage](https://github.com/Jomibe/ba-dev/blob/main/aws-permissions.json) verwendet werden.

### Graylog

Für den programmgesteuerten Zugriff auf Graylog muss ebenfalls ein Benutzer angelegt werden. 

## Verwendung
