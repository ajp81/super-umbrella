"""CLI for the super-umbrella scaffold."""

import argparse

from .config import Settings
from .engine import IntelligenceEngine
from .providers import get_provider_for_settings


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="super-umbrella",
        description="Provider-agnostic AI application scaffold",
    )
    parser.add_argument("prompt", help="Prompt to send to the configured provider")
    args = parser.parse_args()

    settings = Settings.from_env()
    provider = get_provider_for_settings(settings)
    engine = IntelligenceEngine(provider=provider)
    print(engine.ask(args.prompt).text)


if __name__ == "__main__":
    main()
