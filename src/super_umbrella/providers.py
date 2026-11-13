"""Provider implementations and settings-based provider selection."""

from __future__ import annotations

import json
import urllib.request
from urllib.parse import urlparse

from .config import Settings


class DemoProvider:
    """A deterministic placeholder provider for local validation and wire-up checks."""

    def generate(self, prompt: str) -> str:
        return (
            "Demo provider mode: no production AI backend is configured. "
            f"Received {len(prompt)} characters of prompt input."
        )

    def health_check(self, timeout: float = 2.0) -> bool:
        return True


class OpenAIProvider:
    """Thin OpenAI-backed provider adapter."""

    def __init__(self, model: str, api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set when using the OpenAI provider.")

        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise RuntimeError(
                "The OpenAI provider requires the optional 'llm' dependencies. "
                "Install with: pip install -e '.[llm]'"
            ) from exc

        client = OpenAI(api_key=self.api_key)
        completion = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        message = completion.choices[0].message
        content = message.content if isinstance(message.content, str) else "".join(
            part for part in message.content if isinstance(part, str)
        )
        return content.strip() or "OpenAI provider returned an empty response."

    def health_check(self, timeout: float = 2.0) -> bool:
        """Check local configuration only; avoids a paid/network API request."""
        if not self.api_key or not self.api_key.strip():
            raise ValueError("OPENAI_API_KEY must be set when using the OpenAI provider.")
        if not self.model or not self.model.strip():
            raise ValueError("An OpenAI model must be configured.")
        return True


class OllamaProvider:
    """Provider adapter for a local Ollama server."""

    def __init__(self, model: str, base_url: str = "http://localhost:11434") -> None:
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("OLLAMA_BASE_URL must be an absolute HTTP(S) URL.")
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode(
            "utf-8"
        )
        request = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")

        data = json.loads(body)
        result = data.get("response", "")
        if not isinstance(result, str):
            raise ValueError("Unexpected response payload from Ollama provider.")
        return result.strip() or "Ollama provider returned an empty response."

    def health_check(self, timeout: float = 2.0) -> bool:
        """Check whether the configured Ollama server responds to its tags endpoint."""
        request = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
        with urllib.request.urlopen(request, timeout=timeout):
            return True


def get_provider_for_settings(settings: Settings):
    """Instantiate the provider configured for the current runtime settings."""
    provider_name = (settings.provider or "demo").lower()

    if provider_name == "demo":
        return DemoProvider()
    if provider_name == "openai":
        return OpenAIProvider(model=settings.openai_model, api_key=settings.openai_api_key)
    if provider_name == "ollama":
        return OllamaProvider(model=settings.ollama_model, base_url=settings.ollama_base_url)

    raise ValueError(
        f"Unsupported provider '{settings.provider}'. Supported values: demo, openai, ollama."
    )


__all__ = [
    "DemoProvider",
    "OpenAIProvider",
    "OllamaProvider",
    "get_provider_for_settings",
]
