from decimal import Decimal
import unittest

from src.discounts import calculate_total


class CalculateTotalTests(unittest.TestCase):
    def test_returns_rounded_discounted_total(self) -> None:
        self.assertEqual(
            calculate_total(Decimal("19.99"), Decimal("15")),
            Decimal("16.99"),
        )

    def test_accepts_full_discount(self) -> None:
        self.assertEqual(
            calculate_total(Decimal("10.00"), Decimal("100")),
            Decimal("0.00"),
        )

    def test_rejects_negative_subtotal(self) -> None:
        with self.assertRaisesRegex(ValueError, "subtotal"):
            calculate_total(Decimal("-0.01"))

    def test_rejects_discount_over_one_hundred(self) -> None:
        with self.assertRaisesRegex(ValueError, "discount_percent"):
            calculate_total(Decimal("10.00"), Decimal("101"))


if __name__ == "__main__":
    unittest.main()
