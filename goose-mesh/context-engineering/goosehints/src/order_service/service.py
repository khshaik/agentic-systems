"""Pure pricing calculations for the order domain."""

from __future__ import annotations

from dataclasses import dataclass

from .domain import Order


@dataclass(frozen=True, slots=True)
class OrderSummary:
    """Calculated monetary values, all represented in integer cents."""

    subtotal_cents: int
    discount_cents: int
    total_cents: int


def price_order(order: Order) -> OrderSummary:
    """Calculate an order subtotal, discount, and final total."""

    subtotal_cents = sum(line.subtotal_cents for line in order.lines)
    discount_cents = subtotal_cents * order.discount_percent // 100
    total_cents = max(0, subtotal_cents - discount_cents)
    return OrderSummary(
        subtotal_cents=subtotal_cents,
        discount_cents=discount_cents,
        total_cents=total_cents,
    )
