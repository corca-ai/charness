#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
import tempfile
from datetime import date
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_quality_adapter = import_repo_module(__file__, "scripts.quality_adapter_lib")
load_quality_adapter = _quality_adapter.load_quality_adapter
_quality_universes = import_repo_module(__file__, "scripts.quality_universes_lib")
DEFAULT_ARTIFACT_ROOTS = _quality_universes.DEFAULT_ARTIFACT_ROOTS
matching_files = _quality_universes.matching_files
refuse_if_declared_and_empty = _quality_universes.refuse_if_declared_and_empty
resolve_universe = _quality_universes.resolve_universe
_critique_adapter = import_repo_module(__file__, "scripts.review.critique_adapter_lib")
load_critique_adapter = _critique_adapter.load_adapter
_retro_index = import_repo_module(__file__, "scripts.build_retro_lesson_selection_index")
load_retro_paths = _retro_index._load_retro_paths
_markdown_doc_scan = import_repo_module(__file__, "scripts.core.markdown_doc_scan")
iter_doc_lines = _markdown_doc_scan.iter_doc_lines
#: The repo's ONE owner of an artifact's effective grandfathering date. Imported
#: rather than reimplemented: a second date reader on a second proof surface is
#: how the two would come to disagree about which artifacts a floor binds.
_scope = import_repo_module(__file__, "scripts.review.critique_enforcement_scope")
_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process

PRIMARY_ARTIFACT_FAMILIES = (
    "spec",
    "quality",
    "release",
    "dogfood",
    "debug",
    "premortem",
    "design-studies",
)

#: Evidence families added later, and enforced only from `ENFORCED_FROM` forward.
#:
#: These carry citations exactly like the families above -- a goal artifact names
#: the probe that proved its slice, a critique names what it read, a release review
#: names the run it reviewed -- and they were simply never scanned. Measured at the
#: time of widening: 70 already-evaporating citations across 2339 docs in these
#: families, against 0 across the 499 docs in the families already covered.
#:
#: The date anchor is the whole design. Those 70 live almost entirely in CLOSED
#: retros, critiques and goals from months back: frozen records of what happened.
#: Editing them to satisfy a gate would rewrite evidence to make a checker happy,
#: which is the inversion this repo refuses. So history is COUNTED and reported,
#: never rewritten, and the gate binds on artifacts written from the anchor date
#: forward -- the ones whose citations a future session will actually try to follow.
LATE_ARTIFACT_FAMILIES = ("goals", "critique", "retro", "probe", "issues", "release-review")
DOC_GLOBS = tuple(
    f"{DEFAULT_ARTIFACT_ROOTS[family]}/**/*.md" for family in PRIMARY_ARTIFACT_FAMILIES
)
LATE_DOC_GLOBS = tuple(
    f"{DEFAULT_ARTIFACT_ROOTS[family]}/**/*.md" for family in LATE_ARTIFACT_FAMILIES
)
#: The date this widening landed. A doc in `LATE_DOC_GLOBS` is enforced when its
#: FILENAME dates it on or after this; earlier ones are grandfathered. A doc whose
#: filename carries no readable date is enforced whatever its body says -- see
#: `is_enforced_late_doc` for why only that channel grandfathers.
ENFORCED_FROM = date(2026, 8, 22)


def _adapter_owned_default(repo_root: Path, family: str) -> str:
    """Use a skill-owned output directory as the family's portable fallback."""
    if family == "critique":
        data = load_critique_adapter(repo_root).get("data") or {}
        output_dir = data.get("output_dir")
        if isinstance(output_dir, str) and output_dir:
            return output_dir
    if family == "retro":
        try:
            output_dir, _summary_path = load_retro_paths(repo_root)
        except FileNotFoundError:
            pass
        else:
            return output_dir.relative_to(repo_root).as_posix()
    return DEFAULT_ARTIFACT_ROOTS[family]


