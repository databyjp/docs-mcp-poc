"""
Analyze "Time to Hello World" across vector database documentation.

This script measures how many steps and pages a developer needs to navigate
to get a basic "hello world" working (connect, create collection/index, insert, query).

Uses the MCP server to search documentation.
"""

import os
import json
from pathlib import Path
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio


# Products to analyze
PRODUCTS = ["weaviate", "pinecone", "qdrant", "turbopuffer", "chroma"]

# Set up the MCP server connection
vdb_docs_mcp_directory = Path(__file__).parent
vdb_docs_mcp_server = MCPServerStdio(
    command="uv",
    args=["--directory", str(vdb_docs_mcp_directory), "run", "python", "40_build_mcp.py"],
    env=os.environ.copy(),
)

# Create an agent with access to the vector database documentation MCP
analysis_agent = Agent(
    model="claude-haiku-4-5-20251001",
    toolsets=[vdb_docs_mcp_server]
)


@analysis_agent.system_prompt
def set_system_prompt() -> str:
    return """
    You are a documentation analysis expert for vector databases.

    Your task is to analyze "time to hello world" - how long it takes a developer
    to get a basic working example that:
    1. Connects to the database
    2. Creates a collection/index
    3. Inserts some vectors/documents
    4. Performs a basic query/search

    Use the search_documents tool to find getting started documentation.
    Then use fetch_document to get full content of the most relevant pages.

    Be thorough and objective in your analysis.
    """


def analyze_product(product: str) -> dict:
    """
    Analyze a single product's documentation for time-to-hello-world metrics.
    """

    prompt = f"""
    Analyze the {product} documentation to determine the "time to hello world".

    Steps:
    1. Use search_documents to find getting started, quickstart, or tutorial pages for {product}
    2. Use fetch_document to get the full content of the most relevant 3-5 pages
    3. Analyze the documentation and provide a JSON response with these fields:

    {{
        "product": "{product}",
        "steps_count": <number of distinct steps needed>,
        "pages_count": <number of documentation pages a developer needs to visit>,
        "code_blocks_count": <number of code examples they need to reference>,
        "estimated_time_minutes": <rough estimate of time in minutes for an experienced developer>,
        "steps_description": ["step 1", "step 2", ...],
        "complexity_rating": <1-5, where 1=very easy, 5=very complex>,
        "prerequisites": ["prereq 1", "prereq 2", ...],
        "hello_world_code": "minimal working code snippet (10-30 lines) showing connection, create collection, insert, and query",
        "code_source_url": "URL where the code came from or 'synthesized' if combined",
        "notes": "observations about documentation quality or developer experience",
        "analyzed_documents": ["url1", "url2", ...]
    }}

    Important:
    - Use Python code if available
    - Keep code minimal and realistic based on the docs
    - Be objective in your assessment
    - Include all document URLs you analyzed in analyzed_documents

    Return ONLY the JSON object, no other text.
    """

    print(f"  Searching and analyzing {product} documentation...")

    try:
        response = analysis_agent.run_sync(user_prompt=prompt)
        result_text = response.output

        # Parse JSON from response
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            json_str = result_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = result_text.strip()

        result = json.loads(json_str)
        return result

    except Exception as e:
        print(f"  ✗ Error: {e}")
        raise


def main():
    results = []

    # Ensure outputs directory exists
    Path("outputs").mkdir(exist_ok=True)

    print("Analyzing 'Time to Hello World' for vector databases...\n")
    print("Using MCP server for documentation search...\n")

    for product in PRODUCTS:
        print(f"Analyzing {product}...")

        try:
            analysis = analyze_product(product)
            results.append(analysis)

            print(f"  ✓ Steps: {analysis['steps_count']}, "
                  f"Pages: {analysis['pages_count']}, "
                  f"Time: ~{analysis['estimated_time_minutes']} min, "
                  f"Complexity: {analysis['complexity_rating']}/5")
        except Exception as e:
            print(f"  ✗ Error analyzing {product}: {e}")
            continue

        print()

    # Save results
    output_file = Path("outputs/time_to_hello_world_analysis.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Analysis complete! Results saved to {output_file}")

    # Save individual code snippets
    save_code_snippets(results)

    # Generate summary report
    generate_summary_report(results)


