# Feature request: fixed-amount coupons

Add support for an optional fixed-amount coupon after the percentage discount.

Acceptance criteria:
- The coupon amount must be non-negative.
- The final total can never be less than zero.
- Percentage discount is applied before the fixed coupon.
- Existing callers remain compatible.
- Currency remains rounded to two decimal places using ROUND_HALF_UP.
