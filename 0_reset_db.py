import weaviate
from weaviate.classes.config import Configure, Property, DataType, Tokenization

client = weaviate.connect_to_local()

for collection_name in ["Chunks", "Documents"]:
    client.collections.delete(collection_name)

if not client.collections.exists("Chunks"):
    client.collections.create(
        name="Chunks",
        properties=[
            Property(name="product", data_type=DataType.TEXT, tokenization=Tokenization.FIELD),
            Property(name="chunk", data_type=DataType.TEXT),
            Property(name="chunk_no", data_type=DataType.INT),
            Property(name="path", data_type=DataType.TEXT, tokenization=Tokenization.FIELD),
        ],
        vector_config=Configure.Vectors.text2vec_cohere(
            model="embed-v4.0",
            source_properties=["chunk", "path"]
        )
    )

if not client.collections.exists("Documents"):
    client.collections.create(
        name="Documents",
        properties=[
            Property(name="product", data_type=DataType.TEXT, tokenization=Tokenization.FIELD),
            Property(name="body", data_type=DataType.TEXT),
            Property(name="path", data_type=DataType.TEXT, tokenization=Tokenization.FIELD),
        ],
        vector_config=Configure.Vectors.text2vec_cohere(
            model="embed-v4.0",
            source_properties=["path"]
        )
    )

client.close()
