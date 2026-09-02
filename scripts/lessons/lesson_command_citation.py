"""Which command to CITE for the tree the reader actually has.

A refusal that names a path the reader cannot run is worse than one that names
nothing: the operator follows it, gets a second, unrelated error, and reads the tool
as broken rather than the instruction as wrong. That happened for real -- the
lesson-selection path opened from an installed plugin failed with an instruction naming
``scripts/lessons/build_retro_lesson_selection_index.py``, which the consuming repo does not
have, and the recovery from THAT failure named
``skills/public/retro/scripts/refresh_recent_lessons.py``, which exists in neither the
consuming repo nor the installed plugin (the exporter flattens it to
``skills/retro/``). The first message additionally warned that running an installed
copy was the CAUSE of the failure, so the only way forward was the action the message
warned against.

This module is the one home for the two questions that fixes:

* which tree does this copy belong to (repo root here, ``plugins/<pkg>`` installed);
* is the TARGET repo one that owns a competing copy, or an ordinary consuming repo.

The second question is asked with ``helper_provenance_lib.is_charness_source_tree``
rather than a file test, because the two must not disagree about one invocation: the
materialized ``plugins/charness/`` export owns the builder and carries no packaging
manifest, so a file test alone classified it as a competing source tree and told the
operator to run the exported builder against the export -- the one action the repo's
shell gates refuse outright.

Split out of ``recent_lessons_lib`` when that file passed its length cap. The grouping
is the concept, not the spill: every function here answers "what do I tell this
reader to run", including the explicit lesson-ledger seed command.
"""

from __future__ import annotations

from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.helper_provenance_lib import is_charness_source_tree  # noqa: E402

INDEX_SCRIPT_NAME = "build_retro_lesson_selection_index.py"
INDEX_SCRIPT_RELATIVE = Path("scripts") / "lessons" / INDEX_SCRIPT_NAME
LESSON_SCRIPT_NAMES = frozenset(
    {
        "build_retro_lesson_selection_index.py",
        "check_lesson_ledger.py",
        "init_lesson_ledger.py",
        "lesson_command_citation.py",
        "lesson_ledger_lib.py",
        "lesson_ledger_writer_lib.py",
        "lesson_score_outcome_lib.py",
        "lesson_selection_preview_lib.py",
        "recent_lesson_selection.py",
        "recent_lessons_lib.py",
        "record_lesson_lifecycle.py",
        "record_lesson_score.py",
        "render_lesson_selection_preview.py",
        "seed_lesson_transitions.py",
    }
)
# BOTH spellings, because a reference can resolve in one layout and not the other. The
# source tree has `skills/public/retro/`; the export flattens it to `skills/retro/`.
REFRESH_SCRIPT_RELATIVE = (
    Path("skills") / "public" / "retro" / "scripts" / "refresh_recent_lessons.py",
    Path("skills") / "retro" / "scripts" / "refresh_recent_lessons.py",
)
# `<...>` in a shell is a redirection, so a bracketed placeholder inside a
# copy-pasteable command turns "file not found" into a different, wronger error. The
# bare token cannot be mistaken for a path that exists.
PLUGIN_DIR_TOKEN = "CHARNESS_PLUGIN_DIR"


def script_tree_root() -> Path:
    """The tree this copy belongs to: repo root here, `plugins/<pkg>` when installed."""
    script_path = Path(__file__).resolve()
    marker = Path("scripts") / "adapter_lib.py"
    for parent in script_path.parents:
        if (parent / marker).is_file():
            return parent
    # Keep synthetic/partial trees on the existing no-candidate path. Real source and
    # exported trees are marker-backed; this fallback lets callers report the named
    # installed shape when neither tree carries the builder.
    return script_path.parent.parent


def repo_or_installed_command(repo_root: Path, script_name: str, *args: str) -> str:
    """Spell a repo-owned script for the tree the reader actually has."""
    relative = (
        Path("scripts")
        / ("lessons" if script_name in LESSON_SCRIPT_NAMES else "")
        / script_name
    )
    candidates: list[Path] = []
    if is_charness_source_tree(repo_root):
        candidates.append(repo_root / relative)
    candidates.append(script_tree_root() / relative)
    tail = " ".join(args)
    for candidate in candidates:
        if candidate.is_file():
            return f"python3 {spell(candidate, repo_root, relative)} {tail}".rstrip()
    return f"python3 {PLUGIN_DIR_TOKEN}/{relative.as_posix()} {tail}".rstrip()


def repo_carries_index_builder(repo_root: Path) -> bool:
    """True when the target is a charness SOURCE tree that owns its own index builder.

    Both conditions, not just the file test. See the module docstring for the export
    case that made the file test alone wrong.
    """
    return is_charness_source_tree(repo_root) and (repo_root / INDEX_SCRIPT_RELATIVE).is_file()


