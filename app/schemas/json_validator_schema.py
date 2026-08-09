from typing import Any

from pydantic import BaseModel, Field


class JSONValidationRequest(BaseModel):
    schema: dict[str, Any] = Field(
        ...,
        description= "JSON Schema used to validate the data.",
    )

    data: Any = Field(
        ...,
        description= "Arbitary JSON data to validate.",
    )

class ValidationErrorDetail(BaseModel):
    path: str
    message: str

class JSONValidationResponse(BaseModel):
    valid: bool
    errors: list[ValidationErrorDetail]