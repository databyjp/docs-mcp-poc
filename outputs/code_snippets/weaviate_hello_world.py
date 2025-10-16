# Weaviate - Hello World Example
# Source: https://docs.weaviate.io/weaviate/quickstart - synthesized from multiple code examples
# Estimated time: ~45 minutes
# Complexity: 3/5

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