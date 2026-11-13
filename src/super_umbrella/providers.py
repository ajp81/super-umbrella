"""Demo provider implementation used during early project scaffolding."""


class DemoProvider:
    """A deterministic placeholder provider for local validation and wire-up checks."""

    def generate(self, prompt: str) -> str:
        return (
            "Demo provider mode: no production AI backend is configured. "
            f"Received {len(prompt)} characters of prompt input."
        )
