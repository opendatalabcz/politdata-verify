import os
import requests
from dotenv import load_dotenv

load_dotenv()
JINA_API_KEY = os.getenv("JINA_API_KEY")

def jina_ai_to_markdown(url: str) -> str:

    url = f"https://r.jina.ai/{url}"
    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "X-Retain-Images": "none"
    }

    response = requests.get(url, headers=headers)

    print(response.text)
    return response.text

def create_chunks_from_markdown(md_content: str):
    pass

if __name__ == "__main__":
    url = "https://www.starostove.cz/files/dobry-program-starostove.pdf"
    # url_auto = "https://36beec02.delivery.rocketcdn.me/wp-content/uploads/Volebni_program-2025_MOTORISTE-SOBE.pdf"
    # url_ano = "https://www.anobudelip.cz/file/edee/ke-stazeni/volebni-program-2025.pdf"
    # md_content = jina_ai_to_markdown(url_ano)
    # print(md_content)