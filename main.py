import asyncio

import uvicorn
from dotenv import load_dotenv

from hospital_client.doc_monitoring_agent import monitoring_agent
from server import app

# Load environment variables from .env file
load_dotenv()


# def main():
#     # Format: YYYY-MM-DD_HH-MM-SS
#     date_time_string = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
#     wavfilename = f"recording_{date_time_string}"
#     # TODO @Mayuresh add automated file name as per date and time
#     record_audio(
#         filename=f"{wavfilename}.wav",
#         duration=90,
#         sample_rate=48000,
#         channels=1,
#         sample_format="int16",
#     )

#     transcribe_audio_file(filename=wavfilename)
#     get_generated_text(filename=wavfilename, action="Summarize in points")
#     convert_markdown_to_pdf(filename=f"{wavfilename}_summarized")
#     send_email_with_attachments(
#         subject=f"Meeting {date_time_string} ",
#         body="Summary",
#         recipient_emails=[
#             "mayuresh.anand@rotman.utoronto.ca",
#         ],
#         attachment_paths=[f"{wavfilename}_summarized.pdf"],
#     )


async def run_uvicorn():
    # Run the FastAPI app with uvicorn in the same event loop
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    # Get the event loop
    loop = asyncio.get_event_loop()

    # Start the monitoring agent as a background task
    loop.create_task(monitoring_agent())

    # Run FastAPI app using uvicorn in the same event loop
    loop.create_task(run_uvicorn())

    # Run the event loop
    loop.run_forever()
