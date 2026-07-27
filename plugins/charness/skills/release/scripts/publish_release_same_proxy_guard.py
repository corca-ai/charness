"""The same-proxy guard: is this "distinct channel" probe the SAME proxy?

One concept, split out of `publish_release_post_create.py` (which reached its
length cap): given a configured `post_publish_distinct_channel_probe` and the
backend's own `release_view` command, decide whether they are the same query
wearing a different spelling — and say so when that cannot be decided.

North-star P4 lives here. A release confirmed through the very channel it was
supposed to be checked against is not confirmed at all, so this module is
deliberately biased toward FLAGGING: every branch that cannot ESTABLISH
distinctness returns True.
"""
from __future__ import annotations

import shlex
from pathlib import PurePosixPath
from typing import Any

# Executables that run ANOTHER command rather than being the command, so the
# same-proxy check must look through them instead of at them.
_COMMAND_WRAPPERS = frozenset(
    {"sh", "bash", "zsh", "dash", "env", "command", "nohup", "time", "stdbuf", "nice", "setsid"}
)
_WRAPPER_INLINE_FLAGS = frozenset({"-c", "-lc", "-cl", "-ic"})


_UNWRAP_BUDGET = 32


def _normalize_tokens(tokens: list[str], *, drop: set[str] | None = None) -> set[str]:
    """Tokens as a comparison set: EVERY token reduced to its path basename, not
    only the executable. Basenaming just the first token let a wrapper and an
    absolute path compose into an escape (`sudo /usr/bin/gh release view v1`),
    even though each half alone was caught."""
    dropped = drop or set()
    return {PurePosixPath(token).name for token in tokens if token and token not in dropped}


def _unwrap_command_tokens(tokens: list[str], *, depth: int = _UNWRAP_BUDGET) -> tuple[list[str], bool]:
    """``(tokens, exhausted)`` after stripping leading env assignments and wrapper
    executables and descending into a wrapper's inline `-c "<command>"` payload.

    ``exhausted`` is True when the budget ran out with unwrapping still to do.
    The caller treats that as same-proxy: a probe nested past the budget is one
    this check could not establish anything about, and at a publish boundary an
    unestablished scope must not read as a clean pass.
    """
    while tokens:
        if depth <= 0:
            return tokens, True
        head = tokens[0]
        # `FOO=bar gh ...`
        if "=" in head and not head.startswith("-") and "/" not in head.split("=", 1)[0]:
            tokens, depth = tokens[1:], depth - 1
            continue
        if PurePosixPath(head).name in _COMMAND_WRAPPERS:
            rest = tokens[1:]
            if rest and rest[0] in _WRAPPER_INLINE_FLAGS:
                try:
                    tokens = shlex.split(rest[1], comments=True) if len(rest) > 1 else []
                except ValueError:
                    return tokens, True
            else:
                tokens = rest
            depth -= 1
            continue
        break
    return tokens, False


def release_view_shape(backend: dict[str, Any], backend_command, tag_name: str) -> set[str] | None:
    """The backend's own ``release_view`` command as a tag-free comparison set,
    or ``None`` when the template cannot discriminate.

    A degenerate template — empty, or a single generic token like ``gh`` — makes
    subset matching meaningless in both directions: it would refuse every probe
    sharing an executable, or pass everything. ``None`` says the guard could not
    be evaluated, which the caller records rather than silently reading as
    "distinct" (the class-(a) shape this audit tracks).
    """
    view_tokens = backend_command(backend, "release_view", ["gh", "release", "view", "{tag}"], tag=tag_name)
    shape = _normalize_tokens(view_tokens, drop={tag_name})
    return shape if len(shape) >= 2 else None


def _probe_matches_release_view_shape(
    rendered_command: str, *, backend: dict[str, Any], backend_command, tag_name: str
) -> bool:
    """Data-driven same-proxy check (P4): True when the rendered probe command IS
    the backend's own ``release_view`` command -- the exact command
    ``verify_release_visible`` already used for tag/version visibility -- derived
    from the backend config via ``backend_command``, never an enumerated list of
    forbidden command strings.

    Matching is by NORMALIZED TOKEN CONTAINMENT, not by positional prefix. A
    prefix comparison was defeated by everything that does not change what runs
    (D3): moving a flag ahead of the tag, `sh -c "..."`, `env`, or an absolute
    `/usr/bin/gh` path all slipped through while running the identical query.
    Wrappers are unwrapped, the executable is reduced to its basename, and the
    probe matches when it contains every token of the view command in any order.

    Deliberately biased toward FLAGGING at this boundary: a probe wrongly called
    same-proxy costs the operator one genuinely distinct probe, while a same-proxy
    probe wrongly called distinct is a release confirming itself through the
    channel it was supposed to be checked against. Every branch that cannot
    ESTABLISH distinctness therefore returns True, including an unparseable
    command and an unwrap budget exhausted mid-descent.

    The TAG is excluded from the comparison. `gh release view` with no tag
    defaults to the latest release — which, moments after publish, is the release
    being confirmed — so requiring the tag to appear let the same query through
    by omitting an argument.
    """
    view_shape = release_view_shape(backend, backend_command, tag_name)
    if view_shape is None:
        # A degenerate `release_view` template (empty, or a single generic token
        # like `gh`) cannot discriminate: subset-matching against it would either
        # refuse every probe sharing an executable or silently pass everything.
        # Neither verdict is established, so do not render one.
        return False
    try:
        raw_tokens = shlex.split(rendered_command, comments=True)
    except ValueError:
        return True
    probe_tokens, exhausted = _unwrap_command_tokens(raw_tokens)
    if exhausted:
        return True
    if not probe_tokens:
        return False
    return view_shape.issubset(_normalize_tokens(probe_tokens))
