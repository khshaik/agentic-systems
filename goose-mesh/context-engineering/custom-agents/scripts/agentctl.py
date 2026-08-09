#!/usr/bin/env python3
"""Dependency-free lifecycle helper for Goose custom-agent Markdown files.

This is a repository convenience tool, not a built-in Goose command. Goose itself
reads the generated Markdown files from .agents/agents/.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class AgentError(Exception):
    """An expected validation or lifecycle error."""


@dataclass(frozen=True)
class Agent:
    path: Path
    name: str
    description: str | None
    model: str | None
    instructions: str


def yaml_scalar(value: str) -> str:
    """Encode a string as a JSON-compatible YAML quoted scalar."""
    return json.dumps(value, ensure_ascii=False)


def parse_scalar(raw: str) -> str:
    value = raw.strip()
    if not value:
        return ""
    if value[0] == '"':
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise AgentError(f"invalid quoted frontmatter value: {value}") from exc
        if not isinstance(parsed, str):
            raise AgentError("frontmatter values must be strings")
        return parsed
    if value[0] == "'" and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def parse_agent(path: Path) -> Agent:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AgentError(f"cannot read {path}: {exc}") from exc

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise AgentError(f"{path}: missing opening YAML frontmatter delimiter")

    try:
        closing = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise AgentError(f"{path}: missing closing YAML frontmatter delimiter") from exc

    metadata: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:closing], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            raise AgentError(f"{path}:{line_number}: expected 'key: value'")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if key not in {"name", "description", "model"}:
            raise AgentError(f"{path}:{line_number}: unsupported field '{key}'")
        if key in metadata:
            raise AgentError(f"{path}:{line_number}: duplicate field '{key}'")
        metadata[key] = parse_scalar(raw_value)

    name = metadata.get("name", "").strip()
    instructions = "\n".join(lines[closing + 1 :]).strip()
    return Agent(
        path=path,
        name=name,
        description=metadata.get("description") or None,
        model=metadata.get("model") or None,
        instructions=instructions,
    )


def validate_agent(agent: Agent, *, enforce_filename: bool = True) -> list[str]:
    errors: list[str] = []
    if not agent.name:
        errors.append("missing required 'name'")
    elif not NAME_RE.fullmatch(agent.name):
        errors.append("name must use lowercase letters, digits, and single hyphens")
    if enforce_filename and agent.name and agent.path.stem != agent.name:
        errors.append(f"filename must be '{agent.name}.md'")
    if not agent.instructions:
        errors.append("instruction body is empty")
    if agent.description is not None and not agent.description.strip():
        errors.append("description is empty")
    if agent.model is not None and not agent.model.strip():
        errors.append("model is empty")
    return errors


def render_agent(name: str, description: str | None, model: str | None, instructions: str) -> str:
    lines = ["---", f"name: {name}"]
    if description:
        lines.append(f"description: {yaml_scalar(description)}")
    if model:
        lines.append(f"model: {yaml_scalar(model)}")
    lines.extend(["---", instructions.strip(), ""])
    return "\n".join(lines)


def default_agents_dir(root: Path) -> Path:
    return root / ".agents" / "agents"


def iter_agent_files(directory: Path) -> Iterable[Path]:
    if not directory.exists():
        return []
    return sorted(p for p in directory.glob("*.md") if p.is_file())


def require_name(name: str) -> None:
    if not NAME_RE.fullmatch(name):
        raise AgentError("name must use lowercase letters, digits, and single hyphens")


def read_instructions(args: argparse.Namespace, current: str | None = None) -> str:
    if getattr(args, "instructions", None) is not None:
        value = args.instructions
    elif getattr(args, "instructions_file", None) is not None:
        try:
            value = Path(args.instructions_file).read_text(encoding="utf-8")
        except OSError as exc:
            raise AgentError(f"cannot read instructions file: {exc}") from exc
    elif current is not None:
        value = current
    else:
        raise AgentError("provide --instructions or --instructions-file")
    if not value.strip():
        raise AgentError("instructions cannot be empty")
    return value.strip()


def cmd_list(args: argparse.Namespace) -> int:
    directory = Path(args.agents_dir)
    rows = []
    for path in iter_agent_files(directory):
        try:
            agent = parse_agent(path)
            errors = validate_agent(agent)
            rows.append(
                {
                    "name": agent.name or path.stem,
                    "description": agent.description,
                    "model": agent.model,
                    "path": str(path),
                    "valid": not errors,
                    "errors": errors,
                }
            )
        except AgentError as exc:
            rows.append(
                {
                    "name": path.stem,
                    "description": None,
                    "model": None,
                    "path": str(path),
                    "valid": False,
                    "errors": [str(exc)],
                }
            )

    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0

    if not rows:
        print(f"No agents found in {directory}")
        return 0
    for row in rows:
        status = "OK" if row["valid"] else "INVALID"
        model = f" | model={row['model']}" if row["model"] else ""
        description = row["description"] or "(no description)"
        print(f"{status:7} {row['name']}: {description}{model}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.paths] if args.paths else list(iter_agent_files(Path(args.agents_dir)))
    if not paths:
        raise AgentError("no agent files found")

    all_errors: list[str] = []
    names: dict[str, Path] = {}
    for path in paths:
        try:
            agent = parse_agent(path)
            errors = validate_agent(agent, enforce_filename=not args.allow_filename_mismatch)
            if agent.name in names:
                errors.append(f"duplicate agent name also used by {names[agent.name]}")
            elif agent.name:
                names[agent.name] = path
            if errors:
                all_errors.extend(f"{path}: {error}" for error in errors)
            else:
                print(f"OK {path}")
        except AgentError as exc:
            all_errors.append(str(exc))

    if all_errors:
        for error in all_errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(paths)} agent file(s).")
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    require_name(args.name)
    directory = Path(args.agents_dir)
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / f"{args.name}.md"
    if destination.exists() and not args.force:
        raise AgentError(f"{destination} already exists; use --force to replace it")
    instructions = read_instructions(args)
    destination.write_text(
        render_agent(args.name, args.description, args.model, instructions),
        encoding="utf-8",
    )
    print(destination)
    return 0


def cmd_edit(args: argparse.Namespace) -> int:
    require_name(args.name)
    directory = Path(args.agents_dir)
    path = directory / f"{args.name}.md"
    if not path.exists():
        raise AgentError(f"agent not found: {path}")
    agent = parse_agent(path)

    if args.open_editor:
        editor = args.editor or None
        if editor is None:
            import os

            editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
        if not editor:
            raise AgentError("set VISUAL/EDITOR or pass --editor")
        completed = subprocess.run([editor, str(path)], check=False)
        if completed.returncode != 0:
            raise AgentError(f"editor exited with status {completed.returncode}")
        revised = parse_agent(path)
        errors = validate_agent(revised)
        if errors:
            raise AgentError("edited file is invalid: " + "; ".join(errors))
        print(path)
        return 0

    description = agent.description if args.description is None else (args.description or None)
    model = agent.model if args.model is None else (args.model or None)
    instructions = read_instructions(args, current=agent.instructions)
    path.write_text(render_agent(agent.name, description, model, instructions), encoding="utf-8")
    print(path)
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    source = Path(args.source)
    if not source.is_file():
        raise AgentError(f"import source is not a file: {source}")
    agent = parse_agent(source)
    errors = validate_agent(agent, enforce_filename=False)
    if errors:
        raise AgentError("cannot import invalid agent: " + "; ".join(errors))

    directory = Path(args.agents_dir)
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / f"{agent.name}.md"
    if destination.exists() and not args.force:
        raise AgentError(f"{destination} already exists; use --force to replace it")
    destination.write_text(
        render_agent(agent.name, agent.description, agent.model, agent.instructions),
        encoding="utf-8",
    )
    print(destination)
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    require_name(args.name)
    source = Path(args.agents_dir) / f"{args.name}.md"
    if not source.is_file():
        raise AgentError(f"agent not found: {source}")
    agent = parse_agent(source)
    errors = validate_agent(agent)
    if errors:
        raise AgentError("cannot export invalid agent: " + "; ".join(errors))

    output = Path(args.output)
    if output.suffix.lower() == ".md":
        destination = output
        destination.parent.mkdir(parents=True, exist_ok=True)
    else:
        output.mkdir(parents=True, exist_ok=True)
        destination = output / source.name
    if destination.exists() and not args.force:
        raise AgentError(f"{destination} already exists; use --force to replace it")
    shutil.copy2(source, destination)
    print(destination)
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    source_dir = Path(args.agents_dir)
    if args.global_install:
        destination_dir = Path.home() / ".agents" / "agents"
    else:
        if not args.target:
            raise AgentError("provide --target for a project install, or use --global")
        destination_dir = Path(args.target).resolve() / ".agents" / "agents"
    destination_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for source in iter_agent_files(source_dir):
        agent = parse_agent(source)
        errors = validate_agent(agent)
        if errors:
            raise AgentError(f"{source} is invalid: {'; '.join(errors)}")
        destination = destination_dir / source.name
        if destination.exists() and not args.force:
            raise AgentError(f"{destination} exists; rerun with --force to replace files")
        shutil.copy2(source, destination)
        copied += 1
    if copied == 0:
        raise AgentError(f"no agents found in {source_dir}")
    print(f"Installed {copied} agent(s) into {destination_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agents-dir",
        default=str(default_agents_dir(root)),
        help="agent directory (default: this repository's .agents/agents)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list agents")
    list_parser.add_argument("--json", action="store_true")
    list_parser.set_defaults(func=cmd_list)

    validate_parser = subparsers.add_parser("validate", help="validate agent files")
    validate_parser.add_argument("paths", nargs="*")
    validate_parser.add_argument("--allow-filename-mismatch", action="store_true")
    validate_parser.set_defaults(func=cmd_validate)

    create_parser = subparsers.add_parser("create", help="create an agent")
    create_parser.add_argument("name")
    create_parser.add_argument("--description")
    create_parser.add_argument("--model")
    create_parser.add_argument("--instructions")
    create_parser.add_argument("--instructions-file")
    create_parser.add_argument("--force", action="store_true")
    create_parser.set_defaults(func=cmd_create)

    edit_parser = subparsers.add_parser("edit", help="edit an agent")
    edit_parser.add_argument("name")
    edit_parser.add_argument("--description", help="set description; pass an empty string to remove")
    edit_parser.add_argument("--model", help="set model preference; pass an empty string to remove")
    edit_parser.add_argument("--instructions")
    edit_parser.add_argument("--instructions-file")
    edit_parser.add_argument("--open-editor", action="store_true")
    edit_parser.add_argument("--editor", help="editor executable used with --open-editor")
    edit_parser.set_defaults(func=cmd_edit)

    import_parser = subparsers.add_parser("import", help="import a portable agent Markdown file")
    import_parser.add_argument("source")
    import_parser.add_argument("--force", action="store_true")
    import_parser.set_defaults(func=cmd_import)

    export_parser = subparsers.add_parser("export", help="export a portable agent Markdown file")
    export_parser.add_argument("name")
    export_parser.add_argument("--output", required=True)
    export_parser.add_argument("--force", action="store_true")
    export_parser.set_defaults(func=cmd_export)

    install_parser = subparsers.add_parser("install", help="install all sample agents into a project or globally")
    target_group = install_parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument("--target", help="target repository directory")
    target_group.add_argument("--global", dest="global_install", action="store_true")
    install_parser.add_argument("--force", action="store_true")
    install_parser.set_defaults(func=cmd_install)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except AgentError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
