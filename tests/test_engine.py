import unittest
from unittest.mock import patch

from super_umbrella.config import Settings
from super_umbrella.engine import IntelligenceEngine
from super_umbrella.models import PromptRequest
from super_umbrella.providers import DemoProvider, OllamaProvider, OpenAIProvider, get_provider_for_settings
from super_umbrella.service import (
    IntelligenceService,
    PromptValidationError,
    ProviderError,
    TemplateValidationError,
)


class RecordingProvider:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return "test-response"


class IntelligenceEngineTests(unittest.TestCase):
    def test_ask_strips_prompt_and_returns_provider_result(self) -> None:
        provider = RecordingProvider()
        response = IntelligenceEngine(provider).ask("  hello world  ")
        self.assertEqual(provider.prompts, ["hello world"])
        self.assertEqual(response.text, "test-response")

    def test_ask_rejects_empty_prompt(self) -> None:
        provider = RecordingProvider()
        with self.assertRaises(ValueError):
            IntelligenceEngine(provider).ask("   \n  ")
        self.assertEqual(provider.prompts, [])

    def test_defaults_to_demo_provider(self) -> None:
        self.assertIsInstance(get_provider_for_settings(Settings.from_env()), DemoProvider)

    def test_service_builds_structured_result_and_request_id(self) -> None:
        service = IntelligenceService(provider=RecordingProvider(), settings=Settings(provider="demo"))
        result = service.ask("  hello  ", metadata={"source": "unit-test"}, request_id="trace-1")
        self.assertEqual(result.request, PromptRequest(text="hello", metadata={"source": "unit-test"}))
        self.assertEqual(result.text, "test-response")
        self.assertEqual(result.provider, "demo")
        self.assertEqual(result.request_id, "trace-1")
        self.assertGreaterEqual(result.latency_ms, 0)

    def test_service_rejects_empty_prompt(self) -> None:
        service = IntelligenceService(provider=RecordingProvider(), settings=Settings(provider="demo"))
        with self.assertRaises(PromptValidationError):
            service.ask("   ")

    def test_service_rejects_oversized_prompt_without_provider_call(self) -> None:
        provider = RecordingProvider()
        service = IntelligenceService(
            provider=provider, settings=Settings(provider="demo", max_prompt_chars=4)
        )
        with self.assertRaises(PromptValidationError):
            service.ask("12345")
        self.assertEqual(provider.prompts, [])

    def test_service_rejects_malformed_and_missing_template_variables(self) -> None:
        service = IntelligenceService(provider=RecordingProvider(), settings=Settings(provider="demo"))
        with self.assertRaises(TemplateValidationError):
            service.ask("ignored", template="Hello {name", variables={})
        with self.assertRaises(TemplateValidationError):
            service.ask("ignored", template="Hello {name}", variables={})

    def test_service_wraps_provider_errors(self) -> None:
        class FailingProvider:
            def generate(self, prompt: str) -> str:
                raise RuntimeError("backend exploded")

        service = IntelligenceService(provider=FailingProvider(), settings=Settings(provider="demo"))
        with self.assertRaises(ProviderError):
            service.ask("hello", request_id="request-test")

    def test_health_checks_demo_and_openai_configuration(self) -> None:
        self.assertTrue(IntelligenceService(settings=Settings(provider="demo")).health_check()["healthy"])
        no_key_service = IntelligenceService(
            provider=OpenAIProvider("model", None), settings=Settings(provider="openai")
        )
        self.assertFalse(no_key_service.health_check()["healthy"])
        configured_service = IntelligenceService(
            provider=OpenAIProvider("model", "not-a-real-key"), settings=Settings(provider="openai")
        )
        self.assertTrue(configured_service.health_check()["healthy"])

    def test_ollama_health_check_uses_configured_timeout(self) -> None:
        provider = OllamaProvider("model", "http://localhost:11434")
        service = IntelligenceService(
            provider=provider, settings=Settings(provider="ollama", health_timeout_seconds=0.5)
        )
        with patch("urllib.request.urlopen") as urlopen:
            self.assertTrue(service.health_check()["healthy"])
            self.assertEqual(urlopen.call_args.kwargs["timeout"], 0.5)

    def test_service_supports_templates_and_formatting(self) -> None:
        service = IntelligenceService(provider=RecordingProvider(), settings=Settings(provider="demo"))
        result = service.ask(
            "hello", metadata={"source": "unit-test"}, template="Say hello to {audience}",
            variables={"audience": "team"},
        )
        self.assertEqual(result.request.text, "Say hello to team")
        self.assertEqual(result.request.template, "Say hello to {audience}")
        self.assertEqual(result.format(), "[demo] Say hello to {audience}: test-response")


if __name__ == "__main__":
    unittest.main()
