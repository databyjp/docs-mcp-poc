"""
Usage Example: Product-Specific Documentation Assistant

This script demonstrates how to use the MCP server for local testing and demos.

Usage:
    1. Configure the PRODUCT variable below (weaviate)
    2. Run: uv run python usage_example.py

The script will:
    - Launch a product-specific MCP server via stdio
    - Create a Pydantic AI agent with access to the documentation tools
    - Run example prompts against the documentation

Reference: https://ai.pydantic.dev/agents/
"""
from pydantic_ai import Agent
from pathlib import Path
from pydantic_ai.mcp import MCPServerStdio
import os

# Configuration - change this to test different products
PRODUCT = "weaviate"  # Options: weaviate

# Set up the MCP server connection
vdb_docs_mcp_directory = Path(__file__).parent
vdb_docs_mcp_server = MCPServerStdio(
    command="uv",
    args=[
        "--directory",
        str(vdb_docs_mcp_directory),
        "run",
        "python",
        "serve_mcp.py",
        "--product",
        PRODUCT
    ],
    env=os.environ.copy(),
)

# Create an agent with access to the product-specific documentation MCP
# The MCP server provides product-specific tools, resources, and prompts
basic_agent = Agent(
    model="claude-haiku-4-5-20251001",
    toolsets=[vdb_docs_mcp_server]
)


@basic_agent.system_prompt
def set_system_prompt() -> str:
    """
    The MCP server provides an 'assistant_instructions' prompt with product-specific
    guidance including:
    - Citation guidelines
    - Search strategy recommendations
    - Code example handling
    - Accuracy guidelines

    Here we use a simplified system prompt that complements the MCP prompt.
    """
    return f"""
    You are a helpful assistant for {PRODUCT} documentation.
    You have access to the latest {PRODUCT} documentation via MCP tools.

    Always use available tools to search and retrieve documentation when the
    latest state of features will affect your response.

    Cite all documentation sources using:
    [<DOCUMENT_TITLE>](<SOURCE_URL>)

    Example:
    [Basic collection operations](https://docs.weaviate.io/weaviate/manage-collections/collection-operations)
    """


# Example usage patterns demonstrating different MCP tool capabilities
# Note: These examples are for the configured PRODUCT (currently: {PRODUCT})

weaviate_prompts = [
    # Example 1: Basic connection
    "How do I connect to Weaviate Cloud in Python? Show me a complete example.",

    # Example 2: Specific feature
    "I'm using Weaviate Cloud. How do I create a read-only RBAC role? Show me an end to end code example in Python.",

    # Example 3: Advanced feature
    "How do I perform hybrid search with filtering in Weaviate? Include a code example.",
]

# Select prompts
example_prompts = weaviate_prompts

if __name__ == "__main__":
    print(f"=== {PRODUCT.upper()} Documentation Assistant ===\n")

    # Run a single example (change index to try different prompts)
    prompt = example_prompts[1]
    print(f">> RUNNING PROMPT: {prompt}\n")
    model_response = basic_agent.run_sync(user_prompt=prompt)
    print(f"\nAgent response:")
    print(model_response.output)
    print("\n" + "="*80 + "\n")

    # Uncomment to run all example prompts
    # for i, prompt in enumerate(example_prompts, 1):
    #     print(f">> EXAMPLE {i}: {prompt}\n")
    #     model_response = basic_agent.run_sync(user_prompt=prompt)
    #     print(f"Agent response:")
    #     print(model_response.output)
    #     print("\n" + "="*80 + "\n")
