#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import re
import shlex
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.skill_markdown_lib import count_fence_blocks, extract_h2_section_lines
from scripts.skill_portability_lib import find_portability_errors
REQUIRED_FRONTMATTER_KEYS = ("name", "description")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_SKILL_MD_LINES = 200
MAX_PUBLIC_FENCE_BLOCKS_WITHOUT_SCRIPTS = 2

# CHARNESS_BASELINE: commands a public skill may call in its Bootstrap block
# without declaring them. See create-skill/references/binary-preflight.md.
CHARNESS_BASELINE = frozenset({
    "sh", "bash", "dash", "zsh",
    "if", "then", "else", "elif", "fi", "for", "while", "until",
    "do", "done", "case", "esac", "in", "function", "select",
    "git", "python", "python3",
    "sed", "find", "awk", "grep", "cut", "tr", "sort", "uniq", "wc",
    "head", "tail", "diff", "cmp", "paste", "join", "tee", "xargs", "seq",
    "echo", "cat", "ls", "mkdir", "rmdir", "cp", "mv", "rm", "ln", "touch",
    "pwd", "printf", "true", "false", "test", "expr", "date", "env",
    "basename", "dirname", "readlink", "realpath", "sleep",
    "command", "type", "which", "read", "exit", "return", "set", "unset",
    "export", "eval", "trap", "source", "local", "shift", "getopts",
    "[", "]", "[[", "]]", ":",
})

BOOTSTRAP_HEADING_RE = re.compile(r"^##\s+Bootstrap\s*$")
NEXT_SECTION_RE = re.compile(r"^##\s+\S")
FENCE_OPEN_RE = re.compile(r"^```(?:bash|sh)?\s*$")
FENCE_CLOSE_RE = re.compile(r"^```\s*$")
REQUIRED_TOOLS_RE = re.compile(r"^\s*#\s*Required Tools:\s*(.+?)\s*$")
ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
SCRIPT_EXTENSION_RE = re.compile(r"\.(sh|bash|zsh|py|js|ts|rb|pl|lua|rs|go|json|yaml|yml|md)$")
REDIRECT_PREFIX_RE = re.compile(r"^[0-9]*[<>&]")
NUMERIC_RE = re.compile(r"^[0-9]+$")
COMMAND_SEPARATORS = frozenset({"|", "||", "&&", ";", "&"})


class ValidationError(Exception):
    pass

def extract_frontmatter(contents: str) -> list[str]:
    lines = contents.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        raise ValidationError("missing YAML frontmatter delimited by ---")

    frontmatter: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            if not frontmatter:
                raise ValidationError("frontmatter is empty")
            return frontmatter
        frontmatter.append(line)
    raise ValidationError("frontmatter is missing closing --- delimiter")
def parse_frontmatter(path: Path) -> dict[str, str]:
    contents = path.read_text(encoding="utf-8")
    lines = extract_frontmatter(contents)
    data: dict[str, str] = {}
    for index, raw in enumerate(lines, start=2):
        if not raw.strip():
            continue
        if ":" not in raw:
            raise ValidationError(f"invalid YAML-like frontmatter line {index}: missing ':'")
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValidationError(f"invalid YAML-like frontmatter line {index}: empty key")
        if not value:
            raise ValidationError(f"invalid YAML-like frontmatter line {index}: empty value")
        data[key] = value
    for key in REQUIRED_FRONTMATTER_KEYS:
        if key not in data:
            raise ValidationError(f"missing field `{key}`")
    return data
def validate_quoted_string(field: str, value: str) -> None:
    if len(value) < 2 or not (value.startswith('"') and value.endswith('"')):
        raise ValidationError(
            f"`{field}` must be double-quoted so standard YAML parsers accept punctuation safely"
        )
def validate_frontmatter(path: Path) -> None:
    data = parse_frontmatter(path)
    name = data["name"]
    if not SKILL_NAME_RE.fullmatch(name):
        raise ValidationError("`name` must be a lowercase slug")
    if name != path.parent.name:
        raise ValidationError(f"`name` must match directory name `{path.parent.name}`")

    validate_quoted_string("description", data["description"])
