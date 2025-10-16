import os
import weaviate
from weaviate.classes.generate import GenerativeConfig
from weaviate.classes.query import Filter
from typing import Optional
from utils import PRODUCTS


client = weaviate.connect_to_local(
    headers={
        "X-Cohere-Api-Key": os.getenv("COHERE_API_KEY"),
        "X-Anthropic-Api-Key": os.getenv("ANTHROPIC_API_KEY"),
    },
)

chunks = client.collections.use("Chunks")
documents = client.collections.use("Documents")


rag_config = GenerativeConfig.anthropic(
    # model="claude-haiku-4-5-20251001",
    model="claude-3-5-haiku-latest",
)


# for product in PRODUCTS[:3]:
#     filter = Filter.by_property("product").equal(product)

#     response = chunks.generate.hybrid(
#         query="Add documents to the database Python",
#         limit=5,
#         grouped_task="How do I add documents a this database using Python? Cite the source URLs please.",
#         filters=filter,
#         generative_provider=rag_config
#     )

#     print(response.generative.text)

#     for o in response.objects:
#         print(o.properties["path"])


def search_chunks(query: str, product: Optional[str] = None, limit: int = 5) -> list[dict]:
    if product:
        filter = Filter.by_property("product").equal(product)
    else:
        filter = None

    response = chunks.query.hybrid(
        query=query,
        limit=limit,
        filters=filter
    )
    return [o.properties for o in response.objects]


def search_documents(query: str, product: Optional[str] = None, limit: int = 5) -> list[dict]:
    if product:
        filter = Filter.by_property("product").equal(product)
    else:
        filter = None

    response = documents.query.hybrid(
        query=query,
        limit=limit,
        filters=filter
    )
    return [o.properties for o in response.objects]


def fetch_document(path: str) -> dict:
    response = documents.query.fetch_objects(
        filters=Filter.by_property("path").equal(path),
        limit=1
    )
    if len(response.objects) == 0:
        return None
    return response.objects[0].properties


for tmp_path in [
    "https://docs.pinecone.io/guides/get-started/overview",
    "https://docs.weaviate.io/weaviate/manage-data/collections"
]:
    doc = fetch_document(tmp_path)
    print(f"\nFetching document {tmp_path}")
    print(doc["path"])
    print(doc["body"][:100] + "...")


for search_query in ["Add documents to the database Python"]:
    print(f"\nSearching for {search_query}")
    results = search_chunks(search_query, product="weaviate", limit=5)
    for result in results:
        print(f"Chunk {result['chunk_no']} from {result['path']}")
        print(result["chunk"][:20] + "...")


for doc_search_query in ["quickstart guide"]:
    for product in PRODUCTS:
        results = search_documents(doc_search_query, product=product, limit=5)
        for result in results:
            print(f"Document {result['path']} from {product}")
            print(result["body"][:500] + "...")
            print()

client.close()
