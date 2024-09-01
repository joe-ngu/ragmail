import os.path
import logging
import base64
from bs4 import BeautifulSoup

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage

from config import settings, setup_logging

setup_logging("gmail_svc")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")


class GmailAPI:
    creds = None

    @classmethod
    def authenticate(cls):
        """Authenticates the user to get access to their gmail inbox"""
        if os.path.exists("token.json"):
            cls.creds = Credentials.from_authorized_user_file(
                "token.json", settings.SCOPES
            )

        if not cls.creds or not cls.creds.valid:
            if cls.creds and cls.creds.expired and cls.creds.refresh_token:
                cls.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, settings.SCOPES
                )
                cls.creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, "w") as token:
                token.write(cls.creds.to_json())

            cls.service = build("gmail", "v1", credentials=cls.creds)

    @classmethod
    def get_messages(cls, max_results=3):
        """Gets the most recent email messages from the authenticated user's inbox. The number of messages to return are limited by max_results."""
        try:
            cls.authenticate()

            inbox_info = (
                cls.service.users()
                .messages()
                .list(userId="me", maxResults=max_results)
                .execute()
            )
            logger.info(f"inbox: {inbox_info}")

            messages = inbox_info.get("messages")
            logger.info(f"messages: {messages}")

            for msg in messages:
                content = (
                    cls.service.users()
                    .messages()
                    .get(userId="me", id=msg["id"])
                    .execute()
                )

                try:
                    payload = content["payload"]
                    headers = payload["headers"]

                    subject = None
                    sender = None
                    for header in headers:
                        match header["name"]:
                            case "Subject":
                                subject = header["value"]
                            case "From":
                                sender = header["value"]

                    parts = payload.get("parts")[0]
                    data = parts["body"]["data"]
                    data = data.replace("-", "+").replace("_", "/")
                    decoded_data = base64.b64decode(data)

                    soup = BeautifulSoup(decoded_data, "lxml")
                    body = soup.get_text()

                    response = {
                        "Sender": sender,
                        "Subject": subject,
                        "Body": body,
                    }
                    return response

                except Exception as e:
                    logger.error(f"Error getting inbox messages: {e}")

        except HttpError as error:
            logger.error(f"An error occurred: {error}")

    @classmethod
    def create_draft(cls, receiver: str, subject: str, content: str):
        """Creates a draft that is to be sent to the receiver, with the given subject and contents of that message"""
        try:
            cls.authenticate()
            user_info = cls.service.users().getProfile(userId="me").execute()
            my_email_address = user_info["emailAddress"]

            message = EmailMessage()
            message.set_content(content)
            message["From"] = my_email_address
            message["To"] = receiver
            message["Subject"] = subject

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {"message": {"raw": encoded_message}}

            draft = (
                cls.service.users()
                .drafts()
                .create(userId="me", body=create_message)
                .execute()
            )
            print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            draft = None
        return draft
