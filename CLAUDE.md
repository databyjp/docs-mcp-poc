# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a vector database documentation crawler and analyzer that:
1. Crawls documentation from multiple vector database providers (Weaviate, Pinecone, Qdrant, Milvus, Chroma, Turbopuffer, pgvector)
2. Processes and indexes the documentation into Weaviate using semantic chunking
3. Provides an MCP (Model Context Protocol) server for searching documentation
4. Analyzes "time to hello world" metrics across different vector databases

## Environment Setup

### Required Environment Variables
- `COHERE_API_KEY` - Used for Cohere embeddings (text2vec-cohere)
- `ANTHROPIC_API_KEY` - Used for Claude models in analysis agents

### Dependencies
Managed with `uv` (Python package manager):
- `crawl4ai` - Web crawling with deep crawl strategies
- `weaviate-client` - Vector database client
- `chonkie` - Text chunking library
- `mcp` - Model Context Protocol server
- `pydantic-ai` - AI agent framework

### Starting Services
```bash
# Start local Weaviate instance
docker-compose up -d

# Verify Weaviate is running on http://localhost:8080
```

## Core Architecture

### Data Pipeline (Numbered Scripts)

The project follows a sequential pipeline workflow:

1. **00_reset_db.py** - Initialize/reset Weaviate collections
   - Creates `Chunks` collection (for semantic search on document chunks)
   - Creates `Documents` collection (for full document retrieval)
   - Both use Cohere embeddings via `text2vec-cohere`

2. **10_get_docs.py** - Crawl documentation sites
   - Uses `crawl4ai` with BFS deep crawl strategy
   - Configurable filters: domain and URL pattern
   - Outputs raw markdown to `crawled_docs/` directory
   - Each product gets its own JSON file: `{product}_crawl4ai.json`

3. **15_supplementary_crawl.py** - Quality control and re-crawling
   - Detects problematic content (security challenges, errors, empty pages)
   - Retries failed scrapes with fresh requests
   - Outputs cleaned data to `crawled_docs_processed/` directory

4. **20_index_docs.py** - Index documents into Weaviate
   - Chunks documents using `TokenChunker` (512 tokens, 128 overlap)
   - Batch inserts chunks and full documents
   - Uses deterministic UUIDs for idempotency

5. **30_inspect_db.py** - Interactive inspection utilities
   - Helper functions: `search_chunks()`, `search_documents()`, `fetch_document()`
   - Examples of hybrid search and document retrieval
   - Useful for testing queries

### MCP Server (serve_mcp.py)

Built with **FastMCP**, using clean decorator-based tool and resource definitions.

**General Tools (All Vector Databases):**
- `search_chunks(query, product?, limit?)` - Semantic search on document chunks across all VDBs
- `search_documents(query, product?, limit?)` - Search full documents (returns first 500 chars + URL)

**Weaviate-Specific Tools:**
- `search_weaviate_chunks(query, limit?)` - Convenience function for Weaviate chunk search
- `search_weaviate_documents(query, limit?)` - Convenience function for Weaviate document search

**Resources (URI-based document fetching):**
- `vdb-doc://{url}` - Fetch complete documentation by full URL
  - Example: `vdb-doc://https://docs.weaviate.io/weaviate/manage-data/collections`
- `weaviate-doc://{path}` - Fetch Weaviate docs by path or full URL
  - Example: `weaviate-doc://weaviate/manage-data/collections`
  - Example: `weaviate-doc://https://docs.weaviate.io/weaviate/manage-data/collections`

**Prompts (System Instructions):**
- `vdb_assistant_prompt` - General vector database assistant with citation guidelines
- `weaviate_assistant_prompt` - Weaviate-specific assistant with optimized tool usage
- `code_generation_prompt` - Guidance for generating code examples from documentation
- `comparative_analysis_prompt` - Instructions for comparing vector databases fairly

**Running the MCP server:**
```bash
uv run python serve_mcp.py
```

The server uses stdio transport and can be integrated into Claude Desktop or other MCP clients.

**FastMCP Benefits:**
- Simple `@mcp.tool()` and `@mcp.resource()` decorators
- Automatic type inference from function signatures and docstrings
- URI-based resources for semantic document access
- Cleaner, more maintainable code

### Agent Examples

**50_agent_example.py** - Basic agent using the MCP server
- Demonstrates `pydantic-ai` agent with MCP toolset
- Shows different query patterns (simple, product-specific, comparative)

**60_time_to_hello_world.py** - Documentation analysis agent
- Analyzes onboarding complexity across vector databases
- Measures steps, pages, time, and complexity to get a basic example working
- Generates JSON analysis, code snippets, and markdown report
- Outputs to `outputs/` directory

## Key Concepts

### Collection Schema

**Chunks Collection:**
- `product` (TEXT, FIELD tokenization) - Vector DB name
- `chunk` (TEXT) - Semantic chunk of documentation
- `chunk_no` (INT) - Sequential chunk number
- `path` (TEXT, FIELD tokenization) - Source URL

**Documents Collection:**
- `product` (TEXT, FIELD tokenization) - Vector DB name
- `body` (TEXT) - Full document markdown
- `path` (TEXT, FIELD tokenization) - Source URL

### Vector Search Strategy

Uses **hybrid search** (combines semantic + keyword):
- Semantic: Cohere embeddings on `["chunk", "path"]` for Chunks, `["path"]` for Documents
- Keyword: BM25 on text fields
- Filtering: By product name using Weaviate filters

### Shared Configuration (utils.py)

- `CRAWLED_DOCS_DIR` = "./crawled_docs"
- `PROCESSED_DOCS_DIR` = "./crawled_docs_processed"
- `PRODUCTS` = List of supported vector databases

## Development Workflow

### Adding a New Vector Database

1. Add product name to `PRODUCTS` list in `utils.py`
2. Add crawl job config to `10_get_docs.py`:
   ```python
   {
       "name": "product_docs",
       "allowed_domains": ["docs.example.com"],
       "start_url": "https://docs.example.com/start",
       "url_pattern": "*/docs/*"  # Optional
   }
   ```
3. Run the full pipeline: `00` → `10` → `15` → `20`

### Running Analysis

```bash
# Run time-to-hello-world analysis
uv run python 60_time_to_hello_world.py

# Check outputs
ls outputs/
ls outputs/code_snippets/
```

### Testing MCP Tools

```bash
# Start MCP server in one terminal
uv run python serve_mcp.py

# Or use the agent example
uv run python 50_agent_example.py
```

## Common Commands

```bash
# Reset and rebuild database from scratch
uv run python 00_reset_db.py
uv run python 10_get_docs.py
uv run python 15_supplementary_crawl.py
uv run python 20_index_docs.py

# Run analysis
uv run python 60_time_to_hello_world.py

# Start MCP server for external clients
uv run python serve_mcp.py

# Run basic agent examples
uv run python 50_agent_example.py

# Inspect database contents
uv run python 30_inspect_db.py
```

## Important Notes

- The project uses `uv` for dependency management (see `pyproject.toml` and `uv.lock`)
- Weaviate must be running locally before executing index/search operations
- Crawling is cached by `crawl4ai` - use `CacheMode.BYPASS` to force refresh
- UUID generation uses `generate_uuid5()` for deterministic IDs, enabling re-indexing without duplicates
- The MCP server connects via stdio, making it suitable for Claude Desktop integration
- Analysis agents use `claude-haiku-4-5-20251001` for cost-effective documentation analysis
