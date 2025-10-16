import os
import weaviate
from weaviate.classes.generate import GenerativeConfig
from weaviate.classes.query import Filter
from utils import PRODUCTS


client = weaviate.connect_to_local(
    headers={
        "X-Cohere-Api-Key": os.getenv("COHERE_API_KEY"),
        "X-Anthropic-Api-Key": os.getenv("ANTHROPIC_API_KEY"),
    },
)

chunks = client.collections.use("Chunks")

rag_config = GenerativeConfig.anthropic(
    # model="claude-haiku-4-5-20251001",
    model="claude-3-5-haiku-latest",
)


for product in PRODUCTS[:3]:
    filter = Filter.by_property("product").equal(product)

    response = chunks.generate.hybrid(
        query="Add documents to the database Python",
        limit=5,
        grouped_task="How do I add documents a this database using Python? Cite the source URLs please.",
        filters=filter,
        generative_provider=rag_config
    )

    print(response.generative.text)

    for o in response.objects:
        print(o.properties["path"])

client.close()
