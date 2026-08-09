# Domain rules loaded through `@` reference

This file is intentionally referenced with `@docs/domain-rules.md` from the root `.goosehints`. Goose's documented `@` syntax places referenced file content in immediate context.

The sample order service follows these rules:

1. A line subtotal is `unit_price_cents × quantity`.
2. An order subtotal is the sum of its line subtotals.
3. A discount is an integer percentage from 0 through 50 inclusive.
4. Discount cents are rounded down using integer division: `subtotal_cents × discount_percent // 100`.
5. The order total is `subtotal_cents - discount_cents` and cannot be negative.
6. An empty order is valid and totals zero cents.
7. Product identifiers must be non-empty after whitespace is removed.

These rules are the source of truth. API and CLI layers must call the domain service rather than reimplement them.
