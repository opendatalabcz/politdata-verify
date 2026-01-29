"""
Module for extracting and analyzing political statements from text data.
"""
from typing import List, Dict

from app.src.clients.openai_client import Client
from app.src.political_statements.models import Statements


def extract_political_statements(text: str) -> Statements:
    """
    Extract political statements from the given text.

    Args:
        text (str): The input text from which to extract political statements.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing extracted political statements and their metadata.
    """
    # Placeholder implementation
    # In a real implementation, this function would use NLP techniques to identify and extract political statements.
    system_prompt = """
    You are an expert in political text analysis.
    Your task is to extract political statements from the provided text.
    For each statement, provide the statement text and relevant metadata such as speaker, date, and context.
    return the results in the following JSON format:
    [
        {
            "statement": "Extracted political statement text",
            "metadata": {
                "speaker": "Name of the speaker",
                "date": "Date of the statement",
                "context": "Context of the statement"
            }
        },
        ...
    ]
    """
    client = Client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]
    response = client.get_structured_response(messages, schema=Statements)
    return response


if __name__ == "__main__":
    sample_text = """
Rychlejší daňové odpisy pro firmy

Část diskuse se věnovala také problematice vysokých cen energií a dopadů na české podniky. Havlíček uvedl, že koalice zvažuje zavedení rychlejších daňových odpisů, které by firmám pomohly kompenzovat zvýšené energetické náklady. Podle něj by mohly začít platit nejdříve v roce 2027, shoda se ale musí najít na koaliční radě.

Rychlejší odpisy by podle Havlíčka pomohly tuzemským firmám zůstat konkurenceschopnými na evropském trhu. Německá vláda totiž představila plán na zavedení takzvané průmyslové ceny elektřiny, která má od ledna 2026 snížit náklady na energie pro energeticky náročné podniky.

Rychlejší odpisy by podle Havlíčka fungovaly také jako nepřímá daňová pobídka. Časový horizont, kdy by si podniky mohly odepisovat daně, by se mohl snížit i zhruba o polovinu, na konkrétních krocích se je ale podle místopředsedy ANO nejdříve nutné domluvit v koalici. 
    """
    extracted_statements = extract_political_statements(sample_text)
    print(extracted_statements)