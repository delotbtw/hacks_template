from typing import Protocol

from pydantic import BaseModel, Field


class PredictInput(BaseModel):
    """Пример входа. Замените поля под задачу хакатона."""

    text: str = Field(min_length=1)


class PredictOutput(BaseModel):
    """Пример выхода. Замените поля под задачу хакатона."""

    label: str
    score: float = Field(ge=0, le=1)


class Predictor(Protocol):
    def predict(self, data: PredictInput) -> PredictOutput: ...
