"""Structured request and response model definitions."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PromptRequest:
    """A normalized prompt payload."""

    text: str
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", self.text.strip())
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True)
class ServiceResult:
    """A structured result emitted by the service layer."""

    text: str
    provider: str
    request: PromptRequest
