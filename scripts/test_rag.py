import sys
sys.path.append(".")

from src.session_store import get_session, add_to_session
from src.rag_chain import build_rag_chain, ask

if __name__ == "__main__":
    print("Testing RAG chain locally...\n")

    chain = build_rag_chain()

    phone = "test_user"
    questions = [
        "What is PM Kisan Samman Nidhi?",
        "My father is a 65 year old farmer with 2 acres of land. Which schemes is he eligible for?",
        "How do I apply for Pradhan Mantri Jan Dhan Yojana?"
    ]

    for q in questions:
        history = get_session(phone)
        print(f"Q: {q}")
        answer = ask(chain, q, history)
        add_to_session(phone, q, answer)
        print(f"A: {answer}")
        print("-" * 60)
