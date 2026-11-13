"""CLI for the super-umbrella scaffold."""

import argparse

from .engine import IntelligenceEngine
from .providers import DemoProvider


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="super-umbrella",
        description="Provider-agnostic AI application scaffold",
    )
    parser.add_argument("prompt", help="Prompt to send to the configured provider")
    args = parser.parse_args()

    engine = IntelligenceEngine(provider=DemoProvider())
    print(engine.ask(args.prompt).text)


if __name__ == "__main__":
    main()
