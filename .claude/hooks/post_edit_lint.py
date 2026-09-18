#!/usr/bin/env python3
"""PostToolUse hook: after Edit/Write on a .py file under cleanit/ or tests/,
auto-format with ruff and surface ruff/mypy issues back to Claude."""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def relative_to_root(file_path: str) -> Path | None:
    try:
        return Path(file_path).resolve().relative_to(PROJECT_ROOT)
    except ValueError:
        return None


def main() -> int:
    payload = json.load(sys.stdin)
    file_path = payload.get("tool_input", {}).get("file_path") or payload.get("tool_response", {}).get("filePath")
    if not file_path or not file_path.endswith(".py"):
        return 0

    rel = relative_to_root(file_path)
    if rel is None:
        return 0

    parts = rel.parts
    in_cleanit = len(parts) > 1 and parts[0] == "cleanit"
    in_tests = len(parts) > 1 and parts[0] == "tests"
    if not (in_cleanit or in_tests):
        return 0

    errors = []

    subprocess.run(
        ["uv", "run", "ruff", "format", str(file_path)],
        cwd=PROJECT_ROOT,
        capture_output=True,
    )

    check = subprocess.run(
        ["uv", "run", "ruff", "check", str(file_path)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if check.returncode != 0:
        errors.append("ruff check found issues:\n" + check.stdout + check.stderr)

    if in_cleanit:
        mypy = subprocess.run(
            ["uv", "run", "mypy", "cleanit"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        if mypy.returncode != 0:
            errors.append("mypy found issues:\n" + mypy.stdout + mypy.stderr)

    if errors:
        sys.stderr.write("\n\n".join(errors))
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
