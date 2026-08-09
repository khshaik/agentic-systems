"""Runnable demonstration for the order pricing service."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from order_service.api.handlers import calculate_order


DEFAULT_PAYLOAD = {
    "lines": [
        {"product_id": "keyboard", "unit_price_cents": 7500, "quantity": 1},
        {"product_id": "mouse", "unit_price_cents": 2500, "quantity": 2},
    ],
    "discount_percent": 10,
}


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description="Calculate an order total")
    parser.add_argument(
        "--payload",
        help="JSON object; defaults to a built-in demonstration order",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the order calculation and print formatted JSON."""

    args = build_parser().parse_args(argv)
    try:
        payload = json.loads(args.payload) if args.payload else DEFAULT_PAYLOAD
    except json.JSONDecodeError as exc:
        print(json.dumps({"ok": False, "error": f"invalid JSON: {exc.msg}"}, indent=2))
        return 2

    if not isinstance(payload, dict):
        print(json.dumps({"ok": False, "error": "payload must be a JSON object"}, indent=2))
        return 2

    result = calculate_order(payload)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
