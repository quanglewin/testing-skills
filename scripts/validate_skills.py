#!/usr/bin/env python3
"""Validate the structural integrity of the skills in this repository.

Checks (all stdlib, no dependencies):
  1. SKILL.md frontmatter is well-formed (name, description present; name matches dir).
  2. allowed-tools covers every tool the SKILL.md body explicitly instructs the agent to use.
  3. Every rule file referenced in a SKILL.md exists on disk.
  4. Every rule file on disk is referenced by its skill's SKILL.md (no orphan rules).
  5. The duplicated general-rules directories are byte-identical
     (skills/generate-test-cases/rules/general <-> skills/generate-tests/rules/tests/general).
  6. Every rule file has frontmatter with `title:` and `impact:`.

Exit code 0 = all checks pass, 1 = at least one error. Warnings never fail the build
unless --strict is passed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
INTERNAL_DIR = REPO_ROOT / "internal"  # repo-internal skills, validated identically

SYNCED_DIRS = (
    SKILLS_DIR / "generate-test-cases" / "rules" / "general",
    SKILLS_DIR / "generate-tests" / "rules" / "tests" / "general",
)

# Tools whose use the body can explicitly request. We only match unambiguous
# mentions ("AskUserQuestion tool", "using the Write tool", "use the `Write` tool")
# to avoid false positives; the tool name may be wrapped in backticks or bold.
def _tool_mention(name: str, flags: int = re.IGNORECASE) -> re.Pattern[str]:
    return re.compile(rf"[`*]*{name}[`*]*\s+tool\b", flags)


TOOL_MENTION_PATTERNS = {
    "AskUserQuestion": re.compile(r"\bAskUserQuestion\b"),
    "Write": _tool_mention("Write"),
    "Edit": _tool_mention("Edit"),
    "Agent": _tool_mention("Agent", flags=0),
    "Bash": _tool_mention("Bash"),
}

RULE_REF_RE = re.compile(r"`(\.?/?[\w./-]+\.md)`")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

errors: list[str] = []
warnings: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def parse_frontmatter(text: str, path: Path) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        error(f"{rel(path)}: missing or malformed frontmatter block")
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip('"')
    return fields


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def body_of(text: str) -> str:
    match = FRONTMATTER_RE.match(text)
    return text[match.end():] if match else text


def resolve_rule_ref(ref: str, skill_dir: Path) -> Path | None:
    """Resolve a rule reference the way the skill instructions imply."""
    cleaned = ref.lstrip("./")
    candidates = [
        skill_dir / cleaned,
        skill_dir / "rules" / cleaned,
        skill_dir / "rules" / "tests" / cleaned,
        REPO_ROOT / cleaned,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    # Bare basename: search the skill's rules tree, then the eval harness
    if "/" not in cleaned:
        search_roots = [skill_dir / "rules", REPO_ROOT / "harness"]
        for root in search_roots:
            if root.is_dir():
                matches = sorted(root.rglob(cleaned))
                if matches:
                    return matches[0]
    return None


def check_skill(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        error(f"{rel(skill_dir)}: missing SKILL.md")
        return

    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text, skill_md)
    body = body_of(text)

    # 1. Frontmatter fields
    if not fm.get("name"):
        error(f"{rel(skill_md)}: frontmatter missing 'name'")
    elif fm["name"] != skill_dir.name:
        error(f"{rel(skill_md)}: frontmatter name '{fm['name']}' != directory '{skill_dir.name}'")
    if not fm.get("description"):
        error(f"{rel(skill_md)}: frontmatter missing 'description'")

    # 2. allowed-tools vs body tool usage
    allowed = {t.strip() for t in fm.get("allowed-tools", "").split(",") if t.strip()}
    if allowed:
        for tool, pattern in TOOL_MENTION_PATTERNS.items():
            if tool not in allowed and pattern.search(body):
                error(
                    f"{rel(skill_md)}: body instructs use of '{tool}' "
                    f"but frontmatter allowed-tools omits it"
                )
    else:
        warn(f"{rel(skill_md)}: no allowed-tools declared")

    # 3. Referenced rule files must exist
    referenced_basenames: set[str] = set()
    for ref in RULE_REF_RE.findall(body):
        if ref.endswith("SKILL.md") or ref.endswith(("MEMORY.md",)):
            continue
        resolved = resolve_rule_ref(ref, skill_dir)
        if resolved is None:
            error(f"{rel(skill_md)}: references '{ref}' which does not exist")
        else:
            referenced_basenames.add(resolved.name)

    # 4. No orphan rule files
    rules_dir = skill_dir / "rules"
    if rules_dir.is_dir():
        for rule_file in sorted(rules_dir.rglob("*.md")):
            if rule_file.name not in referenced_basenames and rule_file.name not in body:
                error(f"{rel(rule_file)}: not referenced anywhere in {rel(skill_md)}")

            # 6. Rule frontmatter
            rule_fm = parse_frontmatter(rule_file.read_text(encoding="utf-8"), rule_file)
            for field in ("title", "impact"):
                if not rule_fm.get(field):
                    error(f"{rel(rule_file)}: rule frontmatter missing '{field}'")


def check_general_rules_sync() -> None:
    dir_a, dir_b = SYNCED_DIRS
    if not dir_a.is_dir() or not dir_b.is_dir():
        error(f"synced rule directory missing: {rel(dir_a)} or {rel(dir_b)}")
        return
    names_a = {p.name for p in dir_a.glob("*.md")}
    names_b = {p.name for p in dir_b.glob("*.md")}
    for name in sorted(names_a - names_b):
        error(f"{name}: exists in {rel(dir_a)} but missing from {rel(dir_b)}")
    for name in sorted(names_b - names_a):
        error(f"{name}: exists in {rel(dir_b)} but missing from {rel(dir_a)}")
    for name in sorted(names_a & names_b):
        if (dir_a / name).read_bytes() != (dir_b / name).read_bytes():
            error(
                f"{name}: content differs between {rel(dir_a)} and {rel(dir_b)} "
                f"— general rules must stay in sync (see CLAUDE.md)"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()

    if not SKILLS_DIR.is_dir():
        print(f"ERROR: skills directory not found at {SKILLS_DIR}", file=sys.stderr)
        return 1

    skill_dirs = [p for root in (SKILLS_DIR, INTERNAL_DIR) if root.is_dir()
                  for p in sorted(root.iterdir()) if p.is_dir()]
    for skill_dir in skill_dirs:
        check_skill(skill_dir)
    check_general_rules_sync()

    for msg in warnings:
        print(f"WARN  {msg}")
    for msg in errors:
        print(f"ERROR {msg}")

    failed = bool(errors) or (args.strict and bool(warnings))
    print(
        f"\nvalidate_skills: {len(skill_dirs)} skills checked, "
        f"{len(errors)} error(s), {len(warnings)} warning(s) — "
        f"{'FAIL' if failed else 'OK'}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
