"""
Module for extracting and analyzing political statements from text data.
"""
import asyncio
import time
from typing import List, Dict

from app.src.clients.openai_client import Client
from app.src.political_statements.models import Speakers, SpeakerStatements, ExtractionResult
from app.src.political_statements.utils import resolve_party

MODEL = "gpt-4o-mini"

SPEAKER_PROMPT = """
Read the entire text and identify all speakers who make political statements.
For each speaker provide their full name and party ONLY if explicitly mentioned in the text.
Do not guess party from outside knowledge.
"""

STATEMENT_PROMPT = """
You are extracting political statements made by {speaker_name} from the text below.

RULES:
- Extract ONLY statements clearly attributable to {speaker_name}
- One statement = one atomic political claim
- Make each statement self-contained — resolve references using full context
- Skip procedural remarks, greetings, meta-commentary
- confidence: how certain you are this statement belongs to {speaker_name}
- return statements in czech language
  1.0 = speaker said it directly
  0.7 = attributed indirectly ("podle něj...", "uvedl že...")
  below 0.6 = skip it

Text:
{text}
"""

async def find_speakers(text: str) -> Speakers:
    client = Client()
    messages = [
        {"role": "system", "content": SPEAKER_PROMPT},
        {"role": "user", "content": text},
    ]
    return await client.get_structured_response_async(messages, schema=Speakers, model=MODEL)

async def extract_statements_for_speaker(text: str, speaker_name: str) -> SpeakerStatements:
    client = Client()
    messages = [
        {"role": "system", "content": STATEMENT_PROMPT.format(
            speaker_name=speaker_name, text=text
        )},
        {"role": "user", "content": f"Extract statements for {speaker_name}"},
    ]
    return await client.get_structured_response_async(messages, schema=SpeakerStatements, model=MODEL)



async def extract_political_statements(text: str, speakers_list: Speakers = None) -> ExtractionResult:
    """Extract political statements from the given text."""
    start = time.time()
    speakers = await find_speakers(text)
    print(f"find_speakers: {time.time() - start:.2f}s")
    tasks = [extract_statements_for_speaker(text, speaker.name) for speaker in speakers.speakers]
    start = time.time()
    results = await asyncio.gather(*tasks)
    print(f"extract statements: {time.time() - start:.2f}s")

    speaker_results = []
    for speaker, stmt_result in zip(speakers.speakers, results):
        party, resolution = resolve_party(
            speaker=speaker,
            provided_speakers=speakers_list,
        )

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
        result = await extract_political_statements(text)
        end = time.perf_counter()
        print(result.model_dump_json(indent=2, ensure_ascii=False))
        print(f"Extraction took {end - start:.2f} seconds")

    asyncio.run(main())

