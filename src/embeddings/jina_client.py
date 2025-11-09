"""
jina AI client to interact with jina AI embedding service
"""
import json
import os
from typing import Dict, List, Any

import requests
from dotenv import load_dotenv
load_dotenv()
JINA_API_KEY = os.getenv("JINA_API_KEY")
URL = "https://api.jina.ai/v1/embeddings"
Model = "jina-embeddings-v4"

class JinaEmbedder:
    def __init__(self):
        pass

    @staticmethod
    def get_embedding(texts: List[Dict[str, Any]], task: str, **kwargs) -> List[List[float]]:
        url = "https://api.jina.ai/v1/embeddings"
        model = kwargs.get("model", Model)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {JINA_API_KEY}"
        }
        data = {
            "model": model,
            "task": task,
            "input": texts
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(response.json())
        return response.json()["data"]



if __name__ == "__main__":
    embedder = JinaEmbedder()
    texts = [
        {"text": "Hello, world!"},
        {"text": "Jina AI is awesome."}
    ]
    embeddings = embedder.get_embedding(texts, task="text-matching")
    print(embeddings)