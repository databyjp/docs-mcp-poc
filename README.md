# Vector Database Documentation Crawler & MCP Server

A comprehensive tool for crawling, indexing, and searching vector database documentation using semantic search. Provides an MCP (Model Context Protocol) server for integration with Claude Code and other AI tools.

## Features

- **Web Crawling**: Automated documentation crawling for multiple vector databases (Weaviate, Pinecone, Qdrant, Milvus, Chroma, Turbopuffer, pgvector)
- **Semantic Search**: Hybrid search combining semantic embeddings and keyword matching
- **MCP Server**: FastMCP-based server with tools and resources for AI agents
- **AI Analysis**: Automated "time-to-hello-world" analysis across different databases
- **Weaviate-Optimized**: Special tools and resources for Weaviate documentation

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd vdb-docs

# Install dependencies with uv
uv sync

# Set up environment variables
export COHERE_API_KEY="your-cohere-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Start Weaviate
docker-compose up -d
```

### 2. Build the Documentation Index

```bash
# Initialize database schema
uv run python 00_reset_db.py

# Crawl documentation sites
uv run python 10_get_docs.py

# Process and clean crawled content
uv run python 15_supplementary_crawl.py

# Index into Weaviate
uv run python 20_index_docs.py
```

### 3. Use the MCP Server

```bash
# Start the MCP server
uv run python serve_mcp.py
```

## Configuring for Claude Code

To use this MCP server with Claude Code, you need to add it to your MCP settings file.

### Configuration File Location

The MCP settings file location depends on your operating system:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Configuration Steps

1. **Locate or create the configuration file** at the path above.

2. **Add the MCP server configuration** (e.g. `.mcp.json`):

```json
{
  "mcpServers": {
    "vdb-docs": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/vdb-docs",
        "run",
        "python",
        "serve_mcp.py"
      ],
      "env": {
        // Uncomment these if your environment variables are not set
        // "COHERE_API_KEY": "your-cohere-api-key",
        // "ANTHROPIC_API_KEY": "your-anthropic-api-key"
      }
    }
  }
}
```

3. **Update the configuration**:
   - Replace `/absolute/path/to/vdb-docs` with the actual path to this repository
   - Add your API keys to the `env` section

4. **Enable the MCP server**:
   - Add the server name to the `enabledMcpjsonServers` section, e.g. in `.claude/settings.local.json`:

```json
  "enabledMcpjsonServers": [
    "vdb-docs"
  ],
```

5. **Restart Claude Code** for the changes to take effect.

### Verifying the Configuration

Once configured, Claude Code will have access to these tools:

**General Tools:**
- `search_chunks` - Search across all vector database documentation
- `search_documents` - Search full documentation pages

**Weaviate-Specific Tools:**
- `search_weaviate_chunks` - Search Weaviate documentation chunks
- `search_weaviate_documents` - Search Weaviate documentation pages

**Resources:**
- `vdb-doc://<url>` - Fetch any vector database documentation
- `weaviate-doc://<path>` - Fetch Weaviate documentation

**Prompts:**
- `vdb_assistant_prompt` - General assistant instructions with citation guidelines
- `weaviate_assistant_prompt` - Weaviate-focused assistant instructions
- `code_generation_prompt` - Code generation best practices
- `comparative_analysis_prompt` - Fair comparison guidelines

### Example Usage with Claude Code

Once configured, you can ask Claude Code questions like:

```
"Using the vdb-docs MCP, how do I create a read-only RBAC role in Weaviate Cloud?"

"Search the Weaviate documentation for examples of filtering during vector search"

"Compare how Weaviate and Qdrant handle batch insertions"
```

#### Using MCP Prompts

Claude Code can also use the built-in prompts from the MCP server. These prompts provide consistent instructions for different use cases:

**General Documentation Assistant:**
```
Use the vdb_assistant_prompt to help me understand how vector databases handle similarity search.
```

**Weaviate-Specific Queries:**
```
Using weaviate_assistant_prompt, explain how to set up multi-tenancy in Weaviate.
```

**Code Generation:**
```
Using code_generation_prompt, create a Python script that connects to Pinecone and performs a basic search.
```

**Comparative Analysis:**
```
Using comparative_analysis_prompt, compare filtering capabilities across Weaviate, Qdrant, and Pinecone.
```

