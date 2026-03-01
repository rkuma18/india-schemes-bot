from fastapi import FastAPI, Form, Response, BackgroundTasks
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from src.session_store import get_session, add_to_session, clear_session
from src.rag_chain import build_rag_chain, ask
from dotenv import load_dotenv
import logging
import threading
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="India Schemes WhatsApp Bot")
rag_chain = None

def get_rag_chain():
    global rag_chain
    if rag_chain is None:
        rag_chain = build_rag_chain()
    return rag_chain

def warmup():
    try:
        logger.info("Warming up RAG chain...")
        get_rag_chain()
        logger.info("RAG chain ready.")
    except Exception as e:
        logger.error(f"Warmup failed: {e}")

threading.Thread(target=warmup, daemon=True).start()

GREETING_KEYWORDS = {"hi", "hello", "namaste", "hey", "helo", "hii"}
RESET_KEYWORDS = {"reset", "clear", "start over", "restart", "new"}

WELCOME_MESSAGE = """Namaste! I am your India Government Schemes Assistant.

I can help you find schemes for:
- Farmers and agriculture
- Women and girl child
- Senior citizens
- Students and education
- Health and insurance
- Housing and shelter
- Employment and skill development

Example questions:
1. My father is a 65-year-old farmer, which schemes is he eligible for?
2. What is PM Kisan Samman Nidhi and how to apply?
3. Which schemes are available for girl child education?

Just ask your question in simple English or Hindi."""


def chunk_message(text: str, limit: int = 1500) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()
    return chunks


def send_whatsapp_reply(to: str, message: str):
    """Send reply via Twilio API (used for async responses)."""
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    chunks = chunk_message(message)
    for chunk in chunks:
        client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
            to=to,
            body=chunk
        )


def process_rag_query(phone_number: str, user_message: str):
    """Run RAG in background and send reply via Twilio API."""
    try:
        history = get_session(phone_number)
        answer = ask(get_rag_chain(), user_message, history)
        add_to_session(phone_number, user_message, answer)
        send_whatsapp_reply(phone_number, answer)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        send_whatsapp_reply(phone_number, "Sorry, I am unable to process your request right now. Please try again or visit myscheme.gov.in")


@app.get("/")
def health_check():
    return {"status": "ok", "service": "India Schemes WhatsApp Bot"}


@app.post("/webhook")
async def webhook(
    background_tasks: BackgroundTasks,
    From: str = Form(...),
    Body: str = Form(...)
):
    phone_number = From.strip()
    user_message = Body.strip()
    logger.info(f"Message from {phone_number}: {user_message}")

    twiml = MessagingResponse()

    if user_message.lower() in GREETING_KEYWORDS:
        twiml.message(WELCOME_MESSAGE)
        return Response(content=str(twiml), media_type="application/xml")

    if user_message.lower() in RESET_KEYWORDS:
        clear_session(phone_number)
        twiml.message("Conversation cleared. Send 'hi' to start again.")
        return Response(content=str(twiml), media_type="application/xml")

    # Return empty 200 immediately, process RAG in background
    background_tasks.add_task(process_rag_query, phone_number, user_message)
    return Response(content=str(MessagingResponse()), media_type="application/xml")