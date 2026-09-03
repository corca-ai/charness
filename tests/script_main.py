from __future__ import annotations

import contextlib
import functools
import importlib.util
import io
import os
import sys
from pathlib import Path
from types import SimpleNamespace


@functools.cache
def load_script_module(module_name: str, module_path: str | Path) -> object:
    """Load a script in-process the way a child interpreter would see it.

    A child interpreter puts the script's own directory first on `sys.path`, so a
    flat sibling import (`from runtime_budget_sizing_lib import ...` inside a lib
    the script loads) resolves. This loader restores `sys.path` afterwards, which
    is right, but until 2026-09-03 it never ADDED the directory either, so those
    imports resolved only when an earlier test happened to have left the directory
    on the path: the two `render_runtime_summary` / `inventory_ci_recoverable_gates`
    rows of the YAML contract test passed in the full run and failed in any
    focused selection, which is where the changed-line gate runs them.
    """
    path = Path(module_path)
    saved_path = list(sys.path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        sys.path.insert(0, str(path.resolve().parent))
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = saved_path
    return module


def run_loaded_script_main(
    script_name: str,
    module: object,
    *args: str,
    env: dict[str, str] | None = None,
    cli_error_names: tuple[str, ...] = ("ValidationError", "ExportError"),
    cli_error_types: tuple[type[BaseException], ...] = (),
) -> SimpleNamespace:
    out, err = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    saved_env = os.environ.copy()
    sys.argv = [script_name, *args]
    if env is not None:
        # A caller-supplied env REPLACES the environment, which would drop the
        # session-wide git identity and config isolation that seeded repos rely on
        # (and the #225 discovery ceiling). Carry those through unless the caller
        # deliberately set them, so an in-process main behaves like a subprocess one.
        carried = {
            name: os.environ[name]
            for name in (
                "GIT_AUTHOR_NAME",
                "GIT_AUTHOR_EMAIL",
                "GIT_COMMITTER_NAME",
                "GIT_COMMITTER_EMAIL",
                "GIT_CONFIG_GLOBAL",
                "GIT_CONFIG_NOSYSTEM",
                "GIT_CEILING_DIRECTORIES",
            )
            if name in os.environ and name not in env
        }
        os.environ.clear()
        os.environ.update(carried)
        os.environ.update(env)
    os.environ.setdefault("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", "1")
    returncode = 0
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                returncode = module.main() or 0
            except SystemExit as exc:
                if isinstance(exc.code, int):
                    returncode = exc.code
                elif exc.code is None:
                    returncode = 0
                else:
                    returncode = 1
                    print(str(exc.code), file=sys.stderr)
            except Exception as exc:
                if not isinstance(exc, cli_error_types) and exc.__class__.__name__ not in cli_error_names:
                    raise
                returncode = 1
                print(str(exc), file=sys.stderr)
    finally:
        sys.argv = saved_argv
        os.environ.clear()
        os.environ.update(saved_env)
    return SimpleNamespace(returncode=returncode, stdout=out.getvalue(), stderr=err.getvalue())
