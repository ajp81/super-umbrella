"""Service layer for the super-umbrella application."""

from __future__ import annotations

import string
import time

from .config import Settings
from .engine import IntelligenceEngine
from .models import PromptRequest, ServiceResult, _SafeDict
from .providers import get_provider_for_settings


class ServiceError(RuntimeError):
    """Base exception for service-layer failures."""


class PromptValidationError(ServiceError, ValueError):
    """Raised when a prompt is empty or otherwise invalid."""


class TemplateValidationError(ServiceError, ValueError):
    """Raised when a template is malformed or variables are missing."""


class ProviderError(ServiceError):
    """Raised when a provider fails during request execution."""


class IntelligenceService:
    """Facade wrapping provider selection, validation, and result shaping."""

    def __init__(self, provider=None, settings: Settings | None = None) -> None:
        self._settings = settings or Settings.from_env()
        self._provider = provider or get_provider_for_settings(self._settings)
        self._engine = IntelligenceEngine(self._provider)

    @property
    def settings(self) -> Settings:
        return self._settings

    @staticmethod
    def _normalize_metadata(metadata: dict[str, str] | None) -> dict[str, str]:
        if metadata is None:
            return {}
        if not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary of string keys and values.")

        normalized: dict[str, str] = {}
        for key, value in metadata.items():
            key_text = str(key)
            value_text = str(value)
            if len(key_text) > 128:
                raise ValueError("metadata keys must be 128 characters or shorter.")
            if len(value_text) > 2048:
                raise ValueError("metadata values must be 2048 characters or shorter.")
            normalized[key_text] = value_text
        return normalized

    @staticmethod
    def _render_template(prompt: str, template: str | None, variables: dict[str, str] | None) -> str:
        if template is None:
            return prompt
        if not isinstance(template, str):
            raise TypeError("template must be a string or None.")
        if variables is None:
            variables = {}
        if not isinstance(variables, dict):
            raise TypeError("variables must be a dictionary of string keys and values.")

        formatter = string.Formatter()
        placeholders = {
            field_name
            for _, field_name, _, _ in formatter.parse(template)
            if field_name is not None
        }
        missing = sorted(field for field in placeholders if field not in variables)
        if missing:
            raise TemplateValidationError(
                "Missing template variables: " + ", ".join(missing)
            )

        return template.format_map(_SafeDict(variables))

    def ask(
        self,
        prompt: str,
        *,
        metadata: dict[str, str] | None = None,
        template: str | None = None,
        variables: dict[str, str] | None = None,
    ) -> ServiceResult:
        """Ask a prompt through the configured provider and return a structured result."""
        normalized_prompt = str(prompt) if prompt is not None else ""
        if not normalized_prompt.strip():
            raise PromptValidationError("Prompt must not be empty.")

        normalized_metadata = self._normalize_metadata(metadata)
        resolved_prompt = self._render_template(normalized_prompt, template, variables)
        request = PromptRequest(
            text=resolved_prompt,
            metadata=normalized_metadata,
            template=template,
        )

        started = time.perf_counter()
        try:
            response = self._engine.ask(request.text)
        except ValueError as exc:
            raise PromptValidationError(str(exc)) from exc
        except Exception as exc:
            raise ProviderError(
                f"Provider '{self._settings.provider}' failed to generate a response."
            ) from exc

        latency_ms = max(0, int((time.perf_counter() - started) * 1000))

        return ServiceResult(
            text=response.text,
            provider=self._settings.provider,
            request=request,
            template=template,
            latency_ms=latency_ms,
            status="ok",
        )
