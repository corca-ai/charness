"""Shared issue-backend invocation primitives.

`issue_close` and `issue_create` both turn an adapter-resolved backend command
template into a concrete argv and run it without a shell. Keeping the templating
and subprocess primitives here means there is one source of truth for how a
backend op is rendered and invoked — no shell string interpolation anywhere, so
multi-line / Unicode / quote / dollar-sign content in a body file reaches the
backend byte-for-byte.
"""

from __future__ import annotations

import re
import runpy
import shutil
import string
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir.parent))
    from scripts.core.subprocess_guard import run_process

BACKEND_TIMEOUT_SECONDS = 60
BACKEND_PROBE_TIMEOUT_SECONDS = 60
PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
IDENTITY = _load_local("issue_identity", "issue_backend_identity")
answer_repo = IDENTITY.answer_repo
issue_identity_mismatches = IDENTITY.issue_identity_mismatches
require_exact_issue_identity = IDENTITY.require_exact_issue_identity


def run_backend(argv: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a backend argv with no shell, capturing text output.

    `argv` is a list passed straight to the OS — body/title content lives in the
    args or in a `--body-file`, never in a shell command string, so there is no
    quoting layer to corrupt it.
    """
    try:
        return run_process(argv, cwd=Path.cwd(), timeout_seconds=BACKEND_TIMEOUT_SECONDS)
    except OSError as exc:
        return subprocess.CompletedProcess(argv, 127, "", str(exc))


def _scope_waived(
    backend: dict[str, Any], subs: dict[str, str], *, waivable: frozenset[str]
) -> frozenset[str]:
    """Required placeholders this backend may omit because its BINARY already carries them.

    `{repo}` is half of an issue's identity, and a template that does not spell it silently
    drops the caller's repo: `resolve_op` validates that every placeholder the TEMPLATE uses is
    allowed and that every REQUIRED one is used, but a substitution the caller supplies and the
    template never consumes is dropped without comment. Against a host binary whose default
    repository differs from the one being asked about, the answer is then about a different
    repository's issue with the same number -- and a downstream number check cannot see it,
    because that issue's number is the number that was asked for. The observed result is a live
    backlog citation reported CLOSED, with no diagnostic anywhere.

    Requiring `{repo}` outright was rejected for a real reason: a host binary genuinely bound
    to one repository declares no `{repo}` and was working. So the requirement stands and the
    WAIVER becomes a declaration -- with two conditions a bounded round showed are both
    load-bearing:

    - **It names the repository.** `repo_scoped: owner/repo`, never a bare `true`. This skill
      routes to TWO targets (an upstream harness repo and the local one), and a waiver that
      cannot say which repository it covers would drop the repo on the target the binary is
      not bound to -- reintroducing the defect for the case nobody would test.
    - **The CALL SITE opts in.** `waivable` defaults to empty, so no existing caller is
      loosened by this existing. A staleness READER can afford the waiver, because its wrong
      answer is a stale pickup line. The closeout verifier cannot, because its wrong answer
      closes a real issue, and that boundary is not reversible.

    Only `repo` is ever waivable. `number` is not, and deliberately so: no binary carries the
    issue number implicitly, and a `view_state` template omitting it resolves to a listing
    whose first row is then read as the asked-about issue's state.
    """
    if "repo" not in waivable:
        return frozenset()
    scoped = backend.get("repo_scoped")
    if not isinstance(scoped, str) or not scoped.strip():
        return frozenset()
    asked = subs.get("repo")
    # The declaration covers ONE repository, so the waiver needs a repo to compare against.
    # FAIL CLOSED when there is none: the first version skipped the comparison whenever `repo`
    # was absent from the substitutions, which waived unconditionally — a waiver that cannot
    # say which repository it covers is the exact thing requiring the named value removed.
    if not isinstance(asked, str) or asked.strip().lower() != scoped.strip().lower():
        return frozenset()
    return frozenset({"repo"})


def backend_binary(backend: dict[str, Any], adapter_key: str = "issue_backend") -> str:
    """The binary an adapter-declared backend runs, or a refusal naming the key to configure.

    Split out of `resolve_op` so a caller whose BUILT-IN DEFAULT is not a template can still
    reach the binary rule without re-deriving it. `issue_source_capture_lib` is that caller:
    its gh default is a conditionally assembled GraphQL invocation, so it cannot delegate the
    rendering, but it was re-implementing `backend.get("binary") or backend.get("id")` to build
    it -- the cheapest half of this rule and the half a copy delegates first.
    """
    binary = backend.get("binary") or backend.get("id")
    if not binary:
        raise RuntimeError(
            f"{adapter_key} produced no binary; configure {adapter_key}.id and "
            f"{adapter_key}.binary in the adapter file."
        )
    return binary


def resolve_op(
    backend: dict[str, Any],
    op: str,
    default: list[str],
    allowed: frozenset[str],
    required: frozenset[str] = frozenset(),
    waivable: frozenset[str] = frozenset(),
    adapter_key: str = "issue_backend",
    **subs: str,
) -> list[str]:
    """Render one backend op template into a concrete argv.

    Uses the adapter's `commands.<op>` template when present, else the `gh`
    default for the default backend. Validates the template's placeholders
    against the op's allowlist and required set so an adapter cannot smuggle an
    unknown placeholder or omit a required one.
    """
    extra_subs = sorted(set(subs) - allowed)
    if extra_subs:
        raise RuntimeError(
            f"resolve_op({op}): caller passed placeholders {extra_subs!r} "
            f"not in op's allowlist {sorted(allowed)!r}"
        )
    # `adapter_key` names the SUBJECT of the messages, not a second rule. The rendering rule
    # reads only `binary`, `id` and `commands`, so it was already agnostic about which adapter
    # key produced the dict -- the only coupling to `issue_backend` was in these strings, which
    # is why a second skill had to copy the whole function to get a message naming its own key.
    binary = backend_binary(backend, adapter_key)
    commands = backend.get("commands") or {}
    template = commands.get(op)
    if template is None:
        if backend.get("id", "gh") != "gh":
            raise RuntimeError(
                f"{adapter_key}.id={backend.get('id')} did not declare commands.{op}; "
                "configure the adapter command template before calling this op."
            )
        template = default
    if not isinstance(template, list) or any(not isinstance(part, str) for part in template):
        raise RuntimeError(f"resolve_op({op}): adapter template must be a list of strings")
    formatter = string.Formatter()
    used: set[str] = set()
    try:
        for part in template:
            for _literal, field_name, format_spec, conversion in formatter.parse(part):
                if field_name is None:
                    continue
                if format_spec or conversion:
                    raise RuntimeError(
                        f"resolve_op({op}): adapter placeholders cannot use conversions or format specs; "
                        "literal braces must be doubled as '{{' and '}}'"
                    )
                used.add(field_name)
    except ValueError as exc:
        raise RuntimeError(
            f"resolve_op({op}): adapter template has malformed format grammar: {exc}"
        ) from exc
    unknown = sorted(used - allowed)
    if unknown:
        raise RuntimeError(
            f"resolve_op({op}): adapter template uses unknown placeholders {unknown!r}; "
            f"allowed for {op}: {sorted(allowed)!r}"
        )
    missing_required = sorted(required - used - _scope_waived(backend, subs, waivable=waivable))
    if missing_required:
        raise RuntimeError(
            f"resolve_op({op}): adapter template is missing required placeholders "
            f"{missing_required!r}"
        )
    try:
        rendered = [part.format(**subs) if "{" in part else part for part in template]
    except (KeyError, ValueError, IndexError, AttributeError) as exc:
        raise RuntimeError(f"resolve_op({op}): adapter template rendering failed: {exc}") from exc
    return [binary, *rendered]


def op_is_declared(backend: dict[str, Any], op: str) -> bool:
    """Whether this backend can build `op` at all: it declared a template, or it is `gh`."""
    if (backend.get("commands") or {}).get(op) is not None:
        return True
    return backend.get("id", "gh") == "gh"


def try_resolve_op(
    backend: dict[str, Any],
    op: str,
    default: list[str],
    allowed: frozenset[str],
    required: frozenset[str] = frozenset(),
    waivable: frozenset[str] = frozenset(),
    adapter_key: str = "issue_backend",
    **subs: str,
) -> list[str] | None:
    """`resolve_op`, except an UNDECLARED op on a non-`gh` backend returns None.

    Same rendering, same placeholder validation, one different answer to one question.
    `resolve_op` raises there because its callers are acting on the tracker and an
    unconfigured op is a configuration error. A reader that only reports FACTS needs the
    opposite: `handoff`'s staleness path turns None into UNKNOWN, and raising -- or guessing
    -- would manufacture the stale verdict that surface exists to refuse.

    That difference is why the rule was copied into two other modules instead of reused. It is
    the only difference, so it is expressed as one extra entry point here rather than as a
    second implementation of the binary/template/substitution rules. Everything else still
    raises: a bad placeholder is a caller bug in both worlds and must not become a silent None.
    """
    if not op_is_declared(backend, op):
        return None
    return resolve_op(backend, op, default, allowed, required, waivable, adapter_key, **subs)


def run_probe(binary: str, args: list[str]) -> dict[str, Any]:
    result = run_process(
        [binary, *args], cwd=Path.cwd(), timeout_seconds=BACKEND_PROBE_TIMEOUT_SECONDS
    )
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def probe_backend(backend: dict[str, Any]) -> dict[str, Any]:
    # Same binary rule as `resolve_op`, through the same helper — this function had its own
    # copy of the expression, which is the shape the consolidation exists to remove.
    binary = backend_binary(backend)
    binary_path = shutil.which(binary)
    selected: dict[str, Any] = {
        "id": backend.get("id", "gh"),
        "binary": binary,
        "binary_path": binary_path,
        "found": binary_path is not None,
        "commands": backend.get("commands"),
        "auth_status": None,
        "version": None,
    }
    if binary_path is None:
        return selected
    if selected["id"] == "gh":
        selected["auth_status"] = run_probe(binary, ["auth", "status"])
    else:
        selected["version"] = run_probe(binary, ["--version"])
    return selected


def backend_ok(selected: dict[str, Any]) -> bool:
    if not selected["found"]:
        return False
    if selected["id"] == "gh":
        return bool(selected["auth_status"]) and selected["auth_status"]["exit_code"] == 0
    return bool(selected["version"]) and selected["version"]["exit_code"] == 0


def build_preflight_payload(resolved: dict[str, Any]) -> dict[str, Any]:
    try:
        selected = probe_backend(resolved["backend"])
    except RuntimeError as exc:
        return {
            "ok": False,
            "error": str(exc),
            "adapter": resolved["adapter"],
            "selected_backend": resolved["backend"],
        }
    ok = resolved["adapter_ok"] and backend_ok(selected)
    payload: dict[str, Any] = {
        "ok": ok,
        "selected_backend": selected,
        "adapter": resolved["adapter"],
    }
    if selected["id"] == "gh":
        payload.update(
            gh_found=selected["found"],
            gh_path=selected["binary_path"],
            auth_status=selected["auth_status"],
        )
    if not selected["found"]:
        payload["error"] = (
            f"issue_backend binary {selected['binary']!r} not found on PATH. "
            f"Install the declared backend or update issue_backend in "
            f".agents/issue-adapter.yaml so it matches a backend the host exposes."
        )
    return payload
