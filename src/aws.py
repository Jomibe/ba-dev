"""
Diese Datei enthält Funktionen für die Kommunikation mit Amazon Web Services, u.A. für den Upload von Dateien in S3
sowie für die Umwandlung zwischen Sprache und Text.
"""

# Imports aus Standardbibliotheken
from time import sleep
import json
import os

# Imports von Drittanbietern
import boto3  # AWS Python SDK
import asyncio
import aiofile
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

# Eigene Imports
import constants
from constants import SAVEDIR_TELEGRAM_DL_FILES
from debugging import console, INFO, WARN, ERR, SUCC


def init_s3_api():
    """
    Diese Funktion prüft die Verbindung zur AWS API und bereitet den Zugriff auf den S3-Bucket vor.
    """
    if not constants.ENABLE_FAILSAFE_TRANSCRIPTION:
        # Die Verbindung zu S3 wird nur benötigt, wenn die Option ENABLE_FAILSAFE_TRANSCRIPTION aktiviert ist.
        # Siehe constants.py
        return True

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

    if not constants.ENABLE_FAILSAFE_TRANSCRIPTION:
        # Die Verbindung zu Transcribe über boto3 wird nur benötigt, wenn die Option ENABLE_FAILSAFE_TRANSCRIPTION
        # aktiviert ist. Siehe constants.py
        return True

    console("Prüfe Verbindung zu AWS Transcribe in der Region", constants.aws_region, mode=INFO)
    constants.aws_transcribe_obj = boto3.client(
        service_name='transcribe',
        region_name=constants.aws_region,
        aws_access_key_id=constants.aws_access_key_id,
        aws_secret_access_key=constants.aws_secret_access_key
    )
    console("Verbindung zu AWS Transcribe aufgebaut", mode=SUCC)

    return True


def init_transcribe_rt_api():
    """
    Diese Funktion prüft die Verbindung zur AWS API und bereitet den Zugriff auf den Transcribe-Übersetzungsdienst für
    Echtzeit-Transkription vor.
    :return: bool, ob die Aktion erfolgreich war.
    """

    if constants.ENABLE_FAILSAFE_TRANSCRIPTION:
        # Die Verbindung zu Transcribe über das AWS Transcribe SDK wird nur benötigt, wenn die Option
        # ENABLE_FAILSAFE_TRANSCRIPTION aktiviert ist. Siehe constants.py
        return True

    console("Stelle Verbindung zu AWS Transcribe in der Region", constants.aws_region, "her", mode=INFO)
    # Die Übermittlung der API-Zugangsdaten erfolgt über Umgebungsvariablen
    constants.aws_transcribe_rt_obj = TranscribeStreamingClient(region=constants.aws_region)

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
    upload_file_to_s3(filename, SAVEDIR_TELEGRAM_DL_FILES)

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


class TranscriptEventHandler(TranscriptResultStreamHandler):
    text = ""  # Variable für das Ergebnis der Transkription

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        # This handler can be implemented to handle transcriptions as needed.
        # Here's an example to get started.
        results = transcript_event.transcript.results

        for result in results:
            for alt in result.alternatives:
                if not result.is_partial:  # Quelle: https://stackoverflow.com/questions/72875996
                    console("Transkription abgeschlossen. Ergebnis:", alt.transcript, mode=SUCC)
                else:
                    self.text = alt.transcript
                    console("Transkription wird durchgeführt, nicht finales Ergebnis wurde übermittelt:",
                            alt.transcript, mode=INFO)


async def basic_transcribe(filename):
    console("Beginne mit Datenübertragung zu AWS Transcribe", mode=INFO)
    # Start transcription to generate our async stream
    stream = await constants.aws_transcribe_rt_obj.start_stream_transcription(
        language_code="de-DE",
        media_sample_rate_hz=16000,
        media_encoding="ogg-opus",
        enable_partial_results_stabilization="True"
    )

    async def write_chunks():
        async with aiofile.AIOFile(filename, "rb") as afp:
            reader = aiofile.Reader(afp, chunk_size=1024 * 16)
            async for chunk in reader:
                console("Übertrage Abschnitt von", f"{1024*16}B", "der Datei", filename, "an AWS Transcribe", mode=INFO)
                await stream.input_stream.send_audio_event(audio_chunk=chunk)
        await stream.input_stream.end_stream()
        console("Datenübertragung abgeschlossen. Warte auf Abschluss des Transkriptionsprozesses", mode=SUCC)

    # Instantiate our handler and start processing events
    handler = TranscriptEventHandler(stream.output_stream)
    console("Bereite Verarbeitung der von AWS Transcribe übermittelten Daten vor", mode=INFO)
    await asyncio.gather(write_chunks(), handler.handle_events())
    return handler.text


def transcribe_realtime(filename):
    console("Beginne mit Echtzeitübersetzung Sprache zu Text", mode=INFO)

    os.environ["AWS_ACCESS_KEY_ID"] = constants.aws_access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = constants.aws_secret_access_key

    # loop = asyncio.get_event_loop()
    loop = asyncio.new_event_loop()
    # Der Rückgabewert der asynchronen Funktion wird durchgereicht
    text = loop.run_until_complete(basic_transcribe(filename))
    loop.close()

    return text
