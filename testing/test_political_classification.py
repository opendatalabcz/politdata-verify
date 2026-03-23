import pytest
import json
import asyncio

from app.src.clients.openai_client import Client
from app.src.milvus.milvus_interface import MilvusInterface
from app.src.political_statements.statement_classification import classify_statement

with open('test_scenarios.json', 'r', encoding='utf-8') as f:
    scenarios_data = json.load(f)

test_cases = []
for party, statements in scenarios_data.items():
    for case in statements:
        test_cases.append((party, case['statement'], case['expected']))


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    "party, statement, expected_verdict",
    test_cases,
    ids=[f"{party}".lower().replace(" ", "_").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ý","y").replace("č","c").replace("ř","r").replace("š","s").replace("ž","z").replace("ě","e").replace("ň","n").replace("ď","d").replace("ť","t") for party, _, _ in test_cases]
)
async def test_political_statement_classification(party, statement, expected_verdict,
                                                  collection_name="test_collection"):

    interface = MilvusInterface()
    client = Client()

    result = await classify_statement(
        query=statement,
        collection_name=collection_name,
        client=client,
        party=party,
        year=2025,
        interface=interface
    )

    assert result.verdict == expected_verdict, (
        f"Verdict: {result.verdict} | "
        f"Confidence: {result.confidence} | "
        f"Rationale: {result.rationale}"
    )
    assert result.confidence >= 0.0
    if result.verdict in ["SUPPORTED", "CONTRADICTED"]:
        assert len(result.evidence) > 0