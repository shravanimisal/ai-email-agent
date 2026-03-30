import os
import base64
import json
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# 🔑 AUTH (Render ENV based)
def get_gmail_service():
    token_data = os.environ.get("GOOGLE_TOKEN")

    if not token_data:
        raise Exception("❌ GOOGLE_TOKEN not found")

    creds_dict = json.loads(token_data)
    creds = Credentials.from_authorized_user_info(creds_dict, SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build('gmail', 'v1', credentials=creds)


# 📤 SEND EMAIL
def send_email(to, subject, body, attachment=None):
    try:
        service = get_gmail_service()

        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        if attachment and os.path.exists(attachment):
            with open(attachment, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(attachment)}"'
            )
            message.attach(part)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        service.users().messages().send(
            userId="me",
            body={'raw': raw}
        ).execute()

        return "✅ Sent"

    except Exception as e:
        return f"❌ Error: {str(e)}"


# 📤 BULK EMAIL
def send_bulk_emails(email_list, subject, body):
    results = []

    for email in email_list:
        status = send_email(email, subject, body)
        results.append({"email": email, "status": status})

    return results