def _resolved_artifact_docs(repo_root: Path, families: tuple[str, ...]):
    adapter = load_quality_adapter(repo_root)
    docs_by_family: dict[str, list[Path]] = {}
    empty_families: list[str] = []
    for family in families:
        universe = resolve_universe(
            adapter,
            f"artifact_roots.{family}",
            default=_adapter_owned_default(repo_root, family),
        )
        files = [
            path for path in matching_files(repo_root, universe) if path.suffix.lower() == ".md"
        ]
        refusal = refuse_if_declared_and_empty(universe, files, "check-spec-evidence-durability")
        if refusal:
            raise ValueError(refusal)
        if not files:
            empty_families.append(family)
        docs_by_family[family] = files
    return docs_by_family, empty_families


#: `docs/**` is deliberately NOT here. Doctrine that NAMES a runtime path
#: (`artifact-policy.md` explaining where `.charness/quality/runtime-signals.json`
#: is written) is not an artifact CITING that file as its own proof, and the 9
#: hits there are all the former. Folding them in would train the marker onto
#: prose that was never a citation, which costs the marker its meaning.
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
BACKTICK_CONTENT_RE = re.compile(r"`([^`\n]+)`")
PATHY_TOKEN_RE = re.compile(r"^(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]+\.[A-Za-z0-9._-]+$")
REPRODUCTION_MARKER_RE = re.compile(r"<!--\s*reproduction-source\s*-->", re.IGNORECASE)
MARKDOWN_BLOCK_START_RE = re.compile(r"(?:[-*+] |\d+[.)] |>|```|~~~|#)")
LIST_ITEM_START_RE = re.compile(r"(?:[-*+] |\d+[.)] )")
REPO_REFERENCE_PREFIXES = (
    ".agents/",
    ".charness/",
    ".github/",
    "artifacts/",
    "charness-artifacts/",
    "docs/",
    "evals/",
    "integrations/",
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


def looks_like_repo_path(candidate: str) -> bool:
    target = candidate.lstrip("./").split("#", 1)[0].strip()
    if target.startswith(REPO_REFERENCE_PREFIXES):
        return True
    return bool(PATHY_TOKEN_RE.match(target))


def resolve_relative_to_repo(root: Path, doc: Path, candidate: str) -> Path | None:
    raw = candidate.split("#", 1)[0].strip()
    if not raw or "://" in raw or raw.startswith("mailto:"):
        return None
    if raw.startswith("./") or raw.startswith("../"):
        resolved = (doc.parent / raw).resolve()
    elif raw.startswith("/"):
        return None
    else:
        resolved = (root / raw).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved


def git_check_ignore(root: Path, paths: list[Path]) -> set[Path] | None:
    """Return the subset of `paths` that match a `.gitignore` rule.

    Returns `None` when the root is not inside a git work tree so the caller
    can skip evidence-durability checks gracefully (e.g., tarball install).
    """
    if not paths:
        return set()
    if not (root / ".git").exists():
        return None
    rel_inputs: list[str] = []
    for path in paths:
        try:
            rel_inputs.append(str(path.relative_to(root)))
        except ValueError:
            continue
    if not rel_inputs:
        return set()
    request = "\0".join(rel_inputs).encode("utf-8") + b"\0"
    with tempfile.NamedTemporaryFile() as input_file:
        input_file.write(request)
        input_file.flush()
        result = run_process(
            f"git check-ignore --stdin -z < {shlex.quote(input_file.name)}",
            cwd=root,
            shell=True,
            timeout_seconds=None,
        )
    if result.returncode not in (0, 1):
        rendered = result.stderr.strip()
        if "not a git repository" in rendered.lower():
            return None
        raise ValidationError(f"git check-ignore failed: {rendered or 'unknown error'}")
    ignored: set[Path] = set()
    for raw in result.stdout.split("\0"):
        token = raw.strip()
        if not token:
            continue
        ignored.add((root / token).resolve())
    return ignored


def iter_citation_lines(doc: Path) -> list[tuple[int, str, list[str]]]:
    """Return (lineno, raw_line, candidate_paths) for each non-fence line."""
    out: list[tuple[int, str, list[str]]] = []
    lines = doc.read_text(encoding="utf-8").splitlines()
    for lineno, line, in_fence in iter_doc_lines(doc):
        if in_fence:
            continue
        candidates: list[str] = []
        for raw_target in LINK_RE.findall(line):
            target = raw_target.strip()
            if target and looks_like_repo_path(target):
                candidates.append(target)
        for backtick_match in BACKTICK_CONTENT_RE.finditer(line):
            inner = backtick_match.group(1).strip()
            if inner and looks_like_repo_path(inner):
                candidates.append(inner)
        if candidates:
            marker_scope = line
            continuation = lines[lineno] if lineno < len(lines) else ""
            indentation = len(continuation) - len(continuation.lstrip(" "))
            if (
                LIST_ITEM_START_RE.match(line.lstrip()) is not None
                and indentation in (2, 3)
                and not MARKDOWN_BLOCK_START_RE.match(continuation.lstrip())
            ):
                # CommonMark continuation lines belong to the same list item.
                # Keep the evidence marker coupled to the semantic bullet, not
                # to an arbitrary physical wrap chosen by the author/formatter.
                marker_scope += "\n" + lines[lineno]
            out.append((lineno, marker_scope, candidates))
    return out


def citation_candidates(root: Path, doc: Path) -> dict[Path, list[tuple[int, str]]]:
    citation_lines = iter_citation_lines(doc)
    if not citation_lines:
        return {}
    candidates_by_path: dict[Path, list[tuple[int, str]]] = {}
    for lineno, line, candidates in citation_lines:
        if REPRODUCTION_MARKER_RE.search(line):
            continue
        for candidate in candidates:
            resolved = resolve_relative_to_repo(root, doc, candidate)
            if resolved is None:
                continue
            candidates_by_path.setdefault(resolved, []).append((lineno, candidate))
    return candidates_by_path


def violations_for_doc(
    root: Path,
    doc: Path,
    *,
    candidates_by_path: dict[Path, list[tuple[int, str]]] | None = None,
    ignored_paths: set[Path] | None = None,
) -> list[str]:
    if candidates_by_path is None:
        candidates_by_path = citation_candidates(root, doc)
    if not candidates_by_path:
        return []
    ignored = (
        git_check_ignore(root, list(candidates_by_path)) if ignored_paths is None else ignored_paths
    )
    if ignored is None or not ignored:
        return []
    ignored = {
        path
        for path in candidates_by_path
        if path in ignored and not under_generated_export(root, path)
    }
    if not ignored:
        return []
    rel_doc = doc.relative_to(root).as_posix() if doc.is_absolute() else str(doc)
    messages: list[str] = []
    for resolved_path, hits in candidates_by_path.items():
        if resolved_path not in ignored:
            continue
        for lineno, candidate in hits:
            messages.append(
                f"{rel_doc}:{lineno}: cited path `{candidate}` resolves to a gitignored target "
                "(`" + resolved_path.relative_to(root).as_posix() + "`); cite a checked-in proof "
                "artifact or mark the citation bullet `<!-- reproduction-source -->` "
                "on the same line or its immediately following plain-text continuation. "
                "See skills/public/spec/references/evidence-durability.md."
            )
    return messages


def generated_export_roots(root: Path) -> set[Path]:
    """Repo-relative roots the packaging manifests DECLARE as generated exports.

    Read from `packaging/*.json` rather than spelled here, so this gate cannot come
    to disagree with the manifests about where the export lives.
    """

    roots: set[Path] = set()
    for manifest in sorted((root / "packaging").glob("*.json")):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, str) and node.startswith("./") and "/" in node[2:]:
                roots.add(root / node[2:])
    return roots


