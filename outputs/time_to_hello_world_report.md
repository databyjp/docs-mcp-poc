# Time to Hello World Analysis

Comparison of onboarding complexity across vector databases.

*Generated using MCP server for documentation search*

## Quick Summary

| Product | Steps | Pages | Time (min) | Complexity |
|---------|-------|-------|------------|------------|
| Chroma | 7 | 2 | 5 | 1/5 |
| Qdrant | 6 | 2 | 10 | 2/5 |
| Turbopuffer | 6 | 4 | 10 | 2/5 |
| Pinecone | 8 | 4 | 25 | 2/5 |
| Weaviate | 7 | 3 | 45 | 3/5 |

## Key Insights

- **Fastest to get started:** Chroma (~5 min)
- **Most time required:** Weaviate (~45 min)
- **Simplest complexity:** Chroma (1/5)
- **Highest complexity:** Weaviate (3/5)
- **Average time to hello world:** ~19.0 minutes
- **Average number of steps:** 6.8


## Detailed Analysis

### Chroma

**Complexity Rating:** 1/5  
**Estimated Time:** ~5 minutes  
**Pages to Visit:** 2  
**Code Examples Needed:** 6  

**Prerequisites:**
- Python 3.x installed
- pip package manager
- Basic Python knowledge
- No external API keys required for default setup

**Steps:**
1. Install chromadb via pip
2. Import chromadb and create a Client instance
3. Create a collection with a name
4. Add text documents to the collection with unique IDs
5. Query the collection with query text
6. Inspect the query results
7. Combine everything into a single working script

**Hello World Code:**

```python
import chromadb

# Create client
chroma_client = chromadb.Client()

# Create collection
collection = chroma_client.get_or_create_collection(name="my_collection")

# Add documents
collection.upsert(
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges"
    ],
    ids=["id1", "id2"]
)

# Query the collection
results = collection.query(
    query_texts=["This is a query document about florida"],
    n_results=2
)

print(results)
```

*Source: https://docs.trychroma.com/docs/overview/getting-started*

**Notes:** Chroma has an exceptionally low barrier to entry. The documentation provides a clear 7-step tutorial that goes from zero to working code in under 5 minutes. The ephemeral client requires no configuration - just `chromadb.Client()` works immediately. Automatic embedding handling (using sentence-transformers by default) eliminates a major complexity point. The documentation includes a complete working example early in the guide. The API is intuitive with familiar patterns (add/query). However, the ephemeral client loses data on program termination - developers need to read 'Next Steps' section to understand persistence options. Multiple client types (Ephemeral, Persistent, HttpClient, CloudClient) available but not required for initial learning.

**Documentation References:**
- https://docs.trychroma.com/docs/overview/getting-started
- https://docs.trychroma.com/docs/overview/introduction
- https://docs.trychroma.com/cloud/getting-started
- https://docs.trychroma.com/docs/collections/manage-collections

---

### Qdrant

**Complexity Rating:** 2/5  
**Estimated Time:** ~10 minutes  
**Pages to Visit:** 2  
**Code Examples Needed:** 6  

**Prerequisites:**
- Docker installed and running
- Python 3.6+ installed
- pip package manager
- Basic understanding of vector embeddings (optional but helpful)

**Steps:**
1. Install Docker and pull qdrant/qdrant image
2. Start Qdrant container with port mappings and storage volume
3. Install qdrant-client Python package (pip install qdrant-client)
4. Initialize QdrantClient and connect to localhost:6333
5. Create a collection with vector configuration (size and distance metric)
6. Add vectors with payloads and perform a similarity search query

**Hello World Code:**

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Connect to Qdrant server
client = QdrantClient(url="http://localhost:6333")

# Create a collection
client.create_collection(
    collection_name="test_collection",
    vectors_config=VectorParams(size=4, distance=Distance.DOT),
)

# Add vectors
client.upsert(
    collection_name="test_collection",
    wait=True,
    points=[
        PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
        PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}),
        PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}),
    ],
)

# Search
results = client.query_points(
    collection_name="test_collection",
    query=[0.2, 0.1, 0.9, 0.7],
    limit=3,
).points

for point in results:
    print(f"ID: {point.id}, Score: {point.score}")
