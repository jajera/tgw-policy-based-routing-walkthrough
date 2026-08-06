#!/usr/bin/env python3
"""Normalize Markdown headings and fenced code blocks.

Fixes:
  - Headings — blank line before/after (e.g. `#### Acceptance Criteria`)
  - Fences — blank lines around blocks; label bare ``` with an inferred language

Does not rewrite table markup (see format-md-tables.py). Path from argv[1] or
STDIN JSON (`filePath` / `path` / `file`) for Kiro hooks.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FENCE_OPEN = re.compile(r"^([`~]{3,})([^\s`]*)\s*$")
HEADING = re.compile(r"^(#{1,6})\s+\S")

LANG_HINTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^(docs/)?_?site/|\.jekyll-|vendor/|\.sass-cache", re.M), "gitignore"),
    (re.compile(r"^#!/.+\b(bash|sh)\b|^\$\s|^\./", re.M), "bash"),
    (re.compile(r"^source\s+[\"']https://rubygems|^\s*gem\s+", re.M), "ruby"),
    (re.compile(r"^(name|on|jobs|permissions|version):\s", re.M), "yaml"),
    (re.compile(r"^(services|volumes|image|command):\s", re.M), "yaml"),
    (re.compile(r"^\{%\s|</?[a-zA-Z]", re.M), "html"),
    (re.compile(r"^\$[a-z-]+:\s|^@import\s", re.M), "scss"),
    (re.compile(r"^---\s*$", re.M), "yaml"),
    (re.compile(r"^python3\s|^from\s+\w+\s+import\s|^def\s+", re.M), "bash"),
    (re.compile(r"^graph\s|^sequenceDiagram\s|^flowchart\s", re.M), "mermaid"),
    (re.compile(r"^\s*<svg\b", re.M | re.I), "svg"),
    (re.compile(r"^[│├└─┌┐┘┴┬┤┼]", re.M), "text"),
]


def dirty_markdown_paths() -> list[Path]:
    """Markdown files with unstaged/untracked changes (Kiro runCommand has no file arg)."""
    import subprocess

    paths: set[Path] = set()
    try:
        tracked = subprocess.run(
            ["git", "ls-files", "-m", "--", "*.md", "*.markdown"],
            check=False,
            capture_output=True,
            text=True,
        )
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--", "*.md", "*.markdown"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return []
    for blob in (tracked.stdout, untracked.stdout):
        for line in blob.splitlines():
            line = line.strip()
            if line:
                paths.add(Path(line))
    return sorted(p for p in paths if p.is_file())


def resolve_paths(argv: list[str], stdin_text: str) -> list[Path]:
    if len(argv) >= 2 and argv[1] in {"--dirty", "--changed"}:
        return dirty_markdown_paths()

    if len(argv) >= 2 and argv[1].strip() and argv[1] not in {"{{filePath}}", "{{file}}"}:
        return [Path(p).expanduser() for p in argv[1:] if p.strip()]

    raw = stdin_text.strip()
    if not raw:
        return dirty_markdown_paths()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        candidate = Path(raw)
        return [candidate] if candidate.exists() else dirty_markdown_paths()

    for key in ("filePath", "path", "file", "filepath"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return [Path(value).expanduser()]
    return dirty_markdown_paths()


def infer_fence_language(body: str) -> str:
    sample = body.strip()
    if not sample:
        return "text"
    for pattern, lang in LANG_HINTS:
        if pattern.search(sample):
            return lang
    return "text"


def format_fences(lines: list[str]) -> tuple[list[str], int]:
    out: list[str] = []
    fixes = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        open_match = FENCE_OPEN.match(line.strip())
        if not open_match:
            out.append(line)
            i += 1
            continue

        marker = open_match.group(1)
        lang = open_match.group(2) or ""
        body: list[str] = []
        j = i + 1
        closed = False
        while j < len(lines):
            close_match = FENCE_OPEN.match(lines[j].strip())
            if close_match and lines[j].strip().startswith(marker) and not close_match.group(2):
                closed = True
                break
            body.append(lines[j])
            j += 1

        if not closed:
            out.append(line)
            i += 1
            continue

        if not lang:
            lang = infer_fence_language("\n".join(body))
            fixes += 1
        open_line = f"{marker}{lang}"

        if out and out[-1].strip() != "":
            out.append("")
            fixes += 1

        out.append(open_line)
        out.extend(body)
        out.append(marker)

        after = j + 1
        if after < len(lines) and lines[after].strip() != "":
            out.append("")
            fixes += 1

        i = j + 1

    return out, fixes


def format_headings(lines: list[str]) -> tuple[list[str], int]:
    out: list[str] = []
    fixes = 0
    in_fence = False
    fence_marker = ""

    for idx, line in enumerate(lines):
        open_match = FENCE_OPEN.match(line.strip())
        if open_match:
            marker = open_match.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif line.strip().startswith(fence_marker) and not open_match.group(2):
                in_fence = False
                fence_marker = ""
            out.append(line)
            continue

        if in_fence or not HEADING.match(line):
            out.append(line)
            continue

        if out and out[-1].strip() != "":
            out.append("")
            fixes += 1

        out.append(line)

        nxt = lines[idx + 1] if idx + 1 < len(lines) else None
        if nxt is not None and nxt.strip() != "":
            out.append("")
            fixes += 1

    collapsed: list[str] = []
    blank_run = 0
    for line in out:
        if line.strip() == "":
            blank_run += 1
            if blank_run <= 1:
                collapsed.append("")
            else:
                fixes += 1
            continue
        blank_run = 0
        collapsed.append(line)

    return collapsed, fixes


def format_structure(text: str) -> tuple[str, dict[str, int]]:
    lines = text.splitlines()
    lines, fence_fixes = format_fences(lines)
    lines, heading_fixes = format_headings(lines)
    result = "\n".join(lines)
    if text.endswith("\n"):
        result += "\n"
    return result, {"fences": fence_fixes, "headings": heading_fixes}


def process_file(path: Path) -> int:
    if path.suffix.lower() not in {".md", ".markdown"}:
        print(f"format-md-structure: skip non-markdown {path}")
        return 0
    if not path.is_file():
        print(f"format-md-structure: missing file {path}", file=sys.stderr)
        return 2

    original = path.read_text(encoding="utf-8")
    updated, counts = format_structure(original)
    total = sum(counts.values())
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        detail = ", ".join(f"{k}={v}" for k, v in counts.items() if v)
        print(f"format-md-structure: fixed {total} issue(s) in {path} ({detail})")
    else:
        print(f"format-md-structure: ok {path}")
    return 0


def main() -> int:
    stdin_text = ""
    if not sys.stdin.isatty():
        stdin_text = sys.stdin.read()
    paths = resolve_paths(sys.argv, stdin_text)
    if not paths:
        print("format-md-structure: skip (no markdown paths)")
        return 0
    rc = 0
    for path in paths:
        rc = max(rc, process_file(path))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
