import weaviate
from dotenv import load_dotenv
import os

load_dotenv(override=True)


def connect_to_weaviate():
    """
    Connect to Weaviate instance using environment variables.
    """
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WCD_URL"),
        auth_credentials=os.getenv("WCD_KEY"),
        headers={
            "X-Cohere-Api-Key": os.getenv("COHERE_API_KEY"),
            "X-Anthropic-Api-Key": os.getenv("ANTHROPIC_API_KEY")        },
    )
    return client


CRAWLED_DOCS_DIR ="./crawled_docs"
PROCESSED_DOCS_DIR = "./crawled_docs_processed"
CRAWL_JOBS = [
    {
        "name": "weaviate",
        "allowed_domains": ["docs.weaviate.io"],
        "start_url": "https://docs.weaviate.io/weaviate",
        "url_pattern": None
    },
    # {
    #     "name": "turbopuffer",
    #     "allowed_domains": ["turbopuffer.com"],
    #     "start_url": "https://turbopuffer.com/docs",
    #     "url_pattern": "*/docs/*"
    # },
    # {
    #     "name": "pinecone",
    #     "allowed_domains": ["docs.pinecone.io"],
    #     "start_url": "https://docs.pinecone.io/guides/get-started/overview",
    #     "url_pattern": None
    # },
    # {
    #     "name": "milvus",
    #     "allowed_domains": ["milvus.io"],
    #     "start_url": "https://milvus.io/docs",
    #     "url_pattern": ["*/docs/*", "*/api-reference/pymilvus/*"]
    # },
    # {
    #     "name": "qdrant",
    #     "allowed_domains": ["qdrant.tech"],
    #     "start_url": "https://qdrant.tech/documentation/",
    #     "url_pattern": ["*/documentation/*"]
    # },
    # {
    #     "name": "chroma",
    #     "allowed_domains": ["docs.trychroma.com"],
    #     "start_url": "https://docs.trychroma.com/docs/overview/introduction",
    #     "url_pattern": None
    # },
    # {
    #     "name": "pgvector",
    #     "allowed_domains": ["raw.githubusercontent.com"],
    #     "start_url": "https://raw.githubusercontent.com/pgvector/pgvector/refs/heads/master/README.md",
    #     "url_pattern": ["pgvector/pgvector/refs/heads/master/README.md"]
    # },
    {
        "name": "togetherai",
        "allowed_domains": ["docs.together.ai"],
        "start_url": "https://docs.together.ai/intro",
        "url_pattern": None
    }
]

PRODUCTS = [p["name"] for p in CRAWL_JOBS]
