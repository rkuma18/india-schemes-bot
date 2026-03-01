from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv
import os

load_dotenv()

COLLECTION_NAME = "india_schemes"
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 100


def get_embeddings():
    """Load BGE embeddings model."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


def get_qdrant_client():
    """Connect to Qdrant Cloud."""
    return QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )


def create_collection_if_not_exists(client: QdrantClient):
    """Create Qdrant collection if it doesn't exist."""
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
        print(f"Created collection: {COLLECTION_NAME}")
    else:
        print(f"Collection already exists: {COLLECTION_NAME}")


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Split documents into chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]
    )

    chunks = []
    for doc in documents:
        splits = splitter.split_text(doc["content"])
        for i, split in enumerate(splits):
            chunks.append({
                "content": split,
                "metadata": {
                    "title": doc["title"],
                    "source": doc["source"],
                    "chunk_index": i
                }
            })

    print(f"Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks


def index_documents(documents: list[dict]):
    """Full pipeline: chunk -> embed -> upload to Qdrant."""
    print("Starting indexing pipeline...")

    # Step 1: Chunk
    chunks = chunk_documents(documents)
    if not chunks:
        print("No chunks to index.")
        return

    # Step 2: Connect to Qdrant
    client = get_qdrant_client()
    create_collection_if_not_exists(client)

    # Step 3: Load embeddings
    print("Loading embedding model (first time will download ~400MB)...")
    embeddings = get_embeddings()

    # Step 4: Upload to Qdrant
    texts = [c["content"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )
    vectorstore.add_texts(texts=texts, metadatas=metadatas)
    print(f"Successfully indexed {len(chunks)} chunks to Qdrant.")


def get_vectorstore():
    """Get existing vectorstore for querying."""
    client = get_qdrant_client()
    embeddings = get_embeddings()
    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )