#!/usr/bin/env python3
"""
Compute sort order by issue number after first '_' and print git mv pairs.
Renames only the leading NNN prefix; slug after first '_' preserved.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def tail_after_first_underscore(name: str) -> str:
    parts = name.split("_", 1)
    assert len(parts) == 2, name
    return parts[1]


def parse_issue_key(filename: str) -> tuple[int, int]:
    """

    Tuple (major, minor) for sorting. minor is 0 unless pattern is M-minor-slug
    (e.g. 7-1-..., 44-1-..., 29-1-...).

    Glued digit+letter: 4Foo, 11Агрессия, 111Созидание -> (4|11|111, 0).
    """
    tail = tail_after_first_underscore(filename)
    if tail.endswith(".md"):
        stem = tail[: -len(".md")]
    else:
        stem = tail

    # M-minor-rest: 7-1-foo, 44-1-foo, 29-2-foo
    m = re.match(r"^(\d+)-(\d+)-", stem)
    if m:
        return int(m.group(1)), int(m.group(2))

    # Glued: digits then letter (Cyrillic/Latin)
    m = re.match(r"^(\d+)([А-Яа-яA-Za-z])", stem)
    if m:
        return int(m.group(1)), 0

    # M-only: 25, 23-Имидж, 40-Секс
    m = re.match(r"^(\d+)(?:$|-)", stem)
    if m:
        return int(m.group(1)), 0

    raise ValueError(f"Cannot parse issue key from: {filename!r}")


def build_plan(root: Path) -> list[tuple[str, str]]:
    rassylki = root / "rassylki"
    files = sorted(rassylki.glob("*.md"))
    if not files:
        return []

    decorated: list[tuple[tuple[int, int], str, Path]] = []
    for p in files:
        key = parse_issue_key(p.name)
        decorated.append((key, p.name, p))

    decorated.sort(key=lambda t: (t[0][0], t[0][1], t[1]))
    plan: list[tuple[str, str]] = []
    for i, (_k, old_name, _path) in enumerate(decorated, start=1):
        tail = tail_after_first_underscore(old_name)
        new_name = f"{i:03d}_{tail}"
        plan.append((old_name, new_name))
    return plan


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    apply_mode = "--apply" in sys.argv
    plan = build_plan(root)
    if not plan:
        print("No md files", file=sys.stderr)
        return 1
    rassylki = root / "rassylki"

    if apply_mode:
        import subprocess

        stage = rassylki / ".rename_stage_rassylki"
        stage.mkdir(exist_ok=True)
        for old_name, _ in plan:
            subprocess.run(
                ["git", "mv", f"rassylki/{old_name}", f"rassylki/.rename_stage_rassylki/{old_name}"],
                cwd=root,
                check=True,
            )
        for old_name, new_name in plan:
            subprocess.run(
                ["git", "mv", f"rassylki/.rename_stage_rassylki/{old_name}", f"rassylki/{new_name}"],
                cwd=root,
                check=True,
            )
        stage.rmdir()
        return 0

    for old_name, new_name in plan:
        if new_name != old_name:
            print(f"git mv rassylki/{old_name} rassylki/{new_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
