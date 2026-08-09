from fastapi import APIRouter, status

from app.schemas.json_validator_schema import (
    JSONValidationRequest,
    JSONValidationResponse,
)
from app.services.json_validator_services import JSONValidatorService

router = APIRouter(
    prefix= "/json-validator",
    tags= ["JSON VALIDATOR"],
)

service = JSONValidatorService()

@router.post("/validate", response_model= JSONValidationResponse, status_code= status.HTTP_200_OK)
async def validate_json(request: JSONValidationRequest) -> JSONValidationResponse:
    return await service.validate_json(
        request
    )