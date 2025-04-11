import asyncio
import os
from pathlib import Path
from typing import List

from hospital_client.constant import (
    GOV_POLICY_SUMMARY_MAP,
    GOVT_DOC_DIR_PATH,
    HOS_POLICY_SUMMARY_MAP,
    HOSP_DOC_DIR_PATH,
)
from hospital_client.emailer import send_email_with_attachments
from hospital_client.logger_config import setup_logger
from hospital_client.pdf_generator import convert_markdown_txt_to_pdf
from hospital_client.summarizer import (
    check_inconsistencies,
    generate_summary_txt_path,
    get_summarized_txt_from_pdf,
)

logger = setup_logger(__name__)


def sync_index_file(filepath: str):
    path = Path(filepath)
    if not path.exists():
        logger.warning(f"Index file path not found: {filepath}")
        return False
    files = [f for f in path.parent.iterdir() if f.is_file()]
    files.sort()
    with open(path, "w") as file:
        for filename in files:
            file.write(filename + "\n")
        logger.info(f"Completed writin to {path}")
    return True


async def init_policy_summary_maps(
    gov_doc_files: List[Path], hos_doc_files: List[Path]
):
    for file in gov_doc_files:
        if file.suffix != ".pdf":
            continue
        summary_text_path = generate_summary_txt_path(file, ".txt")
        if not summary_text_path.exists:
            get_summarized_txt_from_pdf(file)
        with open(summary_text_path, "r") as f:
            text = f.read()
        GOV_POLICY_SUMMARY_MAP[file.stem] = text

    for file in hos_doc_files:
        if file.suffix != ".pdf":
            continue
        summary_text_path = generate_summary_txt_path(file, ".txt")
        if not summary_text_path.exists:
            get_summarized_txt_from_pdf(file)
        with open(summary_text_path, "r") as f:
            text = f.read()
        HOS_POLICY_SUMMARY_MAP[file.stem] = text
    logger.info(f"received summary of all the files...")


async def monitoring_agent():
    logger.info("Running monitoring agent...")
    cwd = os.getcwd()
    gov_doc_dir = Path(os.path.join(cwd, GOVT_DOC_DIR_PATH))
    hos_doc_dir = Path(os.path.join(cwd, HOSP_DOC_DIR_PATH))
    if not gov_doc_dir.exists():
        logger.error(f"Directory not found: {hos_doc_dir}")
    if not hos_doc_dir.exists():
        logger.error(f"Directory not found: {hos_doc_dir}")
    gov_doc_files = [
        f for f in gov_doc_dir.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"
    ]
    hos_doc_files = [
        f for f in hos_doc_dir.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"
    ]

    await init_policy_summary_maps(gov_doc_files, hos_doc_files)
    while True:
        temp_gov_doc_files = [
            f
            for f in gov_doc_dir.iterdir()
            if f.is_file() and f.suffix.lower() == ".pdf"
        ]
        temp_hos_doc_files = [
            f
            for f in hos_doc_dir.iterdir()
            if f.is_file() and f.suffix.lower() == ".pdf"
        ]
        if len(temp_gov_doc_files) > len(gov_doc_files):
            for file in temp_gov_doc_files:
                if file not in gov_doc_files:
                    logger.info(
                        "summarize the file and send email to all. new government policy file added"
                    )
                    get_summarized_txt_from_pdf(file)
                    summary_text_path = generate_summary_txt_path(file, ".txt")
                    convert_markdown_txt_to_pdf(summary_text_path)
                    with open(summary_text_path, "r") as f:
                        text = f.read()
                    GOV_POLICY_SUMMARY_MAP[summary_text_path.stem] = text
                    send_email_with_attachments(
                        subject=f"IMPORTANT: New government policy file added",
                        body="Please find summary of file attached with email",
                        recipient_emails=[
                            "mayuresh.anand@rotman.utoronto.ca",
                        ],
                        attachment_paths=[generate_summary_txt_path(file, ".pdf")],
                    )
                    # delete summary txt
                    for hos_file in hos_doc_files:
                        answer = check_inconsistencies(
                            text,
                            HOS_POLICY_SUMMARY_MAP[hos_file.stem],
                        )
                        if "yes" in answer[:3].lower():
                            send_email_with_attachments(
                                subject=f"IMPORTANT: Found inconsistency in hospital policies {hos_file.stem} VS {summary_text_path.stem}",
                                body=answer,
                                recipient_emails=[
                                    "mayuresh.anand@rotman.utoronto.ca",
                                ],
                            )
        elif len(temp_gov_doc_files) < len(gov_doc_files):
            for file in gov_doc_files:
                if file not in temp_gov_doc_files:
                    send_email_with_attachments(
                        subject=f"IMPORTANT: Policy removed from government policies",
                        body=f"Please check {file}",
                        recipient_emails=[
                            "mayuresh.anand@rotman.utoronto.ca",
                        ],
                    )

        if len(temp_hos_doc_files) > len(hos_doc_files):
            for file in temp_hos_doc_files:
                if file not in hos_doc_files:
                    logger.info(
                        "summarize the file and send email to all. New hospital policy file added"
                    )
                    get_summarized_txt_from_pdf(file)
                    summary_text_path = generate_summary_txt_path(file, ".txt")
                    convert_markdown_txt_to_pdf(summary_text_path)
                    with open(summary_text_path, "r") as f:
                        text = f.read()
                    HOS_POLICY_SUMMARY_MAP[summary_text_path.stem] = text
                    send_email_with_attachments(
                        subject=f"IMPORTANT: New hospital policy file added",
                        body="Please find summary of file attached with email",
                        recipient_emails=[
                            "mayuresh.anand@rotman.utoronto.ca",
                        ],
                        attachment_paths=[generate_summary_txt_path(file, ".pdf")],
                    )
                    # delete summary txt
                    for gov_file in gov_doc_files:
                        answer = check_inconsistencies(
                            text,
                            GOV_POLICY_SUMMARY_MAP[gov_file.stem],
                        )
                        if "yes" in answer[:3].lower():
                            send_email_with_attachments(
                                subject=f"IMPORTANT: Found inconsistency in hospital policies {summary_text_path.stem} VS {gov_file.stem}",
                                body=answer,
                                recipient_emails=[
                                    "mayuresh.anand@rotman.utoronto.ca",
                                ],
                            )
        elif len(temp_hos_doc_files) < len(hos_doc_files):
            for file in hos_doc_files:
                if file not in temp_hos_doc_files:
                    send_email_with_attachments(
                        subject=f"IMPORTANT: Policy removed from hospital policies",
                        body=f"Please check {file}",
                        recipient_emails=[
                            "mayuresh.anand@rotman.utoronto.ca",
                        ],
                    )
        hos_doc_files = temp_hos_doc_files
        gov_doc_files = temp_gov_doc_files

        logger.info("checked database for changes in policies")
        await asyncio.sleep(2)
