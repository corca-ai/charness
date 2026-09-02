"""Coverage producer for the release-owned changed-line mutation gate.

Lever A+B (decided 2026-06-07): instead of a dedicated slow `dynamic_context`
probe, the release-final producer instruments an explicit focused pytest command.
It exports small coverage JSON and stamps a freshness fingerprint. The consumer
(`check_changed_line_mutation_coverage.py --require-fresh-coverage`) trusts that
coverage when its producer-qualified `.changed-line.fingerprint` marker matches
the current changed-pool content.

The transferable doctrine lives in skills/public/quality/references/mutation-testing.md.
"""

from __future__ import annotations

import shlex
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Callable


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

try:
    from scripts.core.subprocess_guard import run_process
except ModuleNotFoundError:  # executed directly from scripts/
    from scripts.core.subprocess_guard import run_process

_sampling = import_repo_module(__file__, "scripts.mutation.mutation_sampling_lib")
_changed_files = import_repo_module(__file__, "scripts.mutation.mutation_changed_files_lib")

#: Every key `mutation_sampling_lib.coverage_subprocess_env` assigns must appear
#: here, because `_with_coverage_env` re-exports these and ONLY these into the
#: instrumented shell command. `COVERAGE_FILE` was missing, and its own owner
#: states the consequence: an ambient value "sends its data to the parent file
#: instead of this report's namespaced database, so the child disappears from the
#: combined JSON" (mutation_sampling_lib.py:153-157). Measured before the repair:
#: every file in `release-changed-line-coverage`'s output read 0.0% except
#: `run_standing_pytest.py` (69.7%) -- the one process `coverage run` wrapped
#: directly. Nothing executed inside pytest or its xdist workers was measured at
#: all, so a BLOCKING release gate was rendering verdicts on coverage data that
#: contained no test-suite execution. `scripts/native_gate_lib.py` read 0.0% here
#: and 89.3% once this key was exported. `test_mutation_coverage_producer.py`
#: pins the containment rather than this literal tuple, so a key added to the
#: producer env cannot silently fail to reach the child again.
_COVERAGE_ENV_KEYS = (
    "COVERAGE_PROCESS_START",
    "COVERAGE_RCFILE",
    "PYTHONPATH",
    "COVERAGE_FILE",
)
#: Re-export, NOT a second definition (SC18). The instrumentation policy is owned
#: by `mutation_sampling_lib.classify_instrumentable_command` so this module and
#: the changed-line gate cannot drift back into opposite answers. Only names this
#: module's body or an external caller actually reads are bound here -- an unread
#: alias is a live trap (`run_standing_pytest.py`'s own re-export block records
#: why), and a first draft of this slice kept a helper-flag alias whose ONLY
#: reader was the test asserting it existed.
classify_instrumentable_command = _sampling.classify_instrumentable_command
is_standing_pytest_runner_command = _sampling.is_standing_pytest_runner_command
is_instrumentable_pytest_command = _sampling.is_instrumentable_pytest_command


def instrument_broad_command(
    command: str,
    data_file: Path,
    *,
    extra_pytest_targets: list[str] | tuple[str, ...] = (),
) -> str:
    """Rewrite an instrumentable pytest command to run under plain `coverage run`,
    preserving the remaining arguments VERBATIM (the `tests/test_*.py` glob must
    stay unquoted so bash still expands it -- which is why this builder does
    string surgery on the raw remainder rather than re-joining argv).

    Accepts exactly what `mutation_sampling_lib.classify_instrumentable_command`
    accepts; only the rendering is local. See that function for why the split is
    at the classifier rather than at a boolean."""
    classified = classify_instrumentable_command(command)
    if classified is None:
        raise ValueError(f"not an instrumentable pytest command: {command!r}")
    kind, interpreter, remainder = classified
    data_file_arg = shlex.quote(str(data_file))
    # The caller's own interpreter spelling, falling back to the SAME default the
    # argv builder uses. Previously this hardcoded `python3` while the argv builder
    # recovered the caller's `/usr/bin/python3` and otherwise used `sys.executable`,
    # so the two builders measured the same accepted command under two different
    # interpreters -- measured by a round-2 reviewer, invisible to a test that
    # compares every token except the first.
    driver = shlex.quote(interpreter or sys.executable)
    prefix = f"{driver} -m coverage run --data-file {data_file_arg}"
    if kind == _sampling.PYTEST_KIND:
        extra_suffix = (
            (" " + shlex.join(list(extra_pytest_targets))) if extra_pytest_targets else ""
        )
        return f"{prefix} -m pytest" + remainder + extra_suffix
    extra_suffix = "".join(
        f" --extra-pytest-target {shlex.quote(target)}" for target in extra_pytest_targets
    )
    return f"{prefix} " + remainder + extra_suffix


def _with_coverage_env(env: dict[str, str], command: str) -> str:
    exports = "; ".join(f"export {key}={shlex.quote(env[key])}" for key in _COVERAGE_ENV_KEYS)
    return f"{exports}; {command}"


def produce_command_coverage(
    repo_root: Path,
    command: str,
    *,
    base_sha: str,
    coverage_json: Path,
    run_command: Callable[[Path, str, str], dict[str, object]],
    phase: str = "verify",
    extra_pytest_targets: list[str] | tuple[str, ...] = (),
    include_paths: Sequence[str] | None = None,
) -> dict[str, object]:
    """Run a pytest command under plain coverage and stamp the freshness marker."""
    data_file, rcfile, env = _sampling.prepare_plain_coverage(repo_root, coverage_json)
    instrumented = _with_coverage_env(
        env,
        instrument_broad_command(command, data_file, extra_pytest_targets=extra_pytest_targets),
    )
    result = dict(run_command(repo_root, instrumented, phase))
    result["command"] = command
    result["instrumented_command"] = instrumented
    if extra_pytest_targets:
        result["mutation_coverage_extra_pytest_targets"] = list(extra_pytest_targets)
    result["produced_mutation_coverage"] = False
    if result.get("returncode") == 0:
        combine_kwargs = {"show_contexts": False}
        if include_paths:
            combine_kwargs["include_paths"] = list(include_paths)
        _sampling.combine_and_export_coverage(
            repo_root, rcfile, data_file, coverage_json, env, **combine_kwargs
        )
        fingerprint = _changed_files.write_coverage_fingerprint_marker(
            repo_root, coverage_json, base_sha
        )
        result["produced_mutation_coverage"] = True
        result["mutation_coverage_base_sha"] = base_sha
        result["mutation_coverage_json"] = str(coverage_json)
        result["mutation_coverage_fingerprint"] = fingerprint
    return result


def default_mutation_base_sha(repo_root: Path) -> str:
    """The merge-base with origin/main — the same base the release consumer uses
    so the producer's freshness fingerprint matches the consumer's recomputation."""
    result = run_process(
        ["git", "-C", str(repo_root), "merge-base", "origin/main", "HEAD"],
        cwd=repo_root,
        timeout_seconds=None,
    )
    return result.stdout.strip() if result.returncode == 0 else ""
