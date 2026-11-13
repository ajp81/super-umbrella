"""Core orchestration contracts; provider implementations live separately."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ServiceResponse:
    """A response from a configured provider."""

    text: str


class Provider(Protocol):
    """Minimal interface implemented by a model or test provider."""

    def generate(self, prompt: str) -> str:
        """Generate a response for prompt."""
        ...


class IntelligenceEngine:
    """Validate input and delegate generation to an injected provider."""

    def __init__(self, provider: Provider) -> None:
        self._provider = provider

    def ask(self, prompt: str) -> ServiceResponse:
        cleaned = prompt.strip()
        if not cleaned:
            raise ValueError("Prompt must not be empty.")
        return ServiceResponse(text=self._provider.generate(cleaned))
