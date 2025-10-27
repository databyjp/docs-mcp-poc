🚀 Do you use AI tools to code? If you do, you might have seen them generate code that's incorrect or out of date. So, I've hacked together an MCP serve to serve Weaviate Docs in AI IDEs.

This MCP (Model Context Protocol) server gives AI models instant access to Weaviate's documentation. This means you can ask (Claude Code, Gemini CLI, Cursor etc.) questions like:
- "How can I reduce my Weaviate memory footprint?"
- "When should I use multi-tenancy?"
- "What does the Query Agent do?"

Why this matters: Instead of context-switching between your IDE, browser tabs, and documentation sites, you can get Weaviate guidance directly in your coding environment.

Try it now - it takes 30 seconds to add:

Option 1 - Add a .mcp.json file to your project root with this content:

```json
{
  "mcpServers": {
    "weaviate-docs": {
      "type": "http",
      "url": "https://weaviate-docs-mcp-3hx7rjpxua-uc.a.run.app/mcp"
    }
  }
}
```

Add with a CLI command - e.g. for Claude Code:

```bash
claude mcp add --transport http weaviate-docs https://weaviate-docs-mcp-3hx7rjpxua-uc.a.run.app/mcp
```

I'd love your feedback:
- Does it answer your questions accurately?
- What queries are you running?
- Are the responses helpful for your actual workflow?
- What would make this more useful?

Give it a try and let me know what you think! 🙏

#Weaviate #AI #DeveloperTools #MCP #VectorDatabase

TIP - working with doc chunks is a relatively simple task, summarising info from context (reading docs). So, I use the Claude Haiku model when I'm working with the MCP to generate answers or code snippets. This will help you preserve your weekly limits ;)
