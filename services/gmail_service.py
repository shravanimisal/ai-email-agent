import os
import base64
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


# =========================
# 🔑 AUTH
# =========================
def get_gmail_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build('gmail', 'v1', credentials=creds)


# =========================
# 📧 SEND EMAIL (UPDATED)
# =========================
def send_email(
    to,
    subject,
    body,
    attachment_data=None,
    attachment_name=None,
    attachment_type=None,
    attachment_path=None  # keep for backward compatibility
):
    try:
        service = get_gmail_service()

        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        # =========================
        # 🔥 PRIORITY 1: attachment_data (BULK)
        # =========================
        if attachment_data and attachment_name:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_data)

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{attachment_name}"'
            )

            message.attach(part)

        # =========================
        # 🔥 PRIORITY 2: attachment_path (SINGLE)
        # =========================
        elif attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(attachment_path)}"'
            )

            message.attach(part)

        # =========================
        # 📤 SEND
        # =========================
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        service.users().messages().send(
            userId="me",
            body={'raw': raw_message}
        ).execute()

        return "sent"

    except Exception as e:
        return f"error: {str(e)}"


# =========================
# 📂 EXTRACT EMAILS FROM FILE
# =========================
def extract_emails_from_file(file_path):
    emails = []

    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        for col in df.columns:
            for val in df[col]:
                if isinstance(val, str) and "@" in val:
                    emails.append(val.strip())

    except Exception as e:
        print("File error:", e)

    return list(set(emails))
