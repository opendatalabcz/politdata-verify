import os
import json
from src.clients.openai_client import Client
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class GlobalContext(BaseModel):
    party_name: str
    year: int
    ideology: str = Field(description="Max 15 words summary")
    main_priorities: str = Field(description="Comma separated top 5 themes")

    def to_context_string(self) -> str:
        """
        Formats the global context into a string to prepend to chunks.
        Example: "CONTEXT: Party: ANO 2011 (2025) | Ideology: Populist centrist... | Focus: Pensions, Tax..."
        """
        return f"CONTEXT: Party: {self.party_name} ({self.year}) | Ideology: {self.ideology} | Priorities: {self.main_priorities}\n--- CHUNK ---\n"

class ContextEnricher:
    def __init__(self):
        self.client = Client()

    def extract_context(self, full_text: str) -> GlobalContext:
        """
        Uses LLM to extract global context from the full document text.
        :param full_text: The complete text of the document.
        :return: GlobalContext object with extracted information.
        """
        model = "gpt-4o-mini"
        messages = [
            {"role": "system", "content": "You are a political analyst. Extract global context JSON."},
            {"role": "user", "content": full_text},
        ]
        response = self.client.get_structured_response(messages, schema=GlobalContext, model=model)
        return response