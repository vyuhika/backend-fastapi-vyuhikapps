from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    app_name: str = "Vyuhika Apps"
    app_env: str = "DEV"
    app_version: str = "1.0.0"

    DATABASE_URL: str = "sqlite:///./auth.db"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    SESSION_SECRET_KEY: str

    FRONTEND_ORIGIN: str = "http://localhost:3000"
    FRONTEND_AUTH_SUCCESS_URL: str
    FRONTEND_AUTH_ERROR_URL: str

    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    MICROSOFT_CLIENT_ID: str | None = None
    MICROSOFT_CLIENT_SECRET: str | None = None
    MICROSOFT_TENANT: str = "common"

    APPLE_CLIENT_ID: str | None = None
    APPLE_CLIENT_SECRET: str | None = None

    class Config:
        env_file = ".env"



settings = Settings()