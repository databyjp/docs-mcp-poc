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
# Prompts (Usage Instructions)
# ============================================================================

@mcp.prompt()
def vdb_assistant_prompt() -> str:
    """System prompt for AI assistants using vector database documentation tools.

    Provides guidance on how to effectively use the documentation search tools
    and cite sources properly.
    """
    return f"""You are a helpful assistant for vector database documentation.
You have good general knowledge of how vector databases work.

However, you are keenly aware that your knowledge may be outdated.
You are also an expert researcher with access to the latest documentation
for multiple vector databases: {PRODUCTS_LIST}.

As a result, you should actively use available tools to search and retrieve
documentation in situations where the latest state of the product or feature
will affect your response.

**Citation Requirements:**
When you refer to any documentation, you MUST cite the source URL at the end
of your response using this format:

[<DOCUMENT_TITLE>](<SOURCE_URL>)

Examples:
- [Basic collection operations](https://docs.weaviate.io/weaviate/manage-collections/collection-operations)
- [Setting up RBAC in Weaviate](https://docs.weaviate.io/deploy/tutorials/rbac)

**Available Tools:**
- search_chunks: Find specific code examples or explanations
- search_documents: Search complete documentation pages
- search_weaviate_chunks: Weaviate-specific chunk search
- search_weaviate_documents: Weaviate-specific document search

**Available Resources:**
- vdb-doc://<url>: Fetch complete documentation by URL
- weaviate-doc://<path>: Fetch Weaviate documentation by path or URL
"""


@mcp.prompt()
def weaviate_assistant_prompt() -> str:
    """System prompt for AI assistants focused on Weaviate documentation.

    Specialized version for Weaviate-specific queries with optimized tool usage.
    """
    return """You are a Weaviate documentation expert and helpful assistant.

You have good general knowledge of Weaviate but are keenly aware that your
knowledge may be outdated. You have access to the latest Weaviate documentation
and should actively use it.

**Recommended Approach:**
1. Use search_weaviate_documents or search_weaviate_chunks for broad searches
2. Use weaviate-doc:// resources to fetch complete documentation pages
3. Always cite sources using: [<DOCUMENT_TITLE>](<SOURCE_URL>)

**Citation Format:**
[Basic collection operations](https://docs.weaviate.io/weaviate/manage-collections/collection-operations)

**Tool Usage:**
- For specific code examples: search_weaviate_chunks
- For conceptual information: search_weaviate_documents
- To read full pages: weaviate-doc://<path>

Always prioritize the latest documentation over your internal knowledge.
"""


@mcp.prompt()
def code_generation_prompt() -> str:
    """System prompt for generating code examples from vector database documentation.

    Optimized for creating working code snippets with proper citations.
    """
    return f"""You are an expert at generating working code examples for vector databases.

**Your Process:**
1. Search documentation for relevant code examples and API references
2. Synthesize working, tested-looking code from the documentation
3. Include comments explaining key concepts
4. Cite all documentation sources at the end

**Available Databases:** {PRODUCTS_LIST}

**Code Quality Requirements:**
- Code should be production-ready and follow best practices
- Include error handling where appropriate
- Add type hints for Python code
- Include setup/installation requirements if needed
- Comment complex sections

**Citation Format:**
Always cite documentation sources:
[<DOCUMENT_TITLE>](<SOURCE_URL>)

**Example Flow:**
1. Use search_chunks to find API examples
2. Use vdb-doc:// resources to read full documentation pages
3. Generate code based on official examples
4. Cite all sources used
"""


@mcp.prompt()
def comparative_analysis_prompt() -> str:
    """System prompt for comparing vector database features and approaches.

    Guides assistants to perform fair, documentation-based comparisons.
    """
    return f"""You are an expert at comparing vector database technologies.

**Your Goal:**
Provide fair, accurate comparisons based on the latest documentation.

**Available Databases:** {PRODUCTS_LIST}

**Comparison Process:**
1. Search documentation for each database being compared
2. Focus on official capabilities, not assumptions
3. Highlight strengths and trade-offs for each
4. Provide code examples when relevant
5. Cite all sources

**Comparison Dimensions:**
- API design and ease of use
- Feature availability
- Performance characteristics (when documented)
- Deployment options
- Integration ecosystems

**Citation Requirements:**
List sources for each database at the end:

**Weaviate:**
[Feature A](url1)
[Feature B](url2)

**Qdrant:**
[Feature A](url3)
[Feature B](url4)

Be objective and base all claims on documentation.
"""


# ============================================================================
# General Tools (All Vector Databases)
# ============================================================================


def search_chunks_generic(query: str, limit: int, product: Optional[str] = None) -> list[dict]:
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
def search_chunks(query: str, product: Optional[str] = None, limit: int = 5) -> list[dict]:
    """Search for relevant text chunks across vector database documentation.

    Returns smaller chunks of text that match the query, useful for finding
    specific code examples or explanations.

    Args:
        query: The search query or question
        product: Optional filter by specific product. Available: weaviate, turbopuffer,
                pinecone, milvus, qdrant, chroma, pgvector
        limit: Number of chunks to retrieve (default: 5)

    Returns:
        List of matching chunks with product, chunk text, chunk number, and source path
    """
    return search_chunks_generic(query=query, limit=limit, product=product)


def search_documents_generic(query: str, limit: int, product: Optional[str] = None) -> list[dict]:
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
def search_documents(query: str, limit: int = 5, product: Optional[str] = None) -> list[dict]:
    """Search for complete documentation pages across vector databases.

    Returns the first 500 characters of documents that match the query.
    Use the vdb-doc:// resource URI to get the full content of a specific document.

    Args:
        query: The search query or question
        limit: Number of documents to retrieve (default: 5)
        product: Optional filter by specific product. Available: weaviate, turbopuffer,
                pinecone, milvus, qdrant, chroma, pgvector

    Returns:
        List of matching documents with product, body preview (500 chars), and full path
    """
    return search_documents_generic(query=query, limit=limit, product=product)


# ============================================================================
# Weaviate-Specific Tools
# ============================================================================

@mcp.tool()
def search_weaviate_chunks(query: str, limit: int = 5) -> list[dict]:
    """Search for relevant text chunks specifically in Weaviate documentation.

    Convenience function that searches only Weaviate docs. Returns smaller chunks
    of text that match the query, useful for finding specific code examples or
    explanations about Weaviate.

    Args:
        query: The search query or question about Weaviate
        limit: Number of chunks to retrieve (default: 5)

    Returns:
        List of matching Weaviate chunks with chunk text, chunk number, and source path
    """
    return search_chunks_generic(query=query, limit=limit, product="weaviate")


@mcp.tool()
def search_weaviate_documents(query: str, limit: int = 5) -> list[dict]:
    """Search for complete documentation pages specifically in Weaviate documentation.

    Convenience function that searches only Weaviate docs. Returns the first 500
    characters of documents that match the query. Use the vdb-doc:// resource URI
    to get the full content of a specific document.

    Args:
        query: The search query or question about Weaviate
        limit: Number of documents to retrieve (default: 5)

    Returns:
        List of matching Weaviate documents with body preview (500 chars) and full path
    """
    return search_documents_generic(query=query, limit=limit, product="weaviate")


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
