from pathlib import Path

root = Path(__file__).resolve().parent.parent
project_rules = (root / ".gooseignore").read_text().splitlines()
global_rules = (root / "global.gooseignore.example").read_text().splitlines()

required_project = {".env", "secrets/", "*.pem"}
required_global = {"**/.env*", "**/*.pem", "**/credentials/**"}

assert required_project <= set(project_rules)
assert required_global <= set(global_rules)
assert (root / "app.txt").is_file()
print("gooseignore sample: valid")

