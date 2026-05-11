"""
Module for extracting and analyzing political statements from text data.
"""
import asyncio
import logging
import time
from typing import Literal

from app.src.clients.openai_client import Client
from app.src.political_statements.models import Speakers, Speaker, SpeakerStatements, ExtractionResult
from app.src.political_statements.utils import resolve_party

MODEL = "gpt-4o"
MODES = Literal["sync", "async"]
logger = logging.getLogger(__name__)

SPEAKER_PROMPT = """
Read the entire text and identify all speakers who make political statements.
For each speaker provide their name, surname and party ONLY if explicitly mentioned in the text.
Do not guess the party from outside knowledge.
"""

STATEMENT_PROMPT = """
You are extracting political statements made by {speaker_name} from the text below.

STRICT RULES:
1. Extract ONLY statements clearly attributable to {speaker_name}.
2. One statement = one atomic political claim (a unique policy proposal, criticism, or stated goal).
3. Make each statement self-contained — resolve pronouns (he, it, this law) to their actual nouns using the full context.
4. HOW TO SPLIT (Crucial):
   - Keep cause and effect together in ONE statement (e.g., "We oppose this tax because it hurts families").
   - Separate distinct proposals into DIFFERENT statements (e.g., "We want to lower taxes" AND "We will build more schools").
5. Skip procedural remarks ("Thank you", "I have a point"), greetings, and meta-commentary.
6. Return statements in the Czech language.

EXAMPLES:
Text: "Reforma superdávky je podle nás špatně nastavená, protože lidé neví, kolik dostanou. Záleží nám na tom, aby zranitelní lidé měli ochranu."
-> Statement 1: "Reforma sociálních dávek (superdávka) je špatně nastavená, protože lidé nemají jistotu ohledně výše podpory."
-> Statement 2: "Zranitelní lidé musí mít dostatečnou sociální ochranu."

Text:
{text}
"""


async def find_speakers(text: str) -> Speakers:
    client = Client()
    messages = [
        {"role": "system", "content": SPEAKER_PROMPT},
        {"role": "user", "content": text},
    ]
    return await client.get_structured_response_async(
        messages,
        schema=Speakers,
        model=MODEL,
        temperature=0.0,
    )


async def extract_statements_for_speaker(text: str, speaker_name: str) -> SpeakerStatements:
    client = Client()
    messages = [
        {"role": "system", "content": STATEMENT_PROMPT.format(
            speaker_name=speaker_name, text=text
        )},
        {"role": "user", "content": f"Extract statements for {speaker_name}"},
    ]
    return await client.get_structured_response_async(
        messages,
        schema=SpeakerStatements,
        model=MODEL,
        temperature=0.0,
    )


async def extract_political_statements(text: str, mode: MODES, speakers_list: list[Speaker] | None = None) -> ExtractionResult:
    """Extract political statements from the given text."""
    start = time.perf_counter()
    speakers = await find_speakers(text)
    logger.info(f"find_speakers: {time.perf_counter() - start:.2f}s")

    logger.info(f"[STATEMENTS_EXTRACTION] Starting statements extraction for {len(speakers.speakers)} speakers in {mode} mode.")
    extraction_start = time.perf_counter()
    if mode == "sync":
        results = []
        for speaker in speakers.speakers:
            result = await extract_statements_for_speaker(text, speaker.name)
            results.append(result)
    else:
        tasks = [extract_statements_for_speaker(text, speaker.name) for speaker in speakers.speakers]
        results = await asyncio.gather(*tasks)

    logger.info(f"[STATEMENTS_EXTRACTION] Finished statements extraction in: {time.perf_counter() - extraction_start:.2f}s")
    speaker_results = []
    for speaker, stmt_result in zip(speakers.speakers, results):
        party, resolution = resolve_party(
            speaker=speaker,
            provided_speakers=speakers_list,
        )

        # discard statements the model assigned low confidence to
        filtered = [s for s in stmt_result.statements if s.confidence >= 0.7]
        if filtered and resolution != "unresolvable":
            speaker_results.append(SpeakerStatements(
                speaker=speaker,
                statements=filtered
            ))
    return ExtractionResult(speakers=speaker_results)


