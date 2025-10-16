# Turbopuffer - Hello World Example
# Source: https://turbopuffer.com/docs/quickstart
# Estimated time: ~10 minutes
# Complexity: 2/5

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