```

*Source: https://qdrant.tech/documentation/quick-start*

**Notes:** Qdrant has an excellent getting started experience with clear documentation. The quickstart guide is comprehensive and includes code examples in multiple programming languages (Python, TypeScript, Rust, Java, C#, Go). Docker setup is straightforward. The main dependency is having Docker running. Two alternative paths exist: (1) Docker-based local development (recommended for quickstart) with REST API access on port 6333, or (2) Python-only local mode using QdrantClient(":memory:") for in-memory storage without Docker. The beginner tutorial mentions completing setup in 5-15 minutes. Code complexity is minimal with clear API design. Error documentation could be more comprehensive, but the API is intuitive. The documentation explicitly notes default security is minimal (no auth), which is fine for local development.

**Documentation References:**
- https://qdrant.tech/documentation/quick-start
- https://qdrant.tech/documentation/beginner-tutorials/search-beginners
- https://qdrant.tech/documentation/guides/installation

---

### Turbopuffer

**Complexity Rating:** 2/5  
**Estimated Time:** ~10 minutes  
**Pages to Visit:** 4  
**Code Examples Needed:** 5  

**Prerequisites:**
- Python 3.6+
- pip package manager
- Turbopuffer account (free tier available at https://turbopuffer.com/join)
- API key from Turbopuffer dashboard
- Vector embeddings (can use random vectors for testing, or OpenAI/Cohere for real embeddings)
- Internet connection

**Steps:**
1. Install turbopuffer Python client with pip
2. Create API key in Turbopuffer dashboard and set environment variable
3. Initialize Turbopuffer client with API key and select region
4. Create/access a namespace (implicitly created on first write)
5. Write/upsert documents with vectors and attributes
6. Query documents using vector search with optional filters

**Hello World Code:**

```python
import turbopuffer
import os
from typing import List

# Initialize client
tpuf = turbopuffer.Turbopuffer(
    api_key=os.getenv("TURBOPUFFER_API_KEY"),
    region="gcp-us-central1"
)

# Create/access namespace (auto-created on first write)
ns = tpuf.namespace('hello-world')

# Simple function to create vectors (using random for demo)
def get_vector(text: str) -> List[float]:
    return [__import__('random').random() for _ in range(2)]

# Write documents with vectors
ns.write(
    upsert_rows=[
        {'id': 1, 'vector': get_vector("hello"), 'text': "hello world"},
        {'id': 2, 'vector': get_vector("goodbye"), 'text': "goodbye world"}
    ],
    distance_metric='cosine_distance'
)

# Query documents
result = ns.query(
    rank_by=("vector", "ANN", get_vector("hello world")),
    top_k=10,
    include_attributes=["text"]
)

# Print results
for row in result.rows:
    print(f"ID: {row.id}, Text: {row.text}, Distance: {row.__dict__.get('$dist', 'N/A')}")
```

*Source: https://turbopuffer.com/docs/quickstart*

**Notes:** Turbopuffer has excellent developer experience for rapid prototyping. The quickstart is comprehensive with working Python code examples. Key strengths: (1) No local database setup needed - fully managed service; (2) Namespace is implicitly created on first write - no schema definition step required; (3) Rich documentation with multiple language clients (Python, TypeScript, Go, Java, Ruby); (4) Vector embeddings optional - can use random vectors for initial testing; (5) Support for both vector search and full-text search; (6) Integrated filtering without separate query language. The only prerequisite complexity is obtaining an API key, which requires account signup. Documentation quality is high with clear examples and links to region selection and API key management.

**Documentation References:**
- https://turbopuffer.com/docs/quickstart
- https://turbopuffer.com/docs/auth
- https://turbopuffer.com/docs/write
- https://turbopuffer.com/docs/query

---

### Pinecone

**Complexity Rating:** 2/5  
**Estimated Time:** ~25 minutes  
**Pages to Visit:** 4  
**Code Examples Needed:** 6  

**Prerequisites:**
- Python 3.x installed
- pip package manager
- Pinecone account (free tier available)
- Valid API key from Pinecone console
- Internet connection for API calls

**Steps:**
1. Sign up for Pinecone account and obtain API key
2. Install Pinecone SDK (pip install pinecone)
3. Initialize Pinecone client with API key
4. Create a dense index with integrated embedding model
5. Wait for index to be ready (if needed)
6. Prepare and structure data records with text and metadata
7. Upsert records into index namespace
8. Perform semantic search query on indexed data

**Hello World Code:**

```python
from pinecone import Pinecone
import time

