"""
Analyze "Time to Hello World" across vector database documentation.

This script measures how many steps and pages a developer needs to navigate
to get a basic "hello world" working (connect, create collection/index, insert, query).
"""

import os
import json
from pathlib import Path
import weaviate
from weaviate.classes.query import Filter
from anthropic import Anthropic


# Products to analyze
PRODUCTS = ["weaviate", "pinecone", "qdrant", "turbopuffer", "chroma"]

# Connect to Weaviate
client = weaviate.connect_to_local(
    headers={
        "X-Cohere-Api-Key": os.getenv("COHERE_API_KEY"),
        "X-Anthropic-Api-Key": os.getenv("ANTHROPIC_API_KEY"),
    },
)

documents = client.collections.use("Documents")

# Initialize Anthropic client for analysis
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def find_getting_started_docs(product: str, limit: int = 10) -> list[dict]:
    """Find getting started / quickstart documentation for a product."""
    queries = [
        "getting started quickstart tutorial",
        "first steps hello world",
        "installation setup guide"
    ]

    all_results = []
    seen_paths = set()

    for query in queries:
        response = documents.query.hybrid(
            query=query,
            limit=limit,
            filters=Filter.by_property("product").equal(product)
        )

        for obj in response.objects:
            path = obj.properties["path"]
            if path not in seen_paths:
                seen_paths.add(path)
                all_results.append(obj.properties)

    return all_results[:limit]


def analyze_time_to_hello_world(product: str, docs: list[dict]) -> dict:
    """
    Use Claude to analyze the documentation and determine time-to-hello-world metrics.
    """

    # Prepare context from docs
    doc_context = "\n\n---\n\n".join([
        f"URL: {doc['path']}\n\nContent:\n{doc['body'][:3000]}..."
        for doc in docs
    ])

    analysis_prompt = f"""Analyze the following {product} documentation to determine the "time to hello world" -
how long it takes a developer to get a basic working example that:
1. Connects to the database
2. Creates a collection/index
3. Inserts some vectors/documents
4. Performs a basic query/search

For each product, provide:
1. **steps_count**: Total number of distinct steps needed (numeric)
2. **pages_count**: Number of documentation pages a developer needs to visit (numeric)
3. **code_blocks_count**: Number of code examples they need to reference (numeric)
4. **estimated_time_minutes**: Rough estimate of time in minutes for an experienced developer (numeric)
5. **steps_description**: A brief list of the steps involved
6. **complexity_rating**: Rate 1-5 (1=very easy, 5=very complex)
7. **prerequisites**: What they need installed/configured first (e.g., API keys, local setup)
8. **notes**: Any observations about the documentation quality or developer experience

Documentation:

{doc_context}

Respond ONLY with valid JSON in this exact format:
{{
    "product": "{product}",
    "steps_count": <number>,
    "pages_count": <number>,
    "code_blocks_count": <number>,
    "estimated_time_minutes": <number>,
    "steps_description": ["step 1", "step 2", ...],
    "complexity_rating": <1-5>,
    "prerequisites": ["prereq 1", "prereq 2", ...],
    "notes": "observations here"
}}
"""

    response = anthropic.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": analysis_prompt
        }]
    )

    # Extract JSON from response
    response_text = response.content[0].text

    # Try to parse JSON (Claude sometimes wraps it in markdown)
    if "```json" in response_text:
        json_str = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        json_str = response_text.split("```")[1].split("```")[0].strip()
    else:
        json_str = response_text.strip()

    return json.loads(json_str)


def main():
    results = []

    print("Analyzing 'Time to Hello World' for vector databases...\n")

    for product in PRODUCTS:
        print(f"Analyzing {product}...")

        # Find relevant documentation
        docs = find_getting_started_docs(product, limit=5)

        if not docs:
            print(f"  ⚠️  No documentation found for {product}")
            continue

        print(f"  Found {len(docs)} relevant documentation pages")

        # Analyze with Claude
        try:
            analysis = analyze_time_to_hello_world(product, docs)
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

    # Generate summary report
    generate_summary_report(results)

    client.close()


def generate_summary_report(results: list[dict]):
    """Generate a markdown summary report."""

    # Sort by estimated time
    sorted_results = sorted(results, key=lambda x: x["estimated_time_minutes"])

    report = "# Time to Hello World Analysis\n\n"
    report += "Comparison of onboarding complexity across vector databases.\n\n"
    report += "## Quick Summary\n\n"
    report += "| Product | Steps | Pages | Time (min) | Complexity |\n"
    report += "|---------|-------|-------|------------|------------|\n"

    for r in sorted_results:
        report += f"| {r['product'].capitalize()} | {r['steps_count']} | {r['pages_count']} | {r['estimated_time_minutes']} | {r['complexity_rating']}/5 |\n"

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

        report += f"**Notes:** {r['notes']}\n\n"
        report += "---\n\n"

    # Save report
    report_file = Path("outputs/time_to_hello_world_report.md")
    with open(report_file, "w") as f:
        f.write(report)

    print(f"✓ Summary report saved to {report_file}")


if __name__ == "__main__":
    main()
