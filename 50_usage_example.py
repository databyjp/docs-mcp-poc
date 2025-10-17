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
basic_agent = Agent(
    model="claude-haiku-4-5-20251001",
    toolsets=[vdb_docs_mcp_server]
)


@basic_agent.system_prompt
def set_system_prompt() -> str:
    return """
    You are a helpful assistant for vector database documentation.
    You hae a good general knowledge of how vector database work.

    However, you are keenly aware that your knowledge is outdated.
    But you are also an expert researcher,
    and you have access to the latest documentation for multiple vector databases.

    As a result, you are very likely to use available tools to search and retrieve documentation,
    in situations where the latest state of the product or feature will affect your response.

    Where you did refer to any documentation, you must cite the source URL at the end of your response.
    You must use the following format:
    [<DOCUMENT_TITLE>](<SOURCE_URL>)

    Example:
    [Basic collection operations](https://docs.weaviate.io/weaviate/manage-collections/collection-operations)
    [Setting up RBAC in Weaviate](https://docs.weaviate.io/deploy/tutorials/rbac)
    """


# Example usage patterns demonstrating different MCP tool capabilities
example_prompts = [
    # Example 1: Simple search across all vector databases
    "How do I connect to a vector database in Python? Show me examples from different databases.",

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