def save_code_snippets(results: list[dict]):
    """Save individual code snippets to separate files for easy reference."""
    snippets_dir = Path("outputs/code_snippets")
    snippets_dir.mkdir(exist_ok=True)

    for r in results:
        if 'hello_world_code' in r:
            product = r['product']
            snippet_file = snippets_dir / f"{product}_hello_world.py"

            with open(snippet_file, "w") as f:
                f.write(f"# {product.capitalize()} - Hello World Example\n")
                if 'code_source_url' in r:
                    f.write(f"# Source: {r['code_source_url']}\n")
                f.write(f"# Estimated time: ~{r['estimated_time_minutes']} minutes\n")
                f.write(f"# Complexity: {r['complexity_rating']}/5\n\n")
                f.write(r['hello_world_code'])

            print(f"  ✓ Code snippet saved: {snippet_file}")


def generate_summary_report(results: list[dict]):
    """Generate a markdown summary report."""

    # Sort by estimated time
    sorted_results = sorted(results, key=lambda x: x["estimated_time_minutes"])

    report = "# Time to Hello World Analysis\n\n"
    report += "Comparison of onboarding complexity across vector databases.\n\n"
    report += f"*Generated using MCP server for documentation search*\n\n"
    report += "## Quick Summary\n\n"
    report += "| Product | Steps | Pages | Time (min) | Complexity |\n"
    report += "|---------|-------|-------|------------|------------|\n"

    for r in sorted_results:
        report += f"| {r['product'].capitalize()} | {r['steps_count']} | {r['pages_count']} | {r['estimated_time_minutes']} | {r['complexity_rating']}/5 |\n"

    report += "\n## Key Insights\n\n"

    # Find fastest and slowest
    fastest = sorted_results[0]
    slowest = sorted_results[-1]
    report += f"- **Fastest to get started:** {fastest['product'].capitalize()} (~{fastest['estimated_time_minutes']} min)\n"
    report += f"- **Most time required:** {slowest['product'].capitalize()} (~{slowest['estimated_time_minutes']} min)\n"

    # Find simplest and most complex
    simplest = min(sorted_results, key=lambda x: x['complexity_rating'])
    most_complex = max(sorted_results, key=lambda x: x['complexity_rating'])
    report += f"- **Simplest complexity:** {simplest['product'].capitalize()} ({simplest['complexity_rating']}/5)\n"
    report += f"- **Highest complexity:** {most_complex['product'].capitalize()} ({most_complex['complexity_rating']}/5)\n"

    # Average stats
    avg_time = sum(r['estimated_time_minutes'] for r in sorted_results) / len(sorted_results)
    avg_steps = sum(r['steps_count'] for r in sorted_results) / len(sorted_results)
    report += f"- **Average time to hello world:** ~{avg_time:.1f} minutes\n"
    report += f"- **Average number of steps:** {avg_steps:.1f}\n\n"

    report += "\n## Detailed Analysis\n\n"

    for r in sorted_results:
        report += f"### {r['product'].capitalize()}\n\n"
        report += f"**Complexity Rating:** {r['complexity_rating']}/5  \n"
        report += f"**Estimated Time:** ~{r['estimated_time_minutes']} minutes  \n"
        report += f"**Pages to Visit:** {r['pages_count']}  \n"
        report += f"**Code Examples Needed:** {r['code_blocks_count']}  \n\n"

        report += "**Prerequisites:**\n"
        for prereq in r['prerequisites']:
            report += f"- {prereq}\n"
        report += "\n"

        report += "**Steps:**\n"
        for i, step in enumerate(r['steps_description'], 1):
            report += f"{i}. {step}\n"
        report += "\n"

        # Add code snippet
        if 'hello_world_code' in r:
            report += "**Hello World Code:**\n\n"
            # Detect language from product or use python as default
            lang = "python"
            report += f"```{lang}\n{r['hello_world_code']}\n```\n\n"
            if 'code_source_url' in r:
                report += f"*Source: {r['code_source_url']}*\n\n"

        report += f"**Notes:** {r['notes']}\n\n"

        # Add analyzed documents
        if 'analyzed_documents' in r:
            report += "**Documentation References:**\n"
            for doc_path in r['analyzed_documents']:
                report += f"- {doc_path}\n"
            report += "\n"

        report += "---\n\n"

    # Save report
    report_file = Path("outputs/time_to_hello_world_report.md")
    with open(report_file, "w") as f:
        f.write(report)

    print(f"✓ Summary report saved to {report_file}")


if __name__ == "__main__":
    main()
