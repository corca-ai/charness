"""Git plumbing for `generate_prompt_mutants.py`: units in, throwaway commits out.

The splitting half lives in `prompt_mutant_split_lib.py` (pure, no I/O); its
public names are re-exported here so existing importers keep working. This module
builds and cleans up throwaway mutant commits over the selected units
using object-database plumbing ONLY (`git hash-object` / `read-tree` /
`update-index --cacheinfo` / `write-tree` / `commit-tree` / `update-ref`) --
NEVER `git checkout`/`add`/`commit`/`reset`/`stash` in the shared worktree
(#258 hygiene; charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md
plan-critique F4).

Canonical prompt surface: mutants target `plugins/charness/skills/<skill>/**`
(the installed-plugin mirror `capture-skill-run.sh` actually resolves), not
only the `skills/public/<skill>/**` source (plan-critique F1). The
`skills/public/...` sibling is mutated too when it contains an
identical-by-content copy of the selected section.

See `prompt_mutant_split_lib.py` for what a "unit" is and which units tile a file
losslessly -- the invariant every rewrite below depends on.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from prompt_mutant_files_lib import (
    list_skill_files_at_ref,
    read_file_at_ref,
    skill_plugin_root,
)
from prompt_mutant_rewrite_lib import (
    applied_replacement_text,
    remove_unit_by_lines,
    rewrite_matching_public_unit,
    rewrite_unit_by_lines,
)
from prompt_mutant_split_lib import (
    GRANULARITIES,
    PromptMutantError,
    build_split_manifest,
    build_unit_id,
    reassemble_top_level,
    split_units,
    unit_content_sha256,
    units_for_file,
)

# Exactly the splitter names re-exported for importers that predate the split
# (`from prompt_mutant_lib import build_split_manifest`, ...). Listed explicitly so
# the linter does not prune imports that are deliberately part of this module's
# surface. This module's OWN public functions are not listed: they are defined
# here, so they need no re-export, and mixing the two would document neither.
__all__ = [
    "GRANULARITIES",
    "PromptMutantError",
    "build_split_manifest",
    "build_unit_id",
    "reassemble_top_level",
    "split_units",
    "unit_content_sha256",
    "units_for_file",
]

MUTANT_REF_PREFIX = "refs/prompt-mutants"
NEUTRAL_COMMIT_MESSAGE = "chore: snapshot"
# Fixed neutral identity (#423-class leak, plan-critique F5): a descriptive
# message would let a captured run read which unit was removed, or that it is
# in an experiment, via `git log`. The commit DATE deliberately does NOT use a
# fixed epoch: it reuses the baseline commit's own committer date (see
# `resolve_baseline_committer_date` below), so the baseline snapshot and every
# mutant snapshot stay metadata-identical apart from their trees, while still
# remaining deterministic per baseline.
NEUTRAL_AUTHOR_NAME = "charness"
NEUTRAL_AUTHOR_EMAIL = "charness@example.invalid"
GIT_ENV_ALLOWLIST = {
    "GIT_AUTHOR_DATE",
    "GIT_AUTHOR_EMAIL",
    "GIT_AUTHOR_NAME",
    "GIT_COMMITTER_DATE",
    "GIT_COMMITTER_EMAIL",
    "GIT_COMMITTER_NAME",
    "GIT_INDEX_FILE",
}


# --- mutant construction (object-database plumbing only) --------------------


def _run_git(repo_root: Path, args: list[str], *, env: dict | None = None, input_text: str | None = None) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
        env=scrub_git_env(env),
        input=input_text,
    )
    if result.returncode != 0:
        raise PromptMutantError(f"git {' '.join(args)} failed (rc={result.returncode}): {result.stderr.strip()}")
    return result.stdout.strip()


def scrub_git_env(env: dict[str, str] | None = None) -> dict[str, str]:
    """Remove ambient git routing/config variables while preserving explicit git plumbing keys."""
    base = dict(os.environ if env is None else env)
    return {key: value for key, value in base.items() if key in GIT_ENV_ALLOWLIST or not key.startswith("GIT_")}


def resolve_baseline_sha(repo_root: Path, baseline_ref: str) -> str:
    """Resolve the original baseline provenance ref to a commit SHA."""
    return _run_git(repo_root, ["rev-parse", baseline_ref])


def resolve_baseline_tree_sha(repo_root: Path, baseline_sha: str) -> str:
    """Resolve the original baseline commit's tree for the capture-facing snapshot."""
    return _run_git(repo_root, ["rev-parse", f"{baseline_sha}^{{tree}}"])


def resolve_baseline_committer_date(repo_root: Path, baseline_sha: str) -> str:
    """The original baseline commit's own committer date, in git's `--date=raw` form
    (`<unix-seconds> <tz-offset>` -- directly usable as GIT_AUTHOR_DATE /
    GIT_COMMITTER_DATE). Deterministic per baseline (same input, same output
    every call) and never a fixed epoch a real baseline's child would
    visibly mismatch (#423-class leak, plan-critique F5)."""
    return _run_git(repo_root, ["show", "-s", "--format=%cd", "--date=raw", baseline_sha])


