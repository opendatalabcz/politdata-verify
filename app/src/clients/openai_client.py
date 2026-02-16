from typing import List, Dict, Any, TypeVar, Type

from openai import OpenAI
from dotenv import load_dotenv
import os

from pydantic import BaseModel

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
            messages=messages, # type: ignore
            temperature=temperature,
        )
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
        return response.choices[0].message.parsed
