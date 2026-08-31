#!/usr/bin/env python3
"""Suggest a focused pytest command for changed-line coverage production."""
from __future__ import annotations

import argparse
import ast
import re
import shlex
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:  # pragma: no cover - import bootstrap
    sys.path.insert(0, str(REPO_ROOT))

from scripts.mutation_changed_files_lib import changed_pool_files_vs_base  # noqa: E402
from scripts.mutation_coverage_producer import default_mutation_base_sha  # noqa: E402
from scripts.run_standing_pytest import expand_targets  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

HELP_EPILOG = """\
Statuses:
  recommended  all changed mutation-pool files map to standing pytest targets
  partial      at least one changed file maps, and at least one does not
  missing      changed mutation-pool files exist, but none map to standing tests
  noop         no eligible mutation-pool files changed over base -> worktree
  blocked      base discovery failed; pass --base-sha explicitly

Workflow:
  1. Use --detail only when mappings or machine-readable reasoning are needed;
     the default prints only the copyable producer command.
  2. For recommended, pass closeout_args or command to --mutation-coverage-command.
  3. For partial, inspect unmapped_changed_pool_files before trusting the focused
     producer; use broad coverage fallback when those files need proof.
  4. For missing or blocked, run the broad mutation coverage producer instead.
"""

_LITERAL_PATH_LOADERS = frozenset(
    {
        "load_local_skill_module",
        "_load_local_release_module",
        "_load_sibling",
        # `tests/script_loader.load_script_module` is this repo's own by-path test
        # loader, and its call shape hides the reference from every other pattern
        # here: the module name argument is a test-local alias
        # (`"generate_release_notes_under_test"`), and the file argument is a
        # `DIR / "name.py"` expression, so neither the quoted-path, dotted-module,
        # import-statement, segment-chain, nor stem-as-argument pattern can see it.
        # Measured: `generate_release_notes.py` was reported as mapping to NO
        # standing test while `tests/quality_gates/test_release_notes_claims.py`
        # drove it through 27 cases, and the lane warned that it had analyzed 69 of
        # 70 changed pool files with a clean verdict saying nothing about the rest.
        # By the lane's exit contract that incompleteness is not a pass once the
        # analyzed part stops blocking -- an inference from the contract, not an
        # outcome anyone observed, because coverage was still failing at the time.
        # This is the mapper gap `release_changed_line_coverage.py` names as the
        # mapper's to close rather than the policy's.
        "load_script_module",
    }
)


def _module_name(path: str) -> str:
    without_suffix = path[:-3] if path.endswith(".py") else path
    return without_suffix.replace("/", ".")


def _reference_patterns(path: str) -> list[re.Pattern[str]]:
    module = _module_name(path)
    parent, _, name = module.rpartition(".")
    escaped_path = re.escape(path)
    escaped_module = re.escape(module)
    patterns = [
        re.compile(rf"['\"]{escaped_path}['\"]"),
        re.compile(
            r"\s*/\s*".join(
                rf"['\"]{re.escape(segment)}['\"]" for segment in path.split("/")
            )
        ),
    ]
    if path.endswith(".py"):
        # The bare dotted-module pattern belongs ONLY to importable modules. For an
        # extensionless root script there is no `import <name>` to find, so this
        # pattern matches coincidences instead of references -- and for the script
        # literally named `charness` the coincidence is the repository's own name.
        # Measured: `['"]charness['"]` selects 85 of 529 test files; `\bcharness\b`
        # selects 328. All 243 files in the difference were read, and NONE drives the
        # root CLI -- they carry `corca-ai/charness` (a repo slug), `.charness/` (a
        # config directory), or `charness-checkout`. That over-match is what made the
        # "focused" changed-line lane select most of the suite and run for minutes.
        #
        # The over-matching-is-safe note below still holds where a referent exists;
        # it stops holding when the pattern has no referent at all, because then the
        # only thing it can add is noise.
        patterns.append(re.compile(rf"\b{escaped_module}\b"))
    if parent and name:
        patterns.extend(
            [
                re.compile(rf"\bfrom\s+{re.escape(parent)}\s+import\s+.*\b{re.escape(name)}\b"),
                re.compile(rf"\bfrom\s+{escaped_module}\s+import\b"),
                re.compile(rf"\bimport\s+{escaped_module}\b"),
                # The stem as a CALL ARGUMENT: `_load("nose_report_lib")`,
                # `load_script_module("x_under_test", DIR / "x.py")`. This repo's tests
                # routinely import a production module by stem while assembling its
                # directory separately, so none of the patterns above can see the
                # reference — not the quoted path, not the dotted module, not an import
                # statement. That blind spot does not merely FAIL to map: the ancestor
                # climb below then maps the file to whichever OTHER test does mention a
                # loader parent, so the mapper answers confidently with the wrong test.
                # Ground truth for the case that exposed it: `nose_report_shape_lib`'s
                # changed lines are covered by `tests/test_nose_inprocess_coverage.py`
                # (18/18) and by NOTHING in `test_quality_nose_advisory.py`, which is
                # what the mapper returned.
                #
                # Over-matching here is the safe direction: an extra test in the focused
                # set can only ADD measured coverage, never remove it, so a loose match
                # costs runtime while a missed one costs a false block.
                re.compile(rf"\w+\(\s*(?:[^()]*?,\s*)?['\"]{re.escape(name)}['\"]"),
            ]
        )
    return patterns


