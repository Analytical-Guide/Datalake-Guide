"""Utility script to validate internal Markdown links resolve to on-disk files."""
from __future__ import annotations

import pathlib
import re
import sys
from typing import Iterable, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]
MARKDOWN_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

EXTERNAL_PREFIXES: Tuple[str, ...] = (
    "http://",
    "https://",
    "mailto:",
    "tel:",
    "{{",  # Liquid placeholders
)


def iter_markdown_files(root: pathlib.Path) -> Iterable[pathlib.Path]:
    for path in root.rglob("*.md"):
        yield path


def is_external(link: str) -> bool:
    return any(link.startswith(prefix) for prefix in EXTERNAL_PREFIXES)


def resolve_target(link: str, current_file: pathlib.Path) -> pathlib.Path:
    target = link.split("#", 1)[0]
    if not target:
        return current_file  # anchor-only links
    if target.startswith("/"):
        return ROOT / target.lstrip("/")
    return (current_file.parent / target).resolve()


def main() -> int:
    missing: list[str] = []
    for md_file in iter_markdown_files(ROOT):
        text = md_file.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for link in MARKDOWN_PATTERN.findall(line):
                if is_external(link):
                    continue
                target_path = resolve_target(link, md_file)
                if target_path.exists():
                    continue
                missing.append(f"{md_file.relative_to(ROOT)}:{lineno} -> {link}")
    if missing:
        print("Missing internal links detected:")
        for item in missing:
            print(f"  {item}")
        return 1
    print("All internal links resolve to existing files.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
