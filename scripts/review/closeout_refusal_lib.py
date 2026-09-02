"""One refusal shape for the issue-source capture, freeze, and crosswalk lane.

These three tools exist to say no — to an unprovable capture, a stale freeze, an
unauthorized close. Their refusals were converging on the same structure by accident
(a `code`/`detail` pair, a YAML body on stdout, a named line on stderr, exit 1), which
is how two of them end up drifting into reporting the same failure differently and an
operator learns to trust whichever wording they saw first.

Naming that shape once makes it a contract instead of a coincidence: every refusal in
this lane is machine-readable on stdout, human-readable on stderr, and nonzero.
"""

from __future__ import annotations

import sys
from typing import Any, Callable


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

try:
    from scripts.yaml_output import emit_yaml
except ModuleNotFoundError:
    from yaml_output import emit_yaml


class RefusalError(RuntimeError):
    """A refusal carrying a stable machine-readable code and a human detail.

    `code` is what a test or a caller branches on and must stay stable; `detail` is
    what an operator reads and is free to improve. Keeping them separate is what lets
    the message get clearer over time without silently breaking a consumer.
    """

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def emit_refusal(tool: str, exc: RefusalError, *, code_key: str = "error") -> int:
    """Print a refusal to both channels and return the nonzero exit.

    Both channels, always: a caller piping stdout gets structured YAML, and a human
    watching a terminal gets a named line. Emitting only one is how a refusal becomes
    invisible to whichever consumer was not anticipated.
    """
    emit_yaml({"ok": False, code_key: exc.code, "detail": exc.detail})
    print(f"{tool}: REFUSED ({exc.code}) {exc.detail}", file=sys.stderr)
    return 1


def run_cli(
    tool: str,
    action: Callable[[], dict[str, Any]],
    *,
    refusals: tuple[type[Exception], ...],
    code_key: str = "error",
) -> int:
    """Run a CLI action, rendering any declared refusal through `emit_refusal`.

    `refusals` is explicit rather than a blanket `except Exception`: an unexpected
    crash must keep its traceback. A tool that renders a genuine bug as a tidy refusal
    teaches its operator that the refusal path is noisy and can be ignored.
    """
    try:
        payload = action()
    except refusals as exc:  # type: ignore[misc]
        return emit_refusal(tool, exc, code_key=code_key)
    emit_yaml(payload)
    return 0
