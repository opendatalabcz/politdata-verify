"""
jina AI client to interact with jina AI embedding service
"""
import json
import os
from typing import Dict, List, Any
import asyncio, aiohttp
from typing import Any, List, Optional
import requests
from dotenv import load_dotenv
load_dotenv()
JINA_API_KEY = os.getenv("JINA_API_KEY")
URL = "https://api.jina.ai/v1/embeddings"
MODEL = "jina-embeddings-v4"

class JinaEmbedder:
    def __init__(self):
        pass

    @staticmethod
    async def get_embedding(text: Dict[str, Any], task: str, **kwargs) -> List[float]:
        url = "https://api.jina.ai/v1/embeddings"
        model = kwargs.get("model", MODEL)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {JINA_API_KEY}"
        }
        data = {
            "model": model,
            "task": task,
            "input": text
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(response.json())
        data = response.json()["data"]
        embedding = data[0]["embedding"]
        return embedding

    @staticmethod
    async def embed_one(text: str, task: str, session, **kwargs) -> List[float]:
        model = kwargs.get("model", MODEL)
        payload = {
            "model": model,
            "task": task,
            "input": [{"text": text}],
        }
        headers = {
            "Authorization": f"Bearer {JINA_API_KEY}",
            "Content-Type": "application/json",
        }
        async with session.post(URL, headers=headers, json=payload, timeout=60) as r:
            r.raise_for_status()
            data = await r.json()
            return data["data"][0]["embedding"]

    # TODO: Improve batching performance, change names
    async def get_embeddings_batch_jina(self, texts: List[str], task: str, **kwargs) -> List[List[float]]:
        """
        Get embeddings for a batch of texts using Jina API asynchronously
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self.embed_one(text, task, session, **kwargs) for text in texts]
            embeddings = await asyncio.gather(*tasks)
            return embeddings




if __name__ == "__main__":
    async def main():
        embedder = JinaEmbedder()
        texts = [
            {"text": "Hello, world!"},
            {"text": "Jina AI is awesome."}
        ]
        embeddings = await embedder.get_embedding(texts, task="text-matching")
        print(embeddings)
    asyncio.run(main())