"""Refuse transcribed facts on FORWARD-LOOKING prose surfaces.

A number in prose is read as current. When a command can regenerate it, the prose
should carry the COMMAND, not the command's output -- otherwise the number is true
on the day it is written and misleading every day after, and the next reader acts
on it instead of checking.

The seam, which decides whether a surface is in scope at all:

- **Dated, append-only RECORDS** -- retros, critiques, audits, slice logs, commit
  messages. A number there describes one moment that will never be true again, and
  that is exactly what it is for. OUT OF SCOPE, permanently, not by grandfather.
- **Rolling, FORWARD-LOOKING surfaces** -- agent prompt files, conventions, docs,
  skill prose. A number there is read as today's answer. IN SCOPE.

Two ways to satisfy it, and the difference is what the command COSTS:

- A CHEAP command (`git describe`, `gh issue list`, a grep): carry the command
  alone. The reader runs it and gets today's answer for nothing.
- An EXPENSIVE command (a multi-minute suite, a fan-out census, a full-corpus
  sweep): carry the command AND link the checked-in artifact holding its output.
  Telling a reader to re-run an expensive gate to learn one number is not a fix --
  it moves the cost onto every future reader, forever. The artifact is the
  provenance: it records what was run, when, and against what, so the prose links
  it instead of copying numbers out of it.

Portability: nothing here guesses whether an arbitrary `docs/` tree is a current
manual or a historical ledger. Unconfigured defaults cover only canonical
forward-looking entrypoints and shipped skill instructions. Repos opt their docs
tree in through the quality adapter, where they can state its actual record seam.
A consumer's exemptions belong in that consumer's adapter, never in this shipped
file.
"""

from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path

try:
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir))
    from scripts.core.subprocess_guard import run_process

sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_inventory_lib import visible_repo_files  # noqa: E402

RULE_TEXT = (
    "A number in prose is read as current. When a command can regenerate it, the prose "
    "should carry the COMMAND, not the command's output."
)

STAGED_SURFACES = (
    "AGENTS.md",
    "README.md",
    "docs/**/*.md",
)
STAGED_DOCS_PREFIX = STAGED_SURFACES[2].split("**", 1)[0]

# Conservative surfaces a reader can treat as current without knowing the repo's
# documentation taxonomy. An arbitrary docs tree is deliberately NOT a default:
# real consumers keep retros, requests, completed implementation records, and
# lessons there, so a recursive docs default made a hard gate fail historical
# facts while claiming those records were outside its scope.
DEFAULT_SURFACES = (
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "skills/*/*/SKILL.md",
    "skills/*/*/references/*.md",
)

FENCE_RE = re.compile(r"^\s*```")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
LINK_TARGET_RE = re.compile(r"(?<=\])\([^)]*\)")
URL_RE = re.compile(r"<?\bhttps?://\S+>?")

# Each pattern pairs the literal class with the replacement the author should
# write instead, because a refusal that does not say what to do trains avoidance.
PATTERNS = (
    (
        re.compile(r"\b(?:v\d+\.\d+(?:\.\d+)?|\d+\.\d+\.\d+)\b"),
        "a release or tool version",
        "carry `git describe --tags --abbrev=0`, or link the release artifact",
    ),
    (
        re.compile(
            r"\b(?=[0-9a-f]{7,40}\b)(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{7,40}\b",
            re.IGNORECASE,
        ),
        "a commit sha",
        "carry `git rev-parse --short HEAD`, or link the commit",
    ),
    (
        re.compile(
            # The number must END in a digit. An identifier list -- `24, issue 13` --
            # is not a count, and `[\d,]*` alone swallowed the comma and matched it.
            r"(?<![#\w.\-])\d(?:[\d,]*\d)?\s+(?:commits?|issues?|files?|tests?|lines?|artifacts?|skills?|checks?|entries|findings?)\b",
            re.IGNORECASE,
        ),
        "an as-of count",
        "carry the command that recounts it, or link the artifact that measured it",
    ),
)


def scrub(line: str) -> str:
    """Remove the spans the rule asks the author to WRITE.

    Fenced blocks, inline code, link targets, and URLs carry commands and paths.
    Refusing a number inside them would reject the replacement the rule just
    recommended. Link TEXT stays in scope: that is prose a reader believes.
    """
    for pattern in (INLINE_CODE_RE, LINK_TARGET_RE, URL_RE):
        line = pattern.sub(" ", line)
    return line


