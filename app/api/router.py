from fastapi import APIRouter

from app.api.v1.json_validator import router as json_validator_router

api_router = APIRouter()


api_router.include_router(
    json_validator_router
)