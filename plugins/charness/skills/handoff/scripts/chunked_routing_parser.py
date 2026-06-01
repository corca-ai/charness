"""Parser for the handoff ``## Next Session`` block.

Splits a handoff markdown body into ``HandoffEntry`` records carrying
referenced paths, issues, skills, and non-trivial boundary tokens used
by the merge proposer downstream.
"""
import importlib.util
import re
from pathlib import Path


def _load_sibling_types():
    spec = importlib.util.spec_from_file_location(
        "chunked_routing_types",
        Path(__file__).resolve().parent / "chunked_routing_types.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError(
            "chunked_routing_types.py not found beside chunked_routing_parser.py"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_types = _load_sibling_types()
HandoffEntry = _types.HandoffEntry
is_nontrivial_token = _types.is_nontrivial_token


_H2 = re.compile(r"^## (.+?)\s*$", re.MULTILINE)
_NEXT_SESSION_HEADER = "Next Session"
_NUMBERED_BULLET = re.compile(r"^(\d+)\.\s+(.*)$")
_BOLD_TITLE = re.compile(r"^\*\*(.+?)\*\*", re.DOTALL)
_MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_ISSUE_REF = re.compile(r"#(\d+)\b")
_SKILL_PATH = re.compile(r"skills/(?:public|support|profile)/([a-z0-9-]+)")
_GOAL_STATUS = re.compile(r"^Status:\s*([A-Za-z0-9_-]+)\s*$", re.MULTILINE)
_BARE_PATH = re.compile(
    r"(?<![\w/])("
    # file with extension: at least one path segment then file.ext
    r"(?:[a-z0-9_.-]+/)+[a-z0-9_.-]+\.[a-z]{1,6}"
    r"|"
    # multi-segment directory token: ≥2 segments ending in /
    r"(?:[a-z0-9_.-]+/){2,}"
    r")"
)
_WHITESPACE = re.compile(r"\s+")
_LOCAL_STATE_COMMANDS = ("git status", "git log", "gh issue list")
_PREFLIGHT_STATE_TERMS = ("local", "branch", "repo", "worktree", "open issue")
_GOAL_ACTIVATION_TOKENS = ("`/goal @", "`/achieve @", "/goal @", "/achieve @")
_ACTIVATION_WORDS = ("activate", "continue", "resume", "run", "start")
_CONSTRAINT_VERBS = ("enforce", "follow", "keep", "maintain", "preserve", "use")
_CONSTRAINT_NOUNS = ("cadence", "constraint", "invariant")


def extract_next_session_block(text: str) -> str:
    """Return the body of ``## Next Session`` from the handoff markdown.

    Returns an empty string if the section is absent.
    """
    headings = list(_H2.finditer(text))
    for index, match in enumerate(headings):
        if match.group(1).strip() != _NEXT_SESSION_HEADER:
            continue
        body_start = text.find("\n", match.start())
        body_start = body_start + 1 if body_start != -1 else match.end()
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        return text[body_start:body_end]
    return ""


def _split_numbered_items(block: str) -> list[tuple[int, str]]:
    """Split a numbered-list block into ``(index, raw_text)`` tuples."""
    items: list[tuple[int, str]] = []
    current_lines: list[str] = []
    current_index: int | None = None
    for line in block.splitlines():
        match = _NUMBERED_BULLET.match(line)
        if match:
            if current_index is not None:
                items.append((current_index, "\n".join(current_lines).rstrip()))
            current_index = int(match.group(1))
            current_lines = [match.group(2)]
        else:
            if current_index is not None:
                current_lines.append(line)
    if current_index is not None:
        items.append((current_index, "\n".join(current_lines).rstrip()))
    return items


def _extract_title(raw_text: str) -> tuple[str, str]:
    """Split a numbered-bullet body into ``(title, remaining_body)``.

    The title is the leading ``**Bold Title.**`` phrase, with internal
    whitespace collapsed (so a soft-wrapped bold title returns as one
    line). When there is no bold-leading marker, the first sentence
    (up to the first period) is the title and the full text is preserved
    as body.
    """
    stripped = raw_text.strip()
    bold_match = _BOLD_TITLE.match(stripped)
    if bold_match:
        raw_title = bold_match.group(1).rstrip(".").strip()
        title = _WHITESPACE.sub(" ", raw_title)
        remainder = stripped[bold_match.end():].lstrip()
        return title, remainder
    period = stripped.find(".")
    if period == -1:
        return stripped, stripped
    return _WHITESPACE.sub(" ", stripped[:period].strip()), stripped


def _collect_paths(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return ``(markdown_link_targets, bare_path_tokens)`` from ``text``.

    Markdown link targets are deduped in first-seen order. Bare path tokens
    are extension-bearing or trailing-slash directory tokens; URLs (anything
    with a scheme) are excluded.
    """
    link_targets: list[str] = []
    seen_links: set[str] = set()
    for target in _MARKDOWN_LINK.findall(text):
        cleaned = target.split("#", 1)[0].split(" ", 1)[0]
        if cleaned.startswith(("http://", "https://", "mailto:")):
            continue
        if cleaned not in seen_links:
            seen_links.add(cleaned)
            link_targets.append(cleaned)
    bare: list[str] = []
    seen_bare: set[str] = set()
    for match in _BARE_PATH.finditer(text):
        token = match.group(1)
        if token in seen_bare:
            continue
        seen_bare.add(token)
        bare.append(token)
    return tuple(link_targets), tuple(bare)


def _normalize_path(token: str) -> str:
    """Strip ``../`` and ``./`` prefixes so two link forms canonicalize."""
    stripped = token.strip()
    while stripped.startswith(("./", "../")):
        if stripped.startswith("./"):
            stripped = stripped[2:]
        else:
            stripped = stripped[3:]
    return stripped


def _collect_issues(text: str) -> tuple[int, ...]:
    seen: list[int] = []
    seen_set: set[int] = set()
    for match in _ISSUE_REF.finditer(text):
        number = int(match.group(1))
        if number not in seen_set:
            seen_set.add(number)
            seen.append(number)
    return tuple(seen)


def _collect_skills(paths: tuple[str, ...]) -> tuple[str, ...]:
    """Return canonical ``skills/public/<id>/`` tokens from referenced paths."""
    seen: list[str] = []
    seen_set: set[str] = set()
    for path in paths:
        normalized = _normalize_path(path)
        match = _SKILL_PATH.search(normalized)
        if not match:
            continue
        skill_id = match.group(1)
        canonical = f"skills/public/{skill_id}/"
        if canonical not in seen_set:
            seen_set.add(canonical)
            seen.append(canonical)
    return tuple(seen)


def _build_boundary_tokens(
    referenced_paths: tuple[str, ...], referenced_skills: tuple[str, ...]
) -> tuple[str, ...]:
    """Return the deduped non-trivial token set used for merge proposals."""
    seen: list[str] = []
    seen_set: set[str] = set()
    candidates = list(referenced_paths) + list(referenced_skills)
    for raw in candidates:
        token = _normalize_path(raw)
        if not is_nontrivial_token(token):
            continue
        if token in seen_set:
            continue
        seen_set.add(token)
        seen.append(token)
    return tuple(seen)


def _is_operator_preflight(title: str, raw_text: str) -> bool:
    """Return True for pickup checks that are not selectable work chunks."""
    normalized = _WHITESPACE.sub(" ", f"{title} {raw_text}".lower())
    if not any(command in normalized for command in _LOCAL_STATE_COMMANDS):
        return False
    title_normalized = _WHITESPACE.sub(" ", title.lower())
    if not title_normalized.startswith(("verify", "check", "refresh")):
        return False
    return any(term in title_normalized for term in _PREFLIGHT_STATE_TERMS)


def _is_execution_constraint(title: str, raw_text: str) -> bool:
    """Return True for sequencing constraints that should shape a chosen chunk."""
    normalized = _WHITESPACE.sub(" ", f"{title} {raw_text}".lower())
    if not normalized.startswith(("during ", "while ")):
        return False
    return (
        any(verb in normalized for verb in _CONSTRAINT_VERBS)
        and any(noun in normalized for noun in _CONSTRAINT_NOUNS)
    )


def _goal_status(repo_root: Path | None, referenced_path: str) -> str | None:
    if repo_root is None:
        return None
    root = repo_root.resolve()
    path = (root / referenced_path).resolve()
    try:
        if root not in path.parents and path != root:
            return None
    except RuntimeError:
        return None
    if not path.is_file():
        return None
    match = _GOAL_STATUS.search(path.read_text(encoding="utf-8"))
    return match.group(1).strip().lower() if match else None


def _is_completed_goal_activation(
    raw_text: str,
    referenced_paths: tuple[str, ...],
    *,
    repo_root: Path | None,
) -> bool:
    """Return True when an activation entry points at an already complete goal."""
    normalized = raw_text.lower()
    looks_like_activation = (
        any(token in normalized for token in _GOAL_ACTIVATION_TOKENS)
        or any(word in normalized for word in _ACTIVATION_WORDS)
    )
    if not looks_like_activation:
        return False
    for referenced_path in referenced_paths:
        if not referenced_path.startswith("charness-artifacts/goals/"):
            continue
        if _goal_status(repo_root, referenced_path) == "complete":
            return True
    return False


def parse_handoff_entries(
    text: str, *, repo_root: Path | None = None
) -> list[HandoffEntry]:
    """Parse the ``## Next Session`` block of a handoff markdown body."""
    block = extract_next_session_block(text)
    if not block.strip():
        return []
    entries: list[HandoffEntry] = []
    for index, raw_text in _split_numbered_items(block):
        title, body = _extract_title(raw_text)
        link_paths, bare_paths = _collect_paths(raw_text)
        # Dedup after normalization so `../foo.md` and `foo.md` count once.
        normalized_paths: list[str] = []
        seen_normalized: set[str] = set()
        for token in list(link_paths) + list(bare_paths):
            canonical = _normalize_path(token)
            if canonical in seen_normalized:
                continue
            seen_normalized.add(canonical)
            normalized_paths.append(canonical)
        referenced_issues = _collect_issues(raw_text)
        referenced_skills = _collect_skills(tuple(normalized_paths))
        boundary_tokens = _build_boundary_tokens(
            tuple(normalized_paths), referenced_skills
        )
        if _is_operator_preflight(title, raw_text):
            continue
        if _is_execution_constraint(title, raw_text):
            continue
        if _is_completed_goal_activation(
            raw_text, tuple(normalized_paths), repo_root=repo_root
        ):
            continue
        entries.append(
            HandoffEntry(
                index=index,
                title=title,
                body=body,
                referenced_paths=tuple(normalized_paths),
                referenced_issues=referenced_issues,
                referenced_skills=referenced_skills,
                boundary_tokens=boundary_tokens,
            )
        )
    return entries
