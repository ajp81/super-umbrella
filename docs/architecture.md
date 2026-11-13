# Architecture

## Current design

The package uses a small provider boundary:

1. The CLI accepts a prompt.
2. `IntelligenceEngine` validates it and calls an injected `Provider`.
3. The provider returns text, wrapped as a `ServiceResponse`.

The included `DemoProvider` is deterministic placeholder behavior. It makes no network requests and is not an AI model. Tests inject a tiny fake provider so core behavior can be checked without credentials, network access, or model-specific dependencies.

## Integration principles

When adding a real model provider:

- Keep vendor SDK code inside a separate provider module; keep the engine provider-agnostic.
- Read credentials from environment or a secret manager, never source control or command-line arguments.
- Make network use explicit, set timeouts, and handle provider errors without exposing secrets.
- Document data sent to the provider, retention implications, cost controls, and configuration.
- Treat model output as untrusted input. Validate structured output before downstream use, and require human review for consequential actions.
- Add unit tests with mocked provider behavior; keep live API tests opt-in.

## Not implemented

There is no model integration, retrieval pipeline, persistence, agent loop, autonomous action, or domain-specific intelligence yet. These should only be added after the project’s use case and data boundaries are defined.
