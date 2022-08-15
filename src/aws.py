"""
Diese Datei enthält Funktionen für die Kommunikation mit Amazon Web Services, u.A. für den Upload von Dateien in S3
sowie für die Umwandlung zwischen Sprache und Text.
"""

# Imports aus Standardbibliotheken
from time import sleep
import json

# Imports von Drittanbietern
import boto3  # AWS Python SDK

# Eigene Imports
import constants
from debugging import console, INFO, WARN, ERR, SUCC


def init_s3_api():
    """
    Diese Funktion prüft die Verbindung zur AWS API und bereitet den Zugriff auf den S3-Bucket vor.
    """
    console("Prüfe Verbindung zu AWS S3 in der Region", constants.aws_region, mode=INFO)
    constants.aws_s3_obj = boto3.resource(
        service_name='s3',
        region_name=constants.aws_region,
        aws_access_key_id=constants.aws_access_key_id,
        aws_secret_access_key=constants.aws_secret_access_key
    )

    console("Verfügbare S3 Buckets:", list(constants.aws_s3_obj.buckets.all()), mode=INFO)

    console("Verbindung zu AWS S3 aufgebaut", mode=SUCC)

    return True


def init_transcribe_api():
    """
    Diese Funktion prüft die Verbindung zur AWS API und bereitet den Zugriff auf den Transcribe-Übersetzungsdienst vor.
    """

    console("Prüfe Verbindung zu AWS Transcribe in der Region", constants.aws_region, mode=INFO)
    constants.aws_transcribe_obj = boto3.client(
        service_name='transcribe',
        region_name=constants.aws_region,
        aws_access_key_id=constants.aws_access_key_id,
        aws_secret_access_key=constants.aws_secret_access_key
    )
    console("Verbindung zu AWS Transcribe aufgebaut", mode=SUCC)

    return True


def init_polly_api():
    """
    Diese Funktion prüft die Verbindung zur AWS API und bereitet den Zugriff auf den Polly-Übersetzungsdienst vor.
    """

    console("Prüfe Verbindung zu AWS Polly in der Region", constants.aws_region, mode=INFO)
    constants.aws_polly_obj = boto3.client(
        service_name='polly',
        region_name=constants.aws_region,
        aws_access_key_id=constants.aws_access_key_id,
        aws_secret_access_key=constants.aws_secret_access_key
    )
    console("Verbindung zu AWS Polly aufgebaut", mode=SUCC)

    return True


def upload_file_to_s3(filename, filepath):
    """
    Diese Funktion legt eine Datei in einem S3-Bucket ab.
    """

    console("Lade die lokale Datei", f"{filepath}{filename}", "in den S3 Bucket", constants.aws_s3_bucket_name, "unter",
            f"{constants.aws_s3_bucket_voice_dir}{filename}", "hoch", mode=INFO)
    constants.aws_s3_obj.Bucket(constants.aws_s3_bucket_name).\
        upload_file(Filename=f"{filepath}{filename}", Key=f"{constants.aws_s3_bucket_voice_dir}{filename}")


def download_file_from_s3(filename):
    """
    Diese Funktion ruft eine Datei von einem S3-Bucket ab und speichert diese auf dem lokalen Dateisystem.
    """

    console("Lade die Datei", filename, "von",
            f"s3://{constants.aws_s3_bucket_name}/{constants.aws_s3_bucket_voice_dir}", "nach",
            constants.SAVEDIR_TELEGRAM_DL_FILES, "herunter", mode=INFO)

    constants.aws_s3_obj.meta.client.download_file(constants.aws_s3_bucket_name,
                                                   f"{constants.aws_s3_bucket_voice_dir}{filename}",
                                                   f"{constants.SAVEDIR_TELEGRAM_DL_FILES}{filename}")

    return True


