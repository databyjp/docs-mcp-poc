import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LXMLWebScrapingStrategy, CacheMode
import json
from pathlib import Path
from typing import Optional
from utils import CRAWLED_DOCS_DIR, PROCESSED_DOCS_DIR


crawled_docs_dir = Path(CRAWLED_DOCS_DIR)
processed_docs_dir = Path(PROCESSED_DOCS_DIR)
processed_docs_dir.mkdir(parents=True, exist_ok=True)


def is_problematic_content(content: str) -> bool:
    """
    Check if the content indicates a failed or problematic scrape.

    Returns True if the content needs to be re-scraped.
    """
    if not content:
        return True

    # Check for very short content (likely failed)
    if len(content.strip()) < 50:
        return True

    # Check for common security challenge indicators
    security_indicators = [
        "Just a moment...",
        "Enable JavaScript and cookies to continue",
        "Please enable cookies",
        "Checking your browser",
        "Access denied",
        "403 Forbidden",
        "404 Not Found",
        "500 Internal Server Error",
        "Ray ID:",
        "Please verify you are a human",
        "Security check",
        "captcha",
        "CAPTCHA"
    ]

    content_lower = content.lower()
    for indicator in security_indicators:
        if indicator.lower() in content_lower:
            print(f"    ⚠️  Found security indicator: {indicator}")
            return True

    return False


async def retry_scrape_url(url: str) -> Optional[str]:
    """
    Retry scraping a specific URL with basic configuration.

    Returns the markdown content if successful, None otherwise.
    """
    print(f"  Retrying scrape for: {url}")

    config = CrawlerRunConfig(
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=False,
        cache_mode=CacheMode.BYPASS,  # Bypass cache to get fresh content
    )

    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url, config=config)

            if result and len(result) > 0:
                markdown = result[0].markdown

                # Check if the retry also failed
                if is_problematic_content(markdown):
                    print(f"    ⚠️  Retry also returned problematic content")
                    return None

                print(f"    ✓ Successfully re-scraped")
                return markdown
            else:
                print(f"    ✗ Retry failed - no results")
                return None

    except Exception as e:
        print(f"    ✗ Retry failed with error: {e}")
        return None


async def process_file(input_file: Path) -> dict:
    """
    Process a single JSON file, identifying and retrying problematic URLs.

    Returns a dictionary with updated content.
    """
    print(f"\nProcessing {input_file.name}...")

    with open(input_file, 'r') as f:
        data = json.load(f)

    total_urls = len(data)
    problematic_urls = []

    # First pass: identify problematic URLs
    for url, content in data.items():
        if is_problematic_content(content):
            problematic_urls.append(url)

    print(f"  Found {len(problematic_urls)} problematic URLs out of {total_urls} total")

    if not problematic_urls:
        print(f"  ✓ No issues found, copying as-is")
        return data

    # Second pass: retry scraping problematic URLs
    retry_count = 0
    success_count = 0

    for url in problematic_urls:
        retry_count += 1
        new_content = await retry_scrape_url(url)

        if new_content:
            data[url] = new_content
            success_count += 1
        else:
            # Keep the original (problematic) content
            print(f"    Keeping original content for {url}")

    print(f"  Summary: Retried {retry_count} URLs, successfully fixed {success_count}")

    return data


async def main():
    """
    Main function to process all crawled documentation files.
    """
    print("Starting supplementary crawl process...")
    print(f"Input directory: {crawled_docs_dir}")
    print(f"Output directory: {processed_docs_dir}")

    # Get all JSON files from crawled_docs
    json_files = list(crawled_docs_dir.glob("*.json"))

    if not json_files:
        print("No JSON files found in crawled_docs directory")
        return

    print(f"\nFound {len(json_files)} files to process")

    # Process each file
    for input_file in json_files:
        processed_data = await process_file(input_file)

        # Save to processed directory
        output_file = processed_docs_dir / input_file.name
        with open(output_file, 'w') as f:
            json.dump(processed_data, f, indent=2)

        print(f"  ✓ Saved to {output_file.name}")

    print("\n✓ All files processed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
