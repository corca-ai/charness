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
import shutil
import subprocess
from typing import Any

BACKEND_TIMEOUT_SECONDS = 60
BACKEND_PROBE_TIMEOUT_SECONDS = 60

PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")


def run_backend(argv: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a backend argv with no shell, capturing text output.

    `argv` is a list passed straight to the OS — body/title content lives in the
    args or in a `--body-file`, never in a shell command string, so there is no
    quoting layer to corrupt it.
    """
    try:
        return subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            timeout=BACKEND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            argv,
            124,
            str(exc.stdout or ""),
            f"timed out after {BACKEND_TIMEOUT_SECONDS}s",
        )


def _qualified(value: Any) -> str | None:
    """An `owner/repo` slug, or None when the value is not one.

    ONE rule for every shape, because round 2 found the first version applying it to the
    `repository` STRING branch and not to the `repository` DICT branch -- so
    `{"nameWithOwner": "charness"}` still returned a bare `charness`, which compares unequal to
    `corca-ai/charness` and REFUSES a correct verdict. A wrong value is worse than silence here:
    silence is accepted as "the payload does not say", while a wrong one turns a genuinely
    CLOSED issue into a closeout failure. Half an identity is silence.
    """
    if not isinstance(value, str):
        return None
    slug = value.strip().strip("/")
    parts = slug.split("/")
    if len(parts) < 2 or not all(part.strip() for part in parts):
        return None
    return slug


def answer_repo(payload: dict[str, Any]) -> str | None:
    """The `owner/repo` an issue payload says it describes, or None when it does not say.

    Two shapes are read. A `repository` object is what a host-mediated backend most naturally
    emits (`{"repository": {"nameWithOwner": "owner/repo"}}`, or an `owner`/`name` pair). A
    `url` is what the gh provider offers, because `gh issue view` has no `repository` JSON
    field at all -- `--json repository` exits with `Unknown JSON field`.

    The URL shapes recognised are named rather than implied, because a positional guess is what
    made the first version return a WRONG repository:

    - `<host>/<owner>/<repo>/issues|pull/<number>` -- the web URL, any host.
    - `<host>/repos/<owner>/<repo>/issues/<number>` -- the REST API URL.

    Anything else returns None. That includes a path-PREFIXED install
    (`https://host/gh/owner/repo/issues/<n>`) and providers that nest differently, so the guard
    is genuinely inert for those hosts rather than merely believed to cover them. None is the
    safe direction: it is accepted, whereas a wrong value refuses a correct verdict.

    None means the payload does not say, which is NOT the same as saying the wrong thing. The
    caller must treat those two differently or a correct backend that reports no repository
    becomes permanently UNKNOWN.
    """
    repository = payload.get("repository")
    if isinstance(repository, dict):
        for key in ("nameWithOwner", "full_name"):
            qualified = _qualified(repository.get(key))
            if qualified is not None:
                return qualified
        owner = repository.get("owner")
        if isinstance(owner, dict):
            owner = owner.get("login") or owner.get("name")
        name = repository.get("name")
        if isinstance(owner, str) and isinstance(name, str):
            # Each half must be a single unqualified segment, or `a/b` + `c` silently yields a
            # three-segment slug that names nothing.
            if owner.strip() and name.strip() and "/" not in owner and "/" not in name:
                return f"{owner.strip()}/{name.strip()}"
        return None
    qualified = _qualified(repository)
    if qualified is not None:
        return qualified
    url = payload.get("url")
    if isinstance(url, str):
        path = url.strip().split("://", 1)[-1]
        path = path.split("#", 1)[0].split("?", 1)[0]
        parts = [part for part in path.rstrip("/").split("/") if part]
        if len(parts) == 5 and parts[3] in {"issues", "pull", "issue"} and parts[4]:
            return _qualified(f"{parts[1]}/{parts[2]}")
        if len(parts) == 6 and parts[1] == "repos" and parts[4] == "issues" and parts[5]:
            return _qualified(f"{parts[2]}/{parts[3]}")
    return None


def issue_identity_mismatches(
    payload: object, *, expected_repo: str, expected_number: int
) -> list[dict[str, Any]]:
    """Return every mismatch between an issue answer and its requested target.

    A command containing ``--repo`` and ``number`` is only a request. The answer is
    the evidence, and an omitted repository or a non-integer number is an unknown
    target, not a successful match. Keeping this rule here prevents close and
    verify-closeout from maintaining subtly different identity floors.
    """
    if not isinstance(payload, dict):
        return [{"field": "payload", "expected": "issue object", "actual": type(payload).__name__}]
    mismatches: list[dict[str, Any]] = []
    reported_number = payload.get("number")
    if type(reported_number) is not int or reported_number != expected_number:
        mismatches.append(
            {"field": "number", "expected": expected_number, "actual": reported_number}
        )
    reported_repo = answer_repo(payload)
    if not isinstance(reported_repo, str) or reported_repo.strip().lower() != expected_repo.strip().lower():
        mismatches.append(
            {"field": "repository", "expected": expected_repo, "actual": reported_repo}
        )
    return mismatches


def require_exact_issue_identity(
    payload: object, *, expected_repo: str, expected_number: int, context: str
) -> None:
    """Raise when a live issue response cannot prove the requested target."""
    mismatches = issue_identity_mismatches(
        payload, expected_repo=expected_repo, expected_number=expected_number
    )
    if mismatches:
        labels = {"repository": "different repository", "number": "different issue"}
        details = ", ".join(
            f"{labels.get(item['field'], item['field'])}: expected {item['expected']!r}, "
            f"got {item['actual']!r}"
            for item in mismatches
        )
        raise RuntimeError(f"{context} did not prove the requested issue target: {details}")


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
    used = {match for part in template for match in PLACEHOLDER_RE.findall(part)}
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
    rendered = [part.format(**subs) if "{" in part else part for part in template]
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
    try:
        result = subprocess.run(
            [binary, *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=BACKEND_PROBE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "exit_code": 124,
            "stdout": str(exc.stdout or "").strip(),
            "stderr": f"timed out after {BACKEND_PROBE_TIMEOUT_SECONDS}s",
        }
    return {"exit_code": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


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
    return True


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
    payload: dict[str, Any] = {"ok": ok, "selected_backend": selected, "adapter": resolved["adapter"]}
    if selected["id"] == "gh":
        payload.update(gh_found=selected["found"], gh_path=selected["binary_path"], auth_status=selected["auth_status"])
    if not selected["found"]:
        payload["error"] = (
            f"issue_backend binary {selected['binary']!r} not found on PATH. "
            f"Install the declared backend or update issue_backend in "
            f".agents/issue-adapter.yaml so it matches a backend the host exposes."
        )
    return payload
