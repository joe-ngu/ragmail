import logging
import sys

from services.gmail import GmailAPI
from llm.langgraph import workflow
from config import setup_logging

setup_logging("app")
logger = logging.getLogger(__name__)

# == COMPILE LANGGRAPH == #
app = workflow.compile()


# == GET EMAIL MESSAGE == #
type SenderInfo = tuple[str, str]
type EmailMessage = tuple[SenderInfo, str, str]


def get_email_message() -> EmailMessage:
    """
    Gets email messages from the authenticated user's inbox and returns information about
    the message(s), including the name and email address of the sender, the subject, and
    contents of the email message(s). The number of messages to fetch is defined in the
    GmailAPI class which wraps the Gmail API's service calls.
    """
    if (response := GmailAPI.get_messages()) is None:
        logger.error("failed to get email")
        sys.exit(1)

    sender = parse_sender(response["Sender"])
    subject = response["Subject"]
    body = response["Body"]

    logger.info(
        f"""
        Sender: {sender},
        Subject: {subject},
        Body: {body},
    """
    )
    return sender, subject, body


def parse_sender(sender) -> SenderInfo:
    """Helper function to parse the sender info into name and email address"""
    sender = sender.strip()
    parts = sender.rsplit(" ", 1)
    name = parts[0]
    email = parts[1].strip("<>")
    return name, email


# == PASS EMAIL QUESTION TO LANGGRAPH == #
def answer_question(question) -> str | None:
    """
    Given a question, pass it through the LangGraph nodes which route the question
    to the appropriate nodes, generate an answer, check for hallucinations, grade
    the answer, and return an approriate response
    """
    inputs = {"question": question}
    answer = None
    has_output = False
    for output in app.stream(inputs):
        for _, value in output.items():
            has_output = True

    if not has_output:
        logger.error("failed to get output from langgraph")
        sys.exit(1)

    if (answer := value["generation"]) is None:
        logger.error("failed to generate answer from langgraph")
        sys.exit(1)

    logger.info(answer)
    return answer


# == CREATE EMAIL DRAFT == #
def create_draft(reciever, subject, content) -> bool:
    """
    Given an email address to send to, a subject, and message contents, generate
    an email draft in the authenticated user's email drafts
    """
    draft = GmailAPI.create_draft(receiver=reciever, subject=subject, content=content)
    if draft is None:
        logger.error("failed to generate draft")
    return True if draft else False


if __name__ == "__main__":
    sender_info, subject, body = get_email_message()
    sender_name, sender_email_address = sender_info
    answer = answer_question(body)
    created_draft = create_draft(
        reciever=sender_email_address,
        subject=f"Re: {subject}",
        content=answer,
    )
    if created_draft:
        print(f"Generated reply to {sender_name}")
