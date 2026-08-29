from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from .seeding_support import load_module
from .support import ROOT


def _load_release_module(name: str):
    module_path = ROOT / "skills" / "public" / "release" / "scripts" / f"{name}.py"
    return load_module(f"release_{name}", module_path)


def test_release_adapter_defaults_to_gh_backend(tmp_path: Path) -> None:
    resolve = _load_release_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is True
    backend = payload["data"]["release_backend"]
    assert backend == {"id": "gh", "binary": "gh", "commands": None}


def test_release_adapter_parses_custom_backend(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "release_backend:",
                "  id: acme-github",
                "  binary: acme",
                "  commands:",
                "    auth_check:",
                "      - acme",
                "      - github",
                "      - auth",
                "      - status",
                "    release_view:",
                "      - acme",
                "      - github",
                "      - release",
                "      - view",
                "      - '{tag}'",
                "    release_create:",
                "      - acme",
                "      - github",
                "      - release",
                "      - create",
                "      - '{tag}'",
                "      - '--title'",
                "      - '{title}'",
                "",
            ]
        ),
        encoding="utf-8",
    )
    resolve = _load_release_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is True
    backend = payload["data"]["release_backend"]
    assert backend["id"] == "acme-github"
    assert backend["binary"] == "acme"
    assert backend["commands"]["release_view"] == ["acme", "github", "release", "view", "{tag}"]


def test_release_adapter_preserves_fresh_checkout_probes(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "fresh_checkout_probes:",
                "- npm run claims:evidence-state:check",
                "- npm run generated:drift:check",
                "",
            ]
        ),
        encoding="utf-8",
    )
    resolve = _load_release_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is True
    assert payload["data"]["fresh_checkout_probes"] == [
        "npm run claims:evidence-state:check",
        "npm run generated:drift:check",
    ]


def test_release_adapter_rejects_invalid_fresh_checkout_probes(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "fresh_checkout_probes:",
                "- npm run ok",
                "- 12",
                "",
            ]
        ),
        encoding="utf-8",
    )
    resolve = _load_release_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is False
    assert "fresh_checkout_probes must be a list of strings" in payload["errors"]


@dataclass
class _FakeCompleted:
    returncode: int
    stdout: str = ""
    stderr: str = ""


def test_release_adapter_preflight_blocks_on_focused_failure(tmp_path: Path) -> None:
    preflight = _load_release_module("publish_release_preflight")
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs):
        calls.append(command)
        return _FakeCompleted(returncode=1, stderr="focused failure")

    payload = {
        "status": "required",
        "commands": [["pytest", "tests/quality_gates/test_release_backend.py", "-q"]],
    }

    with pytest.raises(SystemExit) as exc:
        preflight.run_release_adapter_preflight(tmp_path, payload, run_command=fake_run)

    assert calls == [["pytest", "tests/quality_gates/test_release_backend.py", "-q"]]
    assert "release adapter focused preflight blocked publish before mutation" in str(exc.value)
    assert payload["execution"]["status"] == "failed"
    assert payload["execution"]["failed_command"] == "pytest tests/quality_gates/test_release_backend.py -q"
    assert payload["execution"]["executed_commands"] == []


def test_release_adapter_preflight_records_what_it_executed(tmp_path: Path) -> None:
    """The record renders `execution`; without it a `required` status plus a command
    list reads as a satisfied requirement when nothing ran."""
    preflight = _load_release_module("publish_release_preflight")
    payload = {
        "status": "required",
        "commands": [
            ["python3", "skills/public/release/scripts/resolve_adapter.py", "--repo-root", "."],
            ["pytest", "tests/quality_gates/test_release_backend.py", "-q"],
        ],
    }

    preflight.run_release_adapter_preflight(
        tmp_path, payload, run_command=lambda command, **_kwargs: _FakeCompleted(returncode=0)
    )

    assert payload["execution"]["status"] == "passed"
    assert payload["execution"]["executed_commands"] == [
        "python3 skills/public/release/scripts/resolve_adapter.py --repo-root .",
        "pytest tests/quality_gates/test_release_backend.py -q",
    ]


def test_bump_rationale_refuses_a_forged_release_state_sentinel() -> None:
    """The value is rendered verbatim into the record, and other surfaces prove
    release state by substring-matching it. Refused at argument time, before any
    mutation -- unlike a heading, a sentinel cannot be demoted without changing what
    the operator wrote about release state."""
    preflight = _load_release_module("publish_release_preflight")
    claims = _load_release_module("publish_release_claims_review")

    assert preflight.validate_bump_rationale_arg(None) is None
    assert preflight.validate_bump_rationale_arg("patch: a validator repair") == "patch: a validator repair"

    with pytest.raises(SystemExit) as exc:
        preflight.validate_bump_rationale_arg(f"patch <!-- {claims.MARKER} -->")

    assert "--bump-rationale" in str(exc.value)


