"""Structured request and response model definitions."""

from dataclasses import dataclass, field


class _SafeDict(dict):
    """A dictionary that returns an empty string for missing template keys."""

    def __missing__(self, key: str) -> str:
        return ""


@dataclass(frozen=True)
class PromptRequest:
    """A normalized prompt payload."""

    text: str
    metadata: dict[str, str] = field(default_factory=dict)
    template: str | None = None

    def __post_init__(self) -> None:
        if self.text is None:
            raise ValueError("Prompt text must not be None.")

        cleaned_text = str(self.text).strip()
        if not cleaned_text:
            raise ValueError("Prompt text must not be empty.")

        object.__setattr__(self, "text", cleaned_text)

        normalized_metadata: dict[str, str] = {}
        for key, value in dict(self.metadata).items():
            normalized_metadata[str(key)] = str(value)
        object.__setattr__(self, "metadata", normalized_metadata)

        if self.template is not None:
            object.__setattr__(self, "template", str(self.template))


@dataclass(frozen=True)
class ServiceResult:
    """A structured result emitted by the service layer."""

    text: str
    provider: str
    request: PromptRequest
    template: str | None = None
    latency_ms: int | None = None
    status: str = "ok"

    def format(self) -> str:
        """Render a compact, human-readable version of the result."""
        prefix = f"[{self.provider}]"
        if self.template:
            prefix = f"{prefix} {self.template}"
        return f"{prefix}: {self.text}"
