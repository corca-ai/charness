#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os.path
import re
import sys
from collections import defaultdict
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_doc_file_population = import_repo_module(__file__, "scripts.gates_support.doc_file_population")
DOC_GLOBS = _doc_file_population.DOC_GLOBS
RepoFileSnapshot = _doc_file_population.RepoFileSnapshot
iter_docs = _doc_file_population.iter_docs
iter_known_repo_paths = _doc_file_population.iter_known_repo_paths
iter_known_markdown_paths = _doc_file_population.iter_known_markdown_paths
_quality_adapter_module = import_repo_module(__file__, "scripts.adapters.quality_adapter_lib")
load_quality_adapter = _quality_adapter_module.load_quality_adapter
_markdown_doc_scan = import_repo_module(__file__, "scripts.core.markdown_doc_scan")
iter_doc_lines = _markdown_doc_scan.iter_doc_lines
classify_link_shape = _markdown_doc_scan.classify_link_shape
iter_link_targets = _markdown_doc_scan.iter_link_targets
resolve_relative_link = _markdown_doc_scan.resolve_relative_link
ABSOLUTE_LINK = _markdown_doc_scan.ABSOLUTE_LINK
BARE_LINK = _markdown_doc_scan.BARE_LINK
INERT_LINK = _markdown_doc_scan.INERT_LINK
_portable_command_carrier = import_repo_module(__file__, "scripts.gates_support.portable_command_carrier")
iter_unportable_command_targets = _portable_command_carrier.iter_unportable_command_targets

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
# Command-shaped references: `python3 scripts/x.py`, `bash scripts/x.sh`,
# `./scripts/x.sh`. The link checker skips fences and the backtick checker waves
# through any span containing whitespace, so a documented command is the syntax
# where a rename rots unseen -- in a fence and in an inline span alike.
COMMAND_TARGET_RE = re.compile(
    r"(?:^|[\s|(\"'=&;])(?:python3?\s+|bash\s+|sh\s+|\./)([A-Za-z0-9._<>/-]+\.(?:py|sh))"
)
PATH_TOKEN_RE = re.compile(
    r"\b(?:README\.md|(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]+\.md)(?:#[A-Za-z0-9._-]+)?\b"
)
BACKTICK_CONTENT_RE = re.compile(r"`([^`\n]+)`")
PATHY_TOKEN_RE = re.compile(r"^(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9_-]+\.[A-Za-z0-9._-]+$")
EXTENSION_TOKEN_RE = re.compile(r"^[A-Za-z0-9_.-]+\.[A-Za-z][A-Za-z0-9]{0,5}$")
PORTABLE_SKILL_KINDS = {"public", "support"}
# `<authoring-repo>/` is deliberately SEPARATE from `<repo-root>/`, not a synonym.
# `<repo-root>/` means "the tree the reader is operating on", so it is
# unverifiable from here and exempt by design. That exemption is what let 13
# broken commands accumulate: a reference to charness's OWN script wearing the
# consumer's placeholder is indistinguishable from a typo, to this gate and to a
# human. `<authoring-repo>/` says "this resolves in the charness repo, not
# yours" — which a consumer can read at a glance, and which
# `inventory_skill_script_references.py` can actually RESOLVE here instead of
# waving through.
# The companion inventory resolves `<authoring-repo>/<path>` against the full
# authoring tree, including `docs/` and `charness-artifacts/`. This keeps the
# placeholder a checked reference rather than a disclosure-only escape hatch.
PORTABLE_PLACEHOLDER_PREFIXES = (
    "<repo-root>/",
    "<plugin-dir>/",
    "<skill-dir>/",
    "<authoring-repo>/",
)
# The remedies, single-sourced so the author-time forecast (the rules mode of
# `check_doc_authoring_preflight.py`, i.e. running it with no `--path`) renders
# the SAME sentence this gate raises instead of restating it and drifting.
TREE_MARKER_REASONS = frozenset({"unmarked-tree", "portable-absolute"})
TREE_MARKER_REMEDY = (
    "name the tree it lives in: `<plugin-dir>/` when the file ships to consumers, "
    "`<authoring-repo>/` when it exists only in charness, `<repo-root>/` when it is "
    "the reader's own, `<skill-dir>/` for this skill's own package"
)
LINK_FORM_REMEDY = "use markdown links so renames do not rot"
BARE_INTERNAL_REF_REMEDY = "use markdown links in prose"
MISSING_COMMAND_TARGET_REMEDY = (
    "a documented command must name a runnable script, or use a `<repo-root>/...` "
    "placeholder when it only resolves in a consuming repo"
)
REPO_REFERENCE_PREFIXES = (
    ".agents/",
    "charness-artifacts/",
    "docs/",
    "evals/",
    "packaging/",
    "plugins/",
    "presets/",
    "profiles/",
    "scripts/",
    "skills/",
    "tests/",
)


