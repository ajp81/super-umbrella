"""Service layer for the super-umbrella application."""

from __future__ import annotations

import logging
import string
import time
import uuid

from .config import Settings
from .engine import IntelligenceEngine
from .models import PromptRequest, ServiceResult
from .providers import get_provider_for_settings

logger = logging.getLogger(__name__)


class ServiceError(RuntimeError):
    """Base exception for service-level failures."""


class PromptValidationError(ServiceError, ValueError):
    """Raised when a prompt is missing or invalid."""


class TemplateValidationError(ServiceError, ValueError):
    """Raised when a template is malformed or contains missing variables."""


class ProviderError(ServiceError):
    """Raised when a provider fails during request execution."""


class IntelligenceService:
    """Facade wrapping provider selection, validation, and result shaping."""

    def __init__(self, provider=None, settings: Settings | None = None) -> None:
        self._settings = settings or Settings.from_env()
        self._provider = provider if provider is not None else get_provider_for_settings(self._settings)
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
    def _render_template(
        prompt: str,
        template: str | None,
        variables: dict[str, str] | None,
    ) -> str:
        if template is None:
            return prompt

        if not isinstance(template, str):
            raise TypeError("template must be a string or None.")

        if variables is None:
            variables = {}

        if not isinstance(variables, dict):
            raise TypeError("variables must be a dictionary of string keys and values.")

        formatter = string.Formatter()
        try:
            placeholders = {
                field_name
                for _, field_name, _, _ in formatter.parse(template)
                if field_name is not None
            }
        except ValueError as exc:
            raise TemplateValidationError("Template has invalid format syntax.") from exc

        missing = sorted(field for field in placeholders if field not in variables)
        if missing:
            raise TemplateValidationError("Missing template variables: " + ", ".join(missing))

        try:
            return template.format_map({str(k): str(v) for k, v in variables.items()})
        except (KeyError, IndexError, ValueError, AttributeError) as exc:
            raise TemplateValidationError("Template could not be rendered.") from exc

    def health_check(self) -> dict[str, str | bool]:
        """Check provider readiness without generating a model response."""
        provider_name = self._settings.provider
        check = getattr(self._provider, "health_check", None)
        try:
            healthy = bool(check(timeout=self._settings.health_timeout_seconds)) if check else True
        except Exception as exc:
            logger.warning(
                "Provider health check failed",
                extra={"provider": provider_name, "error_type": type(exc).__name__},
            )
            return {"provider": provider_name, "healthy": False, "error": type(exc).__name__}

        return {"provider": provider_name, "healthy": healthy}

    def ask(
        self,
        prompt: str,
        *,
        metadata: dict[str, str] | None = None,
        template: str | None = None,
        variables: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> ServiceResult:
        """Ask a prompt, logging operational metadata without logging prompt content."""
        request_id = request_id or str(uuid.uuid4())
        normalized_prompt = str(prompt) if prompt is not None else ""
        if not normalized_prompt.strip():
            logger.info(
                "Prompt rejected",
                extra={"request_id": request_id, "provider": self._settings.provider,
                       "reason": "empty_prompt"},
            )
            raise PromptValidationError("Prompt must not be empty.")

        normalized_metadata = self._normalize_metadata(metadata)
        resolved_prompt = self._render_template(normalized_prompt, template, variables)
        if len(resolved_prompt) > self._settings.max_prompt_chars:
            raise PromptValidationError(
                f"Prompt exceeds the configured limit of {self._settings.max_prompt_chars} characters."
            )

        request = PromptRequest(
            text=resolved_prompt,
            metadata=normalized_metadata,
            template=template,
        )

        started = time.perf_counter()
        logger.info(
            "Provider request started",
            extra={"request_id": request_id, "provider": self._settings.provider,
                   "prompt_chars": len(request.text), "metadata_fields": len(request.metadata)},
        )
        try:
            response = self._engine.ask(request.text)
        except ValueError as exc:
            logger.warning(
                "Provider request rejected",
                extra={"request_id": request_id, "provider": self._settings.provider,
                       "error_type": type(exc).__name__},
            )
            raise PromptValidationError(str(exc)) from exc
        except Exception as exc:
            logger.error(
                "Provider request failed",
                extra={"request_id": request_id, "provider": self._settings.provider,
                       "error_type": type(exc).__name__},
            )
            raise ProviderError(
                f"Provider '{self._settings.provider}' failed to generate a response. "
                f"Request ID: {request_id}"
            ) from exc

        latency_ms = max(0, int((time.perf_counter() - started) * 1000))
        logger.info(
            "Provider request completed",
            extra={"request_id": request_id, "provider": self._settings.provider,
                   "latency_ms": latency_ms, "status": "ok"},
        )

        return ServiceResult(
            text=response.text,
            provider=self._settings.provider,
            request=request,
            template=template,
            latency_ms=latency_ms,
            status="ok",
            request_id=request_id,
        )
