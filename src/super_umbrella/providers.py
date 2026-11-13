"""Local demonstration provider; deliberately does not pretend to be AI."""


class DemoProvider:
    """Return a placeholder response without network or model access."""

    def generate(self, prompt: str) -> str:
        return (
            "Demo mode: no AI model is configured. "
            f"Received {len(prompt)} characters of input."
        )