class ValidationError(Exception):
    pass


def build_unique_basename_index(known_repo_paths: set[str], *, keep=None) -> dict[str, str]:
    # `keep` narrows what counts toward uniqueness, for callers resolving a
    # canonical source out of a listing that also carries generated mirrors.
    groups: dict[str, list[str]] = defaultdict(list)
    for rel_path in known_repo_paths:
        if keep is not None and not keep(rel_path):
            continue
        groups[os.path.basename(rel_path)].append(rel_path)
    return {name: paths[0] for name, paths in groups.items() if len(paths) == 1}


def build_known_directories(known_repo_paths: set[str]) -> set[str]:
    dirs: set[str] = set()
    for rel_path in known_repo_paths:
        parent = os.path.dirname(rel_path)
        while parent:
            dirs.add(parent)
            parent = os.path.dirname(parent)
    return dirs


def normalize_surface_token(candidate: str) -> str:
    token = candidate.split("#", 1)[0].strip().rstrip("/")
    while token.startswith("./"):
        token = token[2:]
    return token


def portable_skill_package_root(root: Path, doc: Path) -> Path | None:
    try:
        rel = doc.relative_to(root)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) >= 3 and parts[0] == "skills" and parts[1] in PORTABLE_SKILL_KINDS:
        package_root = root.joinpath(*parts[:3])
        if package_root.is_dir():
            return package_root
    if len(parts) >= 3 and parts[0:2] == ("skills", "shared"):
        package_root = root / "skills" / "shared"
        if package_root.is_dir():
            return package_root
    return None


def has_portable_placeholder(candidate: str) -> bool:
    return candidate.startswith(PORTABLE_PLACEHOLDER_PREFIXES)


def looks_like_repo_reference(candidate: str) -> bool:
    # `lstrip("./")` is a CHARACTER-set strip, not a prefix strip: it turned
    # `.agents/x.yaml` into `agents/x.yaml`, which matches no entry, so the
    # `.agents/` prefix in the list below could never fire -- on the most
    # consumer-relevant path family in these docs. Strip the `./` prefix only.
    stripped = candidate.split("#", 1)[0].strip()
    while stripped.startswith("./"):
        stripped = stripped[2:]
    return stripped.startswith(REPO_REFERENCE_PREFIXES)


def normalize_backtick_candidate(candidate: str) -> str | None:
    if not candidate or any(ch.isspace() for ch in candidate):
        return None
    bare = candidate.split("#", 1)[0].strip()
    if not bare or any(ch in bare for ch in "*?[]"):
        return None
    return bare


def load_canonical_markdown_surfaces(root: Path) -> set[str]:
    payload = load_quality_adapter(root)
    if payload.get("errors"):
        rendered = "; ".join(str(error) for error in payload["errors"])
        raise ValidationError(
            f"quality adapter errors while loading canonical markdown surfaces: {rendered}"
        )
    surfaces = payload.get("data", {}).get("canonical_markdown_surfaces", [])
    return {normalize_surface_token(surface) for surface in surfaces if isinstance(surface, str)}


