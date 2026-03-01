import sys
sys.path.append(".")
from src.indexing import get_qdrant_client, COLLECTION_NAME

client = get_qdrant_client()
results = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=3,
    with_payload=True,
    with_vectors=False
)

for point in results[0]:
    print(f"ID: {point.id}")
    print(f"Metadata: {point.payload.get('metadata', {})}")
    print(f"Content preview: {point.payload.get('page_content', '')[:300]}")
    print("-" * 60)