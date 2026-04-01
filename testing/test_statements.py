import json
import pytest
import os
from app.src.political_statements.statements_extraction import extract_political_statements

TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "test_cases.json")


def load_test_cases():
    if not os.path.exists(TEST_DATA_PATH):
        pytest.skip(f"Test data file not found at {TEST_DATA_PATH}")

    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)
    for i, case in enumerate(cases):
        case["_id"] = f"tc_{i + 1:03d}"
    return cases


@pytest.mark.asyncio
@pytest.mark.parametrize("case", load_test_cases(), ids=lambda c: c["_id"])
async def test_extraction_from_json(case):

    text = case["text"]
    expected = case["expected"]

    result = await extract_political_statements(text, speakers_list=None)

    extracted_full_names = [f"{s.speaker.name} {s.speaker.surname}" for s in result.speakers]

    assert len(result.speakers) == expected["speaker_count"], \
        f"Očekáváno {expected['speaker_count']} řečníků, ale nalezeno {len(result.speakers)}: {extracted_full_names}"

    speaker_dict = {f"{s.speaker.name} {s.speaker.surname}": s.statements for s in result.speakers}

    for exp_speaker in expected["speakers"]:
        full_name = f"{exp_speaker['name']} {exp_speaker['surname']}"

        assert full_name in speaker_dict, \
            f"Očekávaný řečník '{full_name}' nebyl vůbec nalezen v extrakci."

        statements = speaker_dict[full_name]
        num_extracted_statements = len(statements)

        min_stmts = exp_speaker["min_statements"]
        max_stmts = exp_speaker["max_statements"]

        assert min_stmts <= num_extracted_statements <= max_stmts, \
            f"Řečník '{full_name}': Očekáváno {min_stmts} až {max_stmts} výroků, ale extrahováno jich bylo {num_extracted_statements}.\n" \
            f"Extrahované výroky:\n" + "\n".join([f"- {s.statement}" for s in statements])