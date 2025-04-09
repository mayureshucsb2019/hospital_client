import os

import google.generativeai as genai
from dotenv import load_dotenv

from hospital_client.logger_config import setup_logger

logger = setup_logger(__name__)
# Load environment variables from .env file
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


def get_generated_text(filename: str, action: str):
    global model
    with open(f"{filename}.txt", "r") as file:
        logger.info("Text generation started...")
        response = model.generate_content(f"{action}: {file.read()}")
        logger.info("Text generation completed...")
    summarizedFileName = f"{filename}_summarized.txt"
    with open(summarizedFileName, "w") as file:
        logger.info(f"Write started {summarizedFileName}...")
        file.write(response.text)
        logger.info("Write summary completed...")
