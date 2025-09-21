import bentoml
from typing import List

client = bentoml.SyncHTTPClient("http://localhost:3000")

# Specify the texts to summarize
texts: List[str] = [
    "Paragraph one to summarize",
    "Paragraph two to summarize",
    "Paragraph three to summarize"
]

# Call the exposed API
response = client.summarize(texts=texts)

print(f"Summarized results: {response}")