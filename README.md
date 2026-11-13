# super-umbrella

`super-umbrella` is a Python-based foundation for an AI-assisted intelligence application. The project is intentionally provider-agnostic: the execution layer is separated from model/provider implementations so real model integrations can be added without coupling core logic to a single vendor.

This repository is in Phase 1 of the project plan. The goal of this phase is to establish a clean package structure, a provider contract, a minimal CLI, and a testable core workflow.

## Status

- Phase: 1 / foundation
- Runtime: Python 3.11+
- Model integrations: none yet
- Default behavior: demo provider only

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m super_umbrella "Summarize the purpose of this project"
```

## Project structure

```text
super-umbrella/
├── LICENSE
├── CONTRIBUTING.md
├── README.md
├── pyproject.toml
├── .gitignore
├── src/
│   └── super_umbrella/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── engine.py
│       └── providers.py
├── tests/
│   └── test_engine.py
├── docs/
│   ├── architecture.md
│   └── roadmap.md
└── .venv/
```

## Why this structure

- `engine.py` contains the orchestration and validation logic.
- `providers.py` defines a local demo provider and leaves room for future OpenAI, Azure, Ollama, or custom providers.
- `cli.py` exposes a minimal command-line interface.
- `tests/` verifies the core behavior without an external dependency.
- `docs/` captures architecture decisions and roadmap plans.

## Development

```bash
python -m unittest discover -s tests -v
```

See [docs/architecture.md](docs/architecture.md) and [docs/roadmap.md](docs/roadmap.md) for the technical plan.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