def under_generated_export(root: Path, path: Path) -> bool:
    """Whether a gitignored citation still names durable evidence.

    A path is UNDURABLE when nothing can bring it back. The plugin export is
    gitignored, but it is regenerated from tracked source by a repo-owned producer
    (`scripts/plugin_export/sync_root_plugin_manifests.py`, run by `charness init`/`update` and by
    the release version bump), and that regeneration was proven byte-identical for
    all 1,042 files when the tree was untracked on 2026-08-29. A citation into it is
    therefore reproducible, which is exactly what this gate asks for -- the gitignore
    bit alone was standing in for the question.

    Without this, untracking a generated tree retroactively invalidates every
    historical artifact that ever cited it: this fired on 20+ debug artifacts dating
    to 2026-04, none of which changed.

    Matched on the TOP-LEVEL directory a declared export root sits in, not on the
    root itself, because artifacts cite the generated tree at every depth: the export
    root (`plugins/charness/skills/...`), the tree root (`plugins/`), and glob spans
    across it (`plugins/*/skills`). Only the first is under the declared root, and all
    three name the same regenerated tree.

    Blind class: this trusts the DECLARATION, not the producer, and it exempts the
    WHOLE top-level directory. If a declared export root stops being regenerable, or
    if a non-generated sibling is ever added beside it under the same top-level
    directory, citations there keep passing. This gate does not run the exporter and
    cannot see either.
    """

    generated_tops = {
        relative.parts[0]
        for export_root in generated_export_roots(root)
        if (relative := _relative_or_none(root, export_root)) is not None and relative.parts
    }
    relative_path = _relative_or_none(root, path)
    return (
        relative_path is not None
        and bool(relative_path.parts)
        and relative_path.parts[0] in generated_tops
    )


