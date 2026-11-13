"""Command-line entry point."""

import argparse

from .engine import IntelligenceEngine
from .providers import DemoProvider


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="super-umbrella",
        description="AI-assisted intelligence app scaffold (demo provider only).",
    )
    parser.add_argument("prompt", help="Text to pass to the configured provider")
    args = parser.parse_args()

    engine = IntelligenceEngine(provider=DemoProvider())
    print(engine.ask(args.prompt).text)


if __name__ == "__main__":
    main()
