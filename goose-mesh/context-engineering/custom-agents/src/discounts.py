"""Small dependency-free module used by the Custom Agents examples."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


MONEY = Decimal("0.01")


def calculate_total(subtotal: Decimal, discount_percent: Decimal = Decimal("0")) -> Decimal:
    """Return a non-negative discounted total rounded to two decimal places.

    Args:
        subtotal: Original amount. Must be zero or greater.
        discount_percent: Percentage in the inclusive range 0..100.
    """
    if subtotal < 0:
        raise ValueError("subtotal must be non-negative")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("discount_percent must be between 0 and 100")

    multiplier = Decimal("1") - (discount_percent / Decimal("100"))
    return (subtotal * multiplier).quantize(MONEY, rounding=ROUND_HALF_UP)
