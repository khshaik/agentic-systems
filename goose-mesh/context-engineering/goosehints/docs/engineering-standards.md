# Engineering standards

## Python

- Public functions and methods require type hints.
- Raise `ValueError` for invalid domain values at construction boundaries.
- Prefer `pathlib.Path` over string-based filesystem manipulation.
- Use clear names rather than comments that restate code.
- Avoid catch-all exception handlers unless translating an error at an adapter boundary.

## Testing

- Use `python3 -m unittest discover -s tests -v`.
- New behavior requires a focused test that fails before the implementation change.
- Tests must not depend on execution order.

## Change discipline

- Do not modify unrelated files.
- Do not silently weaken validation.
- Do not add a dependency when the standard library is adequate.
- Do not claim commands passed unless their exit code was zero in the current run.
