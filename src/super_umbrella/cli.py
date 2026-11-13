"""Provider implementations and provider resolution logic."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from .config import Settings


class DemoProvider:
    """A deterministic placeholder provider for local validation and wire-up checks."""

    def generate(self, prompt: str) -> str:
        return (
            "Demo provider mode: no production AI backend is configured. "
            f"Received {len(prompt)} characters of prompt input."
        )


class OpenAIProvider:
    """Optional provider that calls OpenAI using environment configuration."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set. Configure the environment or choose a different provider.")

        try:
            import openai  # type: ignore
        except ImportError as exc:  # pragma: no cover - import error path
            raise RuntimeError("OpenAI support requires: pip install \"super-umbrella[llm]\"") from exc

        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        if hasattr(response, "output_text") and response.output_text:
            return response.output_text

        if hasattr(response, "output"):
            fragments: list[str] = []
            for item in response.output:
                if hasattr(item, "content"):
                    for block in item.content:
                        if hasattr(block, "text"):
                            fragments.append(block.text)
            if fragments:
                return "\n".join(fragments)

        raise RuntimeError("OpenAI response format was not recognized.")


class OllamaProvider:
    """Optional local provider using the Ollama HTTP API."""

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1")

    def generate(self, prompt: str) -> str:
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:  # pragma: no cover - network-dependent path
            raise RuntimeError(
                "Could not reach Ollama. Ensure the local service is running and OLLAMA_BASE_URL is correct."
            ) from exc

        if "response" in body:
            return body["response"]
        raise RuntimeError("Ollama response format was not recognized.")


def get_provider_for_settings(settings: Settings):
    """Return a provider instance determined by runtime settings."""
    provider_name = settings.provider
    if provider_name == "demo":
        return DemoProvider()
    if provider_name == "openai":
        return OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_model)
    if provider_name == "ollama":
        return OllamaProvider(base_url=settings.ollama_base_url, model=settings.ollama_model)
    raise ValueError(f"Unsupported provider: {provider_name}")
