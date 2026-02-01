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
        # print(response.json())
        data = response.json()["data"]
        embedding = data[0]["embedding"]
        return embedding

    @staticmethod
    async def get_embeddings_batch_jina(texts: List[str], task: str, batch_size: int = 30, **kwargs) -> List[List[float]]:
        """
        Get embeddings for a batch of texts using Jina API asynchronously
        """
        model = kwargs.get("model", MODEL)
        headers = {
            "Authorization": f"Bearer {JINA_API_KEY}",
            "Content-Type": "application/json",
        }

        all_embeddings = []
        async with aiohttp.ClientSession() as session:
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i: i + batch_size]

                batch_input = [{"text": t} for t in batch_texts]
                payload = {
                    "model": model,
                    "task": task,
                    "input": batch_input,
                }

                try:
                    async with session.post(URL, headers=headers, json=payload) as response:
                        if response.status == 429:
                            print(f"Rate limit hit. Retrying batch {i} in 5s...")
                            await asyncio.sleep(5)
                            # Simple retry logic
                            async with session.post(URL, headers=headers, json=payload) as retry_resp:
                                retry_resp.raise_for_status()
                                resp_json = await retry_resp.json()
                        else:
                            response.raise_for_status()
                            resp_json = await response.json()

                        data = resp_json["data"]
                        data.sort(key=lambda x: x["index"])
                        batch_embeddings = [item["embedding"] for item in data]
                        all_embeddings.extend(batch_embeddings)

                except Exception as e:
                    print(f"Error processing batch {i}: {e}")
                    raise e

        return all_embeddings


if __name__ == "__main__":
    async def main():
        embedder = JinaEmbedder()
        texts = ["Test chunk 1", "Test chunk 2"] * 20  # 40 chunks total
        print("Sending batch...")
        embeddings = await embedder.get_embeddings_batch_jina(texts, task="retrieval.passage")
        print(embeddings)
        print(f"Success! Received {len(embeddings)} embeddings.")


    asyncio.run(main())