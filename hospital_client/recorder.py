from typing import Literal

import sounddevice as sd
from scipy.io.wavfile import write

from hospital_client.logger_config import setup_logger

logger = setup_logger(__name__)

AudioFormat = Literal["int16", "int8", "float32"]


def record_audio(
    filename: str = "output.wav",
    duration: float = 90.0,
    sample_rate: int = 44100,
    channels: int = 1,
    sample_format: AudioFormat = "int16",
) -> bool:
    """Records audio from the microphone and saves it as a WAV file using sounddevice.

    Args:
        filename: The name of the output WAV file. Defaults to "output.wav".
        duration: The recording duration in seconds. Defaults to 5.0.
        sample_rate: The sampling rate (frames per second). Defaults to 44100.
        channels: The number of audio channels (1 for mono, 2 for stereo). Defaults to 1.
        sample_format: The audio sample format ('int16', 'int8', 'float32').
                       Defaults to 'int16' (16-bit integer).

    Returns:
        True if the recording was successful, False otherwise.
    """
    try:
        logger.info(
            f"Recording for {duration} seconds at {sample_rate} Hz with {channels} channels in {sample_format} format..."
        )

        # Determine the dtype for sounddevice
        dtype = sample_format

        # Record audio
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype=dtype,
        )
        sd.wait()  # Wait until recording is finished

        # Save as WAV file using scipy
        write(filename, sample_rate, recording)
        logger.info(f"Recording saved to '{filename}'")
        return True

    except Exception as e:
        logger.error(f"Error during recording: {e}")
        return False
