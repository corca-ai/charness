from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts import probe_record_lib

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "check_probe_record.py"

# The source every record in this module quotes from, so `verify_source_quote` has
# something real to read. Written into `tmp_path`, never into the repo.
SOURCE_BODY = """\
def resolve(payload):
    # A refused version means nothing the repo declared was honored.
    if payload["errors"]:
        raise SystemExit("refusing: the adapter version was not reconciled")
    return payload["value"]
"""
QUOTED = '        raise SystemExit("refusing: the adapter version was not reconciled")'


SECTION_KEYS = ("source_text", "stimulus", "base_observable", "head_observable")


def _record(**overrides: str) -> str:
    """A complete, measured record. Each test names ONLY the field it is about, so a
    later required-field addition fails every test loudly instead of silently changing
    what any one of them proves."""
    fields = {
        "claim": "the loader refuses instead of returning a charness default",
        "claim_kind": "change",
        "observable": "the process exit status of the resolve call",
        "source_ref": "adapter.py",
        "source_conditions": "the adapter declares a version the reader cannot speak",
        "base_ref": "aaaaaaa",
        "head_ref": "bbbbbbb",
        "base_arm": "base-observed",
        "call_sites_unproven": "none",
    }
    sections = {
        "source_text": QUOTED,
        "stimulus": "python3 -c 'resolve({\"errors\": [\"unknown version\"]})'",
        "base_observable": "exit 0 (returned the charness default)",
        "head_observable": "exit 1 (SystemExit: refusing)",
    }
    for key, value in overrides.items():
        target = sections if key in SECTION_KEYS else fields
        target[key] = value
    body = "# Probe Record: test\n\n"
    body += "".join(f"{name.replace('_', ' ').capitalize()}: {value}\n" for name, value in fields.items())
    for key, content in sections.items():
        body += f"\n## {key.replace('_', ' ').capitalize()}\n\n```\n{content}\n```\n"
    return body


def _resolve(text: str, tmp_path: Path) -> dict:
    (tmp_path / "adapter.py").write_text(SOURCE_BODY, encoding="utf-8")
    return probe_record_lib.resolve_probe_record_text(text, repo_root=tmp_path)


def _reasons(result: dict) -> str:
    return " | ".join(result["undetermined_reasons"])


# --- the measured case ------------------------------------------------------


