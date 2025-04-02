"""openapi.py

The OpenAPI document, openapi.json, specifies the format that a valid request
to the Campus API must conform to.

The OpenAPIValidator class is used to validate a Flask request against the
OpenAPI document.
"""
import json
from dataclasses import dataclass
from typing import Any, Literal

from flask import Request as FlaskRequest

from .base import ValidationResult, Validator

# Enums
class _Status:
    SUCCESS = "success"
    ERROR = "error"


# Error classes
@dataclass(frozen=True)
class InvalidRequestPath(ValidationResult):
    status: Literal["success", "error"] = _Status.ERROR
    data: str = "Invalid request path"


@dataclass(frozen=True)
class InvalidRequestMethod(ValidationResult):
    status: Literal["success", "error"] = _Status.ERROR
    data: str = "Invalid request method"


@dataclass(frozen=True)
class InvalidRequestBody(ValidationResult):
    status: Literal["success", "error"] = _Status.ERROR
    data: dict = {}


class OpenAPIValidator(Validator[FlaskRequest]):
    """Validate Flask requests against OpenAPI schema."""

    def __init__(
            self,
            *,
            path: str | None = None,
            json_str: str | None = None,
        ):
        """Initialize with OpenAPI schema.

        Keyword Args:
            path: Path to openapi.json file.
        """
        if path:
            with open(path) as f:
                self.schema = json.load(f)
        elif json_str:
            self.schema = json.loads(json_str)
        else:
            raise ValueError("No schema provided")

    def _get_path_schema(self, path: str, method: str) -> dict[str, Any]:
        """Get schema for path and method."""
        path_spec = self.schema['paths'][path]

        return path_spec[method.lower()]

    def _get_server_url(self, url: str, server_schemas: list[dict]) -> str | None:
        """Return a matching server URL for the request.
        Returns None if not found.
        """
        for server in server_schemas:
            if url.startswith(server["url"]):
                return server["url"]
        return None

    def _get_request_schema(self, method: str, request_schema: dict) -> dict | None:
        """Return a matching request schema for the request.
        Returns None if not found.
        """
        return request_schema["paths"].get(method.lower(), None)

    def _validate_request_body(self, request_body: dict, request_schema: dict) -> dict:
        """Validate request body against schema.
        Returns a dict representing validation outcome.

        Dict keys:
        - "missing": list of missing properties
        - "invalid": list of invalid properties
        """
        raise NotImplementedError

    def validate(self, value: FlaskRequest) -> ValidationResult:
        """Validate request against OpenAPI schema.

        Args:
            request: Flask request object

        Returns:
            ValidationResult with validation status and data/errors
        """
        url = self._get_server_url(value.root_url, self.schema["servers"])
        if not url:
            return InvalidRequestPath("error", "Incorrect request path prefix")
        # Prefix is not specified in OpenAPI path, strip it
        path = value.root_url[len(url):]

        schema = self._get_request_schema(value.method, self.schema["paths"][path])
        if not schema:
            return InvalidRequestMethod("error", "Invalid request method")

        errors = self._validate_request_body(value.get_json(), schema["requestBody"])
        if errors:
            return InvalidRequestBody("error", errors)

        return ValidationResult("success", None)