def neutral_commit_env(commit_date: str) -> dict[str, str]:
    """Environment for capture-facing neutral commits."""
    return {
        **scrub_git_env(),
        "GIT_AUTHOR_NAME": NEUTRAL_AUTHOR_NAME,
        "GIT_AUTHOR_EMAIL": NEUTRAL_AUTHOR_EMAIL,
        "GIT_AUTHOR_DATE": commit_date,
        "GIT_COMMITTER_NAME": NEUTRAL_AUTHOR_NAME,
        "GIT_COMMITTER_EMAIL": NEUTRAL_AUTHOR_EMAIL,
        "GIT_COMMITTER_DATE": commit_date,
    }


def _hash_object(repo_root: Path, content: str) -> str:
    return _run_git(repo_root, ["hash-object", "-w", "--stdin"], input_text=content)


def build_snapshot_commit(repo_root: Path, tree_sha: str, commit_date: str) -> str:
    return _run_git(repo_root, ["commit-tree", tree_sha, "-m", NEUTRAL_COMMIT_MESSAGE], env=neutral_commit_env(commit_date))


def build_mutant_commit(
    repo_root: Path,
    baseline_sha: str,
    plugin_path: str,
    new_plugin_content: str,
    public_path: str | None,
    new_public_content: str | None,
    commit_date: str,
) -> str:
    """One mutant snapshot whose tree equals `baseline_sha`'s tree except
    `plugin_path` (and `public_path`, when given) are replaced -- built purely
    via a TEMPORARY `GIT_INDEX_FILE`, `read-tree`/`update-index --cacheinfo`/
    `write-tree`/`commit-tree`. Never touches the real index or working tree.
    `commit_date` is the original baseline commit's own committer date (see
    `resolve_baseline_committer_date`), reused for BOTH author and committer
    date so the mutant snapshot stays metadata-identical to the capture-facing
    baseline snapshot apart from the tree."""
    with tempfile.TemporaryDirectory(prefix="charness-prompt-mutant-") as tmp:
        index_path = str(Path(tmp) / "index")
        index_env = {**scrub_git_env(), "GIT_INDEX_FILE": index_path}
        _run_git(repo_root, ["read-tree", baseline_sha], env=index_env)
        plugin_blob = _hash_object(repo_root, new_plugin_content)
        _run_git(repo_root, ["update-index", "--cacheinfo", f"100644,{plugin_blob},{plugin_path}"], env=index_env)
        if public_path is not None and new_public_content is not None:
            public_blob = _hash_object(repo_root, new_public_content)
            _run_git(
                repo_root, ["update-index", "--cacheinfo", f"100644,{public_blob},{public_path}"], env=index_env
            )
        tree_sha = _run_git(repo_root, ["write-tree"], env=index_env)
    return build_snapshot_commit(repo_root, tree_sha, commit_date)


def mutant_ref_name(skill: str, content_sha256: str) -> str:
    """Legacy `refs/prompt-mutants/<skill>/<content-sha256>` name helper.

    The leaf stays digest-only, with no unit slug or heading name, so a manual
    cleanup ref never leaks the targeted section from the ref name itself. The
    normal generate path no longer creates or depends on these refs."""
    return f"{MUTANT_REF_PREFIX}/{skill}/{content_sha256}"


def collect_baseline_units(
    repo_root: Path, baseline_sha: str, skill: str, granularity: str = "section"
) -> tuple[dict[str, dict], dict[str, str]]:
    """Split every file of `skill` freshly at `baseline_sha` (ref-aware, never
    the working tree) so unit ids match the baseline content exactly. Returns
    (units_by_id, file_text_by_relpath); file_text covers both plugin and
    (when present) public-sibling files."""
    file_pairs = list_skill_files_at_ref(repo_root, baseline_sha, skill)
    if not file_pairs:
        raise PromptMutantError(
            f"no SKILL.md found for skill {skill!r} under {skill_plugin_root(skill)} at {baseline_sha}"
        )
    units_by_id: dict[str, dict] = {}
    file_text: dict[str, str] = {}
    for plugin_relpath, public_relpath in file_pairs:
        text = read_file_at_ref(repo_root, baseline_sha, plugin_relpath)
        if text is None:
            continue
        file_text[plugin_relpath] = text
        for entry in units_for_file(plugin_relpath, text, granularity):
            entry["public_sibling"] = public_relpath
            if entry["unit_id"] in units_by_id:
                # Paragraph granularity can produce byte-identical blocks inside one
                # section, and `unit_id` is path+heading+content-digest. A silent
                # overwrite would drop an arm and quietly shrink the experiment.
                raise PromptMutantError(
                    f"duplicate unit id {entry['unit_id']!r}: two units have the same file, "
                    "heading path, and content. Disambiguate the source text or select by a "
                    "narrower granularity."
                )
            units_by_id[entry["unit_id"]] = entry
        if public_relpath is not None and public_relpath not in file_text:
            public_text = read_file_at_ref(repo_root, baseline_sha, public_relpath)
            if public_text is not None:
                file_text[public_relpath] = public_text
    return units_by_id, file_text


