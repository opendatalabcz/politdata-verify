import logging
import uuid

from dotenv import load_dotenv
load_dotenv()  # must run before any module reads os.getenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.src.api.jobs import router
from app.src.api.auth import verify_api_key
from app.src.api.admin_auth import ADMIN_PASSWORD, create_admin_token, verify_admin_token
from fastapi.responses import JSONResponse

from app.src.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
app = FastAPI(title="Political RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1/jobs", tags=["jobs"])

class LoginRequest(BaseModel):
    password: str

@app.post("/api/v1/auth/login")
async def admin_login(body: LoginRequest):
    if not ADMIN_PASSWORD or body.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Nesprávné heslo.")
    return {"token": create_admin_token()}

@app.get("/health")
async def health_check():
    logger.info("Health check")
    return {"status": "running"}

@app.get("/api/v1/collections", dependencies=[Depends(verify_api_key)])
async def list_collections():
    from app.src.milvus.milvus_interface import MilvusInterface
    interface = MilvusInterface()
    stats = await interface.list_collections_with_stats()
    return JSONResponse(content={"collections": stats})

@app.get("/api/v1/speakers", dependencies=[Depends(verify_api_key)])
async def list_speakers():
    import asyncio
    from app.src.political_statements.utils import get_active_politicians, POLITICAL_PARTIES_MAPPING
    df = await asyncio.to_thread(get_active_politicians)
    clubs = df[(df['org_type'] == "174") & (df['org_ID'] == "1")][['politician_name', 'org_name']].drop_duplicates('politician_name')
    speakers = []
    for _, row in clubs.iterrows():
        party = row['org_name']
        if party in POLITICAL_PARTIES_MAPPING:
            party = POLITICAL_PARTIES_MAPPING[party]
        speakers.append({"name": row['politician_name'], "party": party})
    speakers.sort(key=lambda s: s['name'])
    return JSONResponse(content={"speakers": speakers})

@app.delete("/api/v1/collections/{collection_name}/parties/{party}", dependencies=[Depends(verify_admin_token)])
async def delete_party(collection_name: str, party: str):
    from app.src.milvus.milvus_interface import MilvusInterface
    interface = MilvusInterface()
    deleted = await interface.delete_chunks_by_party(collection_name=collection_name, party_name=party)
    logger.info(f"[DELETE_PARTY] Collection: {collection_name}, Party: {party}, Deleted: {deleted}")
    return JSONResponse(content={"deleted_chunks": deleted})

@app.delete("/api/v1/collections/{collection_name}", dependencies=[Depends(verify_admin_token)])
async def delete_collection(collection_name: str):
    from app.src.milvus.milvus_interface import MilvusInterface
    interface = MilvusInterface()
    await interface.drop_collection(collection_name)
    logger.info(f"[DELETE_COLLECTION] Collection: {collection_name}")
    return JSONResponse(content={"deleted": collection_name})