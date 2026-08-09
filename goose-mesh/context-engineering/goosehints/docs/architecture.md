# Architecture

The repository uses a small ports-and-adapters shape without external dependencies.

- `src/order_service/domain.py` contains immutable domain values and validation.
- `src/order_service/service.py` contains deterministic pricing calculations.
- `src/order_service/api/handlers.py` translates JSON-compatible dictionaries to and from domain values.
- `src/order_service/cli.py` is a runnable command-line adapter.
- `tests/` verifies domain, API, CLI-facing behavior, and repository hint tooling.

Dependencies point inward: adapters may import the domain package, but the domain package must not import adapters.
