"""
main pipeline
"""
import asyncio
import logging
import time
from typing import Literal

from app.src.clients.openai_client import Client
from app.src.milvus.milvus_interface import MilvusInterface
from app.src.political_statements.models import Speaker, StatsResult
from app.src.political_statements.statement_classification import classify_statement, classify_with_context
from app.src.political_statements.statements_extraction import extract_political_statements
from app.src.political_statements.utils import generate_stats
logger = logging.getLogger(__name__)
semaphore = asyncio.Semaphore(5)
MODES = Literal["sync", "async"]

async def verify_political_statements(text: str, mode: MODES, speakers_list: list[Speaker] | None = None,
                                          collection_name: str = "test_collection",
                                          year: int = 2025) -> StatsResult:
    """
    Placeholder function for verifying political statements job.
    """
    # 1. Extract statements from the text
    # 2. Classify each statement using the classify_statement function
    # 3. Return the results in a structured format
    start_time = time.perf_counter()
    extracted_statements = await extract_political_statements(text, mode, speakers_list)
    end_time = time.perf_counter()
    logger.info(f"[EXTRACTION] Extracted statements in {end_time - start_time:.2f} seconds.")
    logger.info(f"[EXTRACTION] Extracted statements for {len(extracted_statements.speakers)} speakers.")
    # For each extracted statement, classify it and store the results
    client = Client()
    interface = MilvusInterface()

    if mode == "sync":
        classifications = []
        all_statements = sum([len(speaker_statements.statements) for speaker_statements in extracted_statements.speakers])
        logger.info(f"[CLASSIFICATION] Starting classification of {all_statements} statements.")
        start_time = time.perf_counter()
        for speaker_statements in extracted_statements.speakers:
            if not speaker_statements.speaker.party:
                logger.warning (f"[CLASSIFICATION] Skipping speaker {speaker_statements.speaker.name} due to missing party affiliation.")
                continue
            for statement in speaker_statements.statements:
                classification = await classify_with_context(
                    client=client,
                    speaker=speaker_statements.speaker,
                    statement=statement.statement,
                    semaphore=semaphore,
                    collection_name=collection_name,
                    milvus_interface=interface,
                    year=year
                )
                classifications.append(classification)
        end_time = time.perf_counter()
        logger.info(f"[CLASSIFICATION] Completed classification in {end_time - start_time:.2f} seconds.")

    else:
        tasks = []
        for speaker_statements in extracted_statements.speakers:
            if not speaker_statements.speaker.party:
                logger.warning (f"[CLASSIFICATION] Skipping speaker {speaker_statements.speaker.name} due to missing party affiliation.")
                continue
            for statement in speaker_statements.statements:
                tasks.append(classify_with_context(
                    client=client,
                    speaker=speaker_statements.speaker,
                    statement=statement.statement,
                    semaphore=semaphore,
                    collection_name=collection_name,
                    milvus_interface=interface,
                    year=year
                ))
        logger.info(f"[CLASSIFICATION] Starting classification of {len(tasks)} statements.")
        start_time = time.perf_counter()
        classifications = await asyncio.gather(*tasks)
        end_time = time.perf_counter()
        logger.info(f"[CLASSIFICATION] Completed classification in {end_time - start_time:.2f} seconds.")
    stats = generate_stats(classifications, extracted_statements)
    stats.pretty_print()
    return stats


if __name__ == "__main__":
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
        result = await verify_political_statements(text)
        end = time.perf_counter()
        print(result.model_dump_json(indent=2, ensure_ascii=False))
        print(f"Extraction took {end - start:.2f} seconds")


    asyncio.run(main())
