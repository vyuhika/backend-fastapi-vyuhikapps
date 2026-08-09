from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from app.schemas.json_validator_schema import (
    JSONValidationResponse,
    JSONValidationRequest,
    ValidationErrorDetail,
)

class JSONValidatorService:

    async def validate_json(self, request: JSONValidationRequest,) -> JSONValidationResponse:
        schema = request.schema
        data = request.data

        try:
            Draft202012Validator.check_schema(schema)

        except SchemaError as exc:
            return JSONValidationResponse(
                valid= False,
                errors= [
                    ValidationErrorDetail(
                        path="schema",
                        message=f"Invalid JSON Schema: {exc.message}",
                    )
                ],
            )

        validator = Draft202012Validator(schema)

        validation_erros = sorted(
            validator.iter_errors(data),
            key= lambda error: list(error.path),
        )

        errors: list[ValidationErrorDetail] = []

        for error in validation_erros:
            path = self._build_error_path(
                error.path
            )

            errors.append(
                ValidationErrorDetail(
                    path= path,
                    message= error.message,
                )
            )

        return JSONValidationResponse(
            valid= len(errors) == 0,
            errors= errors,
        )

    @staticmethod
    def _build_error_path(path: Any) -> str:
        if not path:
            return "$"

        result = "$"

        for part in path:
            if isinstance(part, int):
                result += f"[{part}]"

            else:
                result += f".{part}"

        return result