def extract_bootstrap_fences(contents: str) -> list[tuple[int, list[str]]]:
    """Return `(first_line_index, lines_inside_fence)` tuples for the fenced
    code blocks under the `## Bootstrap` heading. Line indices are 1-based.
    """
    lines = contents.splitlines()
    bootstrap_start: int | None = None
    for i, line in enumerate(lines):
        if BOOTSTRAP_HEADING_RE.match(line):
            bootstrap_start = i
            break
    if bootstrap_start is None:
        return []
    next_section = len(lines)
    for i in range(bootstrap_start + 1, len(lines)):
        if NEXT_SECTION_RE.match(lines[i]):
            next_section = i
            break
    fences: list[tuple[int, list[str]]] = []
    i = bootstrap_start + 1
    while i < next_section:
        if FENCE_OPEN_RE.match(lines[i]):
            fence_body_start = i + 1
            j = fence_body_start
            while j < next_section and not FENCE_CLOSE_RE.match(lines[j]):
                j += 1
            fences.append((fence_body_start + 1, lines[fence_body_start:j]))
            i = j + 1
        else:
            i += 1
    return fences
def tokenize_shell_line(line: str) -> list[str]:
    try:
        return shlex.split(line, comments=False, posix=True)
    except ValueError:
        return line.split()
def classify_command_token(tok: str) -> str | None:
    """Return a baseline-comparable command name, or None for non-commands."""
    if not tok:
        return None
    tok = tok.lstrip("!")
    if tok in ("{", "}", "(", ")", "!"):
        return None
    if ENV_ASSIGN_RE.match(tok):
        return None
    if REDIRECT_PREFIX_RE.match(tok):
        return None
    if NUMERIC_RE.match(tok):
        return None
    if "/" in tok:
        base = tok.rsplit("/", 1)[-1]
        if SCRIPT_EXTENSION_RE.search(base):
            return None
        return base or None
    return tok
def non_baseline_commands_in_line(line: str) -> set[str]:
    tokens = tokenize_shell_line(line)
    if not tokens:
        return set()
    non_base: set[str] = set()
    expect_command = True
    for tok in tokens:
        if expect_command:
            if ENV_ASSIGN_RE.match(tok):
                continue
            name = classify_command_token(tok)
            if name and name not in CHARNESS_BASELINE:
                non_base.add(name)
            expect_command = False
        if tok in COMMAND_SEPARATORS:
            expect_command = True
    return non_base
def has_swallow_pattern(line: str) -> bool:
    """Detect `2>/dev/null` or `|| true` / `|| :` shell-operator swallows."""
    if "2>/dev/null" in line:
        return True
    tokens = tokenize_shell_line(line)
    for i, tok in enumerate(tokens):
        if tok == "||" and i + 1 < len(tokens) and tokens[i + 1] in ("true", ":"):
            return True
    return False


def validate_bootstrap_binary_preflight(contents: str) -> None:
    """Enforce the Binary Preflight contract on public SKILL.md Bootstrap
    fences. See create-skill/references/binary-preflight.md for the contract.
    """
    fences = extract_bootstrap_fences(contents)
    if not fences:
        return
    any_declared = False
    for fence_start_line, fence_lines in fences:
        declared: set[str] = set()
        detected: set[str] = set()
        swallow_errors: list[str] = []
        for offset, raw in enumerate(fence_lines):
            line_num = fence_start_line + offset
            declaration_match = REQUIRED_TOOLS_RE.match(raw)
            if declaration_match:
                declared.update(
                    tool.strip()
                    for tool in declaration_match.group(1).split(",")
                    if tool.strip()
                )
                continue
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            non_base = non_baseline_commands_in_line(raw)
            if not non_base:
                continue
            detected.update(non_base)
            if has_swallow_pattern(raw):
                swallow_errors.append(
                    f"Bootstrap line {line_num}: non-baseline "
                    f"{', '.join(sorted(non_base))} wrapped in "
                    f"`|| true` / `2>/dev/null` swallow; rewrite without the "
                    f"swallow or guard with a `command -v` sentinel (see "
                    f"`create-skill/references/binary-preflight.md`)"
                )
        if swallow_errors:
            raise ValidationError("; ".join(swallow_errors))
        missing = detected - declared
        if missing:
            bins = ", ".join(sorted(missing))
            raise ValidationError(
                f"Bootstrap fence at line {fence_start_line} calls non-baseline "
                f"binary/binaries `{bins}` without a `# Required Tools:` "
                f"declaration inside the same fence"
            )
        unused = declared - detected
        if unused:
            bins = ", ".join(sorted(unused))
            raise ValidationError(
                f"Bootstrap fence at line {fence_start_line} declares "
                f"`# Required Tools: {bins}` but the fence never calls it; "
                f"remove the declaration or add the usage"
            )
        if declared:
            any_declared = True
    if any_declared and "binary-preflight" not in contents:
        raise ValidationError(
            "`# Required Tools:` is declared but SKILL.md body has no "
            "`binary-preflight` pointer; add a prose reference to "
            "`create-skill/references/binary-preflight.md`"
        )


