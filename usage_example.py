# Reference: https://ai.pydantic.dev/agents/
from pydantic_ai import Agent
from pathlib import Path
from pydantic_ai.mcp import MCPServerStdio
import os

# Set up the MCP server connection
vdb_docs_mcp_directory = Path(__file__).parent
vdb_docs_mcp_server = MCPServerStdio(
    command="uv",
    args=["--directory", str(vdb_docs_mcp_directory), "run", "python", "serve_mcp.py"],
    env=os.environ.copy(),
)

# Create an agent with access to the vector database documentation MCP
# Note: The system prompt is now provided by the MCP server itself via prompts
basic_agent = Agent(
    model="claude-haiku-4-5-20251001",
    toolsets=[vdb_docs_mcp_server]
)


@basic_agent.system_prompt
def set_system_prompt() -> str:
    """
    Use the MCP-provided prompt for consistent behavior.
    The MCP server exposes several prompts:
    - vdb_assistant_prompt: General vector database assistant (recommended)
    - weaviate_assistant_prompt: Weaviate-specific assistant
    - code_generation_prompt: For generating code examples
    - comparative_analysis_prompt: For comparing databases

    Here we fetch and use the general assistant prompt.
    """
    # In practice, MCP clients can retrieve prompts from the server
    # For now, we'll use a simplified version that references the MCP guidance
    return """
    You are a helpful assistant for vector database documentation.
    You have access to the latest documentation for multiple vector databases
    via MCP tools.

    Always use available tools to search and retrieve documentation when the
    latest state of products or features will affect your response.

    Cite all documentation sources using:
    [<DOCUMENT_TITLE>](<SOURCE_URL>)

    Example:
    [Basic collection operations](https://docs.weaviate.io/weaviate/manage-collections/collection-operations)
    """


# Example usage patterns demonstrating different MCP tool capabilities
example_prompts = [
    # Example 1: Simple search across all vector databases
    "How do I connect to a vector database in Python? Show me examples from two different databases.",

    # Example 2: Product-specific search
    "I'm using Weaviate Cloud. How do I create an read-only RBAC role? Show me an end to end code example in Python.",

    # Example 3: Comparative search
    "Compare how Weaviate and Qdrant handle filtering during vector search.",
]

if __name__ == "__main__":
    prompt = example_prompts[1]
    print(f">> RUNNING PROMPT: {prompt}\n")
    model_response = basic_agent.run_sync(user_prompt=prompt)
    print(f"Agent response:")
    print(model_response.output)
    print("\n" + "="*80 + "\n")

    # for prompt in example_prompts:
    #     print(f">> RUNNING PROMPT: {prompt}\n")
    #     model_response = basic_agent.run_sync(user_prompt=prompt)
    #     print(f"Agent response:")
    #     print(model_response.output)
    #     print("\n" + "="*80 + "\n")
