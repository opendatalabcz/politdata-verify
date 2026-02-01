import os
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyQuery
from starlette.status import HTTP_403_FORBIDDEN

API_KEY_NAME = "x-api-key"
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)

ADMIN_API_TOKEN = os.getenv("ADMIN_API_TOKEN")

async def verify_api_key(api_key: str = Security(api_key_query)):
    if api_key == ADMIN_API_TOKEN:
        return api_key
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )