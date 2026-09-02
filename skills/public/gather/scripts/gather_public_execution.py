"""Run gather helper commands and decode their structured output.

This module owns the execution seam used when gather invokes acquisition and
record-writing helpers: it isolates bare sibling imports for in-process runs,
captures their output, and refuses anything that is not a mapping. Keeping
that execution policy together lets ``gather_public_url.py`` own only the
acquisition and record decisions that are specific to its command.
"""

from __future__ import annotations

import contextlib
import io
import runpy
import sys
from pathlib import Path
from types import ModuleType


def _evict_shadowing_siblings(sibling_dir: str) -> dict[str, ModuleType]:
    """Snapshot sys.modules and drop bare names that shadow a sibling file.

    Returns the snapshot so the caller can restore the table after the run.
    """
    saved_modules = dict(sys.modules)
    for name, loaded in list(sys.modules.items()):
        loaded_file = getattr(loaded, "__file__", None)
        if "." in name or not loaded_file or not (Path(sibling_dir) / f"{name}.py").is_file():
            continue
        if not str(Path(loaded_file).resolve()).startswith(sibling_dir):
            del sys.modules[name]
    return saved_modules


def run_json(
    command: list[str],
    *,
    input_text: str | None = None,
    yaml_module,
    support_acquire: Path,
    write_record: Path,
    run_process,
) -> dict[str, object]:
    """Run a gather helper and return its YAML/JSON mapping payload.

    The caller supplies the existing gather paths and guarded runner so this
    seam preserves the author's dependency-resolution and monkeypatch surface.
    """
    self_script = Path(command[1]) if len(command) > 1 and command[0] == sys.executable else None
    if self_script is not None and self_script.resolve() in {
        support_acquire.resolve(),
        write_record.resolve(),
    }:
        sibling_dir = str(self_script.resolve().parent)
        added_sibling_dir = sibling_dir not in sys.path
        if added_sibling_dir:
            sys.path.insert(0, sibling_dir)
        # A child interpreter started with an empty module table; this in-process run
        # does not. The sibling imports bare names (`resolve_adapter`, `gather_writer_lib`)
        # and fifteen skills ship a `resolve_adapter.py`, so a process that already
        # imported another skill's copy would hand gather that skill's adapter and write
        # the record under its output directory. Evict any bare-name entry that shadows
        # a sibling file, and restore the table afterwards so the run leaves no trace.
        saved_modules = _evict_shadowing_siblings(sibling_dir)
        try:
            module = runpy.run_path(str(self_script))
        except Exception as exc:
            sys.modules.clear()
            sys.modules.update(saved_modules)
            if added_sibling_dir:
                sys.path.remove(sibling_dir)
            raise SystemExit(str(exc)) from exc
        old_argv = sys.argv
        old_stdin = sys.stdin
        stdout = io.StringIO()
        stderr = io.StringIO()
        sys.argv = [str(self_script), *command[2:]]
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                if input_text is not None:
                    sys.stdin = io.StringIO(input_text)
                code = module["main"]()
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
        finally:
            sys.argv = old_argv
            sys.stdin = old_stdin
            sys.modules.clear()
            sys.modules.update(saved_modules)
            if added_sibling_dir:
                sys.path.remove(sibling_dir)
        completed_stdout = stdout.getvalue()
        completed_stderr = stderr.getvalue()
        if code:
            raise SystemExit(
                completed_stderr.strip()
                or completed_stdout.strip()
                or f"command failed: {command!r}"
            )
        raw_stdout = completed_stdout
    else:
        if run_process is None:
            raise SystemExit("guard_unavailable:subprocess_guard.py not reachable")
        completed = run_process(command, cwd=Path.cwd(), timeout_seconds=None)
        if completed.returncode != 0:
            raise SystemExit(
                completed.stderr.strip()
                or completed.stdout.strip()
                or f"command failed: {command!r}"
            )
        raw_stdout = completed.stdout
    try:
        payload = yaml_module.safe_load(raw_stdout)
    except yaml_module.YAMLError as exc:
        raise SystemExit(f"command did not emit a readable payload: {command!r}") from exc
    if not isinstance(payload, dict):
        # `yaml.safe_load` returns a scalar where `json.loads` raised, so the mapping
        # check keeps unreadable stdout a refusal rather than an AttributeError later.
        raise SystemExit(f"command did not emit a readable payload: {command!r}")
    return payload