def strip_inline_markup(line: str) -> str:
    without_links = MARKDOWN_LINK_RE.sub("", line)
    return INLINE_CODE_RE.sub("", without_links)


def strip_markdown_links(line: str) -> str:
    return MARKDOWN_LINK_RE.sub("", line)


def classify_prefixed_backtick(
    candidate: str, known_repo_paths: set[str], known_directories: set[str]
) -> str | None:
    stripped = candidate.rstrip("/")
    while stripped.startswith("./"):
        stripped = stripped[2:]
    if stripped in known_repo_paths or stripped in known_directories:
        return "prefix"
    return "missing-artifact" if looks_like_repo_reference(candidate) else None


def classify_pathlike_backtick(bare: str, known_repo_paths: set[str]) -> str | None:
    if PATHY_TOKEN_RE.match(bare) and bare in known_repo_paths:
        return "pathy"
    if "/" not in bare:
        return None
    if not PATHY_TOKEN_RE.match(bare):
        return None
    return "missing-artifact" if looks_like_repo_reference(bare) else None


def iter_bare_internal_doc_refs(
    root: Path,
    doc: Path,
    known_markdown_paths: set[str],
    canonical_markdown_surfaces: set[str],
) -> list[str]:
    matches: list[str] = []
    for _lineno, line, in_fence in iter_doc_lines(doc):
        if in_fence:
            continue
        scrubbed = strip_inline_markup(line)
        for match in PATH_TOKEN_RE.findall(scrubbed):
            candidate = match.split("#", 1)[0]
            if normalize_surface_token(candidate) in canonical_markdown_surfaces:
                continue
            if candidate in known_markdown_paths:
                matches.append(match)
    return matches


def classify_backtick_token(
    candidate: str,
    known_repo_paths: set[str],
    unique_basename_index: dict[str, str],
    known_directories: set[str],
    canonical_markdown_surfaces: set[str],
    portable_package_root: Path | None,
    package_root_relative: Path | None = None,
) -> str | None:
    """Return a short reason tag if the backticked token must become a markdown link.

    - "pathy": contains "/" with a valid extension-bearing tail and resolves to a tracked file.
    - "prefix": starts with "./" or "../" and resolves to a tracked file or directory; the
      backtick form is never correct when the target exists, since renames silently break it.
    - "unique-basename": bare filename whose basename is unique among tracked files.
    - "portable-absolute": an absolute repo-shaped path inside a portable skill package.
    - "unmarked-tree": a repo-shaped path in a SHIPPED skill doc that names no tree.
      The verdict is about the missing statement, not about which tree is right.

    Returns None when the token should be allowed as-is (concept, ambiguous basename, whitespace
    command invocation, version string, dotted property path, domain-like token, `./`-prefixed
    token that does not resolve to a real repo path, etc.).
    """
    bare = normalize_backtick_candidate(candidate)
    if bare is None:
        return None
    if has_portable_placeholder(bare):
        return None
    # BEFORE the portable branch, deliberately. A canonical markdown surface is an
    # agreed name that means the same file in every tree (`AGENTS.md`),
    # so it needs no tree marker -- and running the portable
    # rule first made the armed check demand one, which would have been a false
    # positive in a blocking gate on the repo's own agreed vocabulary.
    if normalize_surface_token(candidate) in canonical_markdown_surfaces:
        return None
    if portable_package_root is not None:
        if bare.startswith("/") and PATHY_TOKEN_RE.match(bare.lstrip("/")):
            return "portable-absolute"
        # A path-shaped token in a SHIPPED skill doc must say which tree it means.
        # This rule used to be off entirely inside portable packages, because a
        # markdown link from a skill package to an authoring-repo file cannot
        # resolve for a consumer -- which was true, and is what the placeholder
        # vocabulary now answers. With `<authoring-repo>/`, `<repo-root>/` and a
        # resolvable `<plugin-dir>/` all available, "unmarked" is no longer a
        # forced choice; it is a missing statement.
        #
        # The verdict needs no judgement about WHICH tree, only that the author
        # named one: a bare `scripts/x.py` is refused whether it meant charness's
        # tree or the reader's, because the reader cannot tell either. That is what
        # turns this axis from a per-site judgement into a mechanical check.
        if not PATHY_TOKEN_RE.match(bare):
            return None
        if package_root_relative is None:
            # Preserve the direct helper's historical API for callers that only
            # supply the package root. Production callers pass the explicit
            # repo-relative path so the shallower shared package is handled too.
            package_root_relative = portable_package_root.relative_to(
                portable_package_root.parents[2]
            )
        package_relative = package_root_relative / bare
        if package_relative.as_posix() in known_repo_paths:
            # Resolves inside the shipped package, so it is reachable as written.
            # Checked against the git listing, not `.exists()`: an untracked helper
            # would otherwise pass locally and fail on a CI checkout, which is the
            # divergence `iter_unresolved_command_targets` already documents.
            return None
        return "unmarked-tree" if looks_like_repo_reference(bare) else None

    if candidate.startswith("./") or candidate.startswith("../"):
        return classify_prefixed_backtick(bare, known_repo_paths, known_directories)

    pathlike_reason = classify_pathlike_backtick(bare, known_repo_paths)
    if pathlike_reason is not None:
        return pathlike_reason

    if not EXTENSION_TOKEN_RE.match(bare):
        return None

    if bare in known_repo_paths:
        return "pathy"

    if bare in unique_basename_index:
        return "unique-basename"

    return None


