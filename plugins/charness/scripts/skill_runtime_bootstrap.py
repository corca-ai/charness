from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _load_runtime_bootstrap_module() -> ModuleType:
    module_path = Path(__file__).resolve().parent / "runtime_bootstrap.py"
    spec = importlib.util.spec_from_file_location("scripts.runtime_bootstrap", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load runtime bootstrap from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_RUNTIME_BOOTSTRAP = _load_runtime_bootstrap_module()
arm_cli_timeout = _RUNTIME_BOOTSTRAP.arm_cli_timeout
native_core_path = _RUNTIME_BOOTSTRAP.native_core_path
load_path_module = _RUNTIME_BOOTSTRAP.load_path_module
require_repo_local_helper = _RUNTIME_BOOTSTRAP.require_repo_local_helper


def run_adapter_cli(
    resolve, *, label: str, repo_root_help: str, description: str | None = None
) -> None:
    """Shared CLI driver for skill adapter resolvers (resolve_adapter/review_adapter mains).

    Reproduces, verbatim, the main() tail every simple resolver duplicated: arm the
    CLI timeout, parse a required ``--repo-root``, then emit ``resolve(repo_root)`` as
    YAML. The per-skill ``resolve`` callable, label, help text, and
    optional parser ``description`` stay local in each script; only this invariant
    driver is shared. ``description`` defaults to ``None`` -- the argparse default --
    so callers that did not set one are byte-identical, including ``--help``. It lives
    beside ``arm_cli_timeout`` -- already called by every resolver main via
    SKILL_RUNTIME -- so sharing it adds no dependency the resolvers did not carry.
    """
    import argparse
    import sys

    render_yaml = load_path_module(
        "scripts.yaml_output", Path(__file__).resolve().parent / "yaml_output.py"
    ).render_yaml
    cancel_timeout = arm_cli_timeout(label=label)
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--repo-root", type=Path, required=True, help=repo_root_help)
    try:
        args = parser.parse_args()
        sys.stdout.write(render_yaml(resolve(args.repo_root.resolve())))
    finally:
        cancel_timeout()


def refuse_foreign_entrypoint(script_file: str | Path, repo_root: str | Path | None = None) -> dict:
    """Refuse a drifted foreign copy at a skill entrypoint, before any mutation.

    The write-site guards (`require_repo_local_helper` inside the libraries that
    write) fire only once a run reaches them — for a release, after bump,
    manifest sync, and the full quality suite. This is the same guard moved to
    the seam the operator actually invokes, so the refusal costs milliseconds
    instead of a rolled-back publish.

    Two details make the entrypoint case different from a write site, and both
    are why this wrapper exists rather than a bare call:

    - ``scan="tree"``, because the module that drifts is usually imported
      lazily, long after the entrypoint; an anchor scan here sees only what is
      already imported and reports ``in-sync``.
    - ``repo_root`` is read from ``sys.argv`` when the caller cannot supply it,
      because the check has to precede the CLI's own argument parsing.
    """
    import sys

    argv = sys.argv[1:]
    # Read-only invocations are not a mutation boundary, and refusing them takes
    # away the operator's cheapest way to inspect the copy they are holding at
    # exactly the moment they are confused about which copy that is.
    if any(token in {"-h", "--help"} for token in argv):
        return {"status": "skipped-read-only"}
    if repo_root is None:
        repo_root = Path.cwd()
        for index, token in enumerate(argv):
            # argparse accepts any unambiguous prefix, so `--repo` reaches
            # `--repo-root`. Matching only the exact spelling let that form
            # bypass the guard while the CLI still mutated the named target.
            if token.startswith("--") and "=" in token:
                flag, _, value = token.partition("=")
                if flag != "--" and "--repo-root".startswith(flag):
                    repo_root = Path(value)
                    continue
            elif token.startswith("--") and len(token) > 2 and "--repo-root".startswith(token):
                if index + 1 < len(argv):
                    repo_root = Path(argv[index + 1])
                    continue
    return require_repo_local_helper(script_file, Path(repo_root).expanduser().resolve(), scan="tree")


def repo_root_from_skill_script(script_file: str | Path) -> Path:
    """Resolve the tree root that owns a skill script, by ancestor walk only.

    The walk is layout-independent: it looks for a real marker
    (`scripts/adapter_lib.py`) rather than counting directory levels, so it
    returns the repo root in the authoring tree and `plugins/<pkg>` in an
    installed one without knowing which it is in.

    There used to be a `parents[4]` fallback here. It was BOTH dead and wrong:
    dead because the walk succeeds for every skill script in either tree
    (measured 2026-08-04 over all of `skills/**/scripts/*.py` and
    `plugins/*/skills/**/scripts/*.py`, 0 failures), and wrong because in an
    installed tree `plugins/<pkg>/skills/<skill>/scripts/x.py` has `parents[4]`
    == `plugins/`, one level ABOVE the package root the walk correctly returns.
    A fallback that cannot be reached cannot be observed to be wrong, so it would
    have stayed wrong until the day the walk first failed -- which is the day you
    least want a silently-off-by-one root. An explicit refusal is the honest
    replacement: a caller with no resolvable root cannot proceed anyway.
    """
    script_path = Path(script_file).resolve()
    for ancestor in script_path.parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            return ancestor
    raise RuntimeError(
        f"cannot resolve a tree root for skill script {script_path}: no ancestor directory "
        "contains `scripts/adapter_lib.py`. Expected the charness repo root (authoring tree) "
        "or a `plugins/<package>` directory (installed tree)."
    )


def _ensure_repo_root_on_syspath(repo_root: Path) -> None:
    import sys

    repo_root_text = str(repo_root)
    if repo_root_text not in sys.path:
        sys.path.insert(0, repo_root_text)


def load_repo_module_from_skill_script(script_file: str | Path, module_name: str) -> ModuleType:
    repo_root = repo_root_from_skill_script(script_file)
    _ensure_repo_root_on_syspath(repo_root)
    import importlib

    return importlib.import_module(module_name)


def load_local_skill_module(
    script_file: str | Path,
    module_name: str,
    *,
    file_name: str | None = None,
) -> ModuleType:
    repo_root = repo_root_from_skill_script(script_file)
    _ensure_repo_root_on_syspath(repo_root)
    script_path = Path(script_file).resolve()
    local_path = script_path.parent / (file_name or f"{module_name}.py")
    module_id = f"{script_path.stem}_{module_name}".replace("-", "_")
    return load_path_module(module_id, local_path)
