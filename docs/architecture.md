# Architecture

## Objectives

The architecture is intentionally simple in Phase 1. It separates the orchestration layer from the provider layer so the project can evolve without a hard dependency on a specific AI vendor.

## Flow

1. The CLI receives a prompt from the user.
2. `IntelligenceEngine` validates the prompt.
3. The engine calls a `Provider` implementation.
4. The provider returns a plain string.
5. The final result is wrapped as `ServiceResponse` and returned to the caller.

## Design principles

- Keep the core engine generic and testable.
- Hide model vendor details behind a provider interface.
- Avoid reading secrets from source control.
- Keep remote API calls explicit and isolated.
- Add environment-based configuration later as the app grows.

## Current implementation

The repo ships with a `DemoProvider` only. It is not an actual model and should not be used for production intelligence workflows. It exists to verify package wiring and to give the project a safe default behavior while the real provider layer is being designed.
