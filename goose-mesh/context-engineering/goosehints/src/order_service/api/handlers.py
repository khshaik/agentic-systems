"""JSON-compatible adapter functions for the order pricing service."""

from __future__ import annotations

from typing import Any

from order_service import Order, OrderLine, price_order


def calculate_order(payload: dict[str, Any]) -> dict[str, Any]:
    """Translate a JSON-compatible payload into a stable result dictionary."""

    try:
        raw_lines = payload.get("lines")
        if not isinstance(raw_lines, list):
            raise ValueError("lines must be a list")

        lines = tuple(
            OrderLine(
                product_id=str(raw_line["product_id"]),
                unit_price_cents=int(raw_line["unit_price_cents"]),
                quantity=int(raw_line["quantity"]),
            )
            for raw_line in raw_lines
        )
        order = Order(
            lines=lines,
            discount_percent=int(payload.get("discount_percent", 0)),
        )
        summary = price_order(order)
        return {
            "ok": True,
            "subtotal_cents": summary.subtotal_cents,
            "discount_cents": summary.discount_cents,
            "total_cents": summary.total_cents,
        }
    except (KeyError, TypeError, ValueError) as exc:
        return {"ok": False, "error": str(exc)}