def _reference_prefilter(path: str) -> str:
    """A literal every `_reference_patterns` entry requires the text to contain.

    Each pattern anchors on the quoted path, the dotted module, an import of the
    module, a path-segment chain, or the stem as a call argument — and the stem is a
    substring of all of them. So a text without the stem cannot match ANY of them, and
    this one `in` check prunes it before the regexes run. That matters because the
    closure now spans the whole mutation pool (~900 sources): without the prefilter the
    scan is `changed_paths x ancestor_levels x sources x patterns` with a backtracking
    stem pattern, which took this mapper from under a second to over five minutes and
    would have made the pre-push lane unusable.
    """
    stem = path.rsplit("/", 1)[-1]
    return stem[:-3] if stem.endswith(".py") else stem


def _loads_local_sibling(text: str, module_stem: str) -> bool:
    token = re.escape(module_stem)
    return bool(
        re.search(
            rf"(?:load_local_skill_module\([^)]*?,\s*|_load_local_release_module\(\s*|"
            rf"_load_sibling\(\s*(?:[^,)]*?,\s*)?)"
            rf"['\"]{token}['\"]",
            text,
        )
        or re.search(rf"with_name\(\s*['\"]{token}\.py['\"]\s*\)", text)
    )


def _loader_literal_tokens(text: str) -> set[str]:
    """Literal path/module tokens nested inside supported dynamic loaders.

    Tests commonly spell a script as
    ``load_local_skill_module(str(SKILL_SCRIPTS / "entry.py"), "sibling")``.
    The existing regex deliberately cannot cross the nested ``str(...)`` call,
    so it misses a real dependency and the focused lane reports the changed file
    as unmapped. AST traversal keeps the exception at the loader boundary instead
    of treating every quoted filename in a test as executable reachability.

    A basename-only match can select an extra test when two directories carry the
    same script name. That is the selector's safe error direction: extra focused
    runtime or a local false stop, never a false covered verdict.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()

    tokens: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Attribute):
            name = function.attr
        elif isinstance(function, ast.Name):
            name = function.id
        else:
            continue
        if name not in _LITERAL_PATH_LOADERS:
            continue
        tokens.update(
            child.value
            for child in ast.walk(node)
            if isinstance(child, ast.Constant) and isinstance(child.value, str)
        )
    return tokens


def _loader_tokens_reference(tokens: set[str], path: str) -> bool:
    target = Path(path)
    return bool(tokens & {path, target.name, target.stem})


def _local_loader_ancestor_levels(repo_root: Path, path: str) -> list[list[str]]:
    """Find same-directory loader parents, nearest first."""
    related = {path}
    frontier = {path}
    levels: list[list[str]] = []
    while frontier:
        parents: set[str] = set()
        for child_path in frontier:
            child = Path(child_path)
            directory = repo_root / child.parent
            if not directory.is_dir():
                continue
            for candidate in directory.glob("*.py"):
                relative = candidate.relative_to(repo_root).as_posix()
                if relative in related:
                    continue
                try:
                    text = candidate.read_text(encoding="utf-8")
                except OSError:
                    continue
                if _loads_local_sibling(text, child.stem):
                    parents.add(relative)
        if not parents:
            break
        level = sorted(parents)
        levels.append(level)
        related.update(parents)
        frontier = parents
    return levels


def _candidate_test_sources(repo_root: Path) -> list[str]:
    paths: list[str] = []
    for target in expand_targets(repo_root):
        absolute = repo_root / target
        if absolute.is_dir():
            paths.extend(
                path.relative_to(repo_root).as_posix()
                for path in absolute.rglob("*.py")
            )
        elif target.endswith(".py") and absolute.is_file():
            paths.append(target)
    return sorted(dict.fromkeys(paths))


def _module_name_to_path(paths: list[str]) -> dict[str, str]:
    return {_module_name(path): path for path in paths}


def _local_import_paths(path: str, text: str, module_paths: dict[str, str]) -> set[str]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    current = _module_name(path).split(".")
    found: set[str] = set()
    for node in ast.walk(tree):
        candidates: list[str] = []
        if isinstance(node, ast.Import):
            candidates.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = current[:-node.level] if node.level else []
            module = node.module.split(".") if node.module else []
            base = ".".join([*prefix, *module])
            if base:
                candidates.append(base)
            candidates.extend(
                ".".join(part for part in (base, alias.name) if part)
                for alias in node.names
                if alias.name != "*"
            )
        found.update(module_paths[module] for module in candidates if module in module_paths)
    return found


def _test_source_closures(source_text: dict[str, str]) -> dict[str, set[str]]:
    module_paths = _module_name_to_path(list(source_text))
    dependencies = {
        path: _local_import_paths(path, text, module_paths)
        for path, text in source_text.items()
    }
    closures: dict[str, set[str]] = {}
    for test_path in source_text:
        if not Path(test_path).name.startswith("test_"):
            continue
        reachable = {test_path}
        frontier = [test_path]
        while frontier:
            dependency = dependencies.get(frontier.pop(), set()) - reachable
            reachable.update(dependency)
            frontier.extend(dependency)
        closures[test_path] = reachable
    return closures


def _candidate_module_sources(repo_root: Path) -> list[str]:
    """Mutation-pool production modules, so the import closure can span them.

    Without these, `_test_source_closures` only walks imports BETWEEN test files, and a
    production module is reachable only when some test mentions it textually. A
    `test -> production_a -> production_b` chain therefore leaves `production_b`
    unmapped even though running that one test covers it. Sourcing the pool from the
    same helper the gate uses keeps the two from disagreeing about what a pool file is.
    """
    from scripts.sample_mutation_files import list_eligible  # local: keeps CLI import cheap

    return sorted(list_eligible(repo_root))


def tests_referencing_paths(repo_root: Path, changed_paths: list[str]) -> dict[str, list[str]]:
    source_text: dict[str, str] = {}
    for source_path in [*_candidate_test_sources(repo_root), *_candidate_module_sources(repo_root)]:
        if source_path in source_text:
            continue
        try:
            source_text[source_path] = (repo_root / source_path).read_text(encoding="utf-8")
        except OSError:
            continue
    test_sources = _test_source_closures(source_text)
    loader_tokens = {
        source_path: _loader_literal_tokens(text)
        for source_path, text in source_text.items()
        if any(loader in text for loader in _LITERAL_PATH_LOADERS)
    }
    matches: dict[str, list[str]] = {}
    for changed_path in changed_paths:
        # A changed file inside the closure of a test is covered BY RUNNING that test —
        # no textual mention required. This is the structural half; the pattern search
        # below stays for references the import graph cannot see (path strings, stems
        # handed to a dynamic loader, subprocess invocations).
        reached_by = sorted(
            test_path
            for test_path, dependencies in test_sources.items()
            if changed_path in dependencies
        )
        path_levels = [[changed_path], *_local_loader_ancestor_levels(repo_root, changed_path)]
        all_found: set[str] = set()
        for level in path_levels:
            probes = [
                (related, _reference_prefilter(related), _reference_patterns(related))
                for related in level
            ]
            referring_sources = {
                source_path
                for source_path, text in source_text.items()
                if any(
                    prefilter in text
                    and (
                        any(pattern.search(text) for pattern in patterns)
                        or _loader_tokens_reference(loader_tokens.get(source_path, set()), related)
                    )
                    for related, prefilter, patterns in probes
                )
            }
            all_found.update(
                test_path
                for test_path, dependencies in test_sources.items()
                if dependencies & referring_sources
            )
        all_found.update(reached_by)
        if all_found:
            matches[changed_path] = sorted(all_found)
    return {path: sorted(paths) for path, paths in matches.items() if paths}


def build_recommendation(repo_root: Path, *, base_sha: str | None = None) -> dict[str, object]:
    base = (base_sha or default_mutation_base_sha(repo_root)).strip()
    if not base:
        return {
            "status": "blocked",
            "reason": "could not resolve merge-base with origin/main; pass --base-sha explicitly",
            "changed_pool_files": [],
        }
    changed = changed_pool_files_vs_base(repo_root, base)
    if not changed:
        return {
            "status": "noop",
            "reason": "no eligible mutation-pool files changed over base -> worktree",
            "base_sha": base,
            "changed_pool_files": [],
        }
    matches = tests_referencing_paths(repo_root, changed)
    missing = [path for path in changed if path not in matches]
    targets = sorted({test_path for paths in matches.values() for test_path in paths})
    if not targets:
        return {
            "status": "missing",
            "reason": (
                "no standing pytest target references the changed pool files or "
                "their local-loader ancestors"
            ),
            "base_sha": base,
            "changed_pool_files": changed,
            "unmapped_changed_pool_files": missing,
        }
    command = shlex.join(
        [
            "python3",
            "scripts/run_standing_pytest.py",
            "--repo-root",
            ".",
            "--mode",
            "read-only",
            *(token for target in targets for token in ("--pytest-target", target)),
        ]
    )
    status = "recommended" if not missing else "partial"
    reason = (
        "direct, imported-helper, or loader-entrypoint references found in standing "
        "pytest targets; use the command as changed-line coverage evidence while "
        "retaining broad proof"
    )
    if status == "partial":
        reason = (
            "textual references found for a subset of changed pool files; the command "
            "only proves mapped files, so inspect unmapped_changed_pool_files or use "
            "the broad coverage fallback"
        )
    return {
        "status": status,
        "reason": reason,
        "base_sha": base,
        "changed_pool_files": changed,
        "mapped_tests_by_file": matches,
        "unmapped_changed_pool_files": missing,
        "command": command,
        "closeout_args": [
            "--produce-mutation-coverage",
            "--mutation-coverage-command",
            command,
        ],
    }


def _format_text_diagnostics(payload: dict[str, object]) -> list[str]:
    status = str(payload["status"])
    reason = str(payload["reason"])
    lines = [f"status: {status}", reason]
    unmapped = payload.get("unmapped_changed_pool_files")
    if isinstance(unmapped, list) and unmapped:
        lines.append("unmapped_changed_pool_files:")
        lines.extend(f"  - {path}" for path in unmapped)
    if status == "partial":
        lines.append(
            "NEXT: pass the printed command only if the mapped subset is enough; "
            "otherwise use the broad coverage fallback."
        )
    elif status == "missing":
        lines.append("NEXT: use the broad coverage fallback; no focused producer was found.")
    elif status == "noop":
        lines.append("NEXT: no mutation coverage producer is needed for this diff.")
    elif status == "blocked":
        lines.append("NEXT: pass --base-sha or ensure origin/main is available.")
    return lines


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--base-sha", default=None)
    parser.add_argument(
        "--detail",
        action="store_true",
        help="emit the full recommendation as YAML instead of compact command output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = args.repo_root.resolve()
    payload = build_recommendation(repo_root, base_sha=args.base_sha)
    if args.detail:
        emit_yaml(payload)
    else:
        command = payload.get("command")
        if command:
            print(command)
            if payload["status"] == "partial":
                print("\n".join(_format_text_diagnostics(payload)), file=sys.stderr)
        else:
            print("\n".join(_format_text_diagnostics(payload)), file=sys.stderr)
    return 0 if payload["status"] in {"recommended", "partial", "noop"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
