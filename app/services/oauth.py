from authlib.integrations.starlette_client import OAuth

from app.core.config import settings

oauth = OAuth()


if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


if settings.MICROSOFT_CLIENT_ID and settings.MICROSOFT_CLIENT_SECRET:
    oauth.register(
        name="microsoft",
        client_id=settings.MICROSOFT_CLIENT_ID,
        client_secret=settings.MICROSOFT_CLIENT_SECRET,
        server_metadata_url=(
            f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT}"
            "/v2.0/.well-known/openid-configuration"
        ),
        client_kwargs={
            "scope": "openid email profile",
        },
        claims_options={
            "iss": {
                "essential": False,
            }
        },
    )


if settings.APPLE_CLIENT_ID and settings.APPLE_CLIENT_SECRET:
    oauth.register(
        name="apple",
        client_id=settings.APPLE_CLIENT_ID,
        client_secret=settings.APPLE_CLIENT_SECRET,
        server_metadata_url="https://appleid.apple.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email name"},
    )


def normalize_oauth_profile(provider: str, token: dict) -> dict:
    userinfo = token.get("userinfo")

    if not userinfo:
        userinfo = token.get("id_token_claims")

    if not userinfo:
        raise ValueError("OAuth provider did not return user info")

    email = (
        userinfo.get("email")
        or userinfo.get("preferred_username")
        or userinfo.get("upn")
    )

    if not email:
        raise ValueError("OAuth provider did not return email")

    return {
        "provider": provider,
        "provider_subject": userinfo["sub"],
        "email": email,
        "name": userinfo.get("name"),
        "avatar_url": userinfo.get("picture"),
    }