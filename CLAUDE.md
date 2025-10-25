# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a vector database documentation crawler and analyzer for:
1. Crawls documentation sites
2. Processes (chunks) and indexes the documentation into Weaviate
3. Provides an MCP (Model Context Protocol) server for searching documentation

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

### Requirements
A Weaviate instance must be running on the cloud; with its credentials set in `.env` or environment variables.

WCD_URL=<your-url>.weaviate.cloud
WCD_KEY=<your-weaviate-api-key>

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

### MCP Server (serve_mcp.py)

Built with **FastMCP**, using clean decorator-based tool and resource definitions. The server is **product-specific** - it serves documentation for one product at a time, specified via CLI argument.

**Architecture:**
- Single-product design: Each server instance serves one product's documentation
- Product specified at runtime via `--product` flag
- Server name becomes `{product}-docs` (e.g., "weaviate-docs", "togetherai-docs")
- To serve multiple products, run multiple server instances

**Tools:**
- `search_chunks(query, limit?)` - Semantic search on document chunks for the specified product
- `search_documents(query, limit?)` - Search full documents (returns first 500 chars + URL)

**Resources (URI-based document fetching):**
- `doc://{url}` - Fetch complete documentation by full URL
  - Example: `doc://https://docs.weaviate.io/weaviate/manage-data/collections`

**Prompts:**
- `assistant_instructions` - Product-specific documentation assistant with citation guidelines, search strategy, and code example handling

**Running the MCP server:**
```bash
# Serve Weaviate documentation
uv run python serve_mcp.py --product weaviate

# Serve TogetherAI documentation
uv run python serve_mcp.py --product togetherai

# Available products determined by CRAWL_JOBS in utils.py
```

The server uses stdio transport and can be integrated into Claude Desktop or other MCP clients. Multiple servers can run simultaneously for different products.

**FastMCP Benefits:**
- Simple `@mcp.tool()`, `@mcp.resource()`, and `@mcp.prompt()` decorators
- Automatic type inference from function signatures and docstrings
- URI-based resources for semantic document access
- Skills-like prompts that load on-demand for token efficiency
- Cleaner, more maintainable code

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
- `CRAWL_JOBS` = List of crawl configurations (name, domains, start URL, patterns)
- `PRODUCTS` = Derived from `CRAWL_JOBS`, used for MCP server product selection

## Development Workflow

### Adding a New Product Documentation

1. Add crawl job config to `CRAWL_JOBS` in `utils.py`:
   ```python
   {
       "name": "product_name",
       "allowed_domains": ["docs.example.com"],
       "start_url": "https://docs.example.com/start",
       "url_pattern": "*/docs/*"  # Optional
   }
   ```
2. Run the full pipeline: `00` → `10` → `15` → `20`
3. Start MCP server: `uv run python serve_mcp.py --product product_name`

## Common Commands

```bash
# Reset and rebuild database from scratch
uv run python 00_reset_db.py
uv run python 10_get_docs.py
uv run python 15_supplementary_crawl.py
uv run python 20_index_docs.py

# Start MCP server (requires --product flag)
uv run python serve_mcp.py --product weaviate
uv run python serve_mcp.py --product togetherai
```

## Important Notes

- The project uses `uv` for dependency management (see `pyproject.toml` and `uv.lock`)
- Weaviate must be running on the cloud (WCD_URL and WCD_KEY in `.env`)
- Crawling is cached by `crawl4ai` - use `CacheMode.BYPASS` to force refresh
- UUID generation uses `generate_uuid5()` for deterministic IDs, enabling re-indexing without duplicates
- The MCP server connects via stdio, making it suitable for Claude Desktop integration
- MCP server is product-specific: use `--product` flag to specify which documentation to serve
- To serve multiple products simultaneously, run multiple server instances
