# Quelle: https://github.com/awslabs/amazon-transcribe-streaming-sdk/blob/v0.6.0/examples/simple_file.py
# @v0.6.0


# Imports aus Standardbibliotheken
import os

# Imports von Drittanbietern
import asyncio
import aiofile

# Eigene Imports
import constants
from debugging import console, INFO, WARN, ERR, SUCC
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent


class MyEventHandler(TranscriptResultStreamHandler):
    text = ""

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        # This handler can be implemented to handle transcriptions as needed.
        # Here's an example to get started.
        results = transcript_event.transcript.results

        for result in results:
            for alt in result.alternatives:
                if not result.is_partial:  # Quelle: https://stackoverflow.com/questions/72875996
                    console("Transkription abgeschlossen. Ergebnis:", alt.transcript, mode=SUCC)
                else:
                    console("Transkription wird durchgeführt, nicht finales Ergebnis wurde übermittelt:",
                            alt.transcript, mode=INFO)


async def basic_transcribe(filename):
    console("Stelle Verbindung zu AWS Transcribe in der Region", "eu-central-1", "her", mode=INFO)
    # Setup up our client with our chosen AWS region
    client = TranscribeStreamingClient(region="eu-central-1")

    console("Beginne mit Datenübertragung zu AWS Transcribe", mode=INFO)
    # Start transcription to generate our async stream
    stream = await client.start_stream_transcription(
        language_code="de-DE",
        media_sample_rate_hz=16000,
        media_encoding="ogg-opus",
    )

    async def write_chunks():
        async with aiofile.AIOFile(filename, "rb") as afp:
            reader = aiofile.Reader(afp, chunk_size=1024 * 16)
            async for chunk in reader:
                console("Übertrage Abschnitt von", "16 KB", "der Datei", filename, "an AWS Transcribe", mode=INFO)
                await stream.input_stream.send_audio_event(audio_chunk=chunk)
        await stream.input_stream.end_stream()
        console("Datenübertragung abgeschlossen. Warte auf Abschluss des Transkriptionsprozesses", mode=SUCC)

    # Instantiate our handler and start processing events
    handler = MyEventHandler(stream.output_stream)
    await asyncio.gather(write_chunks(), handler.handle_events())


def transcribe_rt(filename):
    console("Beginne mit Echtzeitübersetzung Sprache zu Text", mode=INFO)

    os.environ["AWS_ACCESS_KEY_ID"] = constants.aws_access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = constants.aws_secret_access_key

    loop = asyncio.get_event_loop()
    loop.run_until_complete(basic_transcribe(filename))
    loop.close()
