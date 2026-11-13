"""Configuration for runtime provider selection."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    provider: str = "demo"
    openai_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None
    ollama_model: str = "llama3.1"
    ollama_base_url: str = "http://localhost:11434"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            provider=os.getenv("SUPER_UMBRELLA_PROVIDER", "demo").lower(),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
