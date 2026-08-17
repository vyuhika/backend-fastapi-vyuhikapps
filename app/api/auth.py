from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Cookie
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db
from app.core.security import (
    REFRESH_COOKIE_NAME,
    clear_auth_cookies,
    set_auth_cookies,
)
from app.models.refresh_token import RefreshToken
from app.schemas.auth import AuthProviderRequest, LoginRequest, SignupRequest
from app.services.oauth import normalize_oauth_profile, oauth
from app.services.tokens import (
    create_login_tokens,
    hash_refresh_token,
)
from app.services.users import (
    authenticate_password_user,
    create_password_user,
    get_or_create_oauth_user,
)

router = APIRouter()

SUPPORTED_PROVIDERS = {"google", "microsoft", "apple"}


@router.post("/signup")
def signup(
    payload: SignupRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user = create_password_user(
        db=db,
        email=payload.email,
        password=payload.password,
        name=payload.name,
    )

    access_token, refresh_token = create_login_tokens(db, user)
    set_auth_cookies(response, access_token, refresh_token)

    return {"message": "Signup successful"}


@router.post("/login")
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user = authenticate_password_user(db, payload.email, payload.password)

    access_token, refresh_token = create_login_tokens(db, user)
    set_auth_cookies(response, access_token, refresh_token)

    return {"message": "Login successful"}


@router.post("/oauth/start")
def oauth_start(payload: AuthProviderRequest):
    provider = payload.provider.lower()

    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    return {
        "login_url": f"/auth/oauth/{provider}/login",
    }


@router.get("/oauth/{provider}/login")
async def oauth_login(provider: str, request: Request):
    provider = provider.lower()

    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    client = oauth.create_client(provider)

    if not client:
        raise HTTPException(
            status_code=500,
            detail=f"{provider} OAuth is not configured",
        )

    redirect_uri = str(request.url_for("oauth_callback", provider=provider))

    return await client.authorize_redirect(request, redirect_uri)


@router.get("/oauth/{provider}/callback", name="oauth_callback")
async def oauth_callback(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
):
    provider = provider.lower()

    try:
        client = oauth.create_client(provider)

        if not client:
            raise RuntimeError(f"{provider} OAuth is not configured")

        token = await client.authorize_access_token(request)

        profile = normalize_oauth_profile(provider, token)

        user = get_or_create_oauth_user(db=db, **profile)

        access_token, refresh_token = create_login_tokens(db, user)

        response = RedirectResponse(settings.FRONTEND_AUTH_SUCCESS_URL)
        set_auth_cookies(response, access_token, refresh_token)

        return response

    except Exception:
        return RedirectResponse(settings.FRONTEND_AUTH_ERROR_URL)


@router.post("/refresh")
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    token_hash = hash_refresh_token(refresh_token)

    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
        )
        .first()
    )

    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = db_token.user

    db_token.revoked = True
    db.commit()

    access_token, new_refresh_token = create_login_tokens(db, user)
    set_auth_cookies(response, access_token, new_refresh_token)

    return {"message": "Token refreshed"}


@router.post("/logout")
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
    db: Session = Depends(get_db),
):
    if refresh_token:
        token_hash = hash_refresh_token(refresh_token)

        db_token = (
            db.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_hash)
            .first()
        )

        if db_token:
            db_token.revoked = True
            db.commit()

    clear_auth_cookies(response)

    return {"message": "Logged out"}