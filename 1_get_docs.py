import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BFSDeepCrawlStrategy, LXMLWebScrapingStrategy, URLPatternFilter, DomainFilter, FilterChain, CacheMode
import json
from pathlib import Path
from typing import Optional

output_dir = Path("./output")
output_dir.mkdir(parents=True, exist_ok=True)


async def crawl_docs(name: str, allowed_domains: list[str], start_url: str, url_pattern: Optional[str] = None):
    print(f"Crawling {name}...")

    # Create a filter chain for the crawler
    domain_filter = DomainFilter(allowed_domains=allowed_domains)
    filter_list = [domain_filter]
    if url_pattern:
        url_pattern_filter = URLPatternFilter(patterns=url_pattern)
        filter_list.append(url_pattern_filter)
    filter_chain = FilterChain(filter_list)

    # Create a crawler run config
    config = CrawlerRunConfig(
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_depth=4,
                include_external=False,
                filter_chain=filter_chain,
            ),
            scraping_strategy=LXMLWebScrapingStrategy(),
            verbose=True,
            cache_mode=CacheMode.ENABLED,
            semaphore_count=3,
        )

    # Run the crawler
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun(start_url, config=config)

        print(f"Crawled {len(results)} pages in total")

    return results


async def main():

    jobs = [
        {
            "name": "weaviate_docs",
            "allowed_domains": ["docs.weaviate.io"],
            "start_url": "https://docs.weaviate.io/weaviate",
            "url_pattern": None
        },
        {
            "name": "turbopuffer_docs",
            "allowed_domains": ["turbopuffer.com"],
            "start_url": "https://turbopuffer.com/docs",
            "url_pattern": "*/docs/*"
        },
        {
            "name": "pinecone_docs",
            "allowed_domains": ["docs.pinecone.io"],
            "start_url": "https://docs.pinecone.io/guides/get-started/overview",
            "url_pattern": None
        },
        {
            "name": "milvus_docs",
            "allowed_domains": ["milvus.io"],
            "start_url": "https://milvus.io/docs",
            "url_pattern": ["*/docs/*", "*/api-reference/pymilvus/*"]
        },
        {
            "name": "qdrant_docs",
            "allowed_domains": ["qdrant.tech"],
            "start_url": "https://qdrant.tech/documentation/",
            "url_pattern": ["*/documentation/*"]
        },
        {
            "name": "chroma_docs",
            "allowed_domains": ["docs.trychroma.com"],
            "start_url": "https://docs.trychroma.com/docs/overview/introduction",
            "url_pattern": None
        },
        {
            "name": "pgvector_docs",
            "allowed_domains": ["raw.githubusercontent.com"],
            "start_url": "https://raw.githubusercontent.com/pgvector/pgvector/refs/heads/master/README.md",
            "url_pattern": ["pgvector/pgvector/refs/heads/master/README.md"]
        }
    ]

    for job in jobs:
        results = await crawl_docs(**job)
        results_md = {}
        for result in results:
            results_md[result.url] = result.markdown

        with open(output_dir / f"{job['name']}_crawl4ai.json", "w") as f:
            json.dump(results_md, f)


if __name__ == "__main__":
    asyncio.run(main())
