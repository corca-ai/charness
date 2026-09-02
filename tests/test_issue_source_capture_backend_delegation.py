"""The capture lane's command resolution delegates to the backend owner, and refuses typed.

Split out of `test_issue_source_capture.py` when that file crossed its length cap. The split is
cohesive rather than mechanical: everything here is about ONE question — does the capture lane
resolve its backend command through `issue_backend`, the contractual owner of that rule, or
re-derive it? — while the parent file is about capture COMPLETENESS (pagination, totals,
duplicate ids, receipts).

The lane used to carry a fourth copy of the rule: the same binary fallback, the same
`commands.<op>` lookup, the same built-in default, and the same substitution, WITHOUT the
owner's placeholder allowlist. Its built-in gh default genuinely cannot delegate — it is a
conditionally assembled GraphQL invocation, not a template — but that covered only one of two
branches, and the branch needing the allowlist was exactly the branch that fits the owner.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def test_the_capture_allowlist_is_derived_from_the_substitutions_not_restated() -> None:
    """One declaration, asserted as one declaration rather than as two that happen to match.

    A hand-written allowlist beside the `subs` dict is two statements of one set. A missing
    entry silently refuses a previously-valid template; an extra one re-opens the hole the
    allowlist closes. Deriving removes the failure mode instead of testing for it — and this
    pin fails if someone re-introduces the second copy.
    """
    from scripts.issue.issue_source_capture_lib import (
        SOURCE_CAPTURE_PLACEHOLDERS,
        capture_subs,
    )

    offered = capture_subs("o/r", "o", "r", 1, 50, None)
    assert set(offered) == set(SOURCE_CAPTURE_PLACEHOLDERS)
    # Every substitution renders to a string, or `part.format` produces something a shell
    # never sees as one argument.
    assert all(isinstance(value, str) for value in offered.values()), offered
    # And `after` is normalised rather than passed as None, which would render as "None".
    assert offered["after"] == ""


def test_the_backend_owner_loader_is_exercised_not_re_implemented() -> None:
    """CALL the loader. A first version of this test rebuilt the candidate list and asserted on
    its own copy, so it would have passed with the loader deleted, with the wrong package root,
    or with the refusal misspelled — a second copy of the rule under test, inside the slice
    about copies of a rule.
    """
    import scripts.issue.issue_source_capture_lib as lib

    lib._ISSUE_BACKEND_OWNER = None
    owner = lib._issue_backend_owner()
    assert hasattr(owner, "resolve_op") and hasattr(owner, "backend_binary")
    # Memoized: a second call returns the same object rather than re-exec'ing the module.
    assert lib._issue_backend_owner() is owner


def test_the_loader_refuses_a_missing_owner_with_its_own_typed_code(monkeypatch) -> None:
    """And the refusal must SURVIVE the caller's error handling.

    `CaptureRefusal` subclasses `RuntimeError`, so the broad `except RuntimeError` that
    translates the owner's errors swallowed this one and re-raised it as
    `invalid_capture_command` — sending an operator to the adapter file for what is a broken
    install. The code has to reach the caller intact or it is decoration.
    """
    import scripts.issue.issue_source_capture_lib as lib

    monkeypatch.setattr(lib, "_ISSUE_BACKEND_OWNER", None)
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    with pytest.raises(lib.CaptureRefusal) as refusal:
        lib._issue_backend_owner()
    assert refusal.value.code == "issue_backend_owner_missing"

    monkeypatch.setattr(lib, "_ISSUE_BACKEND_OWNER", None)
    backend = {"id": "gh", "binary": "gh", "commands": None}
    with pytest.raises(lib.CaptureRefusal) as through_caller:
        lib.build_page_argv(backend, "o/r", 1, 50, None)
    assert through_caller.value.code == "issue_backend_owner_missing", (
        "the loader's typed refusal was re-wrapped as an adapter-template error"
    )


def test_the_exported_mirror_can_reach_its_own_backend_owner() -> None:
    """The mirror sits at `skills/issue/...`, not `skills/public/issue/...`.

    Checked as a FILESYSTEM fact about the shipped tree rather than by re-deriving the
    candidate list: whatever the loader's logic is, the owner it needs must exist at a path
    reachable from the mirror's own location.
    """
    root = Path(__file__).resolve().parent.parent
    mirror = root / "plugins/charness/scripts/issue/issue_source_capture_lib.py"
    assert mirror.is_file(), mirror
    package_root = mirror.parent.parent.parent
    assert (package_root / "skills/issue/scripts/issue_backend.py").is_file()
    assert not (package_root / "skills/public/issue/scripts/issue_backend.py").exists(), (
        "the installed layout gained a `public` tree; the loader's candidate order needs review"
    )
    # Assert the SOURCE, not only the mirror. A mutation that drops a layout from the source
    # leaves the generated mirror stale until the next sync, so a mirror-only assertion passes
    # over a broken source — measured: this pin SURVIVED that exact mutant before this line.
    source = root / "scripts/issue/issue_source_capture_lib.py"
    for path in (source, mirror):
        text = path.read_text(encoding="utf-8")
        assert "skills/public/issue/scripts/issue_backend.py" in text, path
        assert "skills/issue/scripts/issue_backend.py" in text, (
            f"{path} knows only one layout again"
        )


def test_a_capture_template_that_names_no_repository_is_refused() -> None:
    """`(repo, number)` is the identity here too, and this capture feeds the freeze receipt.

    The owner's `required` is a flat set and cannot express `\u007brepo\u007d` OR
    `\u007bowner\u007d`+`\u007bname\u007d`, so the disjunction is checked in this lane where
    the vocabulary lives. Both real spellings resolve; a template naming neither is refused
    before the backend is reached.
    """
    from scripts.issue.issue_source_capture_lib import CaptureRefusal, build_page_argv

    def argv(parts):
        return build_page_argv(
            {"id": "acme", "binary": "acme", "commands": {"source_capture": parts}},
            "o/r", 1, 50, None,
        )

    assert argv(["cap", "{repo}", "{number}"]) == ["acme", "cap", "o/r", "1"]
    assert argv(["cap", "{owner}", "{name}", "{number}"]) == ["acme", "cap", "o", "r", "1"]
    for missing in (["cap", "{number}"], ["cap", "{owner}", "{number}"], ["cap", "{name}", "{number}"]):
        with pytest.raises(CaptureRefusal, match="names no repository"):
            argv(missing)
    with pytest.raises(CaptureRefusal, match="missing required placeholders"):
        argv(["cap", "{repo}"])


def test_a_brace_bearing_capture_template_refuses_typed_rather_than_escaping() -> None:
    """A `source_capture` template is GraphQL/JSON-shaped, so braces are the EXPECTED case.

    `PLACEHOLDER_RE` matches only `\u007blower_snake\u007d`, so a part carrying a JSON object
    clears the allowlist and then raises inside `str.format`. That escaped this lane untyped —
    the exact defect class the consolidation was filed to remove, re-created by the branch the
    consolidation added.
    """
    from scripts.issue.issue_source_capture_lib import CaptureRefusal, build_page_argv

    backend = {
        "id": "acme",
        "binary": "acme",
        "commands": {"source_capture": ["cap", "{repo}", "{number}", "-f", '{"q":1}']},
    }
    with pytest.raises(CaptureRefusal) as refusal:
        build_page_argv(backend, "o/r", 1, 50, None)
    assert refusal.value.code == "invalid_capture_command"
    assert "doubled" in str(refusal.value)
