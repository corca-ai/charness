"""Which debug artifacts a run JUDGES, and under which ruleset.

Split from `test_debug_artifact.py` at its length cap, on a real seam rather than a
line count: that file owns what the schema RULES are, and this one owns scope and role
-- which artifacts a command reaches (`--paths` vs the corpus, the named-path refusal,
the adapter-declared owned prefix) and which of the two rulesets governs each one (the
current-pointer role, across the symlink and copy layouts).

Every test here exists because a real defect shipped in that seam. A planner emitted a
whole-corpus command for a single authored artifact; scoping that command then made a
named path that resolved to nothing exit 0 having validated nothing; and keying the
ruleset on the filename gave one file two verdicts depending on which name reached it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]


def _load_sibling():
    """The rule-suite module, loaded by PATH rather than imported by name.

    `tests/` is not a package, so a plain `from test_debug_artifact import ...` resolves
    only when pytest happens to have inserted this directory on `sys.path` first --
    which depends on rootdir and invocation, not on anything this file controls.
    Re-declaring the fixtures instead would fork the artifact bodies these two suites
    must agree on, which is the drift the split is supposed to avoid.
    """
    spec = importlib.util.spec_from_file_location(
        "debug_artifact_rule_suite", ROOT / "tests" / "test_debug_artifact.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_RULES = _load_sibling()
seed_repo = _RULES.seed_repo
valid_current_artifact = _RULES.valid_current_artifact


def _load_validator(name: str):
    """A FRESH module object per test, so a monkeypatched or probed helper cannot leak.

    Loaded by path rather than imported: these tests reach private resolvers
    (`_owned_prefix`, `_current_pointer`) that no public surface exposes, and a shared
    module object would let one test's probe change another's answer.
    """
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / "gates" / "validate_debug_artifact.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_validator(*args: str):
    return run_loaded_script_main(
        "validate_debug_artifact.py",
        _load_validator("validate_debug_artifact_cli_under_test"),
        *args,
    )


def test_a_scoped_run_isolates_a_fresh_artifact_from_legacy_corpus_debt(tmp_path: Path) -> None:
    """The reported defect, as the three-artifact case that distinguishes the two modes.

    A corpus validator run unscoped answers "is the whole history clean", and the debug
    planner emitted exactly that while calling it a current-artifact gate. A consumer
    wrote a VALID new record, saw it reported validated, and still got exit 1 -- because
    an unrelated older record carried legacy-schema debt. Nothing in the exit code said
    which artifact was at fault, and the repo's own changed-scope gate passed, so the two
    surfaces answered different questions with the same word.

    The fixture below is the minimum that can tell a real fix from a fake one: scoping to
    a clean corpus would pass for the wrong reason, so the corpus here is deliberately
    red.
    """
    repo = seed_repo(tmp_path, valid_current_artifact())
    debug_dir = repo / "charness-artifacts" / "debug"
    fresh = debug_dir / "2026-08-17-debug-review.md"
    fresh.write_text(valid_current_artifact(), encoding="utf-8")
    legacy = debug_dir / "2026-01-02-legacy-shape.md"
    legacy.write_text(
        "# Legacy\nDate: 2026-01-02\n\n## Problem\n\nno other sections\n", encoding="utf-8"
    )

    # Whole corpus: red, and correctly so -- the legacy record IS out of schema.
    corpus = _run_validator("--repo-root", str(repo), "--all")
    assert corpus.returncode == 1
    assert "2026-01-02-legacy-shape.md" in corpus.stdout + corpus.stderr

    # Scoped to the artifact just authored: green, and it does NOT reach the legacy record.
    scoped = _run_validator(
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/debug/2026-08-17-debug-review.md",
    )
    assert scoped.returncode == 0, scoped.stdout + scoped.stderr
    assert "2026-01-02-legacy-shape.md" not in scoped.stdout + scoped.stderr

    # And a scoped run still REFUSES a malformed artifact -- scoping narrows the
    # population, never the rules. Without this the fix could be "always pass".
    fresh.write_text(
        "# Broken\nDate: 2026-08-17\n\n## Problem\n\nmissing the rest\n", encoding="utf-8"
    )
    scoped_broken = _run_validator(
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/debug/2026-08-17-debug-review.md",
    )
    assert scoped_broken.returncode == 1
    assert "2026-08-17-debug-review.md" in scoped_broken.stdout + scoped_broken.stderr


def test_a_named_debug_path_that_resolves_to_nothing_refuses_instead_of_passing(
    tmp_path: Path,
) -> None:
    """Scoping without an owned prefix is a silent pass, which is worse than no scoping.

    `unresolvable_named_paths` owns nothing unless the validator declares a prefix, and
    debug declared none -- so `--paths <path that does not exist>` printed "No debug
    artifacts in scope." and exited 0 having validated nothing. Harmless while every
    emitted command was unscoped; a silent green the moment the planner and scaffold
    started NAMING the artifact being authored, because running the emitted gate before
    writing the file (or after writing it elsewhere) is the ordinary case, not an exotic
    one. `retro`, `ideation` and `critique` all declare theirs.
    """
    repo = seed_repo(tmp_path, valid_current_artifact())

    missing = _run_validator(
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/debug/2026-08-17-never-written.md",
    )
    assert missing.returncode == 1
    assert "resolve to nothing" in missing.stdout + missing.stderr

    # The two no-ops the refusal must NOT swallow, both load-bearing because `--paths` is
    # fed by tools passing a slice of the changed set.
    unowned = _run_validator("--repo-root", str(repo), "--paths", "docs/index.md")
    assert unowned.returncode == 0, unowned.stdout + unowned.stderr

    real = _run_validator(
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/debug/latest.md",
    )
    assert real.returncode == 0, real.stdout + real.stderr


def test_the_owned_prefix_comes_from_the_adapter_not_a_literal(tmp_path: Path) -> None:
    # Debug is the one family whose output directory is adapter-declared, so a constant
    # prefix would refuse correct paths in any repo that declares a different directory.
    # This repo declares one, and the refusal must key on THAT.
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "artifacts" / "debugs").mkdir(parents=True)
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "version: 1\nrepo: demo\nlanguage: en\noutput_dir: artifacts/debugs\n", encoding="utf-8"
    )
    (repo / "artifacts" / "debugs" / "latest.md").write_text(
        valid_current_artifact(), encoding="utf-8"
    )

    missing = _run_validator(
        "--repo-root",
        str(repo),
        "--paths",
        "artifacts/debugs/2026-08-17-never-written.md",
    )
    assert missing.returncode == 1, missing.stdout + missing.stderr
    assert "resolve to nothing" in missing.stdout + missing.stderr


def _strict_only_violation(body: str) -> str:
    """Remove the falsifiable-hypothesis marker: a CURRENT-schema rule with no legacy analogue."""
    return body.replace(
        " | disconfirmer: add `.runtime-cache` to a fixture and assert it is excluded", ""
    )


def test_the_same_bytes_get_the_same_verdict_under_either_name(tmp_path: Path) -> None:
    """Ruleset keyed on ROLE, not filename -- the defect scoping the emitted command exposed.

    `latest.md` is a symlink in real repos, so the artifact being authored is reached by
    two names. Keyed on filename, `--paths <pointer>` ran the strict current-schema checks
    and `--paths <its target>` ran only the legacy dated ones -- two verdicts for one file.
    Invisible while every emitted command was unscoped, because the corpus glob yields
    `latest.md` too and the strict checks always ran under SOME name. Scoping removed the
    other name, so a current-shaped artifact was judged by legacy rules and a missing
    `disconfirmer:` passed.

    The fixture violates a rule the CURRENT schema has and the legacy one does not, which
    is what makes the two rulesets distinguishable at all.
    """
    repo = seed_repo(tmp_path, valid_current_artifact())
    debug_dir = repo / "charness-artifacts" / "debug"
    record = debug_dir / "2026-08-17-debug-review.md"
    record.write_text(_strict_only_violation(valid_current_artifact()), encoding="utf-8")
    # The real layout: the pointer is a symlink onto the record being authored.
    (debug_dir / "latest.md").unlink()
    (debug_dir / "latest.md").symlink_to(record.name)

    by_pointer = _run_validator(
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/debug/latest.md",
    )
    by_target = _run_validator(
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/debug/2026-08-17-debug-review.md",
    )
    assert by_pointer.returncode == 1, by_pointer.stdout + by_pointer.stderr
    assert by_target.returncode == by_pointer.returncode, (
        "the same bytes were judged differently depending on which name reached them:\n"
        f"pointer rc={by_pointer.returncode} target rc={by_target.returncode}\n"
        f"target output: {by_target.stdout + by_target.stderr}"
    )

    # And a record the pointer does NOT reference stays on the legacy ruleset -- the fix
    # widens strictness to the current artifact's other name, not to the whole corpus.
    unreferenced = debug_dir / "2026-01-02-old-record.md"
    unreferenced.write_text(_strict_only_violation(valid_current_artifact()), encoding="utf-8")
    legacy = _run_validator(
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/debug/2026-01-02-old-record.md",
    )
    assert legacy.returncode == 0, legacy.stdout + legacy.stderr


def test_an_adapter_typo_does_not_silently_disarm_the_refusal(tmp_path: Path) -> None:
    """The regression the first repair shipped, pinned so it cannot come back.

    Keying the resolvers on the adapter's `valid` flag looked conservative and was not.
    Debug's `validate_adapter_data` still populates a perfectly good `output_dir` when
    the adapter is invalid for an UNRELATED reason, so both resolvers returned None --
    which turned the named-path refusal back off and left every artifact on the legacy
    ruleset, with nothing printed, because nothing on this path inspects `valid`. A
    refusal a one-line typo can disable is the class this slice exists to close. Both
    resolvers now read the same `output_dir` the batch resolver reads.

    The typo used to be `version: 9`, and that is no longer an UNRELATED one: a version
    this reader cannot speak now honors no declared field, so `output_dir` would be the
    shipped default rather than this repo's, and the run is refused before scoping
    (asserted in the sibling test below). A bad `repo` TYPE is the case this test was
    always about -- one field refused, `output_dir` untouched.
    """
    module = _load_validator("validate_debug_artifact_adapter_typo")

    repo = seed_repo(tmp_path, valid_current_artifact())
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "version: 1\nrepo: 3\nlanguage: en\noutput_dir: charness-artifacts/debug\n",
        encoding="utf-8",
    )
    assert module.load_adapter(repo)["valid"] is False, "premise: this adapter is invalid"
    assert module._owned_prefix(repo) == "charness-artifacts/debug/"
    assert module._current_pointer(repo) is not None

    # End to end, which is where the regression was invisible: the refusal still fires.
    missing = _run_validator(
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/debug/2026-08-17-never-written.md",
    )
    assert missing.returncode == 1, missing.stdout + missing.stderr
    assert "resolve to nothing" in missing.stdout + missing.stderr


def test_an_unspeakable_version_refuses_before_it_can_mis_scope(tmp_path: Path) -> None:
    """The other half, and the reason the test above changed its fixture.

    `version: 9` leaves NOTHING declared honored, so `_owned_prefix` would invent
    `charness-artifacts/debug/` for a repo that declared elsewhere and `_current_pointer`
    would name a `latest.md` that repo never writes -- silently dropping every artifact
    to the legacy ruleset. The preflight refuses first, so neither resolver runs.
    """
    module = _load_validator("validate_debug_artifact_unspeakable_version")

    repo = seed_repo(tmp_path, valid_current_artifact())
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "version: 9\nrepo: demo\nlanguage: en\noutput_dir: charness-artifacts/debug\n",
        encoding="utf-8",
    )
    assert module._unspeakable_adapter_version(repo) is not None

    refused = _run_validator(
        "--repo-root",
        str(repo),
        "--all",
    )
    combined = refused.stdout + refused.stderr
    assert refused.returncode == 1, combined
    assert "does not speak" in combined, combined
    # Not merely non-zero: it must not read as a validated run either.
    assert "Validated" not in combined, combined


def test_a_blank_declared_output_dir_owns_nothing(tmp_path: Path) -> None:
    # The guard that IS real. An adapter declaring `output_dir: ""` validates clean, and
    # an empty prefix would make EVERY named path look owned -- the refusal would fire on
    # paths belonging to no debug family at all and break ordinary commits, which is the
    # opposite failure from the one the prefix exists to prevent.
    module = _load_validator("validate_debug_artifact_blank_dir")

    for index, declared in enumerate(('""', '"   "')):
        repo = tmp_path / f"repo{index}"
        (repo / ".agents").mkdir(parents=True)
        (repo / ".agents" / "debug-adapter.yaml").write_text(
            f"version: 1\nrepo: demo\nlanguage: en\noutput_dir: {declared}\n", encoding="utf-8"
        )
        assert module.load_adapter(repo)["valid"] is True, "premise: the adapter accepts this"
        assert module._owned_prefix(repo) is None, f"{declared} must own nothing"
        assert module._current_pointer(repo) is None


def test_a_copy_layout_pointer_gets_the_same_verdict_as_its_record(tmp_path: Path) -> None:
    """The layout the first role-keyed repair still left broken.

    `refresh_current_pointer` resolves `auto` to a symlink where the filesystem allows it
    and to a byte COPY otherwise, so a regular-file pointer is a first-class layout. A
    role test that bailed on `not is_symlink()` left the original two-verdicts-for-one-
    file defect verbatim for every repo on the copy path -- and for a hard link, which is
    the same shape. Bytes are the only identity a copy has.
    """
    repo = seed_repo(tmp_path, valid_current_artifact())
    debug_dir = repo / "charness-artifacts" / "debug"
    body = _strict_only_violation(valid_current_artifact())
    record = debug_dir / "2026-08-17-debug-review.md"
    record.write_text(body, encoding="utf-8")
    # A COPY, not a symlink -- the pointer is a regular file with identical bytes.
    (debug_dir / "latest.md").write_text(body, encoding="utf-8")
    assert not (debug_dir / "latest.md").is_symlink(), "premise: the copy layout"

    by_pointer = _run_validator(
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/debug/latest.md",
    )
    by_record = _run_validator(
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/debug/2026-08-17-debug-review.md",
    )
    assert by_pointer.returncode == 1, by_pointer.stdout + by_pointer.stderr
    assert by_record.returncode == by_pointer.returncode, (
        "copy-layout pointer and its record were judged differently:\n"
        f"pointer rc={by_pointer.returncode} record rc={by_record.returncode}\n"
        f"record output: {by_record.stdout + by_record.stderr}"
    )

    # A record whose bytes DIFFER from the pointer stays legacy: the copy arm keys on
    # identity, not on living in the same directory.
    other = debug_dir / "2026-01-02-unrelated.md"
    other.write_text(
        _strict_only_violation(valid_current_artifact()) + "\nextra\n", encoding="utf-8"
    )
    unrelated = _run_validator(
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/debug/2026-01-02-unrelated.md",
    )
    assert unrelated.returncode == 0, unrelated.stdout + unrelated.stderr


def test_a_looping_current_pointer_renders_a_verdict_instead_of_crashing(tmp_path: Path) -> None:
    """`Path.resolve()` raises RuntimeError on a symlink loop, not OSError.

    CPython catches the ELOOP `OSError` and re-raises `RuntimeError("Symlink loop from
    ...")`, so the obvious `except OSError` lets a looping `latest.md` crash the
    validator with a traceback instead of rendering a verdict -- on a surface whose whole
    job is to render one. Found by probing the repair rather than by reading it.
    """
    repo = seed_repo(tmp_path, valid_current_artifact())
    debug_dir = repo / "charness-artifacts" / "debug"
    record = debug_dir / "2026-08-17-debug-review.md"
    record.write_text(valid_current_artifact(), encoding="utf-8")
    (debug_dir / "latest.md").unlink()
    (debug_dir / "latest.md").symlink_to("loop-b.md")
    (debug_dir / "loop-b.md").symlink_to("latest.md")

    result = _run_validator(
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/debug/2026-08-17-debug-review.md",
    )
    assert "Traceback" not in result.stderr, result.stderr
    assert "RuntimeError" not in result.stderr, result.stderr
    # The loop makes the role unprovable, so the record is judged as what it looks like:
    # a dated record. Unprovable-therefore-legacy is the honest arm here -- the strict
    # schema is claimed by the pointer, and the pointer is unreadable.
    assert result.returncode == 0, result.stdout + result.stderr


def test_role_falls_back_to_the_filename_when_no_pointer_is_known(tmp_path: Path) -> None:
    # `current_pointer` is None whenever the adapter declares no usable output directory,
    # and the role test still has to answer. The filename is the only signal left, and it
    # is the pre-existing behavior -- degrading to "no role information" would put the
    # CURRENT artifact on the legacy ruleset, which is the failure this whole surface is
    # about. Asserted directly because no repo state reaches it through the CLI: the
    # batch resolver refuses first.
    module = _load_validator("validate_debug_artifact_no_pointer")

    assert module.is_current_artifact(tmp_path / "latest.md") is True
    assert module.is_current_artifact(tmp_path / "2026-08-17-record.md") is False


def test_an_unreadable_candidate_is_not_current_rather_than_a_crash(tmp_path: Path) -> None:
    # The copy arm compares bytes, so it can meet a path it cannot read. A directory
    # named `*.md` is the deterministic case (the corpus glob yields one), and it raises
    # IsADirectoryError out of `read_bytes`. Unprovable-therefore-not-current is the safe
    # direction: it cannot silently promote an unreadable file to the strict schema, and
    # the artifact's own read fails with a real message immediately after.
    module = _load_validator("validate_debug_artifact_unreadable")

    pointer = tmp_path / "latest.md"
    pointer.write_text("body\n", encoding="utf-8")
    unreadable = tmp_path / "2026-08-17-record.md"
    unreadable.mkdir()

    assert module.is_current_artifact(unreadable, pointer) is False


def test_a_missing_git_binary_refuses_rather_than_crashing(tmp_path: Path) -> None:
    """`check=False` suppresses a failing git, not an ABSENT one.

    `unresolvable_named_paths` shells out to git to learn which named paths are gone
    because this change deleted them. A missing binary raises `FileNotFoundError`
    straight out of `subprocess.run`, and the surrounding docstring's "a git failure
    yields no known deletions" promise did not cover it. The path was dead code until a
    validator declared an `owned_prefix` -- the first one that did made an uncaught
    traceback reachable from a validator, on any image that ships a lint stage without
    git. Refusing is the safe direction; the alternative is passing a run that validated
    nothing.
    """
    # Imported through the repo's own module path, not by file location: this module
    # carries `from __future__ import annotations` dataclasses whose resolution needs
    # the real package context, and a file-location load fails on them.
    sys.path.insert(0, str(ROOT))
    try:
        from scripts.artifacts import artifact_run_scope as module
    finally:
        sys.path.pop(0)

    real_run = module.run_process

    def no_git(cmd, *args, **kwargs):
        if cmd and cmd[0] == "git":
            raise FileNotFoundError(2, "No such file or directory", "git")
        return real_run(cmd, *args, **kwargs)

    module.run_process = no_git
    try:
        refused = module.unresolvable_named_paths(
            tmp_path,
            ["charness-artifacts/debug/never-written.md"],
            owned_prefix="charness-artifacts/debug/",
        )
    finally:
        module.run_process = real_run

    assert refused == ["charness-artifacts/debug/never-written.md"]