def iter_backticked_file_refs(
    root: Path,
    doc: Path,
    known_repo_paths: set[str],
    unique_basename_index: dict[str, str],
    known_directories: set[str],
    canonical_markdown_surfaces: set[str],
) -> list[tuple[int, str, str]]:
    matches: list[tuple[int, str, str]] = []
    portable_package_root = portable_skill_package_root(root, doc)
    package_root_relative = (
        portable_package_root.relative_to(root) if portable_package_root is not None else None
    )
    for lineno, line, in_fence in iter_doc_lines(doc):
        if in_fence:
            continue
        scrubbed = strip_markdown_links(line)
        for match in BACKTICK_CONTENT_RE.finditer(scrubbed):
            candidate = match.group(1).split("#", 1)[0].strip()
            reason = classify_backtick_token(
                candidate,
                known_repo_paths,
                unique_basename_index,
                known_directories,
                canonical_markdown_surfaces,
                portable_package_root,
                package_root_relative,
            )
            if reason is not None:
                matches.append((lineno, candidate, reason))
    return matches


def iter_unresolved_command_targets(
    root: Path,
    doc: Path,
    known_repo_paths: set[str] | None = None,
) -> list[tuple[int, str]]:
    """Compatibility wrapper for the command-carrier module's missing-target check."""
    return _portable_command_carrier.iter_unresolved_command_targets(
        root,
        doc,
        portable_skill_package_root(root, doc),
        known_repo_paths,
    )


AUTHORING_REPO_PHRASE = "authoring-repo-internal"
CONSUMER_PREFIX = "<repo-root>/"
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s")


