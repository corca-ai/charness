from __future__ import annotations

import contextlib
import io
import os
import sys
from types import SimpleNamespace


def run_loaded_script_main(
    script_name: str,
    module: object,
    *args: str,
    env: dict[str, str] | None = None,
    cli_error_names: tuple[str, ...] = ("ValidationError", "ExportError"),
) -> SimpleNamespace:
    out, err = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    saved_env = os.environ.copy()
    sys.argv = [script_name, *args]
    if env is not None:
        os.environ.clear()
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
                if exc.__class__.__name__ not in cli_error_names:
                    raise
                returncode = 1
                print(str(exc), file=sys.stderr)
    finally:
        sys.argv = saved_argv
        os.environ.clear()
        os.environ.update(saved_env)
    return SimpleNamespace(returncode=returncode, stdout=out.getvalue(), stderr=err.getvalue())