@pytest.mark.parametrize(
    "value",
    [
        "patch. <script>",
        "patch.\n<STYLE>",
        "patch. <textarea>",
        "patch. <plaintext>",
        'patch <span title="unterminated',
        "patch. <!-- see the review thread",
        "patch: only `charness worktree create --path <path>` changed",
        "patch: the reviewer read <ref>:<path> to reach the base",
        "patch: see <https://example.test/issues/1>",
        "patch: a < b held after the migration and c > d did not",
        "patch: an unclosed <details> is bounded by the blockquote",
    ],
)
def test_bump_rationale_refuses_nothing_for_how_it_might_render(value: str) -> None:
    """No construct is refused for rendering, and none is rewritten.

    A guard used to enumerate HTML that hides the rest of a rendered record. It was
    widened, narrowed and rebuilt across three review rounds and was wrong in both
    directions each time, because it decided what a renderer shows while nothing here
    can see a renderer -- this repo declares no renderer dependency, so the word
    "measured" in its docstring named an observation no reader could re-run.

    The class is closed by POSITION instead: the section is emitted last, so an
    unterminated construct has nothing below it to swallow. Both the hiders and the
    ordinary prose the wide version blocked are accepted here, and the record test
    beside this one proves the ledger survives them.
    """
    preflight = _load_release_module("publish_release_preflight")

    assert preflight.validate_bump_rationale_arg(value) == value


def test_bump_rationale_still_refuses_a_release_state_sentinel() -> None:
    """The one refusal that survives, and it is renderer-independent: other surfaces
    prove release state by substring-matching this record, so a sentinel cannot be
    neutralised by position or by quoting without changing what the operator wrote."""
    preflight = _load_release_module("publish_release_preflight")
    claims = _load_release_module("publish_release_claims_review")

    with pytest.raises(SystemExit) as exc:
        preflight.validate_bump_rationale_arg(f"patch <!-- {claims.MARKER} -->")

    assert "--bump-rationale" in str(exc.value)


def test_release_adapter_preflight_records_that_nothing_was_required(tmp_path: Path) -> None:
    preflight = _load_release_module("publish_release_preflight")
    payload = {"status": "not_required", "reason": "adapter unchanged", "commands": []}

    def refuse(command: list[str], **_kwargs):  # pragma: no cover - must not run
        raise AssertionError(f"no command should run for a not_required preflight: {command}")

    preflight.run_release_adapter_preflight(tmp_path, payload, run_command=refuse)

    assert payload["execution"] == {
        "status": "not_run",
        "reason": "focused preflight status is `not_required`; no commands were required",
        "executed_commands": [],
    }


def test_release_adapter_warns_when_non_gh_backend_lacks_commands(tmp_path: Path) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir()
    (adapter_dir / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "release_backend:",
                "  id: acme-github",
                "  binary: acme",
                "",
            ]
        ),
        encoding="utf-8",
    )
    resolve = _load_release_module("resolve_adapter")
    payload = resolve.load_adapter(tmp_path)

    assert payload["valid"] is True
    assert any("release_backend.id=acme-github" in warning for warning in payload["warnings"])


def test_backend_command_uses_template_when_provided() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {
        "id": "acme-github",
        "binary": "acme",
        "commands": {"release_view": ["acme", "github", "release", "view", "{tag}"]},
    }

    command = helpers.backend_command(
        backend, "release_view", ["gh", "release", "view", "{tag}"], tag="v1.2.3"
    )

    assert command == ["acme", "github", "release", "view", "v1.2.3"]


def test_backend_command_falls_back_to_default_for_gh() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {"id": "gh", "binary": "gh", "commands": None}

    command = helpers.backend_command(
        backend, "release_view", ["gh", "release", "view", "{tag}"], tag="v1.2.3"
    )

    assert command == ["gh", "release", "view", "v1.2.3"]


def test_backend_command_errors_on_non_gh_without_template() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {"id": "acme-github", "binary": "acme", "commands": None}

    with pytest.raises(SystemExit) as exc:
        helpers.backend_command(backend, "release_create", ["gh", "release", "create"])

    assert "acme-github" in str(exc.value)
    assert "release_create" in str(exc.value)


