from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "agentctl.py"

spec = importlib.util.spec_from_file_location("agentctl", SCRIPT)
assert spec and spec.loader
agentctl = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = agentctl
spec.loader.exec_module(agentctl)


class AgentCtlUnitTests(unittest.TestCase):
    def test_all_checked_in_agents_are_valid(self) -> None:
        paths = sorted((ROOT / ".agents" / "agents").glob("*.md"))
        self.assertGreaterEqual(len(paths), 4)
        for path in paths:
            agent = agentctl.parse_agent(path)
            self.assertEqual(agentctl.validate_agent(agent), [], path)

    def test_render_round_trip_handles_colons_and_quotes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "specialist.md"
            path.write_text(
                agentctl.render_agent(
                    "specialist",
                    'Reviews APIs: "safe" changes only',
                    "provider/model:latest",
                    "Do the work.",
                ),
                encoding="utf-8",
            )
            parsed = agentctl.parse_agent(path)
            self.assertEqual(parsed.description, 'Reviews APIs: "safe" changes only')
            self.assertEqual(parsed.model, "provider/model:latest")
            self.assertEqual(parsed.instructions, "Do the work.")

    def test_rejects_filename_name_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "wrong.md"
            path.write_text(
                agentctl.render_agent("right", None, None, "Instructions"),
                encoding="utf-8",
            )
            errors = agentctl.validate_agent(agentctl.parse_agent(path))
            self.assertIn("filename must be 'right.md'", errors)


class AgentCtlLifecycleTests(unittest.TestCase):
    def run_ctl(self, agents_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--agents-dir", str(agents_dir), *args],
            check=False,
            text=True,
            capture_output=True,
        )

    def test_create_edit_export_import_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            first = temp_path / "one" / ".agents" / "agents"
            second = temp_path / "two" / ".agents" / "agents"
            export_dir = temp_path / "exports"

            created = self.run_ctl(
                first,
                "create",
                "api-reviewer",
                "--description",
                "Reviews APIs",
                "--instructions",
                "Review API compatibility.",
            )
            self.assertEqual(created.returncode, 0, created.stderr)

            edited = self.run_ctl(
                first,
                "edit",
                "api-reviewer",
                "--model",
                "example-model",
                "--instructions",
                "Review API compatibility and security.",
            )
            self.assertEqual(edited.returncode, 0, edited.stderr)

            validated = self.run_ctl(first, "validate")
            self.assertEqual(validated.returncode, 0, validated.stderr)

            exported = self.run_ctl(
                first,
                "export",
                "api-reviewer",
                "--output",
                str(export_dir),
            )
            self.assertEqual(exported.returncode, 0, exported.stderr)

            imported = self.run_ctl(
                second,
                "import",
                str(export_dir / "api-reviewer.md"),
            )
            self.assertEqual(imported.returncode, 0, imported.stderr)

            source_text = (first / "api-reviewer.md").read_text(encoding="utf-8")
            imported_text = (second / "api-reviewer.md").read_text(encoding="utf-8")
            self.assertEqual(source_text, imported_text)

    def test_import_rejects_invalid_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            invalid = temp_path / "invalid.md"
            invalid.write_text("---\ndescription: missing name\n---\nInstructions\n", encoding="utf-8")
            result = self.run_ctl(temp_path / "agents", "import", str(invalid))
            self.assertEqual(result.returncode, 2)
            self.assertIn("missing required 'name'", result.stderr)


if __name__ == "__main__":
    unittest.main()
