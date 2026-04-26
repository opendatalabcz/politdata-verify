import re
import zipfile
import io
from functools import lru_cache
from typing import List

import pandas as pd
import requests

from typing import List
from app.src.political_statements.models import Speaker, ClassifiedStatementWithContext, ExtractionResult, \
    SpeakerStats, StatsResult

URL = "https://www.psp.cz/eknih/cdrom/opendata/poslanci.zip"

POLITICAL_PARTIES_MAPPING = {
    "ANO2011": "ANO 2011",
    "KDU-ČSL": "KDU-ČSL",
    "Piráti": "Piráti",
    "SPD": "SPD",
    "ODS": "ODS",
    "STAN": "Starostové a nezávislí",
    "TOP09": "TOP 09",
    "MS": "Motoristé sobě"
}

def generate_stats(classified_statements: List[ClassifiedStatementWithContext], extracted_statements: ExtractionResult)\
        -> StatsResult:
    all_statements = len([statement for speaker in extracted_statements.speakers for statement in speaker.statements])
    all_speakers = len(extracted_statements.speakers)

    speaker_objects = {
        f"{ss.speaker.name} {ss.speaker.surname}": ss.speaker
        for ss in extracted_statements.speakers
    }

    speakers_stats = []
    for full_name, speaker_obj in speaker_objects.items():
        speaker_stmts = [s for s in classified_statements
                         if f"{s.speaker.name} {s.speaker.surname}" == full_name]
        speakers_stats.append(SpeakerStats(
            speaker=speaker_obj,
            total_statements=len(speaker_stmts),
            supported=[s for s in speaker_stmts if s.verdict == "SUPPORTED"],
            contradicted=[s for s in speaker_stmts if s.verdict == "CONTRADICTED"],
            insufficient=[s for s in speaker_stmts if s.verdict == "INSUFFICIENT"],
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
                "id_osoba": p_id,
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
    provided_speakers: List[Speaker] | None,
) -> tuple[str | None, str]:
    print(f"{speaker.name} {speaker.surname} list: {provided_speakers}")
    if provided_speakers:
        match = next(
            (s for s in provided_speakers if s.name == speaker.name and s.surname == speaker.surname),
            None
        )
        if match and match.party:
            speaker.party = match.party
            return match.party, "provided"

    df = get_active_politicians()
    full_name = f"{speaker.name} {speaker.surname}"
    match = df[(df['politician_name'] == full_name) & (df['org_type'] == "174") & (df['org_ID'] == "1")]
    print(match)

    if not match.empty:
        id_osoba = match.iloc[-1]['id_osoba']
        speaker.photo_url = f"https://www.psp.cz/eknih/cdrom/2025ps/eknih/2025ps/poslanci/i{id_osoba}.jpg"

        if not speaker.party:
            party = match.iloc[-1]['org_name']
            if party in POLITICAL_PARTIES_MAPPING:
                party = POLITICAL_PARTIES_MAPPING[party]
            speaker.party = party
            return party, "psp_lookup"

    if speaker.party:
        return speaker.party, "extracted_from_text"

    return None, "unresolvable"

if __name__ == "__main__":
    # print(get_poslanec_lookup())
    speaker = Speaker(name="Petr", surname="Macinka", party=None)
    print(resolve_party(speaker, None))