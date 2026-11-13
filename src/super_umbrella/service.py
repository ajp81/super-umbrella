"""Service layer for the super-umbrella application."""

from __future__ import annotations

import time

from .config import Settings
from .engine import IntelligenceEngine
from .models import PromptRequest, ServiceResult, _SafeDict
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

    def ask(
        self,
        prompt: str,
        *,
        metadata: dict[str, str] | None = None,
        template: str | None = None,
        variables: dict[str, str] | None = None,
    ) -> ServiceResult:
        """Ask a prompt through the configured provider and return a structured result."""
        resolved_prompt = prompt
        if template is not None:
            resolved_prompt = template.format_map(_SafeDict(variables or {}))

        request = PromptRequest(text=resolved_prompt, metadata=metadata or {}, template=template)

        started = time.perf_counter()
        response = self._engine.ask(request.text)
        latency_ms = max(0, int((time.perf_counter() - started) * 1000))

        return ServiceResult(
            text=response.text,
            provider=self._settings.provider,
            request=request,
            template=template,
            latency_ms=latency_ms,
            status="ok",
        )
