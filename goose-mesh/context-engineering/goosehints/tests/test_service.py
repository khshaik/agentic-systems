from __future__ import annotations

import unittest

from order_service import Order, OrderLine, price_order
from order_service.api.handlers import calculate_order


class OrderPricingTests(unittest.TestCase):
    def test_regular_order_returns_integer_cent_summary(self) -> None:
        order = Order(
            lines=(
                OrderLine("keyboard", 7_500, 1),
                OrderLine("mouse", 2_500, 2),
            ),
            discount_percent=10,
        )

        summary = price_order(order)

        self.assertEqual(summary.subtotal_cents, 12_500)
        self.assertEqual(summary.discount_cents, 1_250)
        self.assertEqual(summary.total_cents, 11_250)

    def test_fractional_discount_cent_rounds_down(self) -> None:
        order = Order(lines=(OrderLine("cable", 101, 1),), discount_percent=10)

        summary = price_order(order)

        self.assertEqual(summary.discount_cents, 10)
        self.assertEqual(summary.total_cents, 91)

    def test_empty_order_totals_zero(self) -> None:
        summary = price_order(Order(lines=()))

        self.assertEqual(summary.subtotal_cents, 0)
        self.assertEqual(summary.discount_cents, 0)
        self.assertEqual(summary.total_cents, 0)

    def test_negative_quantity_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "quantity"):
            OrderLine("mouse", 2_500, -1)

    def test_discount_above_limit_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "between 0 and 50"):
            Order(lines=(), discount_percent=51)

    def test_api_adapter_returns_stable_success_shape(self) -> None:
        result = calculate_order(
            {
                "lines": [
                    {"product_id": "adapter", "unit_price_cents": 1_000, "quantity": 2}
                ],
                "discount_percent": 25,
            }
        )

        self.assertEqual(
            result,
            {
                "ok": True,
                "subtotal_cents": 2_000,
                "discount_cents": 500,
                "total_cents": 1_500,
            },
        )

    def test_api_adapter_translates_invalid_input_to_error(self) -> None:
        result = calculate_order({"lines": "not-a-list"})

        self.assertFalse(result["ok"])
        self.assertIn("lines must be a list", result["error"])


if __name__ == "__main__":
    unittest.main()
