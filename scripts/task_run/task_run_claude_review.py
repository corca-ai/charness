"""Private Codex preflight state for a Claude lane, owned by runtime retention."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Mapping


def reviewer_home(execution_runtime: Path) -> Path:
    """The review writer and later Claude mask share one private-home path."""
    return execution_runtime.resolve() / "brief-critique-home"


def private_review_environment(env: Mapping[str, str], execution_runtime: Path) -> dict[str, str]:
    """Keep reviewer sessions/config writes away from the operator's real home.

    Only authentication is inherited, when environment authentication is absent;
    no configuration, plugin, shell startup file or session tree is copied.
    The enclosing execution runtime owns this directory's retention.
    """
    child = dict(env)
    source = Path(child.get("CODEX_HOME") or Path.home() / ".codex").expanduser()
    home = reviewer_home(execution_runtime)
    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    home.chmod(0o700)
    roots = {
        "HOME": home,
        "CODEX_HOME": home / ".codex",
        "CLAUDE_CONFIG_DIR": home / ".claude",
        "CEAL_HOME": home / ".ceal",
        "XDG_CONFIG_HOME": home / ".config",
        "XDG_CACHE_HOME": home / ".cache",
        "XDG_STATE_HOME": home / ".local/state",
        "TMPDIR": home / "tmp",
        "TMP": home / "tmp",
        "TEMP": home / "tmp",
    }
    for path in set(roots.values()):
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
    for name in ("BASH_ENV", "ENV", "ZDOTDIR"):
        child.pop(name, None)
    child.update({name: str(path) for name, path in roots.items()})
    auth = source / "auth.json"
    target = roots["CODEX_HOME"] / "auth.json"
    if (
        not any(child.get(name) for name in ("OPENAI_API_KEY", "CODEX_API_KEY"))
        and auth.is_file()
        and auth.resolve() != target.resolve()
    ):
        target_fd = os.open(
            target,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW,
            0o600,
        )
        with auth.open("rb") as source_file, os.fdopen(target_fd, "wb") as destination:
            os.fchmod(destination.fileno(), 0o600)
            shutil.copyfileobj(source_file, destination)
    return child
