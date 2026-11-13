# super-umbrella

`super-umbrella` is an early-stage Python scaffold for an AI-assisted intelligence application. It separates the application engine from model providers so a real model integration can be added without coupling the core to a vendor.

> **Status:** foundation only. The included demo provider is deterministic and does not use a language model, access the network, or provide real AI analysis.

## Quick start

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -e .
python -m super_umbrella "Summarize the purpose of this project"
```

The demo command returns a clearly labeled placeholder response. It is there to verify the app wiring, not to simulate model intelligence.

## Project layout

```text
src/super_umbrella/   Core service, provider contract, and CLI
 tests/               Standard-library unit tests
 docs/                Architecture and implementation roadmap
```

## Development

Run the test suite with:

```bash
python -m unittest discover -s tests -v
```

See [Architecture](docs/architecture.md) and [Roadmap](docs/roadmap.md) before adding a model provider. Never commit credentials or sensitive user data. See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance.

## License

This project is licensed under the MIT License; see [LICENSE](LICENSE).
