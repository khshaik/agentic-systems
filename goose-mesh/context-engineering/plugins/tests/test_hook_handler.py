from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
PATH = ROOT / "scripts" / "hook_handler.py"
SPEC = importlib.util.spec_from_file_location("hook_handler", PATH)
assert SPEC and SPEC.loader
HOOK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOOK)


class HookHandlerTests(unittest.TestCase):
    def test_safe_shell_command_is_allowed(self) -> None:
        payload = {"tool_input": {"command": "python3 -m unittest"}}
        self.assertIsNone(HOOK.blocked_reason(payload))

    def test_git_reset_hard_is_blocked(self) -> None:
        payload = {"tool_input": {"command": "git reset --hard HEAD"}}
        self.assertIn("discard", HOOK.blocked_reason(payload))

    def test_invalid_payload_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid hook JSON"):
            HOOK.read_payload(io.StringIO("not json"))

    def test_event_log_is_opt_in_and_redacted(self) -> None:
        payload = {
            "event": "AfterShellExecution",
            "session_id": "demo-1",
            "matcher_context": "make test",
            "tool_input": {"secret": "must-not-be-logged"},
        }
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "events.jsonl"
            with patch.dict(os.environ, {"REPOSITORY_COMPANION_LOG": str(destination)}):
                self.assertEqual(HOOK.record_event(payload), 0)
            record = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(record["event"], "AfterShellExecution")
            self.assertNotIn("tool_input", record)


if __name__ == "__main__":
    unittest.main()