def scan_text(text: str) -> list[tuple[int, str, str, str]]:
    hits: list[tuple[int, str, str, str]] = []
    in_fence = False
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        prose = scrub(raw)
        for pattern, label, remedy in PATTERNS:
            match = pattern.search(prose)
            if match:
                hits.append((lineno, match.group(0).strip(), label, remedy))
                break
    return hits


def staged_paths(repo_root: Path) -> list[str]:
    """Return paths present in the staged diff, or raise an actionable error."""
    try:
        completed = run_process(
            [
                "git",
                "-C",
                str(repo_root),
                "diff",
                "--cached",
                "--name-only",
                "--diff-filter=ACMRTUXBD",
                "-z",
            ],
            cwd=repo_root,
            timeout_seconds=None,
        )
    except OSError as exc:
        raise RuntimeError(f"could not inspect staged paths: {type(exc).__name__}: {exc}") from exc
    if completed.returncode:
        detail = completed.stderr.strip() or f"git exited {completed.returncode}"
        raise RuntimeError(f"could not inspect staged paths: {detail}")
    return [path for path in completed.stdout.split("\0") if path]


def staged_surface_paths(paths: list[str]) -> list[str]:
    """Keep only the three fixed commit-boundary prose surfaces."""
    return [
        path
        for path in paths
        if path in STAGED_SURFACES[:2]
        or (path.startswith(STAGED_DOCS_PREFIX) and path.endswith(".md"))
    ]


def _config(adapter: dict | None) -> dict:
    """Unwrap the adapter result envelope and return the `regenerable_facts` block.

    `load_adapter` returns `{found, valid, data}`, not the adapter body. Accepting
    a bare body too keeps this callable from a test or a host that unwrapped it.
    """
    adapter = adapter or {}
    body = adapter.get("data") if isinstance(adapter.get("data"), dict) else adapter
    return (body or {}).get("regenerable_facts") or {}


def declared_surfaces(adapter: dict | None) -> bool:
    """Did the repo CHOOSE this scope, or is it running on defaults?

    The difference decides what an empty scan means. A repo that declared its
    surfaces and matched nothing has a broken config and must be told. A repo
    that never configured the gate and matched nothing has no forward-looking
    prose at the default locations -- that is "no gate here", which is honest to
    report and wrong to fail on, because failing would make the gate hostile on
    install in every consumer.
    """
    return "surfaces" in _config(adapter)


def resolve_config(adapter: dict | None) -> tuple[tuple[str, ...], dict[str, str]]:
    """Read surfaces and exemptions from the consuming repo's adapter.

    `load_adapter` returns a RESULT envelope (`found`/`valid`/`data`), not the
    adapter body, so the config is read from `data` when that shape is present.
    Accepting the bare body too keeps this callable from a test or a host that
    already unwrapped it.
    """
    config = _config(adapter)
    surfaces = tuple(config.get("surfaces") or ()) if "surfaces" in config else DEFAULT_SURFACES
    exemptions = dict(config.get("exemptions") or {})
    return surfaces, exemptions


def _reason_text(reason: object) -> str:
    return reason.strip() if isinstance(reason, str) else ""


def exemption_for(rel: str, exemptions: dict[str, str]) -> str | None:
    """Return the RECORDED reason, or None when there is not a real one.

    A whitespace-only or non-string reason is treated as absent rather than
    honoured: it would otherwise be an invisible exemption, which is the
    unfalsifiable claim this rule exists to remove.
    """
    for pattern, reason in exemptions.items():
        if rel == pattern or fnmatch.fnmatch(rel, pattern):
            return _reason_text(reason) or None
    return None


