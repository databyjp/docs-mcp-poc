from weaviate.util import generate_uuid5
import json
from chonkie import TokenChunker
from tqdm import tqdm
from utils import PROCESSED_DOCS_DIR
from pathlib import Path
from utils import connect_to_weaviate


client = connect_to_weaviate()

doc_files_dir = Path(PROCESSED_DOCS_DIR)


chunker = TokenChunker(
    tokenizer="word", # Default tokenizer (or use "gpt2", etc.)
    chunk_size=256, # Maximum tokens per chunk
    chunk_overlap=32 # Overlap between chunks
)


crawled_doc_paths = doc_files_dir.glob("*.json")

chunks = client.collections.use("Chunks")
documents = client.collections.use("Documents")

for crawled_doc_path in crawled_doc_paths:
    vdb_name = crawled_doc_path.stem.split("_")[0]
    crawled_doc_dict = json.loads(crawled_doc_path.read_text())
    print(f"Indexing {vdb_name} docs, containing {len(crawled_doc_dict)} pages")

    print("Indexing chunks...")
    with chunks.batch.fixed_size(batch_size=50) as batch:
        for path, text in tqdm(crawled_doc_dict.items()):
            try:
                text_chunks = chunker.chunk(text)
                if len(text_chunks) == 0:
                    continue

                for i, text_chunk in enumerate(text_chunks):
                    batch.add_object(
                        properties={
                            "product": vdb_name,
                            "chunk": text_chunk.text,
                            "chunk_no": i,
                            "path": path
                        },
                        uuid=generate_uuid5("Chunks", f"{vdb_name}-{path}-chunk-{i}")
                    )
            except Exception as e:
                print(f"Error ingesting {path}: {e}")


    print("Indexing documents...")
    with documents.batch.fixed_size(batch_size=50) as batch:
        for path, text in tqdm(crawled_doc_dict.items()):
            batch.add_object(
                properties={
                    "product": vdb_name,
                    "body": text,
                    "path": path
                },
                uuid=generate_uuid5("Documents", f"{vdb_name}-{path}")
            )

client.close()
