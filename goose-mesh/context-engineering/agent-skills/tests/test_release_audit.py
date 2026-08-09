from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
AUDIT_PATH = ROOT / ".agents" / "skills" / "release-readiness" / "scripts" / "release_audit.py"
SPEC = importlib.util.spec_from_file_location("release_audit", AUDIT_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
import sys
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


def write(path: Path, text: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def healthy_repo(root: Path) -> None:
    write(root / "README.md", "# Demo\n")
    write(root / "LICENSE", "Apache-2.0\n")
    write(root / ".gitignore", ".env\n")
    write(root / "CHANGELOG.md", "# Changes\n")
    write(root / "tests" / "test_app.py", "def test_ok():\n    assert True\n")
    write(root / ".github" / "workflows" / "ci.yml", "name: ci\n")
    write(root / "Dockerfile", "FROM scratch\nUSER 10001\n")


class ReleaseAuditTest(unittest.TestCase):
    def test_healthy_repository_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            healthy_repo(repo)
            result = AUDIT.audit(repo, dict(AUDIT.DEFAULT_POLICY), "full")
            self.assertEqual(result.decision(), "READY")
            self.assertFalse(result.findings)

    def test_secret_and_missing_controls_block_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write(repo / "app.py", 'api_key = "real-looking-secret-123456"\n')
            write(repo / ".env", "PASSWORD=super-secret-password\n")
            result = AUDIT.audit(repo, dict(AUDIT.DEFAULT_POLICY), "full")
            self.assertEqual(result.decision(), "BLOCKED")
            categories = {finding.category for finding in result.findings}
            self.assertIn("secret", categories)
            self.assertIn("required-file", categories)
            report = AUDIT.markdown_report(result)
            self.assertNotIn("real-looking-secret-123456", report)
            self.assertNotIn("super-secret-password", report)

    def test_policy_override_can_change_required_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            healthy_repo(repo)
            policy = AUDIT.merge_policy(dict(AUDIT.DEFAULT_POLICY), {"required_files": []})
            (repo / "README.md").unlink()
            result = AUDIT.audit(repo, policy, "quick")
            self.assertFalse(any(f.path == "README.md" for f in result.findings))

    def test_json_report_is_serializable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            healthy_repo(repo)
            result = AUDIT.audit(repo, dict(AUDIT.DEFAULT_POLICY), "full")
            encoded = json.dumps(result.to_dict())
            self.assertIn('"decision": "READY"', encoded)


if __name__ == "__main__":
    unittest.main()