def iter_authoring_repo_contradictions(doc: Path) -> list[tuple[int, str]]:
    """Sentences that call a file authoring-repo-internal and then spell it for the consumer.

    `<repo-root>/` means "the tree the reader is operating on". A sentence that says
    a file is authoring-repo-INTERNAL and reaches for that prefix contradicts itself
    in one breath: it tells the reader the file is not in their tree, then hands them
    a path rooted in their tree. Whichever half is right, the sentence is wrong, and
    `<authoring-repo>/` is the spelling that makes it true.

    Decidable without judgment, which is why it is a gate while the neighbouring axes
    from the same sweep are not: no legitimate sentence asserts both.

    Scoped to the SENTENCE, not the line and not the paragraph. The line is too narrow
    -- this prose wraps, and 4 of the 6 live instances at 2026-08-04 put the phrase on
    one line and the prefix on the next, so a line-anchored ruler reported 2. The
    paragraph is too wide: it would couple an unrelated `<repo-root>/` mention two
    sentences away and manufacture the false positive this rule exists to avoid.
    """
    findings: list[tuple[int, str]] = []
    for block in iter_prose_blocks(doc):
        offset_to_lineno: list[int] = []
        for lineno, line in block:
            offset_to_lineno.extend([lineno] * (len(line) + 1))
        for start, sentence in split_block_into_sentences(block):
            if AUTHORING_REPO_PHRASE not in sentence or CONSUMER_PREFIX not in sentence:
                continue
            # Report where the PHRASE sits, not where its sentence began: the
            # contradiction is what the reader has to go fix.
            phrase_at = min(
                start + sentence.index(AUTHORING_REPO_PHRASE), len(offset_to_lineno) - 1
            )
            findings.append((offset_to_lineno[phrase_at], " ".join(sentence.split())))
    return findings


def iter_prose_blocks(doc: Path) -> list[list[tuple[int, str]]]:
    """Group live lines into blocks that a sentence can legitimately span.

    A blank line or a new list item ends a block. Without that, one bullet's
    `<repo-root>/` gets glued to a neighbouring bullet's `authoring-repo-internal`
    and the rule invents a contradiction across two independent statements --
    the false-positive shape a blocking gate must not have.
    """
    blocks: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    for lineno, line, in_fence in iter_doc_lines(doc):
        if in_fence:
            continue
        if not line.strip() or LIST_ITEM_RE.match(line):
            if current:
                blocks.append(current)
            current = [] if not line.strip() else [(lineno, line)]
            continue
        current.append((lineno, line))
    if current:
        blocks.append(current)
    return blocks