## MCP Server Architecture

### Tools

**General (All Vector Databases):**
- `search_chunks(query, product?, limit?)` - Semantic search on documentation chunks
- `search_documents(query, product?, limit?)` - Search full documentation pages

**Weaviate-Specific:**
- `search_weaviate_chunks(query, limit?)` - Pre-filtered Weaviate chunk search
- `search_weaviate_documents(query, limit?)` - Pre-filtered Weaviate document search

### Resources

Resources provide URI-based access to documentation:

- `vdb-doc://{url}` - Fetch complete documentation by full URL
  - Example: `vdb-doc://https://docs.weaviate.io/weaviate/manage-data/collections`

- `weaviate-doc://{path}` - Fetch Weaviate docs by path or URL
  - Short path: `weaviate-doc://weaviate/manage-data/collections`
  - Full URL: `weaviate-doc://https://docs.weaviate.io/weaviate/manage-data/collections`

## Project Structure

```
vdb-docs/
- 00_reset_db.py              # Initialize Weaviate collections
- 10_get_docs.py              # Crawl documentation sites
- 15_supplementary_crawl.py   # Quality control and re-scraping
- 20_index_docs.py            # Index documents into Weaviate
- 30_inspect_db.py            # Database inspection utilities
- serve_mcp.py                # MCP server (main entry point)
- 50_agent_example.py         # Example agent using MCP server
- 60_time_to_hello_world.py  # Documentation analysis tool
- utils.py                    # Shared configuration
- docker-compose.yml          # Weaviate setup
- pyproject.toml              # Python dependencies
- outputs/                    # Analysis results and code snippets
```

## Development

### Adding a New Vector Database

1. Add the product name to `PRODUCTS` in `utils.py`
2. Add a crawl job configuration in `10_get_docs.py`:
   ```python
   {
       "name": "product_docs",
       "allowed_domains": ["docs.example.com"],
       "start_url": "https://docs.example.com/start",
       "url_pattern": "*/docs/*"  # Optional
   }
   ```
3. Run the pipeline: `00` � `10` � `15` � `20`

### Testing the MCP Server Locally

```bash
# Option 1: Run the server directly
uv run python serve_mcp.py

# Option 2: Use the example agent
uv run python 50_agent_example.py

# Option 3: Inspect the database
uv run python 30_inspect_db.py
```

### Running Analysis

```bash
# Analyze "time to hello world" across databases
uv run python 60_time_to_hello_world.py

# Results are saved to:
# - outputs/time_to_hello_world_analysis.json
# - outputs/time_to_hello_world_report.md
# - outputs/code_snippets/
```

## Technologies

- **FastMCP** - Simple decorator-based MCP server framework
- **Weaviate** - Vector database for document storage and search
- **Cohere** - Embeddings via text2vec-cohere
- **Crawl4AI** - Intelligent web crawling with BFS strategy
- **Chonkie** - Semantic text chunking
- **Pydantic AI** - AI agent framework
- **uv** - Fast Python package manager

## Environment Variables

Required environment variables:

- `COHERE_API_KEY` - For Cohere embeddings (get one at [cohere.com](https://cohere.com))
- `ANTHROPIC_API_KEY` - For Claude models (get one at [anthropic.com](https://anthropic.com))

## Troubleshooting

### MCP Server Not Appearing in Claude Code

1. **Check the config file path** - Make sure you're editing the correct file for your OS
2. **Verify absolute paths** - Use full absolute paths, not relative paths or `~`
3. **Check API keys** - Ensure your environment variables are set correctly
4. **Restart Claude Code** - Changes only take effect after restart
5. **Check logs** - Look for MCP-related errors in Claude Code's developer console

### Weaviate Connection Issues

```bash
# Check if Weaviate is running
docker ps | grep weaviate

# Restart Weaviate
docker-compose down
docker-compose up -d

# Check Weaviate logs
docker-compose logs weaviate
```

### Crawling Issues

If crawls fail or return empty content:
- Run `15_supplementary_crawl.py` to detect and retry problematic pages
- Check `crawled_docs_processed/` for cleaned content
- Some sites may have bot protection - the supplementary crawl helps with this

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
