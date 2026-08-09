from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
PATH = ROOT / "scripts" / "validate_plugin.py"
SPEC = importlib.util.spec_from_file_location("validate_plugin", PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class PluginValidationTests(unittest.TestCase):
    def test_sample_plugin_is_valid(self) -> None:
        self.assertEqual(VALIDATOR.validate(ROOT), [])


if __name__ == "__main__":
    unittest.main()