def validate_portable_skill_invocations(root: Path, skill_dir: Path, contents: str) -> None:
    errors = find_portability_errors(root, skill_dir, contents)
    if errors:
        raise ValidationError("; ".join(errors))


def validate_support_files(root: Path, skill_dir: Path, kind: str) -> None:
    skill_md = skill_dir / "SKILL.md"
    contents = skill_md.read_text(encoding="utf-8")
    lines = contents.splitlines()

    if len(lines) > MAX_SKILL_MD_LINES:
        raise ValidationError(
            f"SKILL.md should stay concise; move detail into references before it grows past {MAX_SKILL_MD_LINES} lines"
        )

    if "## References" not in contents:
        raise ValidationError("missing `## References` section")

    listed_reference_paths = [
        line.split("`")[1]
        for line in lines
        if line.startswith("- `references/")
    ]
    if not listed_reference_paths:
        raise ValidationError("`## References` must list at least one `references/...` file")

    for rel in re.findall(r"`((?:references|scripts)/[^`]+)`", contents):
        if not (skill_dir / rel).exists():
            raise ValidationError(f"referenced path `{rel}` does not exist")

    references_dir = skill_dir / "references"
    if references_dir.exists():
        existing_reference_paths = {
            str(path.relative_to(skill_dir))
            for path in references_dir.iterdir()
            if path.is_file()
        }
        missing_reference_listings = sorted(existing_reference_paths - set(listed_reference_paths))
        if missing_reference_listings:
            formatted = ", ".join(f"`{path}`" for path in missing_reference_listings)
            raise ValidationError(f"unlisted reference file(s): {formatted}")

    has_adapter_example = (skill_dir / "adapter.example.yaml").exists()
    has_scripts_dir = (skill_dir / "scripts").exists()
    bootstrap_fence_blocks = count_fence_blocks(extract_h2_section_lines(contents, "Bootstrap"))
    if has_adapter_example and not has_scripts_dir:
        raise ValidationError("adapter.example.yaml exists but scripts/ is missing")
    if has_adapter_example:
        for required in ("resolve_adapter.py", "init_adapter.py"):
            if not (skill_dir / "scripts" / required).exists():
                raise ValidationError(f"scripts/{required} is missing")

    if kind == "public" and bootstrap_fence_blocks > MAX_PUBLIC_FENCE_BLOCKS_WITHOUT_SCRIPTS and not has_scripts_dir:
        raise ValidationError(
            "public SKILL.md Bootstrap with 3+ fenced examples should move repeated ritual into `scripts/`; "
            "add a helper script or collapse the Bootstrap examples"
        )

    if kind == "public":
        validate_bootstrap_binary_preflight(contents)
        validate_portable_skill_invocations(root, skill_dir, contents)


SKILL_ROOTS = (
    ("public", Path("skills/public")),
    ("support", Path("skills/support")),
)


def iter_skill_dirs(root: Path) -> list[tuple[str, Path]]:
    skill_dirs: list[tuple[str, Path]] = []
    for kind, rel_root in SKILL_ROOTS:
        skill_root = root / rel_root
        if not skill_root.exists():
            continue
        for path in skill_root.iterdir():
            if path.is_dir() and path.name != "generated":
                skill_dirs.append((kind, path))
    return sorted(skill_dirs, key=lambda item: (item[0], item[1].name))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    skill_dirs = iter_skill_dirs(root)
    if not skill_dirs:
        print("No skill packages found.")
        return 0

    validated = 0
    public_validated = 0
    support_validated = 0
    for kind, skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            raise ValidationError(f"{skill_dir}: missing SKILL.md")
        try:
            validate_frontmatter(skill_md)
            validate_support_files(root, skill_dir, kind)
        except ValidationError as exc:
            raise ValidationError(f"{skill_md}: {exc}") from exc
        validated += 1
        if kind == "public":
            public_validated += 1
        else:
            support_validated += 1

    print(
        f"Validated {validated} skill packages "
        f"({public_validated} public, {support_validated} support)."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
