import os
import weaviate
from weaviate.classes.query import Filter
from fastmcp import FastMCP
from utils import PRODUCTS
from typing import Optional


# Initialize FastMCP server
mcp = FastMCP("vdb-docs")

# Available products as a formatted string for descriptions
PRODUCTS_LIST = ", ".join(PRODUCTS)


def get_weaviate_client():
    """Create and return a Weaviate client with API keys."""
    return weaviate.connect_to_local(
        headers={
            "X-Cohere-Api-Key": os.getenv("COHERE_API_KEY"),
            "X-Anthropic-Api-Key": os.getenv("ANTHROPIC_API_KEY"),
        },
    )


@mcp.tool()
def search_chunks(query: str, product: Optional[str] = None, limit: int = 10) -> list[dict]:
    """Search for relevant text chunks across vector database documentation.

    Returns smaller chunks of text that match the query, useful for finding
    specific code examples or explanations.

    Args:
        query: The search query or question
        product: Optional filter by specific product. Available: weaviate, turbopuffer,
                pinecone, milvus, qdrant, chroma, pgvector
        limit: Number of chunks to retrieve (default: 10)

    Returns:
        List of matching chunks with product, chunk text, chunk number, and source path
    """
    client = get_weaviate_client()

    try:
        chunks = client.collections.use("Chunks")

        filter_obj = Filter.by_property("product").equal(product) if product else None

        response = chunks.query.hybrid(
            query=query,
            limit=limit,
            filters=filter_obj
        )

        results = [o.properties for o in response.objects]
        return results

    finally:
        client.close()


@mcp.tool()
def search_documents(query: str, product: Optional[str] = None, limit: int = 10) -> list[dict]:
    """Search for complete documentation pages across vector databases.

    Returns the first 500 characters of documents that match the query.
    Use fetch_document to get the full content of a specific document.

    Args:
        query: The search query or question
        product: Optional filter by specific product. Available: weaviate, turbopuffer,
                pinecone, milvus, qdrant, chroma, pgvector
        limit: Number of documents to retrieve (default: 10)

    Returns:
        List of matching documents with product, body preview (500 chars), and full path
    """
    client = get_weaviate_client()

    try:
        documents = client.collections.use("Documents")

        filter_obj = Filter.by_property("product").equal(product) if product else None

        response = documents.query.hybrid(
            query=query,
            limit=limit,
            filters=filter_obj
        )

        results = [o.properties for o in response.objects]
        for result in results:
            result["body"] = result["body"][:500] + "..."

        return results

    finally:
        client.close()


@mcp.tool()
def fetch_document(path: str) -> dict:
    """Retrieve a specific documentation page by its exact URL path.

    Use this when you have the URL from a previous search result and want
    to read the full content.

    Args:
        path: The full URL path of the document
              (e.g., 'https://docs.weaviate.io/weaviate/manage-data/collections')

    Returns:
        Complete document with product, full body text, and path.
        Returns error dict if document not found.
    """
    client = get_weaviate_client()

    try:
        documents = client.collections.use("Documents")

        response = documents.query.fetch_objects(
            filters=Filter.by_property("path").equal(path),
            limit=1
        )

        if len(response.objects) == 0:
            return {"error": f"Document not found at path: {path}"}

        return response.objects[0].properties

    finally:
        client.close()


if __name__ == "__main__":
    mcp.run()
