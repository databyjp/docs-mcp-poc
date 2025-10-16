# Chroma - Hello World Example
# Source: https://docs.trychroma.com/docs/overview/getting-started
# Estimated time: ~5 minutes
# Complexity: 1/5

import chromadb

# Create client
chroma_client = chromadb.Client()

# Create collection
collection = chroma_client.get_or_create_collection(name="my_collection")

# Add documents
collection.upsert(
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges"
    ],
    ids=["id1", "id2"]
)

# Query the collection
results = collection.query(
    query_texts=["This is a query document about florida"],
    n_results=2
)

print(results)