def split_block_into_sentences(block: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Split one block into `(start_offset_within_block, sentence_text)` pairs."""
    text = "\n".join(line for _lineno, line in block)
    sentences: list[tuple[int, str]] = []
    cursor = 0
    for sentence in SENTENCE_SPLIT_RE.split(text):
        start = text.index(sentence, cursor)
        cursor = start + len(sentence)
        if sentence.strip():
            sentences.append((start, sentence))
    return sentences


def validate_link(root: Path, doc: Path, raw_target: str) -> None:
    target = raw_target.strip()
    shape = classify_link_shape(target)
    if shape == INERT_LINK:
        return
    if shape == ABSOLUTE_LINK:
        raise ValidationError(f"{doc}: absolute link `{target}`; use relative links")
    if shape == BARE_LINK:
        raise ValidationError(
            f"{doc}: relative link `{target}` must start with `./` or `../` so file references "
            "are distinguishable from concept tokens at a glance"
        )

    candidate = resolve_relative_link(doc, target)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValidationError(
            f"{doc}: relative link `{target}` escapes repo root; keep markdown links inside "
            "repo-owned paths"
        ) from exc
    if not candidate.exists():
        raise ValidationError(f"{doc}: broken relative link `{target}`")
    portable_package_root = portable_skill_package_root(root, doc)
    if portable_package_root is not None:
        try:
            candidate.relative_to(portable_package_root)
        except ValueError as exc:
            try:
                candidate.relative_to(root / "skills")
                return
            except ValueError:
                pass
            raise ValidationError(
                f"{doc}: portable skill link `{target}` resolves outside its skill package; "
                "use a backticked placeholder such as `<repo-root>/path` for repo-local artifacts"
            ) from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    snapshot = RepoFileSnapshot(root, require_git=args.require_git_file_listing)
    known_repo_paths = iter_known_repo_paths(
        root, require_git=args.require_git_file_listing, snapshot=snapshot
    )
    known_markdown_paths = {path for path in known_repo_paths if Path(path).suffix == ".md"}
    unique_basename_index = build_unique_basename_index(known_repo_paths)
    known_directories = build_known_directories(known_repo_paths)
    canonical_markdown_surfaces = load_canonical_markdown_surfaces(root)
    try:
        docs = iter_docs(root, require_git=args.require_git_file_listing, snapshot=snapshot)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc
    for doc in docs:
        contents = doc.read_text(encoding="utf-8")
        for target in iter_link_targets(contents):
            validate_link(root, doc, target)
        bare_refs = iter_bare_internal_doc_refs(
            root, doc, known_markdown_paths, canonical_markdown_surfaces
        )
        if bare_refs:
            refs = ", ".join(f"`{ref}`" for ref in bare_refs[:3])
            if len(bare_refs) > 3:
                refs += ", ..."
            raise ValidationError(
                f"{doc}: bare internal markdown reference(s) {refs}; {BARE_INTERNAL_REF_REMEDY}"
            )
        backticked = iter_backticked_file_refs(
            root,
            doc,
            known_repo_paths,
            unique_basename_index,
            known_directories,
            canonical_markdown_surfaces,
        )
        if backticked:
            refs = ", ".join(
                f"`{cand}` (line {ln}, {reason})" for ln, cand, reason in backticked[:3]
            )
            if len(backticked) > 3:
                refs += ", ..."
            # Branch on the reason. Telling an author to "use markdown links" for an
            # `unmarked-tree` finding sends them straight into `validate_link`, which
            # refuses a markdown link that leaves a portable skill package -- two gate
            # cycles to learn a rule the first message could have named.
            if all(reason in TREE_MARKER_REASONS for _ln, _cand, reason in backticked):
                remedy = TREE_MARKER_REMEDY
            else:
                remedy = LINK_FORM_REMEDY
            raise ValidationError(f"{doc}: backticked file reference(s) {refs}; {remedy}")
        contradictions = iter_authoring_repo_contradictions(doc)
        if contradictions:
            lineno, sentence = contradictions[0]
            more = f" (+{len(contradictions) - 1} more)" if len(contradictions) > 1 else ""
            raise ValidationError(
                f"{doc}:{lineno}: this sentence calls a file `{AUTHORING_REPO_PHRASE}` and then spells it "
                f"with the consumer prefix `{CONSUMER_PREFIX}`{more}; `{CONSUMER_PREFIX}` means the "
                "reader's own tree, so the sentence contradicts itself — use `<authoring-repo>/` to say "
                f"the file lives in charness and not in theirs. Sentence: {sentence}"
            )
        unresolved = iter_unresolved_command_targets(root, doc, known_repo_paths)
        if unresolved:
            refs = ", ".join(f"`{cand}` (line {ln})" for ln, cand in unresolved[:3])
            if len(unresolved) > 3:
                refs += ", ..."
            raise ValidationError(
                f"{doc}: fenced command target(s) {refs} do not exist; {MISSING_COMMAND_TARGET_REMEDY}"
            )
        unportable = iter_unportable_command_targets(
            root, doc, portable_skill_package_root(root, doc), known_repo_paths
        )
        if unportable:
            refs = ", ".join(
                f"`{candidate}` (line {lineno}; expected `<plugin-dir>/{shipped}`; "
                f"{'exported' if shipped_exists else 'export missing'})"
                for lineno, candidate, shipped, shipped_exists in unportable[:3]
            )
            if len(unportable) > 3:
                refs += ", ..."
            raise ValidationError(
                f"{doc}: command target(s) {refs} use the authoring-only kind-bearing layout; "
                "use `$SKILL_DIR/...` for this skill's own scripts or `<plugin-dir>/...` "
                "for another shipped package"
            )
    scope_note = " (discovered empty universe)" if not docs else ""
    print(f"Validated markdown links across {len(docs)} document(s){scope_note}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
