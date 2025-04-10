import os

import assemblyai
from dotenv import load_dotenv

from hospital_client.logger_config import setup_logger

# Load environment variables from .env file
load_dotenv()
logger = setup_logger(__name__)


def transcribe_audio_file(filename: str):
    # Upload your audio file
    assemblyai.settings.api_key = os.getenv("ASSEMBLY_AI_API_KEY")
    transcriber = assemblyai.Transcriber()
    # Set the transcription configuration with diarization (speaker labels)
    config = assemblyai.TranscriptionConfig(speaker_labels=True, speakers_expected=10)
    transcript = transcriber.transcribe(
        f"./{filename}.wav", config=config
    )  # or local file path
    transcribeFilename = f"{filename}.txt"
    for utterance in transcript.utterances:
        logger.info(f"Speaker {utterance.speaker}: {utterance.text}")
    with open(transcribeFilename, "w") as file:
        # Print the transcribed text
        logger.info(f"Writing to the text file {transcribeFilename} ...")
        file.write(transcript.text)
        logger.info("Writing completed ...")
