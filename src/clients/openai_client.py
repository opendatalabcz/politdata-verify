from typing import List, Dict, Any, TypeVar, Type

from openai import OpenAI
from dotenv import load_dotenv
import os

from pydantic import BaseModel

from src.milvus.search import search

load_dotenv()

ENDPOINT = "https://api.groq.com/openai/v1"
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "openai/gpt-oss-120b"
TEMPERATURE = 1
T = TypeVar("T", bound=BaseModel)

class Client:
    def __init__(self, **kwargs):
        self.client = OpenAI(api_key=API_KEY)

    def create_completions(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        model = kwargs.get("model", MODEL)
        temperature = kwargs.get("temperature", TEMPERATURE)
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content

    def get_structured_response(self, messages: List[Dict[str, Any]], schema: Type[T], **kwargs) -> str:
        model = kwargs.get("model", MODEL)
        temperature = kwargs.get("temperature", TEMPERATURE)
        response = self.client.responses.parse(
            model=model,
            input=messages,
            text_format = schema,
            temperature=temperature,
        )
        return response.output_parsed

if __name__ == "__main__":
    async def main():
        collection_name = "test_collection"
        query = "ANO 2011 zvažuje zavedení rychlejších daňových odpisů"
        context = await search(collection_name, query)
        ### FACT-CHECKING PROMPT ###
        system_prompt = """
        You are a context-STRICT fact checker.

INPUT:
1) <context> … </context> — zero or more <document> blocks, each containing:
   <year>…</year>, <party>…</party>, <page_number>…</page_number>,
   <metadata>…</metadata>, <content>…</content>
2) <claim>…</claim> — a short statement to verify.

RULES:
- Verify the claim EXCLUSIVELY using the text inside <content> of the provided documents.
- Do NOT use outside knowledge, assumptions, or the web.
- When citing evidence, use this exact inline citation format:
  [party: {party}, year: {year}, page: {page_number}]
- If the context does not provide enough information, do NOT guess.

CLASSIFICATION (choose exactly one):
- "SUPPORTED" — the claim is clearly confirmed by the context.
- "CONTRADICTED" — the claim is clearly denied or opposed by the context.
- "INSUFFICIENT" — the context does not contain enough information to decide.

OUTPUT FORMAT (JSON only, no explanation outside JSON):
{
  "verdict": "SUPPORTED" | "CONTRADICTED" | "INSUFFICIENT",
  "rationale": "brief reasoning in English (max 3 sentences, no outside knowledge)",
  "evidence": [
    {
      "quote": "short relevant quote from the content",
      "citation": "[party: {party}, year: {year}, page: {page_number}]"
    }
  ],
  "confidence": float 0.0–1.0
}

NOTES:
- Use short but precise quotes.
- If a claim contains multiple sub-claims, evaluate each and select the strictest applicable verdict (e.g., one contradictory sub-claim ⇒ CONTRADICTED).
- Produce the final answer in English.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"{context}, <query>{query}</query>",
            },
        ]
        client = Client()
        answer = client.create_completions(messages, model="gpt-5")
        print("=== ANSWER ===")
        print(answer)
    import asyncio
    asyncio.run(main())
