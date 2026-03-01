from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime, timedelta

# Session store: phone_number -> {history, last_active}
sessions = {}

SESSION_TIMEOUT_MINUTES = 30
MAX_WINDOW = 5  # remember last 5 exchanges


def get_session(phone_number: str) -> list:
    """Get or create a message history session for a phone number."""
    now = datetime.utcnow()

    # Clean up expired sessions
    expired = [
        k for k, v in sessions.items()
        if now - v["last_active"] > timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    ]
    for k in expired:
        del sessions[k]

    # Create new session if needed
    if phone_number not in sessions:
        sessions[phone_number] = {
            "history": [],
            "last_active": now
        }

    sessions[phone_number]["last_active"] = now
    return sessions[phone_number]["history"]


def add_to_session(phone_number: str, question: str, answer: str):
    """Append a Q&A exchange to the session, keeping only the last MAX_WINDOW."""
    history = get_session(phone_number)
    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=answer))
    # Trim to last MAX_WINDOW exchanges (each exchange = 2 messages)
    if len(history) > MAX_WINDOW * 2:
        del history[:len(history) - MAX_WINDOW * 2]


def clear_session(phone_number: str):
    """Clear session for a phone number."""
    if phone_number in sessions:
        del sessions[phone_number]


def session_exists(phone_number: str) -> bool:
    return phone_number in sessions
