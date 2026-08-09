from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
PATH = ROOT / "skills" / "repository-health" / "scripts" / "repository_health.py"
SPEC = importlib.util.spec_from_file_location("repository_health", PATH)
assert SPEC and SPEC.loader
HEALTH = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = HEALTH
SPEC.loader.exec_module(HEALTH)


def write(path: Path, text: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class RepositoryHealthTests(unittest.TestCase):
    def test_complete_repository_is_healthy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write(repo / "README.md")
            write(repo / "LICENSE")
            write(repo / "tests" / "test_app.py")
            write(repo / ".github" / "workflows" / "ci.yml")
            result = HEALTH.assess(repo)
            self.assertEqual(result["decision"], "HEALTHY")
            self.assertEqual(result["findings"], [])

    def test_missing_controls_block_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = HEALTH.assess(Path(directory))
            self.assertEqual(result["decision"], "BLOCKED")

    def test_secret_value_is_never_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write(repo / "README.md")
            write(repo / "LICENSE")
            write(repo / "tests" / "test_app.py")
            write(repo / ".github" / "workflows" / "ci.yml")
            value = "real-credential-" + "value-123"
            write(repo / "app.py", f'api_key = "{value}"\n')
            result = HEALTH.assess(repo)
            encoded = str(result)
            self.assertEqual(result["decision"], "BLOCKED")
            self.assertNotIn(value, encoded)


if __name__ == "__main__":
    unittest.main()
