from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from src.session_store import add_to_session
from dotenv import load_dotenv
import os

load_dotenv()

SYSTEM_PROMPT = """You are a helpful assistant that answers questions about Indian government welfare schemes.
You help citizens understand which schemes they are eligible for, how to apply, and what benefits they will receive.

Use the following context from official government documents to answer the question.
If you don't know the answer or it's not in the context, say "I don't have information about that. Please visit myscheme.gov.in for more details."

Keep your answers clear and simple. Avoid jargon. Use plain language that anyone can understand.
Do not use markdown formatting like ** or ## as this is a WhatsApp conversation.
Structure your answer in short paragraphs.

Context:
{context}"""

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])


def get_llm():
    """Initialize Gemini LLM."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
        max_output_tokens=1024
    )


def build_rag_chain():
    """Build a RAG chain using LCEL with MMR retrieval."""
    from src.indexing import get_vectorstore
    vectorstore = get_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "fetch_k": 10}
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {
            "context": RunnableLambda(lambda x: x["question"]) | retriever | format_docs,
            "chat_history": RunnableLambda(lambda x: x["chat_history"]),
            "question": RunnableLambda(lambda x: x["question"]),
        }
        | PROMPT
        | get_llm()
        | StrOutputParser()
    )

    return chain


def ask(chain, question: str, chat_history: list) -> str:
    """Ask a question and get an answer."""
    try:
        answer = chain.invoke({"question": question, "chat_history": chat_history})
        return answer
    except Exception as e:
        print(f"RAG chain error: {e}")
        return "Sorry, I encountered an error. Please try again or visit myscheme.gov.in for help."
