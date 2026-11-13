"""Service layer for the super-umbrella application."""

from __future__ import annotations

from .config import Settings
from .engine import IntelligenceEngine
from .models import PromptRequest, ServiceResult
from .providers import get_provider_for_settings


class IntelligenceService:
    """Facade wrapping provider selection, validation, and result shaping."""

    def __init__(self, provider=None, settings: Settings | None = None) -> None:
        self._settings = settings or Settings.from_env()
        self._provider = provider or get_provider_for_settings(self._settings)
        self._engine = IntelligenceEngine(self._provider)

    @property
    def settings(self) -> Settings:
        return self._settings

    def ask(self, prompt: str, *, metadata: dict[str, str] | None = None) -> ServiceResult:
        request = PromptRequest(text=prompt, metadata=metadata or {})
        response = self._engine.ask(request.text)
        return ServiceResult(
            text=response.text,
            provider=self._settings.provider,
            request=request,
        )
