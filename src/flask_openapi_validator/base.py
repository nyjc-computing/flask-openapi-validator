from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Literal, TypeVar

T = TypeVar('T')


@dataclass(frozen=True)
class ValidationResult:
    """Result of a validation operation"""
    status: Literal["success", "error"]
    data: Any


class Validator(Generic[T], ABC):
    @abstractmethod
    def validate(self, value: T) -> ValidationResult:
        pass
