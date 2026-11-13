# super-umbrella

`super-umbrella` is a Python-based foundation for an AI-assisted intelligence application. The project is intentionally provider-agnostic: the execution layer is separated from model/provider implementations so real model integrations can be added without coupling core logic to a single vendor.

This repository is in Phase 2.1 of the project plan. The foundation is stable, and the service layer now exposes a structured request/response model for clean application integration.

## Status

- Phase: 2.1 / service abstraction
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

The project now includes a small `IntelligenceService` facade that wraps provider selection, validation, and structured result shaping. This keeps the runtime configuration decoupled from the engine logic.

```python
from super_umbrella.service import IntelligenceService

service = IntelligenceService()
result = service.ask("Explain the project purpose")
print(result.text)
```

## Provider configuration

The repository reads provider settings from environment variables. Copy `.env.example` and update it for your target backend.

Supported values:

- `SUPER_UMBRELLA_PROVIDER=demo`
- `SUPER_UMBRELLA_PROVIDER=openai`
- `SUPER_UMBRELLA_PROVIDER=ollama`

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