def speech_to_text(filename):
    """
    Diese Funktion extrahiert mittels dem AWS Übersetzungsdienst Transcribe den gesprochenen Text aus einer Audiodatei.
    """
    console("Starte Umwandlung der Sprachnachricht in Text", mode=INFO)
    s3_uri = f"s3://{constants.aws_s3_bucket_name}/{constants.aws_s3_bucket_voice_dir}{filename}"

    transcription_job = constants.aws_transcribe_obj.start_transcription_job(
        TranscriptionJobName=f"ba-telegram-bot-{filename}",
        Media={
            'MediaFileUri': s3_uri
        },
        LanguageCode="de-DE",
        OutputBucketName=constants.aws_s3_bucket_name,
        OutputKey=constants.aws_s3_bucket_voice_dir
    )

    console("Übertragungsvorgang", f"ba-telegram-bot-{filename}", "gestartet", mode=INFO)

    transcript_s3_uri = None
    while transcript_s3_uri is None:
        sleep(2)
        transcription_job_status = constants.aws_transcribe_obj.get_transcription_job(
           TranscriptionJobName=f"ba-telegram-bot-{filename}"
        )
        if transcription_job_status["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
            console("Übertragungsvorgang abgeschlossen", mode=SUCC)
            # TODO string indices must be integers?
            # console(transcription_job_status, mode=INFO)
            # transcript_s3_uri = \
            #    transcription_job_status["TranscriptionJob"]["TranscriptFileUri"]
            transcript_s3_uri = "TODO"
        elif transcription_job_status["TranscriptionJob"]["TranscriptionJobStatus"] == "QUEUED":
            console("Übertragungsvorgang befindet sich in der Warteschlange", mode=INFO)
        elif transcription_job_status["TranscriptionJob"]["TranscriptionJobStatus"] == "IN_PROGRESS":
            console("Übertragungsvorgang wird ausgeführt", mode=INFO)
        elif transcription_job_status["TranscriptionJob"]["Transcript"] == "FAILED":
            console("Übertragungsvorgang war nicht erfolgreich", mode=ERR)
            return False

    transcript_s3_uri = \
        f"s3://{constants.aws_s3_bucket_name}/{constants.aws_s3_bucket_voice_dir}ba-telegram-bot-{filename}"

    console("Rufe Text von", transcript_s3_uri, "ab", mode=INFO)
    download_file_from_s3(f"ba-telegram-bot-{filename}.json")

    with open(f"{constants.SAVEDIR_TELEGRAM_DL_FILES}ba-telegram-bot-{filename}.json", mode='r', encoding='utf-8') as transcript_result_file:
        transcript_result = json.load(transcript_result_file)["results"]["transcripts"][0]["transcript"]
        console("Extrahierter Text:", transcript_result, mode=SUCC)
        return transcript_result


def text_to_speech(text):
    """
    Diese Funktion wandelt mittels AWS Polly einen Text in Echtzeit in eine Audiodatei mit gesprochenem Text um und
    stellt damit eine Alternative zur Funktion text_to_speech() dar.
    :param text: str, der umzuwandelnde Text
    :return: str, Dateiname der MP3-Datei mit der Ausgabe. Die Datei befindet sich im res-Ordner
    """

    console("Beginne mit Sprachsynthese", mode=INFO)

    tts_job = constants.aws_polly_obj.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId=constants.AWS_POLLY_VOICE,
        Engine=constants.AWS_POLLY_ENGINE,
        LanguageCode='de-DE',
        TextType='text'
    )
    tts_job_task_id = tts_job["ResponseMetadata"]["RequestId"]
    console("Der Sprachsynthesevorgang", tts_job_task_id, "wurde gestartet", mode=SUCC)

    stream = tts_job["AudioStream"]

    console("Schreibe in Datei", mode=INFO)
    with open(f"{constants.SAVEDIR_TELEGRAM_DL_FILES}{tts_job_task_id}.mp3", 'wb') as audio_output:
        audio_output.write(stream.read())

    return f"{tts_job_task_id}.mp3"
