# Use the official uv image for Python 3.13
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN uv sync --frozen

# Set environment variable for transport mode
ENV MCP_TRANSPORT=streamable-http

# Cloud Run will set PORT automatically, but default to 8080
ENV PORT=8080

# Run the MCP server
CMD ["uv", "run", "serve_mcp.py"]
