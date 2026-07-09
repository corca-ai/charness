"""Pure splitter + git-plumbing helpers for `generate_prompt_mutants.py`.

Split a skill's prompt surface (SKILL.md + references/*.md) into section-level
mutation units, and build/cleanup throwaway mutant commits over those units
using object-database plumbing ONLY (`git hash-object` / `read-tree` /
`update-index --cacheinfo` / `write-tree` / `commit-tree` / `update-ref`) --
NEVER `git checkout`/`add`/`commit`/`reset`/`stash` in the shared worktree
(#258 hygiene; charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md
plan-critique F4).

Canonical prompt surface: mutants target `plugins/charness/skills/<skill>/**`
(the installed-plugin mirror `capture-skill-run.sh` actually resolves), not
only the `skills/public/<skill>/**` source (plan-critique F1). The
`skills/public/...` sibling is mutated too when it contains an
identical-by-content copy of the removed section.

A "unit" is one markdown section: a heading line (any level) plus its body up
to the next heading of the SAME OR HIGHER level -- so a `###` nested under a
`##` is folded into the `##` unit's own content, while the `###` heading also
gets its own (finer-grained, independently selectable) unit. Because of that
nesting, the file-reassembly (lossless) invariant holds only over the
TOP-LEVEL units (those not nested inside another unit in the same file) plus
the preamble: those spans are contiguous and non-overlapping and tile the
whole file. Nested units are additional, finer-grained entries for selection,
not part of that flat tiling.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import tempfile
from pathlib import Path

from artifact_naming_lib import slugify

_HEADING_RE = re.compile(r"^(#{1,6})(\s+.*)?$")
_FENCE_RE = re.compile(r"^(`{3,}|~{3,})")

MUTANT_REF_PREFIX = "refs/prompt-mutants"
NEUTRAL_COMMIT_MESSAGE = "chore: snapshot"
# Fixed neutral identity (#423-class leak, plan-critique F5): a descriptive
# message would let a captured run read which unit was removed, or that it is
# in an experiment, via `git log`. The commit DATE deliberately does NOT use a
# fixed epoch: it reuses the baseline commit's own committer date (see
# `resolve_baseline_committer_date` below), because a mutant timestamped
# 2000-01-01 as the child of a real (e.g. 2026-dated) baseline is itself an
# arm-asymmetric oddity a captured run's `git log -1` could notice. Reusing
# the baseline's own date keeps every mutant commit dated identically to its
# parent -- still fully deterministic per baseline, just not a giveaway.
NEUTRAL_AUTHOR_NAME = "charness"
NEUTRAL_AUTHOR_EMAIL = "charness@example.invalid"


class PromptMutantError(RuntimeError):
    pass


# --- splitting (pure, no I/O) ----------------------------------------------


def split_units(text: str) -> list[dict]:
    """Split `text` into section units: one `preamble` unit (content before the
    first heading, always present) followed by one unit per heading line, in
    document order. Each unit's `content` is the exact contiguous slice of
    `text` it owns (0-based line slice `lines[start:end]`), so re-slicing the
    original text at those boundaries is exact -- never re-derived from a hash
    or a fuzzy match. `heading_level` is 0 for the preamble. `top_level` is
    True for the preamble and for headings not nested inside another unit in
    this file (see module docstring); only `top_level` units tile the file
    losslessly."""
    lines = text.splitlines(keepends=True)
    headings: list[tuple[int, int, str]] = []  # (0-based line index, level, title)
    fence_char: str | None = None
    fence_len = 0
    for idx, line in enumerate(lines):
        stripped = line.rstrip("\r\n")
        lstripped = stripped.lstrip()
        fence_match = _FENCE_RE.match(lstripped)
        if fence_match:
            marker = fence_match.group(1)
            if fence_char is None:
                fence_char, fence_len = marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_len:
                fence_char, fence_len = None, 0
            continue
        if fence_char is not None:
            continue
        heading_match = _HEADING_RE.match(stripped)
        if heading_match:
            level = len(heading_match.group(1))
            title = (heading_match.group(2) or "").strip()
            headings.append((idx, level, title))

    units: list[dict] = []
    preamble_end = headings[0][0] if headings else len(lines)
    units.append(
        {
            "heading_level": 0,
            "heading_path": ["preamble"],
            "start_line": 1,
            "end_line": preamble_end,
            "content": "".join(lines[0:preamble_end]),
            "top_level": True,
        }
    )

    ancestors: list[tuple[int, str]] = []
    for position, (idx, level, title) in enumerate(headings):
        end_idx = len(lines)
        for later_idx, later_level, _later_title in headings[position + 1 :]:
            if later_level <= level:
                end_idx = later_idx
                break
        while ancestors and ancestors[-1][0] >= level:
            ancestors.pop()
        top_level = not ancestors
        heading_path = [ancestor_title for _level, ancestor_title in ancestors] + [title]
        units.append(
            {
                "heading_level": level,
                "heading_path": heading_path,
                "start_line": idx + 1,
                "end_line": end_idx,
                "content": "".join(lines[idx:end_idx]),
                "top_level": top_level,
            }
        )
        ancestors.append((level, title))
    return units


def reassemble_top_level(units: list[dict]) -> str:
    """Concatenate the `top_level` units of one file's `split_units` output, in
    order -- the lossless-reassembly proof: this must equal the original text
    byte-for-byte."""
    return "".join(unit["content"] for unit in units if unit["top_level"])


def unit_content_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def build_unit_id(file_relpath: str, heading_path: list[str], content: str) -> str:
    digest = unit_content_sha256(content)
    slug = "/".join(slugify(part) for part in heading_path)
    return f"{file_relpath}#{slug}@{digest[:10]}"


def units_for_file(file_relpath: str, text: str) -> list[dict]:
    """`split_units(text)` decorated with the stable `unit_id` and `file` every
    downstream consumer (manifest output, mutant construction) keys off."""
    entries = []
    for unit in split_units(text):
        content = unit["content"]
        entries.append(
            {
                "unit_id": build_unit_id(file_relpath, unit["heading_path"], content),
                "file": file_relpath,
                "heading_path": unit["heading_path"],
                "heading_level": unit["heading_level"],
                "start_line": unit["start_line"],
                "end_line": unit["end_line"],
                "content_sha256": unit_content_sha256(content),
                "content": content,
                "top_level": unit["top_level"],
            }
        )
    return entries


def remove_unit_by_lines(text: str, start_line: int, end_line: int) -> str:
    """Splice out the 1-based inclusive line range `[start_line, end_line]`
    (as produced by `split_units`) from `text`."""
    lines = text.splitlines(keepends=True)
    return "".join(lines[: start_line - 1] + lines[end_line:])


# --- file discovery (worktree vs baseline-ref-aware) ------------------------


def skill_plugin_root(skill: str) -> str:
    return f"plugins/charness/skills/{skill}"


def skill_public_root(skill: str) -> str:
    return f"skills/public/{skill}"


def list_skill_files_worktree(repo_root: Path, skill: str) -> list[tuple[str, str | None]]:
    """(plugin_relpath, public_relpath_or_None) pairs from the checked-out
    worktree: SKILL.md first, then references/*.md sorted by name."""
    plugin_root = skill_plugin_root(skill)
    public_root = skill_public_root(skill)
    relpaths: list[str] = []
    if (repo_root / plugin_root / "SKILL.md").is_file():
        relpaths.append(f"{plugin_root}/SKILL.md")
    refs_dir = repo_root / plugin_root / "references"
    if refs_dir.is_dir():
        relpaths.extend(
            f"{plugin_root}/references/{path.name}" for path in sorted(refs_dir.glob("*.md"))
        )
    result = []
    for relpath in relpaths:
        suffix = relpath[len(plugin_root) + 1 :]
        candidate_public = f"{public_root}/{suffix}"
        public = candidate_public if (repo_root / candidate_public).is_file() else None
        result.append((relpath, public))
    return result


def read_worktree_file(repo_root: Path, relpath: str) -> str | None:
    try:
        return (repo_root / relpath).read_text(encoding="utf-8")
    except OSError:
        return None


def _git_ls_tree_paths(repo_root: Path, ref: str, path: str) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "ls-tree", "-r", "--name-only", ref, "--", path],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return set()
    return {line for line in result.stdout.splitlines() if line}


def list_skill_files_at_ref(repo_root: Path, ref: str, skill: str) -> list[tuple[str, str | None]]:
    """Ref-aware sibling of `list_skill_files_worktree`: enumerates files via
    `git ls-tree` at `ref` instead of globbing the checkout, so `generate`
    matches unit ids to the BASELINE commit even when it differs from the
    checked-out worktree."""
    plugin_root = skill_plugin_root(skill)
    public_root = skill_public_root(skill)
    plugin_paths = _git_ls_tree_paths(repo_root, ref, plugin_root)
    public_paths = _git_ls_tree_paths(repo_root, ref, public_root)
    relpaths: list[str] = []
    skill_md = f"{plugin_root}/SKILL.md"
    if skill_md in plugin_paths:
        relpaths.append(skill_md)
    refs_prefix = f"{plugin_root}/references/"
    relpaths.extend(
        sorted(p for p in plugin_paths if p.startswith(refs_prefix) and p.endswith(".md"))
    )
    result = []
    for relpath in relpaths:
        suffix = relpath[len(plugin_root) + 1 :]
        candidate_public = f"{public_root}/{suffix}"
        result.append((relpath, candidate_public if candidate_public in public_paths else None))
    return result


def read_file_at_ref(repo_root: Path, ref: str, relpath: str) -> str | None:
    """Read `relpath` at `ref` via `git show`, decoding the captured bytes as
    UTF-8 EXPLICITLY -- never `subprocess.run(..., text=True)`'s locale-
    dependent decode. A locale-default decode can hash-drift a unit id across
    machines/CI (a different codec for the same em-dash bytes changes
    `unit_content_sha256`) or crash outright under a `C`/`POSIX` locale, even
    though this repo's skill prose is UTF-8 by convention."""
    result = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{ref}:{relpath}"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8")


# --- split manifest (used by the `split` CLI subcommand) --------------------


def build_split_manifest(repo_root: Path, skill: str, granularity: str, list_files, read_file) -> dict:
    """Assemble the `split` subcommand's manifest. `list_files(repo_root, skill)`
    and `read_file(repo_root, relpath)` are injected so this same builder
    serves both the worktree-backed `split` CLI and (via a ref-bound closure)
    a baseline-ref-aware split for `generate`."""
    if granularity != "section":
        raise PromptMutantError(f"unsupported granularity: {granularity!r} (only 'section' is implemented)")
    file_pairs = list_files(repo_root, skill)
    if not file_pairs:
        raise PromptMutantError(f"no SKILL.md found for skill {skill!r} under {skill_plugin_root(skill)}")
    files_out = []
    units_out = []
    for plugin_relpath, public_relpath in file_pairs:
        text = read_file(repo_root, plugin_relpath)
        if text is None:
            continue
        for entry in units_for_file(plugin_relpath, text):
            units_out.append(
                {
                    "unit_id": entry["unit_id"],
                    "file": entry["file"],
                    "public_sibling": public_relpath,
                    "heading_path": entry["heading_path"],
                    "heading_level": entry["heading_level"],
                    "start_line": entry["start_line"],
                    "end_line": entry["end_line"],
                    "content_sha256": entry["content_sha256"],
                }
            )
        files_out.append({"path": plugin_relpath, "public_sibling": public_relpath})
    return {"skill": skill, "granularity": granularity, "files": files_out, "units": units_out}


# --- mutant construction (object-database plumbing only) --------------------


def _run_git(repo_root: Path, args: list[str], *, env: dict | None = None, input_text: str | None = None) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
        input=input_text,
    )
    if result.returncode != 0:
        raise PromptMutantError(f"git {' '.join(args)} failed (rc={result.returncode}): {result.stderr.strip()}")
    return result.stdout.strip()


def resolve_baseline_sha(repo_root: Path, baseline_ref: str) -> str:
    return _run_git(repo_root, ["rev-parse", baseline_ref])


def resolve_baseline_committer_date(repo_root: Path, baseline_sha: str) -> str:
    """The baseline commit's own committer date, in git's `--date=raw` form
    (`<unix-seconds> <tz-offset>` -- directly usable as GIT_AUTHOR_DATE /
    GIT_COMMITTER_DATE). Deterministic per baseline (same input, same output
    every call) and never a fixed epoch a real baseline's child would
    visibly mismatch (#423-class leak, plan-critique F5)."""
    return _run_git(repo_root, ["show", "-s", "--format=%cd", "--date=raw", baseline_sha])


def _hash_object(repo_root: Path, content: str) -> str:
    return _run_git(repo_root, ["hash-object", "-w", "--stdin"], input_text=content)


def build_mutant_commit(
    repo_root: Path,
    baseline_sha: str,
    plugin_path: str,
    new_plugin_content: str,
    public_path: str | None,
    new_public_content: str | None,
    commit_date: str,
) -> str:
    """One mutant commit whose tree equals `baseline_sha`'s tree except
    `plugin_path` (and `public_path`, when given) are replaced -- built purely
    via a TEMPORARY `GIT_INDEX_FILE`, `read-tree`/`update-index --cacheinfo`/
    `write-tree`/`commit-tree`. Never touches the real index or working tree.
    `commit_date` is the baseline commit's own committer date (see
    `resolve_baseline_committer_date`), reused for BOTH author and committer
    date so the mutant shares its parent's timestamp instead of a fixed
    epoch."""
    with tempfile.TemporaryDirectory(prefix="charness-prompt-mutant-") as tmp:
        index_path = str(Path(tmp) / "index")
        index_env = {**os.environ, "GIT_INDEX_FILE": index_path}
        _run_git(repo_root, ["read-tree", baseline_sha], env=index_env)
        plugin_blob = _hash_object(repo_root, new_plugin_content)
        _run_git(repo_root, ["update-index", "--cacheinfo", f"100644,{plugin_blob},{plugin_path}"], env=index_env)
        if public_path is not None and new_public_content is not None:
            public_blob = _hash_object(repo_root, new_public_content)
            _run_git(
                repo_root, ["update-index", "--cacheinfo", f"100644,{public_blob},{public_path}"], env=index_env
            )
        tree_sha = _run_git(repo_root, ["write-tree"], env=index_env)
    commit_env = {
        **os.environ,
        "GIT_AUTHOR_NAME": NEUTRAL_AUTHOR_NAME,
        "GIT_AUTHOR_EMAIL": NEUTRAL_AUTHOR_EMAIL,
        "GIT_AUTHOR_DATE": commit_date,
        "GIT_COMMITTER_NAME": NEUTRAL_AUTHOR_NAME,
        "GIT_COMMITTER_EMAIL": NEUTRAL_AUTHOR_EMAIL,
        "GIT_COMMITTER_DATE": commit_date,
    }
    return _run_git(repo_root, ["commit-tree", tree_sha, "-p", baseline_sha, "-m", NEUTRAL_COMMIT_MESSAGE], env=commit_env)


def mutant_ref_name(skill: str, content_sha256: str) -> str:
    """`refs/prompt-mutants/<skill>/<content-sha256>` -- DIGEST-ONLY, with NO
    unit slug or heading name in the leaf. A captured run can enumerate refs
    (or read `git log --decorate`), and a unit-named leaf (the previous
    `<slug>-<hash>` shape) would leak which section was removed just from the
    ref name, even without reading the diff. The manifest (unit_id -> ref/SHA)
    is the only place that maps a unit back to its ref; nothing about the ref
    name itself should be legible."""
    return f"{MUTANT_REF_PREFIX}/{skill}/{content_sha256}"


def collect_baseline_units(repo_root: Path, baseline_sha: str, skill: str) -> tuple[dict[str, dict], dict[str, str]]:
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
        for entry in units_for_file(plugin_relpath, text):
            entry["public_sibling"] = public_relpath
            units_by_id[entry["unit_id"]] = entry
        if public_relpath is not None and public_relpath not in file_text:
            public_text = read_file_at_ref(repo_root, baseline_sha, public_relpath)
            if public_text is not None:
                file_text[public_relpath] = public_text
    return units_by_id, file_text


def mutate_unit(
    repo_root: Path, skill: str, baseline_sha: str, unit: dict, file_text: dict[str, str], commit_date: str
) -> dict:
    """Build and ref one mutant for `unit`. The public sibling is mutated too
    only when it contains the exact unit content (match by content); otherwise
    only the plugin path is mutated and `public_mutated` is False."""
    plugin_path = unit["file"]
    new_plugin_content = remove_unit_by_lines(file_text[plugin_path], unit["start_line"], unit["end_line"])
    public_path = unit.get("public_sibling")
    public_mutated = False
    new_public_content = None
    if public_path is not None:
        public_text = file_text.get(public_path)
        if public_text is not None and unit["content"] in public_text:
            new_public_content = public_text.replace(unit["content"], "", 1)
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
    mutant_ref = mutant_ref_name(skill, unit["content_sha256"])
    _run_git(repo_root, ["update-ref", mutant_ref, mutant_sha])
    files_mutated = [plugin_path] + ([public_path] if public_mutated else [])
    return {
        "unit_id": unit["unit_id"],
        "mutant_ref": mutant_ref,
        "mutant_sha": mutant_sha,
        "files_mutated": files_mutated,
        "public_mutated": public_mutated,
    }


def generate_mutants(repo_root: Path, skill: str, baseline_ref: str, unit_ids: list[str] | None) -> dict:
    """Resolve `baseline_ref`, split fresh at that commit, build one mutant
    commit per selected unit (default: every unit), and return the mutation
    manifest {"skill", "baseline_sha", "units": [...]}. Re-running with the
    same inputs reproduces the same mutant SHAs (the commit's tree/parent/
    message/identity/date are all deterministic -- the date is the baseline
    commit's own committer date, resolved once per baseline_sha), so refs are
    updated in place -- idempotent by construction, not by a separate
    existence check."""
    baseline_sha = resolve_baseline_sha(repo_root, baseline_ref)
    commit_date = resolve_baseline_committer_date(repo_root, baseline_sha)
    units_by_id, file_text = collect_baseline_units(repo_root, baseline_sha, skill)
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
        mutate_unit(repo_root, skill, baseline_sha, units_by_id[unit_id], file_text, commit_date)
        for unit_id in selected
    ]
    return {"skill": skill, "baseline_sha": baseline_sha, "units": results}


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
