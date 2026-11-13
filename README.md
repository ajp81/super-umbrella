# super-umbrella

`super-umbrella` is a Python-based foundation for an AI-assisted intelligence application. The project is intentionally provider-agnostic: the execution layer is separated from model/provider implementations.

## Status

- Phase: 2.4 / operational readiness groundwork
- Runtime: Python 3.11+
- Default behavior: demo provider
- Optional integrations: OpenAI and local Ollama

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[llm]"
cp .env.example .env
python -m super_umbrella "Summarize the purpose of this project"
```

## Service layer

The `IntelligenceService` facade wraps provider selection, validation, health checks, and structured result shaping. It emits standard-library log records with a correlation ID. Prompt text, metadata values, and credentials are deliberately excluded from logs.

```python
from super_umbrella import IntelligenceService

service = IntelligenceService()
result = service.ask("Explain the project purpose")
print(result.text, result.request_id, result.latency_ms)
print(service.health_check())
```

`health_check()` checks demo readiness, OpenAI local configuration (without making a paid API call), or Ollama connectivity. Its response is a dictionary containing the provider name and a boolean `healthy` value; failures include a non-sensitive error class name.

## Operational settings

- `SUPER_UMBRELLA_MAX_PROMPT_CHARS` (default: `100000`) caps prompt size.
- `SUPER_UMBRELLA_HEALTH_TIMEOUT_SECONDS` (default: `2`) bounds Ollama health-check time.
- `SUPER_UMBRELLA_PROVIDER` selects `demo`, `openai`, or `ollama`.

Configure OpenAI with `OPENAI_API_KEY`; configure Ollama with `OLLAMA_BASE_URL`.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