def test_a_measured_record_is_evaluated(tmp_path: Path) -> None:
    result = _resolve(_record(), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_EVALUATED, _reasons(result)
    assert result["supports_claim"] is True
    assert result["undetermined_reasons"] == []
    assert result["source_quote"]["status"] == "verified"
    assert result["covers_all_call_sites"] is True


# --- the whole point: a probe that measured nothing says so -----------------


def test_base_equals_head_measured_nothing(tmp_path: Path) -> None:
    same = "exit 1 (SystemExit: refusing)"
    result = _resolve(_record(base_observable=same, head_observable=same), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert result["supports_claim"] is False
    assert "measured nothing" in _reasons(result)


def test_base_equals_head_ignores_indentation_only_differences(tmp_path: Path) -> None:
    # Formatting is not a behavior change. A record that reflowed one capture and not the
    # other must not read as a disagreement.
    result = _resolve(
        _record(base_observable="  exit 1 (refusing)", head_observable="exit 1 (refusing)  "),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "measured nothing" in _reasons(result)


def test_a_base_that_could_not_run_is_not_a_base_that_disagreed(tmp_path: Path) -> None:
    # The sharpest rule in the module, and the `#528` shape: base and head DO differ
    # here -- base "differs" only because it crashed for an unrelated reason.
    result = _resolve(
        _record(base_arm="base-unrunnable", base_observable="ImportError: no module named x"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "not a base that disagreed" in _reasons(result)


# --- the arms Open Question 1 asked about -----------------------------------


def test_absent_base_establishes_an_existence_claim(tmp_path: Path) -> None:
    result = _resolve(
        _record(claim_kind="existence", base_arm="base-absent", base_observable="the surface does not exist at base"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_EVALUATED, _reasons(result)


def test_absent_base_does_not_establish_a_change_claim(tmp_path: Path) -> None:
    result = _resolve(_record(base_arm="base-absent", base_observable="n/a"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "no prior behavior" in _reasons(result)


def test_not_applicable_base_is_refused_for_a_behavioral_claim(tmp_path: Path) -> None:
    # The escape hatch: declare no base applies while still claiming a flip.
    result = _resolve(_record(base_arm="base-not-applicable"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "reserved for a `refusal` claim" in _reasons(result)


def test_unknown_base_arm_is_refused(tmp_path: Path) -> None:
    result = _resolve(_record(base_arm="base-obviously-fine"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "unknown base arm" in _reasons(result)


# --- a recorded refusal is not evidence of a repair -------------------------


def test_a_recorded_refusal_is_not_configured_not_evaluated(tmp_path: Path) -> None:
    result = _resolve(
        _record(claim_kind="refusal", base_arm="base-not-applicable", refusal_reason="no resolver contract exists for this adapter"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_NOT_CONFIGURED
    assert result["supports_claim"] is False
    assert "NOT evidence of a repair" in _reasons(result)


def test_a_refusal_without_a_reason_is_not_established(tmp_path: Path) -> None:
    result = _resolve(_record(claim_kind="refusal", base_arm="base-not-applicable"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "`Refusal reason:`" in _reasons(result)


# --- stimulus provenance ----------------------------------------------------


def test_a_quote_absent_from_the_cited_source_is_refused(tmp_path: Path) -> None:
    # The `#528` countermeasure at its own level: a stimulus invented from a model of the
    # mechanism cannot be quoted from the source that defines it.
    result = _resolve(_record(source_text="deliberately_absent:\n  - some-key"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert result["source_quote"]["status"] == "absent"
    assert "provenance is unverified" in _reasons(result)


def test_a_nonlocal_source_needs_a_degraded_reason(tmp_path: Path) -> None:
    result = _resolve(_record(source_ref="#628"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert result["source_quote"]["status"] == "unresolvable"
    assert "Source degraded reason" in _reasons(result)


def test_a_nonlocal_source_with_a_degraded_reason_still_evaluates(tmp_path: Path) -> None:
    # An issue body is allowed provenance and cannot be read from here. Demoting every
    # issue-sourced probe would make the mechanism unusable at the boundary it is for.
    result = _resolve(
        _record(source_ref="#628", source_degraded_reason="the issue body is not readable from this repo; quoted from the GitHub UI on 2026-08-18"),
        tmp_path,
    )
    assert result["state"] == probe_record_lib.PROBE_EVALUATED, _reasons(result)
    assert result["source_quote"]["status"] == "unresolvable"


def test_base_observed_with_no_captured_reading_is_refused(tmp_path: Path) -> None:
    # "I measured both sides" with an empty capture is this goal's class in miniature:
    # the arm ASSERTS a measurement the record does not contain.
    result = _resolve(_record(base_observable=""), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "section is empty" in _reasons(result)


def test_a_source_ref_that_names_no_path_is_unresolvable(tmp_path: Path) -> None:
    result = probe_record_lib.verify_source_quote(tmp_path, "the loader docstring", QUOTED)
    assert result["status"] == "unresolvable"
    assert "does not name a readable path" in result["reason"]


def test_an_empty_quote_is_unresolvable_never_verified(tmp_path: Path) -> None:
    result = probe_record_lib.verify_source_quote(tmp_path, "adapter.py", "   ")
    assert result["status"] == "unresolvable"


def _git_repo_with_source(tmp_path: Path) -> str:
    """A repo whose committed `adapter.py` carries `QUOTED` and whose WORKTREE no longer
    does -- the living-document rot the pin exists for."""
    def run(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=tmp_path, capture_output=True, text=True, check=True)

    run("init", "-q")
    run("config", "user.email", "probe@example.invalid")
    run("config", "user.name", "probe")
    (tmp_path / "adapter.py").write_text(SOURCE_BODY, encoding="utf-8")
    run("add", "adapter.py")
    run("commit", "-q", "-m", "seed")
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, capture_output=True, text=True, check=True)
    (tmp_path / "adapter.py").write_text("def resolve(payload):\n    return payload\n", encoding="utf-8")
    return sha.stdout.strip()


def test_an_unpinned_quote_rots_when_the_source_is_edited(tmp_path: Path) -> None:
    _git_repo_with_source(tmp_path)
    assert probe_record_lib.verify_source_quote(tmp_path, "adapter.py", QUOTED)["status"] == "absent"


def test_a_pinned_quote_survives_the_edit(tmp_path: Path) -> None:
    sha = _git_repo_with_source(tmp_path)
    result = probe_record_lib.verify_source_quote(tmp_path, "adapter.py", QUOTED, revision=sha)
    assert result["status"] == "verified", result["reason"]


def test_a_record_may_pin_its_source_revision(tmp_path: Path) -> None:
    sha = _git_repo_with_source(tmp_path)
    text = _record(source_revision=sha)
    result = probe_record_lib.resolve_probe_record_text(text, repo_root=tmp_path)
    assert result["state"] == probe_record_lib.PROBE_EVALUATED, _reasons(result)


def test_an_unresolvable_pin_is_unresolvable_not_verified(tmp_path: Path) -> None:
    _git_repo_with_source(tmp_path)
    result = probe_record_lib.verify_source_quote(tmp_path, "adapter.py", QUOTED, revision="deadbee")
    assert result["status"] == "unresolvable"
    assert "revision" in result["reason"]


def test_an_empty_needle_never_reports_containment() -> None:
    # Without this guard an empty quote matches every source by the empty-slice identity,
    # so "verified" would be the verdict for having quoted nothing.
    assert probe_record_lib._contains_block(["a", "b"], []) is False


def test_a_missing_source_file_is_unresolvable_not_a_crash(tmp_path: Path) -> None:
    result = _resolve(_record(source_ref="no_such_file.py"), tmp_path)
    assert result["source_quote"]["status"] == "unresolvable"
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED


# --- completeness -----------------------------------------------------------


def test_a_missing_required_field_is_refused_before_the_arm_is_read(tmp_path: Path) -> None:
    text = _record().replace("Observable: the process exit status of the resolve call\n", "")
    result = _resolve(text, tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "`observable`" in _reasons(result)


def test_call_sites_unproven_may_not_be_silent(tmp_path: Path) -> None:
    # The census's own blind class replicated per row: a file flipped on one guarded call
    # site while a second still substitutes a default.
    text = _record().replace("Call sites unproven: none\n", "")
    result = _resolve(text, tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "`call_sites_unproven`" in _reasons(result)


def test_named_unproven_call_sites_are_reported_not_hidden(tmp_path: Path) -> None:
    result = _resolve(_record(call_sites_unproven="adapter.py:41 reads the payload through a helper"), tmp_path)
    assert result["covers_all_call_sites"] is False
    assert result["call_sites_unproven"].startswith("adapter.py:41")


def test_none_with_a_reason_still_means_full_coverage(tmp_path: Path) -> None:
    # The markdown gate wraps long lines and a bare `none` loses the reason, so an author
    # writing the better answer must not be told they covered less.
    result = _resolve(_record(call_sites_unproven="none — the wait loop has exactly one call site"), tmp_path)
    assert result["covers_all_call_sites"] is True


def test_none_as_a_negation_is_not_full_coverage(tmp_path: Path) -> None:
    # The trap the anchored grammar exists for: `none of the call sites were checked`
    # says the OPPOSITE and shares its leading word.
    result = _resolve(_record(call_sites_unproven="none of the call sites were checked"), tmp_path)
    assert result["covers_all_call_sites"] is False


def test_a_wrapped_field_value_keeps_its_continuation(tmp_path: Path) -> None:
    # `line-anchored-ledger-fields`: a parser anchored on line starts drops the tail of a
    # value the markdown gate forced to wrap, and reports the truncation as a pass.
    parsed = probe_record_lib.parse_probe_record(
        "Claim: the loader refuses instead of returning a\n  charness default\n"
    )
    assert parsed["fields"]["claim"] == "the loader refuses instead of returning a charness default"


def test_an_unindented_following_line_is_not_a_continuation() -> None:
    parsed = probe_record_lib.parse_probe_record("Claim: the real claim\nsome other prose\n")
    assert parsed["fields"]["claim"] == "the real claim"


def test_a_blank_line_ends_a_wrapped_value() -> None:
    parsed = probe_record_lib.parse_probe_record("Claim: the real claim\n\n  indented prose\n")
    assert parsed["fields"]["claim"] == "the real claim"


def test_a_placeholder_value_is_silence(tmp_path: Path) -> None:
    result = _resolve(_record(observable="TBD"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "`observable`" in _reasons(result)


def test_an_unknown_claim_kind_is_refused(tmp_path: Path) -> None:
    result = _resolve(_record(claim_kind="probably-fine"), tmp_path)
    assert result["state"] == probe_record_lib.PROBE_NOT_ESTABLISHED
    assert "unknown claim kind" in _reasons(result)


# --- parsing ----------------------------------------------------------------


def test_a_field_line_inside_a_fence_is_content_not_a_field(tmp_path: Path) -> None:
    # A stimulus that itself contains `Claim:` must not overwrite the record's claim.
    parsed = probe_record_lib.parse_probe_record(
        "Claim: the real claim\n\n## Stimulus\n\n```\nClaim: not a field\n```\n"
    )
    assert parsed["fields"]["claim"] == "the real claim"
    assert parsed["sections"]["stimulus"] == "Claim: not a field"


def test_a_heading_with_no_fence_is_an_empty_section_not_a_missing_one(tmp_path: Path) -> None:
    parsed = probe_record_lib.parse_probe_record("## Source text\n\n## Stimulus\n\n```\nrun it\n```\n")
    assert parsed["sections"]["source_text"] == ""
    assert parsed["sections"]["stimulus"] == "run it"


# --- the command surface ----------------------------------------------------


def _cli(tmp_path: Path, text: str, *args: str) -> subprocess.CompletedProcess:
    (tmp_path / "adapter.py").write_text(SOURCE_BODY, encoding="utf-8")
    record = tmp_path / "record.md"
    record.write_text(text, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(CLI), "--repo-root", str(tmp_path), "--record", str(record), *args],
        capture_output=True,
        text=True,
    )


def test_cli_reports_without_gating_by_default(tmp_path: Path) -> None:
    same = "exit 1"
    result = _cli(tmp_path, _record(base_observable=same, head_observable=same))
    assert result.returncode == 0, result.stderr
    assert "not-established" in result.stdout


def test_cli_require_evaluated_refuses_an_unmeasured_claim(tmp_path: Path) -> None:
    same = "exit 1"
    result = _cli(tmp_path, _record(base_observable=same, head_observable=same), "--require-evaluated")
    assert result.returncode == 1
    assert "does not establish the claim" in result.stderr


def test_cli_require_evaluated_accepts_a_measured_claim(tmp_path: Path) -> None:
    result = _cli(tmp_path, _record(), "--require-evaluated")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "state: evaluated" in result.stdout


def test_cli_require_evaluated_refuses_a_recorded_refusal(tmp_path: Path) -> None:
    # `not-configured` is an honest state and still not support for a close.
    result = _cli(
        tmp_path,
        _record(claim_kind="refusal", base_arm="base-not-applicable", refusal_reason="cannot be wired: no resolver contract"),
        "--require-evaluated",
    )
    assert result.returncode == 1
    assert "not-configured" in result.stdout


def test_cli_reports_an_unreadable_record_rather_than_crashing(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(CLI), "--repo-root", str(tmp_path), "--record", str(tmp_path / "absent.md")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "not-established" in result.stdout
    assert "could not read the probe record" in result.stdout
    assert "Traceback" not in result.stderr
