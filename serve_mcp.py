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


# ============================================================================
# General Tools (All Vector Databases)
# ============================================================================


def search_chunks_generic(query: str, product: Optional[str] = None, limit: int = 10) -> list[dict]:
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
    return search_chunks_generic(query=query, product=product, limit=limit)


def search_documents_generic(query: str, product: Optional[str] = None, limit: int = 10) -> list[dict]:
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
def search_documents(query: str, product: Optional[str] = None, limit: int = 10) -> list[dict]:
    """Search for complete documentation pages across vector databases.

    Returns the first 500 characters of documents that match the query.
    Use the vdb-doc:// resource URI to get the full content of a specific document.

    Args:
        query: The search query or question
        product: Optional filter by specific product. Available: weaviate, turbopuffer,
                pinecone, milvus, qdrant, chroma, pgvector
        limit: Number of documents to retrieve (default: 10)

    Returns:
        List of matching documents with product, body preview (500 chars), and full path
    """
    return search_documents_generic(query=query, product=product, limit=limit)


# ============================================================================
# Weaviate-Specific Tools
# ============================================================================

@mcp.tool()
def search_weaviate_chunks(query: str, limit: int = 10) -> list[dict]:
    """Search for relevant text chunks specifically in Weaviate documentation.

    Convenience function that searches only Weaviate docs. Returns smaller chunks
    of text that match the query, useful for finding specific code examples or
    explanations about Weaviate.

    Args:
        query: The search query or question about Weaviate
        limit: Number of chunks to retrieve (default: 10)

    Returns:
        List of matching Weaviate chunks with chunk text, chunk number, and source path
    """
    return search_chunks_generic(query=query, product="weaviate", limit=limit)


@mcp.tool()
def search_weaviate_documents(query: str, limit: int = 10) -> list[dict]:
    """Search for complete documentation pages specifically in Weaviate documentation.

    Convenience function that searches only Weaviate docs. Returns the first 500
    characters of documents that match the query. Use the vdb-doc:// resource URI
    to get the full content of a specific document.

    Args:
        query: The search query or question about Weaviate
        limit: Number of documents to retrieve (default: 10)

    Returns:
        List of matching Weaviate documents with body preview (500 chars) and full path
    """
    return search_documents_generic(query=query, product="weaviate", limit=limit)


# ============================================================================
# Resources (Document Fetching by URI)
# ============================================================================


def fetch_document_resource_generic(url: str) -> str:
    client = get_weaviate_client()

    try:
        documents = client.collections.use("Documents")

        response = documents.query.fetch_objects(
            filters=Filter.by_property("path").equal(url),
            limit=1
        )

        if len(response.objects) == 0:
            return f"Error: Document not found at path: {url}"

        doc = response.objects[0].properties
        return f"# {doc['path']}\n\nProduct: {doc['product']}\n\n{doc['body']}"

    finally:
        client.close()


@mcp.resource("vdb-doc://{url}")
def fetch_document_resource(url: str) -> str:
    """Fetch a complete documentation page by its URL.

    This resource provides access to full documentation content using a URI scheme.
    The URL should be the complete documentation URL from a search result.

    URI Format: vdb-doc://{full_url}
    Example: vdb-doc://https://docs.weaviate.io/weaviate/manage-data/collections

    Args:
        url: The complete URL of the documentation page

    Returns:
        Full markdown content of the documentation page
    """
    return fetch_document_resource_generic(url=url)


@mcp.resource("weaviate-doc://{path}")
def fetch_weaviate_document_resource(path: str) -> str:
    """Fetch a complete Weaviate documentation page by its path.

    Convenience resource for accessing Weaviate documentation. You can provide
    either the full URL or just the path portion.

    URI Format: weaviate-doc://{path_or_full_url}
    Examples:
        - weaviate-doc://https://docs.weaviate.io/weaviate/manage-data/collections
        - weaviate-doc://weaviate/manage-data/collections

    Args:
        path: The URL path or full URL of the Weaviate documentation page

    Returns:
        Full markdown content of the Weaviate documentation page
    """
    # Handle both full URLs and partial paths
    if not path.startswith("http"):
        path = f"https://docs.weaviate.io/{path}"

    return fetch_document_resource_generic(url=path)


if __name__ == "__main__":
    mcp.run()
