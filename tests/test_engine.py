import unittest

from super_umbrella.engine import IntelligenceEngine


class RecordingProvider:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return "test response"


class IntelligenceEngineTests(unittest.TestCase):
    def test_strips_prompt_and_returns_provider_response(self) -> None:
        provider = RecordingProvider()
        response = IntelligenceEngine(provider).ask("  hello  ")
        self.assertEqual(provider.prompts, ["hello"])
        self.assertEqual(response.text, "test response")

    def test_rejects_empty_prompt_without_calling_provider(self) -> None:
        provider = RecordingProvider()
        with self.assertRaises(ValueError):
            IntelligenceEngine(provider).ask(" \n ")
        self.assertEqual(provider.prompts, [])


if __name__ == "__main__":
    unittest.main()
