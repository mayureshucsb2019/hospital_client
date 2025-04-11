import asyncio
import os
from pathlib import Path
from typing import List

import google.generativeai as genai
import PyPDF2
from dotenv import load_dotenv

from hospital_client.constant import (
    CHECK_INCONSISTENCTIES,
    GOV_POLICY_SUMMARY_MAP,
    GOVT_DOC_DIR_PATH,
    HOS_POLICY_SUMMARY_MAP,
    HOSP_DOC_DIR_PATH,
    PDF_PAGE_CHUNK_SIZE,
    SUMMARIZE_PDF_FILE,
)
from hospital_client.logger_config import setup_logger

logger = setup_logger(__name__)
# Load environment variables from .env file
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


def generate_summary_txt_path(filepath: Path, extension: str) -> Path:
    # Get the parent directory of the original file
    parent_dir = filepath.parent

    # Define the "summary" directory as a sibling directory to the parent
    summary_dir = parent_dir / "summary"

    # Ensure the "summary" directory exists
    summary_dir.mkdir(parents=True, exist_ok=True)

    # Create the summary file path in the "summary" directory
    summary_path = summary_dir / f"{filepath.stem}_summary{extension}"

    return summary_path


def get_summarized_txt_from_pdf(filepath: Path) -> bool:
    logger.info(filepath)
    try:
        with open(generate_summary_txt_path(filepath, ".txt"), "w") as summary_file:
            with open(filepath, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                page_counter = 1
                total_pages = len(reader.pages)
                text = ""
                while page_counter <= total_pages:
                    page = reader.pages[page_counter - 1]
                    text += page.extract_text()
                    logger.info(f"Page extracted {page_counter} of {total_pages}")
                    if (
                        page_counter % PDF_PAGE_CHUNK_SIZE == 0
                        or page_counter == total_pages
                    ):
                        logger.info(
                            f"Text generation started... completed {page_counter} of {total_pages}"
                        )
                        response = model.generate_content(
                            f"{SUMMARIZE_PDF_FILE}: {text}"
                        )
                        logger.info("Text generation completed...")
                        summary_file.write(response.text + "\n")
                        text = ""
                    page_counter += 1
            return True
    except FileNotFoundError:
        logger.info("Error: PDF not found.")
        return False
    except Exception:
        return False
        logger.info("An error occurred: {e}")


def get_generated_text(filename: str, action: str):
    with open(f"{filename}.txt", "r") as file:
        logger.info("Text generation started...")
        response = model.generate_content(f"{action}: {file.read()}")
        logger.info("Text generation completed...")
    summarizedFileName = f"{filename}_summarized.txt"
    with open(summarizedFileName, "w") as file:
        logger.info(f"Write started {summarizedFileName}...")
        file.write(response.text)
        logger.info("Write summary completed...")


def check_inconsistencies(summary1: str, summary2: str) -> str:
    response = model.generate_content(
        f"{CHECK_INCONSISTENCTIES}: FIRST POLICY: {summary1} -- SECOND POLICY: {summary2}"
    )
    return response.text


def extract_text_pypdf2(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
    except FileNotFoundError:
        return "Error: PDF not found."
    except Exception as e:
        return f"An error occurred: {e}"
    return text


async def get_matching_documents(query: str) -> List[str]:
    document_list = []
    for file in GOV_POLICY_SUMMARY_MAP.keys():
        response = model.generate_content(
            f"Is summary related to query? Just: Yes or No. SUMMARY: {GOV_POLICY_SUMMARY_MAP[file]} QUERY: {query}"
        )
        if "yes" in str(response.text).lower():
            document_list.append(file)
        await asyncio.sleep(5)

    for file in HOS_POLICY_SUMMARY_MAP.keys():
        response = model.generate_content(
            f"Is summary related to query? Just: Yes or No. SUMMARY: {HOS_POLICY_SUMMARY_MAP[file]} QUERY: {query}"
        )
        if "yes" in str(response.text).lower():
            document_list.append(file)
        await asyncio.sleep(5)
    return document_list


async def get_document_references(query: str, filename: str) -> str:
    reference_text = ""
    cwd = os.getcwd()
    try:
        if filename in GOV_POLICY_SUMMARY_MAP.keys():
            pdf_path = Path(os.path.join(cwd, GOVT_DOC_DIR_PATH, filename + ".pdf"))
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                page_counter = 1
                total_pages = len(reader.pages)
                text = ""
                while page_counter <= total_pages:
                    page = reader.pages[page_counter - 1]
                    text += f"PAGE NUMBER {page_counter} " + page.extract_text()
                    logger.info(f"Page extracted {page_counter} of {total_pages}")
                    if (
                        page_counter % PDF_PAGE_CHUNK_SIZE == 0
                        or page_counter == total_pages
                    ):
                        logger.info(
                            f"Text referencing started... completed {page_counter} of {total_pages}"
                        )
                        response = model.generate_content(
                            f"Check if there query can be referenced in these pages and quote accordingly with page numbers? TEXT: {text} QUERY: {query}"
                        )
                        text = ""
                        reference_text += response.text
                    page_counter += 1
                return reference_text
        elif filename in HOS_POLICY_SUMMARY_MAP.keys():
            pdf_path = Path(os.path.join(cwd, HOSP_DOC_DIR_PATH, filename + ".pdf"))
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                page_counter = 1
                total_pages = len(reader.pages)
                text = ""
                while page_counter <= total_pages:
                    page = reader.pages[page_counter - 1]
                    text += f"PAGE NUMBER {page_counter} " + page.extract_text()
                    logger.info(f"Page extracted {page_counter} of {total_pages}")
                    if (
                        page_counter % PDF_PAGE_CHUNK_SIZE == 0
                        or page_counter == total_pages
                    ):
                        logger.info(
                            f"Text referencing started... completed {page_counter} of {total_pages}"
                        )
                        response = model.generate_content(
                            f"Check if there query can be referenced in these pages and quote accordingly with page numbers? TEXT: {text} QUERY: {query}"
                        )
                        text = ""
                        reference_text += response.text
                    page_counter += 1
                return reference_text
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        return "Error: PDF not found."
    except Exception as e:
        return f"An error occurred: {e}"


async def get_summarized_reference(pdf_path: Path, query: str) -> str:
    reference_text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        page_counter = 1
        total_pages = len(reader.pages)
        text = ""
        errored = False
        while page_counter <= total_pages:
            if not errored:
                page = reader.pages[page_counter - 1]
                text += f"PAGE NUMBER {page_counter} " + page.extract_text()
            if page_counter % PDF_PAGE_CHUNK_SIZE == 0 or page_counter == total_pages:
                try:
                    response = model.generate_content(
                        f"Check if the query can be referenced in these pages and quote accordingly with page numbers? TEXT: {text} QUERY: {query}. If yes summarize if else give ONLY one word answer: No"
                        # f"Do you find contex of QUERY: {query} in TEXT: {text}. If yes give well rounded summary and reference in text. If no answer just No."
                    )
                    text = ""
                    if "no" not in response.text[:2].lower():
                        reference_text += (
                            "**" + pdf_path.stem + "**\n" + response.text + "\n"
                        )
                        print(response.text)
                    print("---------", pdf_path.stem, "---------")
                    errored = False
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.info(f"An error occurred: {e} ... retrying...")
                    errored = True
                    await asyncio.sleep(2)
                    continue
            page_counter += 1
        return reference_text


async def lookup_query(query: str) -> str:
    reference_text = "\n\n**REFERENCES:**\n\n"
    cwd = os.getcwd()
    try:
        response = model.generate_content(query)
        print("received generic response")
        for filename in GOV_POLICY_SUMMARY_MAP.keys():
            print(f"Checking file #################### {filename}")
            pdf_path = Path(os.path.join(cwd, GOVT_DOC_DIR_PATH, filename + ".pdf"))
            reference_text += await get_summarized_reference(
                pdf_path=pdf_path, query=query
            )
        for filename in HOS_POLICY_SUMMARY_MAP.keys():
            print(f"Checking file #################### {filename}")
            pdf_path = Path(os.path.join(cwd, HOSP_DOC_DIR_PATH, filename + ".pdf"))
            reference_text += await get_summarized_reference(
                pdf_path=pdf_path, query=query
            )
        return response.text + reference_text
    except FileNotFoundError:
        return "Error: PDF not found."
    except Exception as e:
        return f"An error occurred: {e}"
