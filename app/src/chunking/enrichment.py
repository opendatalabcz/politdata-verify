"""
document-level context enrichment: extracts party/ideology summary prepended to every chunk
so embeddings carry document-level context (HyDE-style enrichment).
"""
from app.src.clients.openai_client import Client
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class GlobalContext(BaseModel):
    party_name: str
    year: int
    ideology: str = Field(description="Max 15 words summary")
    main_priorities: str = Field(description="Comma separated top 5 themes")

    def to_context_string(self) -> str:
        """format context as a prefix string prepended to each chunk before embedding."""
        return f"CONTEXT: Party: {self.party_name} ({self.year}) | Ideology: {self.ideology} | Priorities: {self.main_priorities}\n--- CHUNK ---\n"

class ContextEnricher:
    def __init__(self):
        self.client = Client()

    def extract_context(self, full_text: str) -> GlobalContext:
        """use LLM to extract party name, year, ideology and top priorities from full document text."""
        model = "gpt-4o-mini"
        messages = [
            {"role": "system", "content": "You are a political analyst. Extract global context JSON."},
            {"role": "user", "content": full_text},
        ]
        response = self.client.get_structured_response(messages, schema=GlobalContext, model=model)
        return response