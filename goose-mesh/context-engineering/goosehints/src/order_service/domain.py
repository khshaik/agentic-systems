"""Immutable domain values for order pricing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OrderLine:
    """A product, integer-cent unit price, and quantity."""

    product_id: str
    unit_price_cents: int
    quantity: int

    def __post_init__(self) -> None:
        normalized_product_id = self.product_id.strip()
        if not normalized_product_id:
            raise ValueError("product_id must not be empty")
        if self.unit_price_cents < 0:
            raise ValueError("unit_price_cents must not be negative")
        if self.quantity < 0:
            raise ValueError("quantity must not be negative")
        object.__setattr__(self, "product_id", normalized_product_id)

    @property
    def subtotal_cents(self) -> int:
        """Return the line subtotal in integer cents."""

        return self.unit_price_cents * self.quantity


@dataclass(frozen=True, slots=True)
class Order:
    """An immutable collection of order lines and a discount percentage."""

    lines: tuple[OrderLine, ...]
    discount_percent: int = 0

    def __post_init__(self) -> None:
        if not 0 <= self.discount_percent <= 50:
            raise ValueError("discount_percent must be between 0 and 50")
