from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "src" / "service.py"
SPEC = importlib.util.spec_from_file_location("sample_service", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HealthPayloadTest(unittest.TestCase):
    def test_health_payload(self) -> None:
        self.assertEqual(
            MODULE.health_payload(),
            {"status": "ok", "service": "sample-service"},
        )


if __name__ == "__main__":
    unittest.main()
