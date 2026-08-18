from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api import auth, users
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import user, user_identity, refresh_token
from app.api.router import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title= settings.app_name,
    version= settings.app_version,
    description= "Apps for vyuhika platform.",
    docs_url= None,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    same_site=settings.COOKIE_SAMESITE,
    https_only=settings.COOKIE_SECURE,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix= "/api/v1", tags=["v1"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])


# Server Health Check Endpoint
@app.get('/health', tags=["Health"])
async def health_status_check():
    return {
        'status': 'ONLINE',
        'environment': settings.app_env,
        'errors': {
            'msg': '',
        },
    }

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Vyuhika API Docs",
        swagger_favicon_url="/static/favicon.ico"
    )


if __name__ == "__main__":

    import uvicorn
    
    uvicorn.run(app)