def test_backend_command_rejects_caller_sub_outside_op_allowlist() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {"id": "gh", "binary": "gh", "commands": None}

    with pytest.raises(SystemExit) as exc:
        helpers.backend_command(
            backend,
            "release_view",
            ["gh", "release", "view", "{tag}"],
            tag="v1.2.3",
            title="not allowed for view",
        )

    assert "title" in str(exc.value)
    assert "release_view" in str(exc.value)


def test_backend_command_rejects_adapter_template_with_unknown_placeholder() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {
        "id": "acme-github",
        "binary": "acme",
        "commands": {
            "release_view": ["acme", "release", "view", "{tag}", "--audit", "{audit_id}"],
        },
    }

    with pytest.raises(SystemExit) as exc:
        helpers.backend_command(
            backend, "release_view", ["gh", "release", "view", "{tag}"], tag="v1.2.3"
        )

    assert "audit_id" in str(exc.value)
    assert "unknown placeholders" in str(exc.value)


def test_backend_command_rejects_unknown_op() -> None:
    helpers = _load_release_module("publish_release_helpers")
    backend = {"id": "gh", "binary": "gh", "commands": None}

    with pytest.raises(SystemExit) as exc:
        helpers.backend_command(backend, "rogue_op", ["gh", "release", "list"])

    assert "rogue_op" in str(exc.value)
    assert "OP_PLACEHOLDERS" in str(exc.value)


def _arg_guards():
    return _load_release_module("publish_release_arg_guards")


@pytest.mark.parametrize(
    ("artifact", "expected"),
    [
        ("/abs/charness-artifacts/critique/x.md", "normalized repo-relative path"),
        ("charness-artifacts/critique/../x.md", "normalized repo-relative path"),
        ("docs/notes.md", "critique markdown artifact"),
        ("charness-artifacts/critique/x.txt", "critique markdown artifact"),
    ],
)
def test_critique_artifact_arg_refuses_shapes_that_never_reach_the_filesystem(
    artifact: str, expected: str, tmp_path: Path
) -> None:
    """These refusals moved file when `parse_args`' semantic half was split out, and the
    move took them out of in-process coverage: every remaining exercise ran the CLI as a
    subprocess, where nothing measures them. Called directly here."""
    with pytest.raises(SystemExit) as exc:
        _arg_guards().validate_critique_artifact_arg(
            tmp_path, artifact, run_command=lambda *_a, **_k: _FakeCompleted(returncode=0)
        )

    assert expected in str(exc.value)


def test_critique_artifact_arg_refuses_a_missing_then_an_untracked_artifact(tmp_path: Path) -> None:
    guards = _arg_guards()
    relpath = "charness-artifacts/critique/2026-08-17-demo.md"

    with pytest.raises(SystemExit) as missing:
        guards.validate_critique_artifact_arg(
            tmp_path, relpath, run_command=lambda *_a, **_k: _FakeCompleted(returncode=0)
        )
    assert "does not exist" in str(missing.value)

    (tmp_path / "charness-artifacts" / "critique").mkdir(parents=True)
    (tmp_path / relpath).write_text("# critique\n", encoding="utf-8")

    with pytest.raises(SystemExit) as untracked:
        guards.validate_critique_artifact_arg(
            tmp_path, relpath, run_command=lambda *_a, **_k: _FakeCompleted(returncode=1)
        )
    assert "must be tracked before release" in str(untracked.value)

    assert (
        guards.validate_critique_artifact_arg(
            tmp_path, relpath, run_command=lambda *_a, **_k: _FakeCompleted(returncode=0)
        )
        == relpath
    )


def test_critique_artifact_arg_refuses_a_symlink_that_escapes_the_repo(tmp_path: Path) -> None:
    """The normalization check cannot see this one: the path has no `..` and is not
    absolute, so only RESOLVING it shows that it leaves the repo. A critique artifact
    read from outside the tree is evidence nothing in the release can vouch for."""
    repo = tmp_path / "repo"
    outside = tmp_path / "outside"
    outside.mkdir(parents=True)
    (outside / "x.md").write_text("# elsewhere\n", encoding="utf-8")
    (repo / "charness-artifacts").mkdir(parents=True)
    (repo / "charness-artifacts" / "critique").symlink_to(outside, target_is_directory=True)

    with pytest.raises(SystemExit) as exc:
        _arg_guards().validate_critique_artifact_arg(
            repo,
            "charness-artifacts/critique/x.md",
            run_command=lambda *_a, **_k: _FakeCompleted(returncode=0),
        )

    assert "must stay inside the repo root" in str(exc.value)