# Initialize client
pc = Pinecone(api_key="YOUR_API_KEY")

# Create index
index_name = "quickstart"
if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={"model": "llama-text-embed-v2", "field_map": {"text": "chunk_text"}}
    )

# Get index
index = pc.Index(index_name)

# Upsert data
records = [
    {"_id": "1", "chunk_text": "The Eiffel Tower was completed in 1889.", "category": "history"},
    {"_id": "2", "chunk_text": "Photosynthesis allows plants to convert sunlight into energy.", "category": "science"},
    {"_id": "3", "chunk_text": "Albert Einstein developed the theory of relativity.", "category": "science"}
]
index.upsert_records("example-namespace", records)
time.sleep(2)

# Search
results = index.search(
    namespace="example-namespace",
    query={"top_k": 2, "inputs": {"text": "Famous historical structures"}}
)

# Display results
for hit in results['result']['hits']:
    print(f"ID: {hit['_id']}, Score: {hit['_score']:.2f}, Text: {hit['fields']['chunk_text']}")

# Cleanup
pc.delete_index(index_name)
```

*Source: https://docs.pinecone.io/guides/get-started/quickstart*

**Notes:** Pinecone offers one of the smoothest developer experiences among vector databases. The integrated embedding model feature significantly reduces complexity - developers don't need to manage external embeddings. The quickstart is well-structured with clear examples in multiple languages. Main friction points: (1) Requires account signup and API key acquisition, (2) Index creation can take ~10 seconds to initialize, (3) Upsert operations need a small wait before search (eventual consistency). Documentation is comprehensive but somewhat lengthy. The free Starter plan supports the full hello world scenario. Setup time could be further reduced by providing pre-initialized indexes in trial environments.

**Documentation References:**
- https://docs.pinecone.io/guides/get-started/quickstart
- https://docs.pinecone.io/guides/get-started/overview
- https://docs.pinecone.io/guides/get-started/concepts
- https://docs.pinecone.io/guides/index-data/create-an-index

---

### Weaviate

**Complexity Rating:** 3/5  
**Estimated Time:** ~45 minutes  
**Pages to Visit:** 3  
**Code Examples Needed:** 18  

**Prerequisites:**
- Cloud account (Weaviate Cloud) OR Docker + Ollama installed locally
- Client library installation (pip/npm/go/maven)
- API credentials (REST endpoint URL and API key)
- Optional: LLM API keys (OpenAI/Cohere for RAG features)

**Steps:**
1. Create a Weaviate instance (cloud or local)
2. Install a client library (Python/JS/Go/Java)
3. Connect to Weaviate and verify readiness
4. Define a collection with vectorizer configuration
5. Load and batch import sample data
6. Perform a semantic search query
7. Perform a retrieval augmented generation (RAG) query

**Hello World Code:**

```python
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure
import requests, json, os

# Connect to Weaviate
weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)

# Create collection
questions = client.collections.create(
    name="Question",
    vector_config=Configure.Vectors.text2vec_weaviate(),
)

# Import data
resp = requests.get(
    "https://raw.githubusercontent.com/weaviate-tutorials/quickstart/main/data/jeopardy_tiny.json"
)
data = json.loads(resp.text)
questions_col = client.collections.use("Question")

with questions_col.batch.fixed_size(batch_size=200) as batch:
    for d in data:
        batch.add_object({"answer": d["Answer"], "question": d["Question"], "category": d["Category"]})

# Query data
response = questions_col.query.near_text(query="biology", limit=2)
for obj in response.objects:
    print(json.dumps(obj.properties, indent=2))

client.close()
```

*Source: https://docs.weaviate.io/weaviate/quickstart - synthesized from multiple code examples*

**Notes:** Weaviate documentation provides clear, well-structured quickstart guides with multiple paths (cloud vs local, different languages). Cloud setup is the fastest path (10-30 mins cluster provisioning + 15 mins coding). Local setup requires Docker/Ollama setup time. Documentation includes excellent step-by-step guidance, multiple language examples (Python/JS/Go/Java), and comprehensive error handling guidance. The main complexity is understanding vectorizer configuration and API key setup rather than the code itself. All code examples are self-contained and copy-paste ready.

**Documentation References:**
- https://docs.weaviate.io/weaviate/quickstart
- https://docs.weaviate.io/weaviate/quickstart/local
- https://docs.weaviate.io/cloud/quickstart

---