def mutate_unit(
    repo_root: Path,
    baseline_sha: str,
    unit: dict,
    file_text: dict[str, str],
    commit_date: str,
    replacement_text: str | None = None,
    granularity: str = "section",
) -> dict:
    """Build one mutant snapshot for `unit`.

    When `replacement_text` is None, the selected unit is removed. Otherwise,
    the selected unit content is rewritten to `replacement_text`. The public
    sibling is mutated too only when it contains the exact unit content
    (match by content); otherwise only the plugin path is mutated and
    `public_mutated` is False."""
    plugin_path = unit["file"]
    if replacement_text is None:
        operator_kind = "removal"
        replacement_for_plugin = None
        new_plugin_content = remove_unit_by_lines(file_text[plugin_path], unit["start_line"], unit["end_line"])
    else:
        operator_kind = "rewrite"
        replacement_for_plugin = applied_replacement_text(file_text[plugin_path], unit["end_line"], replacement_text)
        new_plugin_content = rewrite_unit_by_lines(
            file_text[plugin_path], unit["start_line"], unit["end_line"], replacement_text
        )
    public_path = unit.get("public_sibling")
    public_mutated = False
    new_public_content = None
    if public_path is not None:
        public_text = file_text.get(public_path)
        if public_text is not None:
            new_public_content = rewrite_matching_public_unit(
                public_text,
                unit,
                units_for_file(public_path, public_text, granularity),
                replacement_text,
            )
        if new_public_content is not None:
            public_mutated = True
    mutant_sha = build_mutant_commit(
        repo_root,
        baseline_sha,
        plugin_path,
        new_plugin_content,
        public_path if public_mutated else None,
        new_public_content if public_mutated else None,
        commit_date,
    )
    files_mutated = [plugin_path] + ([public_path] if public_mutated else [])
    record = {
        "unit_id": unit["unit_id"],
        "mutant_sha": mutant_sha,
        "files_mutated": files_mutated,
        "public_mutated": public_mutated,
        "operator_kind": operator_kind,
    }
    if replacement_for_plugin is not None:
        record["replacement_content_sha256"] = unit_content_sha256(replacement_for_plugin)
    return record


def generate_mutants(
    repo_root: Path,
    skill: str,
    baseline_ref: str,
    unit_ids: list[str] | None,
    replacement_text: str | None = None,
    granularity: str = "section",
) -> dict:
    """Resolve `baseline_ref`, split fresh at that commit, build one mutant
    commit per selected unit (default: every unit), and return the mutation
    manifest {"skill", "baseline_sha", "baseline_snapshot_sha", "units": [...]}.
    `baseline_sha` stays as provenance for the original baseline commit; the
    capture-facing baseline is `baseline_snapshot_sha`. Re-running with the
    same inputs reproduces the same snapshot SHAs (the commit's tree/
    message/identity/date are all deterministic -- the date is the original
    baseline commit's own committer date, resolved once per baseline_sha), so
    the manifest stays stable without needing live refs."""
    baseline_sha = resolve_baseline_sha(repo_root, baseline_ref)
    commit_date = resolve_baseline_committer_date(repo_root, baseline_sha)
    baseline_tree_sha = resolve_baseline_tree_sha(repo_root, baseline_sha)
    baseline_snapshot_sha = build_snapshot_commit(repo_root, baseline_tree_sha, commit_date)
    units_by_id, file_text = collect_baseline_units(repo_root, baseline_sha, skill, granularity)
    if unit_ids:
        missing = [unit_id for unit_id in unit_ids if unit_id not in units_by_id]
        if missing:
            raise PromptMutantError(
                f"unknown unit id(s) for skill {skill!r} at {baseline_ref} ({baseline_sha}): {', '.join(missing)}"
            )
        selected = unit_ids
    else:
        selected = list(units_by_id.keys())
    results = [
        mutate_unit(
            repo_root,
            baseline_sha,
            units_by_id[unit_id],
            file_text,
            commit_date,
            replacement_text,
            granularity,
        )
        for unit_id in selected
    ]
    return {
        "skill": skill,
        "baseline_sha": baseline_sha,
        "baseline_snapshot_sha": baseline_snapshot_sha,
        "units": results,
    }


# --- cleanup ------------------------------------------------------------


def list_mutant_refs(repo_root: Path, skill: str) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "for-each-ref", "--format=%(refname)", f"{MUTANT_REF_PREFIX}/{skill}/"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line]


def cleanup_mutant_refs(repo_root: Path, skill: str) -> list[str]:
    """Delete every `refs/prompt-mutants/<skill>/*` ref, returning what was
    deleted. A separate explicit step from `generate` (never auto-run) so refs
    stay alive during capture experiments."""
    refs = list_mutant_refs(repo_root, skill)
    for ref in refs:
        _run_git(repo_root, ["update-ref", "-d", ref])
    return refs
