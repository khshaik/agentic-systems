from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
VALIDATOR_PATH = ROOT / ".agents" / "skills" / "release-readiness" / "scripts" / "validate_skill.py"
SPEC = importlib.util.spec_from_file_location("validate_skill", VALIDATOR_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


class SkillValidationTest(unittest.TestCase):
    def test_bundled_skill_is_valid(self) -> None:
        result = VALIDATOR.validate(ROOT / ".agents" / "skills" / "release-readiness")
        self.assertTrue(result["valid"], result["errors"])


if __name__ == "__main__":
    unittest.main()
