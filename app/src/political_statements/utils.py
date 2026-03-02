import re
import zipfile
import io
from functools import lru_cache
import requests

from app.src.political_statements.models import Speakers, Speaker

URL = "https://www.psp.cz/eknih/cdrom/opendata/poslanci.zip"

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

    people: dict[str, str] = {}
    for line in z.read("osoby.unl").decode("windows-1250").splitlines():
        cols = line.split("|")
        if len(cols) >= 4:
            id = cols[0]
            surname = cols[2].strip()
            name = cols[3].strip()
            people[id] = f"{surname} {name}"

    organs: dict[str, str] = {}
    for line in z.read("organy.unl").decode("windows-1250").splitlines():
        cols = line.split("|")
        if len(cols) >= 5:
            id_organ = cols[0]
            title = cols[4].strip()
            if "Poslanecký klub" in title:
                organs[id_organ] = title

    lookup: dict[str, str] = {}
    for line in z.read("zarazeni.unl").decode("windows-1250").splitlines():
        cols = line.split("|")
        if len(cols) >= 5:
            id = cols[0]
            id_organ = cols[1]
            date_to = cols[4].strip()
            if date_to == "" and id in people and id_organ in organs:
                lookup[people[id]] = organs[id_organ]

    return lookup

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

    lookup = get_poslanec_lookup()
    if speaker.name in lookup:
        party = extract_party_from_club(lookup[speaker.name])
        speaker.party = party
        return party, "psp_lookup"

    return None, "unresolvable"

if __name__ == "__main__":
    print(get_poslanec_lookup())
    debug_psp()