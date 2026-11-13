"""CLI for the super-umbrella scaffold."""

import argparse

from .service import IntelligenceService


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="super-umbrella",
        description="Provider-agnostic AI application scaffold",
    )
    parser.add_argument("prompt", help="Prompt to send to the configured provider")
    args = parser.parse_args()

    service = IntelligenceService()
    result = service.ask(args.prompt)
    print(result.text)


if __name__ == "__main__":
    main()
