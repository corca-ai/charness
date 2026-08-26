"""Exact repository and issue identity parsing for provider answers."""

from __future__ import annotations

from typing import Any


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
    if (
        not isinstance(reported_repo, str)
        or reported_repo.strip().lower() != expected_repo.strip().lower()
    ):
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
