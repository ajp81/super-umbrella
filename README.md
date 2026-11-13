# super-umbrella

`super-umbrella` is a Python-based foundation for an AI-assisted intelligence application. The project is intentionally provider-agnostic: the execution layer is separated from model/provider implementations so real model integrations can be added without coupling core logic to a single vendor.

This repository is in Phase 2 of the project plan. The foundation is in place, and the project now supports environment-based provider configuration with optional real model backends.

## Status

- Phase: 2 / provider integration
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

If you do not configure a real provider, the app continues to use the built-in demo provider.

## Provider configuration

The repository reads provider settings from environment variables. Copy `.env.example` and update it for your target backend.

Supported values:

- `SUPER_UMBRELLA_PROVIDER=demo`
- `SUPER_UMBRELLA_PROVIDER=openai`
- `SUPER_UMBRELLA_PROVIDER=ollama`

Environment keys:

```bash
SUPER_UMBRELLA_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o-mini

# or
SUPER_UMBRELLA_PROVIDER=ollama
OLLAMA_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434
```

## Project structure

```text
super-umbrella/
├── LICENSE
├── CONTRIBUTING.md
├── README.md
├── pyproject.toml
├── .gitignore
├── .env.example
├── src/
│   └── super_umbrella/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── engine.py
│       └── providers.py
├── tests/
│   └── test_engine.py
├── docs/
│   ├── architecture.md
│   └── roadmap.md
└── .venv/
```

## Development

```bash
python -m unittest discover -s tests -v
```

See [docs/architecture.md](docs/architecture.md) and [docs/roadmap.md](docs/roadmap.md) for the technical plan.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
