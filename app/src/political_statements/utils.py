import re
import zipfile
import io
from functools import lru_cache
from typing import List

import pandas as pd
import requests

from app.src.political_statements.models import Speakers, Speaker, ClassifiedStatementWithContext, ExtractionResult, \
    SpeakerStats, StatsResult

URL = "https://www.psp.cz/eknih/cdrom/opendata/poslanci.zip"

POLITICAL_PARTIES_MAPPING = {
    "ANO2011": "ANO 2011",
    "KDU-ČSL": "SPOLU",
    "ODS": "SPOLU",
    "STAN": "Starostové a nezávislí",
    "TOP09": "SPOLU",
}

def generate_stats(classified_statements: List[ClassifiedStatementWithContext], extracted_statements: ExtractionResult)\
        -> StatsResult:
    all_statements = len([statement for speaker in extracted_statements.speakers for statement in speaker.statements])
    all_speakers = len(extracted_statements.speakers)

    speakers = set()
    for speaker_statements in extracted_statements.speakers:
        speaker = speaker_statements.speaker
        speakers.add(speaker.name)

    speakers_stats = []
    for speaker in speakers:
        speaker_statements = [s for s in classified_statements if s.speaker == speaker]
        total_statements = len(speaker_statements)
        supported = [s for s in speaker_statements if s.verdict == "SUPPORTED"]
        contradicted = [s for s in speaker_statements if s.verdict == "CONTRADICTED"]
        insufficient = [s for s in speaker_statements if s.verdict == "INSUFFICIENT"]
        party = next((s.party for s in classified_statements if s.speaker == speaker), "Unknown")
        speakers_stats.append(SpeakerStats(
            speaker=speaker,
            party=party,
            total_statements=total_statements,
            supported=supported,
            contradicted=contradicted,
            insufficient=insufficient
        ))
    return StatsResult(total_speakers=all_speakers, total_statements=all_statements, speakers_stats=speakers_stats)

def debug_psp():
    r = requests.get(URL, timeout=30)
    z = zipfile.ZipFile(io.BytesIO(r.content))

    print("Files:", z.namelist())

    for filename in ["osoby.unl", "organy.unl", "zarazeni.unl"]:
        print(f"\n--- {filename} ---")
        lines = z.read(filename).decode("windows-1250").splitlines()
        for line in lines[:10]:
            print(line)


@lru_cache(maxsize=1)
def get_poslanec_lookup() -> dict[str, str]:
    r = requests.get(URL, timeout=30)
    z = zipfile.ZipFile(io.BytesIO(r.content))

    people = {}
    for line in z.read("osoby.unl").decode("windows-1250").splitlines():
        cols = line.split("|")
        if len(cols) >= 4:
            people[cols[0]] = f"{cols[2].strip()} {cols[3].strip()}"

    org_names = {}
    for line in z.read("organy.unl").decode("windows-1250").splitlines():
        cols = line.split("|")
        if len(cols) >= 5:
            name = cols[3].strip() if cols[3].strip() else cols[4].strip()
            org_names[cols[0]] = name

    lookup = {}
    for line in z.read("zarazeni.unl").decode("windows-1250").splitlines():
        cols = line.split("|")
        if len(cols) >= 5:
            p_id = cols[0]
            o_id = cols[1]
            cl_funkce = cols[2]
            do_o = cols[4].strip()

            if do_o == "" and cl_funkce == "0":
                if p_id in people and o_id in org_names:
                    full_name = people[p_id]
                    org_name = org_names[o_id]

                    # valid_parties = ["ODS", "SPD", "ANO2011", "TOP09", "STAN", "KDU-ČSL", "Piráti", "MS"]
                    #
                    # if org_name in valid_parties:
                    #     if org_name == "ANO2011": org_name = "ANO 2011"

                    lookup[full_name] = org_name

    return lookup


def get_active_politicians():
    r = requests.get(URL, timeout=30)
    z = zipfile.ZipFile(io.BytesIO(r.content))

    people = {}
    for line in z.read("osoby.unl").decode("windows-1250").splitlines():
        cols = line.split("|")
        if len(cols) >= 4:
            people[cols[0]] = f"{cols[2].strip()} {cols[3].strip()}"

    types = {}
    for line in z.read("typ_organu.unl").decode("windows-1250").splitlines():
        cols = line.split("|")
        if len(cols) >= 2:
            types[cols[0]] = cols[1].strip()

    orgs = {}
    for line in z.read("organy.unl").decode("windows-1250").splitlines():
        cols = line.split("|")
        if len(cols) >= 5:
            orgs[cols[0]] = {
                "name": cols[3].strip() if cols[3].strip() else cols[4].strip(),
                "type_id": cols[1].strip(),
                "parent_id": cols[2].strip()
            }

    active_ids = set()
    for line in z.read("zarazeni.unl").decode("windows-1250").splitlines():
        cols = line.split("|")
        if len(cols) >= 5 and cols[1] == "174" and cols[4].strip() == "":
            active_ids.add(cols[0])

    debug_data = []
    for line in z.read("zarazeni.unl").decode("windows-1250").splitlines():
        cols = line.split("|")
        p_id = cols[0]
        o_id = cols[1]
        od_o = cols[3].strip()
        do_o = cols[4].strip()

        if p_id in active_ids and do_o == "":
            p_name = people.get(p_id, "Unknown")
            org_info = orgs.get(o_id, {"name": f"Neznámý ({o_id})", "type_id": "?", "parent_id": "?"})

            debug_data.append({
                "politician_name": p_name,
                "from": od_o,
                "to": "ONGOING",
                "org_ID": org_info["parent_id"],
                "org_type": org_info["type_id"],
                "org_name": org_info["name"]
            })

    df = pd.DataFrame(debug_data)
    return df


def extract_party_from_club(club_name: str) -> str:
    return re.sub(r"Poslanecký klub\s*", "", club_name).strip()


def resolve_party(
    speaker: Speaker,
    provided_speakers: Speakers | None,
) -> tuple[str | None, str]:
    if provided_speakers and speaker.name in provided_speakers:
        speaker.party = provided_speakers[speaker.name]
        return provided_speakers[speaker.name], "provided"

    if speaker.party:
        return speaker.party, "extracted_from_text"

    df = get_active_politicians()
    full_name = f"{speaker.surname} {speaker.name}"
    match = df[(df['politician_name'] == full_name) & (df['org_type'] == "174") & (df['org_ID'] == "1")]
    print(match)

    if not match.empty:
        party = match.iloc[-1]['org_name']
        if party in POLITICAL_PARTIES_MAPPING:
            party = POLITICAL_PARTIES_MAPPING[party]
        speaker.party = party
        return party, "psp_lookup"

    return None, "unresolvable"

if __name__ == "__main__":
    # print(get_poslanec_lookup())
    speaker = Speaker(name="Jiří", surname="Pospíšil", party=None)
    print(resolve_party(speaker, None))