if __name__ == "__main__":
    # Example usage
    async def main():
        text = """
        Místopředseda PSP Patrik Nacher: Děkuji. S přednostním právem předsedkyně Olga Richterová. Máte slovo, paní předsedkyně.
Poslankyně Olga Richterová: Děkuji. Už velice krátce. Děkuji za tu reakci. Ano, právě proto nás zajímají ta data, proto se na to ptáme, protože dnes nikdo neví, kolik lidí vypadne z toho rozumného systému podpory, což samozřejmě je špatně. Proto jsme i kritizovali, že nebyla k dispozici ta kalkulačka při přechodu na superdávku. To, co se děje dnes, lidé jsou zafixovaní v tom starém systému, od října 2025 běží přechodné období, a pokud se jim změnila situace, tak dnes pan ministr potvrdil, že ta cesta je zažádat si o mimořádnou okamžitou pomoc, takzvanou mopku. OK, není to systémové řešení, je to nějaké hašení požáru, ale chápeme, že je tady to nezbytně nutné technické přechodné období. Upozorňujeme jako Piráti na to, že tím dnešním hlasováním se toto přechodné období toho zmrazení pro zranitelné lidi prodlouží, proto trváme na tom, že musí být skutečně kontrolováno, že jsou ty mopky lidem nabízeny, že skutečně budou vědět o tom, jakou možnost mají. Záleží nám na tom, aby prostě bylo jasné, že ten náš dnešní souhlas - to, že jsme nedali veto - není žádný bianko šek, ale že trváme na tom, aby pro ty zranitelné domácnosti byl skutečně citlivý a důsledný přístup, který jim nabídne tu mopku, protože nemají trpět technickým selháním státu, že se dál prodlužuje toto moratorium na výpočet státní podpory. (Hluk v sále.) Závěrem...
Místopředseda PSP Patrik Nacher: Pardon, já jenom...
Tady je hluk, tak vás poprosím opět o klid. Já dneska nebudu říkat žádné příměry, ale poprosím, aby paní předsedkyně mohla pokračovat. Ještě tady ta hladina hluku je příliš vysoká. Kolegyně, kolegové, zleva i zprava... Děkuju.
Poslankyně Olga Richterová: Děkuji pěkně, pane předsedající. Závěrem, o co nám jde? Aby lidé, kteří jsou práceschopní, skutečně pracovali, ale aby ti, kteří jsou zranitelní, měli svou ochranu. Chceme jasná data o dopadech superdávky, chceme úpravu definice zranitelnosti, spravedlivé nastavení pro pěstouny, zohlednění reálných, ne vysněných nájmů a motivaci pracovat legálně i v insolvenci. To jsou věci, které vidíme jako nutné ke změně v té reformě superdávky. Současně jsme za Piráty nabídli řešení. Předložili jsme prorodinný balíček. Pro více než 90 procent českých rodin by znamenal snížení daní, nabízíme tu pravidelnou valorizaci rodičovského příspěvku připravenou k odsouhlasení, je to hotová legislativa. Důsledně se zde budeme ptát, jak tato vláda přispívá ke zlepšování života českých rodin, včetně mladých rodin, protože prostě hrozí, že zejména na ty mladé rodiny bude vláda Andreje Babiše zapomínat. Děkuji.
Místopředseda PSP Patrik Nacher: Děkuji, paní předsedkyně. V této chvíli nikdo není přihlášen. Dívám se do sálu... (Ministr Juchelka přistupuje k řečnickému pultu.) Jako závěrečné slovo, nebo... (Ministr juchelka: Ne, jako reakci.) Jako reakce. (Ministr Juchelka: Ano, s přednostním právem.) Ano, s přednostním právem, pane ministře.
        Ministr práce a sociálních věcí ČR Aleš Juchelka: Samozřejmě, že tady tato vládní koalice, která sedí za mnou, myslí na mladé rodiny, myslí na bydlení, myslí na podporu a bude v rámci prorodinného balíčku naopak dělat něco jako je DSSP 2 i pro rodinný přídavek na dítě, například i na věcný systém různých podpor pro ty sociálně slabé. Opravdu jsme vláda, která pracuje pro občany České republiky, včetně mladých rodin i včetně zranitelných skupin i včetně ohrožených dětí, a máme to v našem programovém prohlášení vlády, které je skvělé. Děkuji.
        """
        start = time.perf_counter()
        mode = "sync"
        result = await extract_political_statements(text, mode)
        end = time.perf_counter()
        print(result.model_dump_json(indent=2, ensure_ascii=False))
        print(f"Extraction took {end - start:.2f} seconds")
        num_speakers = len(result.speakers)
        total_statements = sum(len(speaker_group.statements) for speaker_group in result.speakers)

        print(f"Number of speakers: {num_speakers}")
        print(f"Total statements: {total_statements}")
    asyncio.run(main())