def visible_matching_files(repo_root: Path, surfaces: tuple[str, ...]) -> list[Path]:
    """Return the in-scope files, sourced from git rather than a bare tree walk.

    A filesystem walk reads `node_modules/`, `vendor/`, and build output -- files
    no reader treats as this repo's forward-looking prose and the author cannot
    fix. `visible_repo_files` runs `git ls-files --cached --others
    --exclude-standard`, so gitignored paths never enter the candidate set. When
    git is unavailable the glob stands alone, because scanning nothing would be a
    worse answer than scanning a superset.
    """
    try:
        visible = visible_repo_files(repo_root)
    except Exception:  # noqa: BLE001 - a repo without git still gets a scan
        visible = None
    matched: list[Path] = []
    seen: set[Path] = set()
    for pattern in surfaces:
        for path in sorted(repo_root.glob(pattern)):
            if not path.is_file() or path in seen:
                continue
            if visible is not None and path.resolve() not in visible:
                continue
            seen.add(path)
            matched.append(path)
    return matched


def scan_repo(repo_root: Path, adapter: dict | None = None) -> dict:
    surfaces, exemptions = resolve_config(adapter)
    declared = declared_surfaces(adapter)
    findings: list[dict[str, object]] = []
    exempted: list[dict[str, str]] = []
    checked = 0
    for path in visible_matching_files(repo_root, surfaces):
        rel = path.relative_to(repo_root).as_posix()
        reason = exemption_for(rel, exemptions)
        if reason is not None:
            exempted.append({"path": rel, "reason": reason})
            continue
        checked += 1
        for lineno, literal, label, remedy in scan_text(
            path.read_text(encoding="utf-8", errors="ignore")
        ):
            findings.append(
                {"path": rel, "line": lineno, "literal": literal, "label": label, "remedy": remedy}
            )
    unclassified_docs = []
    if not declared:
        checked_paths = {
            path.relative_to(repo_root).as_posix()
            for path in visible_matching_files(repo_root, surfaces)
        }
        unclassified_docs = sorted(
            path.relative_to(repo_root).as_posix()
            for path in visible_matching_files(repo_root, ("docs/*.md", "docs/**/*.md"))
            if path.relative_to(repo_root).as_posix() not in checked_paths
        )
    return {
        "declared": declared,
        "checked": checked,
        "surfaces": list(surfaces),
        "exempted": exempted,
        "findings": findings,
        # A conservative default cannot classify an arbitrary docs tree. Carry
        # that population to the final renderer so a clean README never turns
        # skipped current handoff prose into a terminal green.
        "unclassified_docs": unclassified_docs,
        # An exemption without a stated reason is the same unfalsifiable claim the
        # rule exists to remove, so it is reported rather than honoured silently.
        "unreasoned_exemptions": sorted(p for p, r in exemptions.items() if not _reason_text(r)),
    }


def staged_blob_text(repo_root: Path, rel: str) -> str:
    """The bytes GIT WILL COMMIT for `rel`, read from the index rather than disk.

    A partially staged file makes the two differ, and the commit-boundary advisory
    is about the commit: reading the worktree could hide a staged finding behind an
    unstaged repair, or report a line number that exists in no commit. `git show
    :<path>` is the index copy by definition.
    """
    completed = run_process(
        ["git", "-C", str(repo_root), "show", f":{rel}"],
        cwd=repo_root,
        timeout_seconds=None,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or f"git exited {completed.returncode}"
        raise RuntimeError(f"could not read the staged copy of {rel}: {detail}")
    return completed.stdout


def scan_paths(
    repo_root: Path, paths: list[str], adapter: dict | None = None, *, from_index: bool = False
) -> dict:
    """Scan an explicit path list with the same detector used by ``scan_repo``."""
    _surfaces, exemptions = resolve_config(adapter)
    findings: list[dict[str, object]] = []
    exempted: list[dict[str, str]] = []
    unavailable: list[dict[str, str]] = []
    checked = 0
    for rel in paths:
        path = repo_root / rel
        reason = exemption_for(rel, exemptions)
        if reason is not None:
            exempted.append({"path": rel, "reason": reason})
            continue
        try:
            text = (
                staged_blob_text(repo_root, rel)
                if from_index
                else path.read_text(encoding="utf-8", errors="ignore")
            )
        except (OSError, RuntimeError) as exc:
            unavailable.append({"path": rel, "reason": f"{type(exc).__name__}: {exc}"})
            continue
        checked += 1
        for lineno, literal, label, remedy in scan_text(text):
            findings.append(
                {"path": rel, "line": lineno, "literal": literal, "label": label, "remedy": remedy}
            )
    return {
        "checked": checked,
        "exempted": exempted,
        "findings": findings,
        "unavailable": unavailable,
    }
