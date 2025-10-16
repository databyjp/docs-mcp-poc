# Pinecone - Hello World Example
# Source: https://docs.pinecone.io/guides/get-started/quickstart
# Estimated time: ~25 minutes
# Complexity: 2/5

from pinecone import Pinecone
import time

# Initialize client
pc = Pinecone(api_key="YOUR_API_KEY")

# Create index
index_name = "quickstart"
if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={"model": "llama-text-embed-v2", "field_map": {"text": "chunk_text"}}
    )

# Get index
index = pc.Index(index_name)

# Upsert data
records = [
    {"_id": "1", "chunk_text": "The Eiffel Tower was completed in 1889.", "category": "history"},
    {"_id": "2", "chunk_text": "Photosynthesis allows plants to convert sunlight into energy.", "category": "science"},
    {"_id": "3", "chunk_text": "Albert Einstein developed the theory of relativity.", "category": "science"}
]
index.upsert_records("example-namespace", records)
time.sleep(2)

# Search
results = index.search(
    namespace="example-namespace",
    query={"top_k": 2, "inputs": {"text": "Famous historical structures"}}
)

# Display results
for hit in results['result']['hits']:
    print(f"ID: {hit['_id']}, Score: {hit['_score']:.2f}, Text: {hit['fields']['chunk_text']}")

# Cleanup
pc.delete_index(index_name)