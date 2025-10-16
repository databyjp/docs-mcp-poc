import os
import asyncio
import weaviate
from weaviate.classes.query import Filter
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server
from utils import PRODUCTS
import json


app = Server("vdb-docs")

# Available products as a formatted string for descriptions
PRODUCTS_LIST = ", ".join(PRODUCTS)


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_chunks",
            description=f"Search for relevant text chunks across vector database documentation. Available products: {PRODUCTS_LIST}. Returns smaller chunks of text that match the query, useful for finding specific code examples or explanations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or question"
                    },
                    "product": {
                        "type": "string",
                        "description": f"Optional: filter by specific product. Available options: {PRODUCTS_LIST}",
                        "enum": PRODUCTS
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of chunks to retrieve (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_documents",
            description=f"Search for complete documentation pages across vector databases. Available products: {PRODUCTS_LIST}. Returns the first 500 characters of the documents that match the query. Use the fetch_document tool to get the full content of a specific document.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or question"
                    },
                    "product": {
                        "type": "string",
                        "description": f"Optional: filter by specific product. Available options: {PRODUCTS_LIST}",
                        "enum": PRODUCTS
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of documents to retrieve (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="fetch_document",
            description="Retrieve a specific documentation page by its exact URL path. Use this when you have the URL from a previous search result and want to read the full content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The full URL path of the document (e.g., 'https://docs.weaviate.io/weaviate/manage-data/collections')"
                    }
                },
                "required": ["path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    client = weaviate.connect_to_local(
        headers={
            "X-Cohere-Api-Key": os.getenv("COHERE_API_KEY"),
            "X-Anthropic-Api-Key": os.getenv("ANTHROPIC_API_KEY"),
        },
    )

    try:
        if name == "search_chunks":
            return await search_chunks(client, arguments)
        elif name == "search_documents":
            return await search_documents(client, arguments)
        elif name == "fetch_document":
            return await fetch_document(client, arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    finally:
        client.close()


async def search_chunks(client, arguments: dict) -> list[TextContent]:
    query = arguments["query"]
    product = arguments.get("product")
    limit = arguments.get("limit", 10)

    chunks = client.collections.use("Chunks")

    filter_obj = Filter.by_property("product").equal(product) if product else None

    response = chunks.query.hybrid(
        query=query,
        limit=limit,
        filters=filter_obj
    )

    results = [o.properties for o in response.objects]

    return [TextContent(
        type="text",
        text=json.dumps(results, indent=2)
    )]


async def search_documents(client, arguments: dict) -> list[TextContent]:
    query = arguments["query"]
    product = arguments.get("product")
    limit = arguments.get("limit", 10)

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

    return [TextContent(
        type="text",
        text=json.dumps(results, indent=2)
    )]


async def fetch_document(client, arguments: dict) -> list[TextContent]:
    path = arguments["path"]

    documents = client.collections.use("Documents")

    response = documents.query.fetch_objects(
        filters=Filter.by_property("path").equal(path),
        limit=1
    )

    if len(response.objects) == 0:
        result = {"error": f"Document not found at path: {path}"}
    else:
        result = response.objects[0].properties

    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