def spell(script: Path, repo_root: Path, tree_relative: Path) -> str:
    """Absolute unless the operator's own tree is the one being written.

    A relative spelling is only correct when the reader's cwd is the tree the script
    lives in. Pairing `scripts/<name>.py` with an absolute `--repo-root /other/checkout`
    hands back a command that runs THIS repo's script against a different one -- the
    same class as citing a path that does not exist, with a quieter failure.
    """
    if repo_root.resolve() == script_tree_root():
        return str(tree_relative)
    return str(script)


def index_build_command(repo_root: Path, *flags: str) -> str:
    tail = " ".join(flags)
    bases = ((repo_root,) if repo_carries_index_builder(repo_root) else ()) + (script_tree_root(),)
    for base in bases:
        candidate = base / INDEX_SCRIPT_RELATIVE
        if candidate.is_file():
            spelled = spell(candidate, repo_root, INDEX_SCRIPT_RELATIVE)
            return f"python3 {spelled} --repo-root {repo_root} {tail}".rstrip()
    # Neither tree carries it. Name the shape rather than a path that resolves nowhere,
    # so the reader knows they are looking for a missing file and not mistyping one.
    return (
        f"python3 {PLUGIN_DIR_TOKEN}/{INDEX_SCRIPT_RELATIVE.as_posix()} "
        f"--repo-root {repo_root} {tail}"
    ).rstrip()


def refresh_digest_command(repo_root: Path) -> str:
    # The SAME provenance gate `index_build_command` uses. A bare `is_file()` here was
    # the round-1 defect surviving in the sibling: a target carrying a materialized export
    # (this repo's own `plugins/charness` shape, or any consumer that commits one under
    # its root) got cited its OWN copy while the provenance guard classifies that tree
    # as `consuming-repo` -- so one function cites the repo and the other cites the
    # install for one invocation.
    bases = ((repo_root,) if repo_carries_index_builder(repo_root) else ()) + (script_tree_root(),)
    for base in bases:
        for relative in REFRESH_SCRIPT_RELATIVE:
            candidate = base / relative
            if candidate.is_file():
                return f"python3 {spell(candidate, repo_root, relative)} --repo-root {repo_root}"
    return (
        f"python3 {PLUGIN_DIR_TOKEN}/{REFRESH_SCRIPT_RELATIVE[1].as_posix()} "
        f"--repo-root {repo_root}"
    )


def stale_index_message(index_ref: str, repo_root: Path) -> str:
    """The refusal for a lesson-selection index that no longer matches its generator.

    Order matters. This message used to lead with `--write`, and a real investigation
    followed it: `--write` produced identical bytes (the index was correct for THAT
    repo's code), so the operator concluded the failure was elsewhere and spent a full
    gate cycle on the quality suite. The discriminator has to come first, because when
    a foreign copy wrote the index, `--write` through that same copy is a loop.

    But only where a foreign copy is a hypothesis that CAN be true. Emitting the
    foreign-copy paragraph unconditionally told a consuming repo that the installed
    copy it must use is the cause, then named a `scripts/` path that repo does not
    have -- so the only way forward was the action the message warned against. There,
    the installed copy IS the repo's copy, and the honest reading is plain staleness.
    """
    write_command = index_build_command(repo_root, "--write")
    if repo_carries_index_builder(repo_root):
        return (
            f"retro lesson selection index `{index_ref}` does not match what this "
            "repo's own code produces.\n"
            "FIRST, check who wrote it: if you ran a charness helper from an "
            "installed/exported copy (`~/.agents/...`, `$SKILL_DIR`, "
            "`plugins/charness/...`) against this repo, that copy's schema is the "
            "cause. Re-run from this repo's own copy; running `--write` through the "
            "foreign copy overwrites the fix and re-triggers this failure.\n"
            f"Otherwise the index is genuinely stale: run `{write_command}`. If that "
            "produces no diff, you are in the first case, not this one."
        )
    return (
        f"retro lesson selection index `{index_ref}` does not match what the charness "
        "copy you just ran produces.\n"
        f"This repo carries no `{INDEX_SCRIPT_RELATIVE.as_posix()}` of its own, so the "
        "installed copy is the only copy and there is no foreign-copy question to "
        "settle: the index is stale relative to that copy. Rebuild it with\n"
        f"  {write_command}\n"
        "If the rebuilt index differs in its top-level KEYS or in the field set of its "
        "candidates -- not just in candidate counts -- then the copy you ran is a "
        "different charness version than the one that wrote the file, and the rebuild "
        "is a version upgrade rather than a refresh. Review that diff before "
        "committing it."
    )
