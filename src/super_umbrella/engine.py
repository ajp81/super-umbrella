"""Core orchestration for the super-umbrella intelligence engine."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ServiceResponse:
    """A normalized response returned by a provider."""

    text: str


class Provider(Protocol):
    """The minimal contract expected from a model or service provider."""

    def generate(self, prompt: str) -> str:
        """Return a textual response for the given prompt."""
        ...


class IntelligenceEngine:
    """Validate prompts and delegate execution to a provider."""

    def __init__(self, provider: Provider) -> None:
        self._provider = provider

    def ask(self, prompt: str) -> ServiceResponse:
        cleaned = prompt.strip()
        if not cleaned:
            raise ValueError("Prompt must not be empty.")
        return ServiceResponse(text=self._provider.generate(cleaned))
