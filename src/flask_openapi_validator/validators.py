"""validators.py

Module for custom validators, as specified in
https://swagger.io/docs/specification/v3_0/data-models/data-types/#strings
"""
from .base import ValidationResult, ValidationCallback


def email(value: str) -> ValidationResult:
    """Validate an email address and return a result."""
    raise NotImplementedError


VALIDATORS = [email]

def get_validator(format: str) -> ValidationCallback:
    """Return a validator for the given format."""
    if format == "email":
        return email
    raise ValueError