def _relative_or_none(root: Path, path: Path) -> Path | None:
    try:
        return path.relative_to(root)
    except ValueError:
        return None


def is_enforced_late_doc(doc: Path, text: str) -> bool:
    """Whether a `LATE_DOC_GLOBS` artifact is inside the enforced window.

    Delegates to `critique_enforcement_scope.observed_date`, this repo's ONE
    owner of "the artifact's effective date for grandfathering": the LATER of the
    in-body `Date:` line and the leading `YYYY-MM-DD` of the filename. Not
    mtime and not commit date -- either of those moves when a frozen record is
    touched for an unrelated reason, and the record would drift into enforcement
    without its content changing.

    **An UNDATABLE doc is ENFORCED, not exempt**, and that direction is the whole
    correctness of this function. The first cut read it the other way, and a
    fresh-eye round found the hole: 68 checked-in artifacts in these families
    carry no parseable date, 64 of them in `critique/` and `retro/`, and they are
    overwhelmingly one-shot `*-packet.md` review artifacts -- the files that carry
    the MOST run-output citations, undated by this repo's own naming convention.
    So the exemption was not date-bounded debt that shrinks as history recedes; it
    was an unbounded hole that GROWS with every new packet, opened by omitting a
    filename convention nothing validates. One live violation was already sitting
    in it.

    That reading is not a novel judgement -- it is the rule this repo already
    wrote down twice, after measuring the same mistake:
    `critique_enforcement_scope.observed_date`'s own docstring says callers "must
    NOT treat `None` as fail-open by default", and `validate_critique_artifacts`
    records that its first cut exempted undated artifacts and "handed back the
    whole of C4 through the one input the rule names as never fail-open".

    There is deliberately NO allowlist. Fail-closed leaves exactly three citations
    to resolve across all 68 filename-undated docs, and each is a genuine
    reproduction source that the `<!-- reproduction-source -->` marker already
    exists to label. An exemption list would be larger than the problem.

    **Only the FILENAME channel grandfathers, and `text` is deliberately unused
    for that decision.** The first fail-closed cut delegated to
    `observed_date`, which is `max(body_date, filename_date)` -- and a round-2
    reviewer showed that repair carried a narrowed form of the class it fixed.
    `observed_date`'s safety argument is corroboration: when both channels parse,
    an artifact is exempt only if they agree it is old. Its own docstring records
    the residual -- "an undated filename with a back-dated body is therefore still
    exempt" -- and mitigates it with "the scaffold always emits both".

    That mitigation inverts on THIS corpus. The population here is *defined* by
    having no filename date, so the author-written body line is not a corroborating
    channel, it is the only one. One line, `Date: 2020-01-01`, in the first five
    lines of a new review packet bought a permanent exemption. Four checked-in docs
    already take their date from the body alone, one of them `critique/latest.md` --
    a rolling pointer whose content is replaced while its body date is
    author-maintained, which is exactly the grows-not-shrinks shape the fail-closed
    repair was raised about.

    So the delegation is kept for what it is good at and dropped where its argument
    does not hold: `date_from_filename` is a name nobody edits while rewriting a
    doc's body, and an artifact that wants grandfathering must be NAMED old. This
    also sidesteps a second pre-existing hole the reviewer found in the body
    channel -- `date_from_body` does not strip display fences, so a packet that
    merely QUOTES another artifact's `Date:` header reads the quotation as its own
    claim. That is filed rather than fixed here; this gate simply stops depending
    on it.

    `text` stays in the signature because a future channel (a front-matter field, a
    committed-date corroboration) belongs here and not at the call site.
    """
    observed = _scope.date_from_filename(doc)
    if observed is None:
        return True
    return observed >= ENFORCED_FROM


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    if not (root / ".git").exists():
        print(
            f"Skipping evidence-durability check: no git work tree at {root}.",
        )
        return 0
    try:
        docs_by_family, empty_families = _resolved_artifact_docs(root, PRIMARY_ARTIFACT_FAMILIES)
        late_by_family, late_empty_families = _resolved_artifact_docs(root, LATE_ARTIFACT_FAMILIES)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    docs = [path for family in PRIMARY_ARTIFACT_FAMILIES for path in docs_by_family[family]]
    late_docs = [path for family in LATE_ARTIFACT_FAMILIES for path in late_by_family[family]]
    empty_families.extend(late_empty_families)
    candidates_by_doc = {doc: citation_candidates(root, doc) for doc in [*docs, *late_docs]}
    all_candidate_paths = sorted(
        {path for candidates in candidates_by_doc.values() for path in candidates}
    )
    ignored_paths = git_check_ignore(root, all_candidate_paths) or set()
    all_messages: list[str] = []
    for doc in docs:
        all_messages.extend(
            violations_for_doc(
                root,
                doc,
                candidates_by_path=candidates_by_doc[doc],
                ignored_paths=ignored_paths,
            )
        )
    grandfathered = 0
    for doc in late_docs:
        messages = violations_for_doc(
            root,
            doc,
            candidates_by_path=candidates_by_doc[doc],
            ignored_paths=ignored_paths,
        )
        if not messages:
            continue
        if is_enforced_late_doc(doc, doc.read_text(encoding="utf-8")):
            all_messages.extend(messages)
        else:
            grandfathered += len(messages)
    advisory = grandfathered_advisory(grandfathered)
    if all_messages:
        for message in all_messages:
            print(message, file=sys.stderr)
        # The scope record belongs on a FAILING run too. A failure carries a
        # signal about the failures and nothing about the floors that were off,
        # so an operator who fixes the one named file and re-runs would meet the
        # excluded-count for the first time AFTER forming the belief that this
        # gate's scope was complete. `artifact_validator` names the same class.
        if advisory:
            print(advisory)
        return 1
    scope_note = (
        f" Discovered empty artifact universe(s): {', '.join(empty_families)}."
        if empty_families
        else ""
    )
    print(
        f"Validated spec evidence durability across {len(docs) + len(late_docs)} doc(s)."
        f"{scope_note}"
    )
    if advisory:
        print(advisory)
    return 0


def grandfathered_advisory(grandfathered: int) -> str | None:
    """The excluded-citation count, described as the population it actually is.

    Reported, never silent: a gate that quietly excludes part of its own scope
    reads as "covered everything" when it did not.

    The wording is load-bearing and an earlier cut got it wrong in a way a fresh
    eye caught. It said the excluded citations "remain in artifacts dated before
    <date>" and that "new artifacts in those families are enforced" -- and both
    clauses were false for the undated subset, which was neither dated-before
    anything nor enforced when new. That merged two populations with opposite
    half-lives (one shrinking as history recedes, one growing with every new
    packet) into a single number nobody could read as either. Undated docs are
    now enforced, so the count describes ONE population again and the sentence
    can say what it is.
    """
    if not grandfathered:
        return None
    return (
        f"ADVISORY (evidence durability): {grandfathered} citation(s) to gitignored "
        f"targets remain in artifacts whose FILENAME date precedes {ENFORCED_FROM.isoformat()}; "
        "they are frozen records and are counted, not rewritten. Every artifact in "
        "those families whose filename dates it on or after that -- and every "
        "artifact whose FILENAME carries no readable date at all, whatever its body "
        "says -- is enforced."
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
