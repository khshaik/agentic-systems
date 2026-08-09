from pathlib import Path


root = Path(__file__).resolve().parent.parent
text = (root / "prompts.md").read_text(encoding="utf-8")

required = (
    "Remember these facts in local project memory",
    "Command: make test",
    "def greet(name)",
    "Preference:",
    "Retrieve the local sample_project memory",
)

missing = [value for value in required if value not in text]
if missing:
    raise SystemExit("missing sample content: " + ", ".join(missing))

print("memory-extension: sample check passed")
