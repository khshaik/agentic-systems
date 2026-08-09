from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hints_common import hint_chain_for_path, iter_hint_files, referenced_paths


class HintToolTests(unittest.TestCase):
    def test_iter_hint_files_returns_root_and_nested_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".goosehints").write_text("root", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / ".goosehints").write_text("nested", encoding="utf-8")

            files = [path.relative_to(root) for path in iter_hint_files(root)]

            self.assertEqual(files, [Path(".goosehints"), Path("src/.goosehints")])

    def test_referenced_paths_resolves_root_relative_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            expected = root / "docs" / "rules.md"
            expected.write_text("rules", encoding="utf-8")
            hint = root / ".goosehints"
            hint.write_text("@docs/rules.md", encoding="utf-8")

            references = referenced_paths(hint, root)

            self.assertEqual(references, [("docs/rules.md", expected.resolve())])

    def test_referenced_paths_reports_missing_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hint = root / ".goosehints"
            hint.write_text("@docs/missing.md", encoding="utf-8")

            references = referenced_paths(hint, root)

            self.assertEqual(references, [("docs/missing.md", None)])

    def test_hint_chain_is_ordered_from_root_to_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            target = root / "src" / "api" / "handler.py"
            target.parent.mkdir(parents=True)
            target.write_text("", encoding="utf-8")
            for parent in (root, root / "src", root / "src" / "api"):
                (parent / ".goosehints").write_text("hint", encoding="utf-8")

            chain = hint_chain_for_path(root, target)

            self.assertEqual(
                chain,
                [
                    root / ".goosehints",
                    root / "src" / ".goosehints",
                    root / "src" / "api" / ".goosehints",
                ],
            )


if __name__ == "__main__":
    unittest.main()
