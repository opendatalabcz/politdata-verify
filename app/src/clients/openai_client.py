from typing import List, Dict, Any, TypeVar, Type

from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
import os

from pydantic import BaseModel

load_dotenv()

ENDPOINT = "https://api.groq.com/openai/v1"
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "openai/gpt-oss-120b"
TEMPERATURE = 1
T = TypeVar("T", bound=BaseModel)

# Global token counter
class TokenCounter:
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_tokens = 0
        self.calls = []

    def add(self, input_tokens: int, output_tokens: int, model: str = ""):
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_tokens += input_tokens + output_tokens
        self.calls.append({
            "input": input_tokens,
            "output": output_tokens,
            "total": input_tokens + output_tokens,
            "model": model
        })

    def reset(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_tokens = 0
        self.calls = []

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens,
            "num_calls": len(self.calls)
        }

token_counter = TokenCounter()

class Client:
    def __init__(self, **kwargs):
        self.client = OpenAI(api_key=API_KEY, max_retries=6, timeout=120.0)
        self.async_client = AsyncOpenAI(api_key=API_KEY, max_retries=6, timeout=120.0)

    def create_completions(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        model = kwargs.get("model", MODEL)
        temperature = kwargs.get("temperature", TEMPERATURE)
        response = self.client.chat.completions.create(
            model=model,
            messages=messages, # type: ignore
            temperature=temperature,
        )

        token_counter.add(response.usage.prompt_tokens, response.usage.completion_tokens, model)

        return response.choices[0].message.content

    async def create_completions_async(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        model = kwargs.get("model", MODEL)
        temperature = kwargs.get("temperature", TEMPERATURE)
        response = await self.async_client.chat.completions.create(
            model=model,
            messages=messages, # type: ignore
            temperature=temperature,
        )

        token_counter.add(response.usage.prompt_tokens, response.usage.completion_tokens, model)

        return response.choices[0].message.content

    def get_structured_response(self, messages: List[Dict[str, Any]], schema: Type[T], **kwargs) -> T:
        model = kwargs.get("model", MODEL)
        temperature = kwargs.get("temperature", TEMPERATURE)
        response = self.client.beta.chat.completions.parse(
            messages=messages,  # type: ignore
            model=model,
            temperature=temperature,
            response_format=schema
        )

        token_counter.add(response.usage.prompt_tokens, response.usage.completion_tokens, model)

        return response.choices[0].message.parsed

    async def get_structured_response_async(self, messages: List[Dict[str, Any]], schema: Type[T], **kwargs) -> T:
        model = kwargs.get("model", MODEL)
        temperature = kwargs.get("temperature", TEMPERATURE)
        response = await self.async_client.beta.chat.completions.parse(
            messages=messages,  # type: ignore
            model=model,
            temperature=temperature,
            response_format=schema
        )

        token_counter.add(response.usage.prompt_tokens, response.usage.completion_tokens, model)

        return response.choices[0].message.parsed
