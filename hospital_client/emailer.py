import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from dotenv import load_dotenv

from hospital_client.logger_config import setup_logger

load_dotenv()
logger = setup_logger(__name__)


def send_email_with_attachments(
    subject: str,
    body: str,
    recipient_emails: List[str],
    attachment_paths: Optional[List[str]] = None,
):
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    # Set up the MIME message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Combine the list of recipient emails into a comma-separated string
    message["To"] = ", ".join(recipient_emails)

    # Add attachments if provided
    if attachment_paths:
        for attachment_path in attachment_paths:
            if os.path.isfile(attachment_path):
                try:
                    with open(attachment_path, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)  # Encode the attachment in base64

                        # Add the header to the attachment
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(attachment_path)}",
                        )

                        # Attach the file to the message
                        message.attach(part)
                        logger.info(
                            f"Attachment {os.path.basename(attachment_path)} added successfully!"
                        )
                except Exception as e:
                    logger.info(f"Error adding attachment {attachment_path}: {e}")
                    continue  # Continue with the next file if there is an error
            else:
                logger.info(f"Attachment file {attachment_path} does not exist.")

    try:
        # Connect to the Gmail SMTP server
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, password)  # Log in to the email server

        # Send the email to all recipients
        text = message.as_string()  # Convert the message to string format
        server.sendmail(sender_email, recipient_emails, text)

        logger.info("Email sent successfully to all recipients!")
    except Exception as e:
        logger.info(f"Error: {e}")
    finally:
        server.quit()  # Close the connection to the server
