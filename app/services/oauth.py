import httpx
from fastapi import HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from jose import jwt

from app.core.config import settings



def verify_google_token(token: str) -> dict:
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code = 500,
            detail = "Google login is not configured",
        )

    try:
        payload = google_id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

    except Exception:
        return HTTPException(
            status_code = 401,
            detail = "Invalid Google Token",
        )

    if not payload.get("email"):
        raise HTTPException(
            status_code = 400,
            detail = "Google account has no email",
        )

    return {
        "provider": "google",
        "provider_subject": payload["sub"],
        "email": payload["email"],
        "name": payload.get("name"),
        "avatar_url": payload.get("picture"),        
    }

async def verify_apple_token(token: str) -> dict:
    if not settings.APPLE_CLIENT_ID:
        raise HTTPException(
            status_code = 500,
            detail = "Apple login is not configured!",
        )

    try:
        headers = jwt.get_unverified_header(token)

        async with httpx.AsyncClient() as client:
            response = await client.get("https://appleid.apple.com/auth/keys")
            response.raise_for_status()
            jwks = response.json()

        key = next(
            item for item in jwks["keys"] if item["kid"] == headers["kid"]
        )

        payload = jwt.decode(
            token, 
            key,
            algorithms = ["RS256"],
            audience = settings.APPLE_CLIENT_ID,
            issuer = "https://appleid.apple.com",
        )

    except Exception:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid apple token!",
        )

    email = payload.get("email")

    if not email:
        raise HTTPException(
            status_code = 400,
            detail = "Apple token has no email. Store email during Apple first login!"
        )

    return {
        "provider": "apple",
        "provider_subject": payload["sub"],
        "email": email,
        "name": None,
        "avatar_url": None,
    }

async def verify_microsoft_token(token: str) -> dict:
    if not settings.MICROSOFT_CLIENT_ID:
        raise HTTPException(
            status_code = 500,
            detail = "Microsoft login is not configured"
        )

    tenant = settings.MICROSOFT_TENANT

    try:
        metadata_url = (
            f"https://login.microsoftonline.com/{tenant}/v2.0/"
            ".well-known/openid-configuration"
        )

        async with httpx.AsyncClient() as client:
            metadata_response = await client.get(metadata_url)
            metadata_response.raise_for_status()
            metadata = metadata_response.json()

            jwks_response = await client.get(metadata["jwks_uri"])
            jwks_response.raise_for_status()
            jwks = jwks_response.json()

        headers = jwt.get_unverified_header(token)

        key = next(
            item for item in jwks["keys"] if item["kid"] == headers["kid"]
        )

        payload = jwt.decode(
            token,
            key,
            algorithms = ["RS256"],
            audience = settings.MICROSOFT_CLIENT_ID,
            options = {"verify_iss": False},
        )
    except Exception:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid Microsoft token"
        )

    issuer = payload.get("iss", "")

    if "login.microsoftonline.com" not in issuer:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid Microsoft issuer"
        )

    email = (
        payload.get("email")
        or payload.get("preferred_username")
        or payload.get("upn")
    )

    if not email:
        raise HTTPException(
            status_code = 400,
            detail = "Microsoft account has no email"
        )

    return {
        "provider": "microsoft",
        "provider_subject": payload["sub"],
        "email": email,
        "name": payload.get("name"),
        "avatar_url": None,
    }