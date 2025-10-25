import argparse
from weaviate.classes.query import Filter
from fastmcp import FastMCP
from utils import PRODUCTS, connect_to_weaviate


# Parse command-line arguments
parser = argparse.ArgumentParser(description="MCP server for vector database documentation")
parser.add_argument(
    "--product",
    type=str,
    required=True,
    choices=PRODUCTS,
    help=f"Product documentation to serve. Available: {', '.join(PRODUCTS)}"
)
args = parser.parse_args()

# Store product globally
PRODUCT = args.product

# Initialize FastMCP server with product-specific name
mcp = FastMCP(f"{PRODUCT}-docs")


# ============================================================================
# Documentation Search Tools
# ============================================================================


@mcp.tool()
def search_chunks(query: str, limit: int = 5) -> list[dict]:
    """Search for relevant text chunks in the documentation.

    Returns smaller chunks of text that match the query, useful for finding
    specific code examples or explanations.

    Args:
        query: The search query or question
        limit: Number of chunks to retrieve (default: 5)

    Returns:
        List of matching chunks with chunk text, chunk number, and source path
    """
    client = connect_to_weaviate()

    try:
        chunks = client.collections.use("Chunks")
        filter_obj = Filter.by_property("product").equal(PRODUCT)

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
def search_documents(query: str, limit: int = 5) -> list[dict]:
    """Search for complete documentation pages.

    Returns the first 500 characters of documents that match the query.
    Use the doc:// resource URI to get the full content of a specific document.

    Args:
        query: The search query or question
        limit: Number of documents to retrieve (default: 5)

    Returns:
        List of matching documents with body preview (500 chars) and full path
    """
    client = connect_to_weaviate()

    try:
        documents = client.collections.use("Documents")
        filter_obj = Filter.by_property("product").equal(PRODUCT)

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


# ============================================================================
# Resources (Document Fetching by URI)
# ============================================================================


def fetch_document_by_url(url: str) -> str:
    """Helper function to fetch a document by its full URL."""
    client = connect_to_weaviate()

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


@mcp.resource("doc://{url}")
def fetch_document_resource(url: str) -> str:
    """Fetch a complete documentation page by its URL.

    This resource provides access to full documentation content using a URI scheme.
    The URL should be the complete documentation URL from a search result.

    URI Format: doc://{full_url}
    Example: doc://https://docs.weaviate.io/weaviate/manage-data/collections

    Args:
        url: The complete URL of the documentation page

    Returns:
        Full markdown content of the documentation page
    """
    return fetch_document_by_url(url=url)


if __name__ == "__main__":
    mcp.run()
