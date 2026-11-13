"""Configuration for runtime provider selection and operational guardrails."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    provider: str = "demo"
    openai_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None
    ollama_model: str = "llama3.1"
    ollama_base_url: str = "http://localhost:11434"
    max_prompt_chars: int = 100_000
    health_timeout_seconds: float = 2.0

    def __post_init__(self) -> None:
        if self.max_prompt_chars <= 0:
            raise ValueError("max_prompt_chars must be a positive integer.")
        if self.health_timeout_seconds <= 0:
            raise ValueError("health_timeout_seconds must be positive.")

    @classmethod
    def from_env(cls) -> "Settings":
        try:
            max_prompt_chars = int(os.getenv("SUPER_UMBRELLA_MAX_PROMPT_CHARS", "100000"))
            health_timeout_seconds = float(
                os.getenv("SUPER_UMBRELLA_HEALTH_TIMEOUT_SECONDS", "2")
            )
        except ValueError as exc:
            raise ValueError("Invalid operational limit in environment configuration.") from exc

        return cls(
            provider=os.getenv("SUPER_UMBRELLA_PROVIDER", "demo").lower(),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            max_prompt_chars=max_prompt_chars,
            health_timeout_seconds=health_timeout_seconds,
        )
