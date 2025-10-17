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
    You have access to documentation for multiple vector databases including:
    Weaviate, Pinecone, Milvus, Qdrant, Chroma, Turbopuffer, and pgvector.

    Use the available tools to search and retrieve documentation.

    Always use the tools to find current documentation rather than relying on
    internal knowledge, as syntax and features may have changed.
    """


# Example usage patterns demonstrating different MCP tool capabilities
example_prompts = [
    # Example 1: Simple search across all vector databases
    "How do I connect to a vector database in Python? Show me examples from different databases.",

    # Example 2: Product-specific search
    "I'm using Weaviate Cloud. How do I create an read-only RBAC role? Show me an end to end code example."

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
