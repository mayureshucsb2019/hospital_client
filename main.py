from datetime import datetime

from dotenv import load_dotenv

from hospital_client.emailer import send_email_with_attachments
from hospital_client.pdf_generator import convert_markdown_to_pdf
from hospital_client.recorder import record_audio
from hospital_client.summarizer import get_generated_text
from hospital_client.transcriber import transcribe_audio_file

# Load environment variables from .env file
load_dotenv()


def main():
    # Format: YYYY-MM-DD_HH-MM-SS
    date_time_string = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
    wavfilename = f"recording_{date_time_string}"
    # TODO @Mayuresh add automated file name as per date and time
    record_audio(
        filename=f"{wavfilename}.wav",
        duration=90,
        sample_rate=48000,
        channels=1,
        sample_format="int16",
    )

    transcribe_audio_file(filename=wavfilename)
    get_generated_text(filename=wavfilename, action="Summarize in points")
    convert_markdown_to_pdf(filename=f"{wavfilename}_summarized")
    send_email_with_attachments(
        subject=f"Meeting {date_time_string} ",
        body="Summary",
        recipient_emails=[
            "anand0mayuresh@gmail.com",
            "mayureshucsb@gmail.com",
            "mayuresh.anand@rotman.utoronto.ca",
        ],
        attachment_paths=[f"{wavfilename}_summarized.pdf"],
    )


if __name__ == "__main__":
    transcribe_audio_file("recording_2025_04_09_10_56_18")
