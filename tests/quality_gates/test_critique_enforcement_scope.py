from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

from scripts import critique_enforcement_scope as _scope
from scripts import critique_reviewer_evidence as _evidence

from .support import ROOT, run_script

# Regression floor for the five ways this surface reported a verdict over a scope
# it had not established (bug-hunt rows C1-C4/C6). Each test pairs the defect with
# the control that isolates it, because "the fix works" and "the harness is broken"
# produce the same green otherwise.
#
# The shared shape: every floor here is CONDITIONAL — on a date, a selection mode,
# a probe config, or a trigger line the artifact itself supplies — and each of
# those conditions was silently satisfiable. A floor that is off emits nothing by
# construction, so the surface every other closeout leans on could report clean
# having evaluated almost nothing.

VALIDATOR = "scripts/validate_critique_artifacts.py"

_TIER_BLOCK = """## Reviewer Tier Evidence

- Requested tier: bounded-reviewer
- Requested spawn fields: model, reasoning effort
- Host exposure state: {host}
- Application state: n/a
- Delivery state: {delivery}
"""


def _artifact(repo: Path, name: str, body: str) -> str:
    path = repo / "charness-artifacts" / "critique" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return f"charness-artifacts/critique/{name}"


def _body(*, date: str = "2026-07-28", fresh: str = "parent-delegated", tier: str = "", tail: str = "") -> str:
    return (
        f"# Demo Critique\nDate: {date}\n\n"
        f"## Fresh-Eye Satisfaction\n\n{fresh}\n\n"
        f"{tier}\n"
        "## Boundary Ownership\n\n- Verdict: single-surface\n"
        f"{tail}"
    )


def _packet_binding(repo: Path, *, identity: str = "c" * 64) -> str:
    packet = repo / "charness-artifacts" / "critique" / "reports" / "packet.json"
    packet.parent.mkdir(parents=True, exist_ok=True)
    packet.write_text(
        json.dumps(
            {
                "kind": "charness.critique_prepare_packet",
                # `reviewed_paths` is present because a binding that declares NO
                # paths is refused in integrity-only mode too, not just under the
                # currency check. These tests exercise worker-report and tier
                # axes; the stub has to clear the vacuous-binding floor to reach
                # them, the same way a real packet does.
                "reviewed_input_identity": {
                    "identity_sha256": identity,
                    "reviewed_paths": ["charness-artifacts/critique/reports/packet.json"],
                },
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    packet_sha = hashlib.sha256(packet.read_bytes()).hexdigest()
    return (
        "\n## Reviewed Input Identity\n\n"
        "- Packet path: charness-artifacts/critique/reports/packet.json\n"
        f"- Packet SHA256: {packet_sha}\n"
        f"- Identity SHA256: {identity}\n"
    )


def _validate(repo: Path, relpath: str, *extra: str):
    return run_script(VALIDATOR, "--repo-root", str(repo), "--paths", relpath, *extra)


# --- C1: the record that contradicts its own claim -------------------------


def test_unedited_scaffold_tier_placeholders_do_not_satisfy_the_tier_floor(tmp_path: Path) -> None:
    """Presence was bare truthiness, so `Requested tier: TODO ...` — the scaffold's
    OWN default — satisfied the floor permanently. The block validated itself."""
    repo = tmp_path / "repo"
    tier = (
        "## Reviewer Tier Evidence\n\n"
        "- Requested tier: TODO the fresh-eye reviewer tier requested.\n"
        "- Requested spawn fields: TODO the fields sent to the host spawn surface.\n"
        "- Host exposure state: requested_fields_sent\n"
        "- Application state: n/a\n"
        "- Delivery state: findings-received\n"
    )
    relpath = _artifact(repo, "2026-07-28-stub.md", _body(tier=tier))

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "unedited scaffold `TODO`/`TBD` placeholder" in result.stderr


def test_honest_n_a_tier_value_is_not_treated_as_a_placeholder(tmp_path: Path) -> None:
    """The control that bounds the rule above. `n/a` appears 72 times in the
    checked-in corpus as a real answer — this host exposes no tier to request —
    and refusing it would demand a fabricated value for a thing that does not
    exist. Only unedited `TODO`/`TBD` stubs are refused."""
    repo = tmp_path / "repo"
    tier = (
        "## Reviewer Tier Evidence\n\n"
        "- Requested tier: n/a\n"
        "- Requested spawn fields: n/a\n"
        "- Host exposure state: host-defaulted\n"
        "- Application state: n/a\n"
        "- Delivery state: findings-received\n"
    )
    relpath = _artifact(repo, "2026-07-28-na.md", _body(tier=tier))

    assert _validate(repo, relpath).returncode == 0


def test_parent_delegated_claim_over_a_pending_spawn_record_is_refused(tmp_path: Path) -> None:
    """`parent-delegated` asserts a COMPLETED delegation; `pending-parent-spawn`
    states no reviewer was spawned and no findings arrived. Both floors already
    required and typed these fields — nothing consumed them together, so the
    disproof sat six lines below the claim and validated green."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="pending-parent-spawn", delivery="pending-parent-spawn")
    relpath = _artifact(repo, "2026-07-28-contradiction.md", _body(tier=tier))

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "claims a completed delegation" in result.stderr


def test_consistent_spawn_record_under_the_same_claim_passes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    relpath = _artifact(repo, "2026-07-28-consistent.md", _body(tier=tier))

    assert _validate(repo, relpath).returncode == 0


def test_worker_delivered_requires_the_combined_report_carrier(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="host-defaulted", delivery="findings-received")
    relpath = _artifact(repo, "2026-07-28-worker-missing-report.md", _body(fresh="worker-delivered", tier=tier))

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "durable worker report carrier fields" in result.stderr


def test_worker_delivered_requires_report_approval_and_result_identities(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    packet_tail = _packet_binding(repo)
    packet = repo / "charness-artifacts" / "critique" / "reports" / "packet.json"
    packet_identity = hashlib.sha256(packet.read_bytes()).hexdigest()
    report = repo / "charness-artifacts" / "critique" / "reports" / "attempt.yaml"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        yaml.safe_dump(
            {
                "schema_version": "charness.reviewer_worker_report.v1",
                "execution_mode": "file-backed-worker",
                "approval_eligible": True,
                "delivery_state": "findings-received",
                "receipt_ok": True,
                "ledger_ok": True,
                "provenance_ok": True,
                "packet_identity": packet_identity,
                "reviewed_input_identity": "c" * 64,
                "parent_receipt_identity": "parent-receipt-1",
                "findings_identity": "b" * 64,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    report_identity = hashlib.sha256(report.read_bytes()).hexdigest()
    tier = (
        _TIER_BLOCK.format(host="host-defaulted", delivery="findings-received")
        + "- Worker report: charness-artifacts/critique/reports/attempt.yaml\n"
        + f"- Worker report identity: {report_identity}\n"
        + "- Worker report approval: approval_eligible: true\n"
        + "- Worker report delivery: findings-received\n"
        + f"- Worker report packet identity: {packet_identity}\n"
        + f"- Worker report input identity: {'c' * 64}\n"
        + "- Worker report parent receipt identity: parent-receipt-1\n"
        + f"- Worker report findings identity: {'b' * 64}\n"
    )
    relpath = _artifact(
        repo,
        "2026-07-28-worker-report.md",
        _body(fresh="worker-delivered", tier=tier, tail=packet_tail),
    )

    assert _validate(repo, relpath, "--all").returncode == 0


def test_worker_delivered_requires_artifact_reviewed_input_binding(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    report = _write_report(repo, _approval_report(), "charness-artifacts/critique/reports/report.yaml")
    report_identity = hashlib.sha256(report.read_bytes()).hexdigest()
    tier = (
        _TIER_BLOCK.format(host="host-defaulted", delivery="findings-received")
        + "- Worker report: charness-artifacts/critique/reports/report.yaml\n"
        + f"- Worker report identity: {report_identity}\n"
        + "- Worker report approval: approval_eligible: true\n"
        + "- Worker report delivery: findings-received\n"
        + f"- Worker report packet identity: {'a' * 64}\n"
        + f"- Worker report input identity: {'c' * 64}\n"
        + "- Worker report parent receipt identity: parent-receipt-1\n"
        + f"- Worker report findings identity: {'b' * 64}\n"
    )
    relpath = _artifact(repo, "2026-07-28-worker-no-input-binding.md", _body(fresh="worker-delivered", tier=tier))

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "Reviewed Input Identity binding" in result.stderr


def _valid_worker_report_tier(*, approval: str = "approval_eligible: true", delivery: str = "findings-received", packet: str = "a" * 64) -> str:
    return (
        _TIER_BLOCK.format(host="host-defaulted", delivery="findings-received")
        + "- Worker report: charness-artifacts/critique/reports/attempt.yaml\n"
        + f"- Worker report identity: {'e' * 64}\n"
        + f"- Worker report approval: {approval}\n"
        + f"- Worker report delivery: {delivery}\n"
        + f"- Worker report packet identity: {packet}\n"
        + f"- Worker report input identity: {'c' * 64}\n"
        + "- Worker report parent receipt identity: parent-receipt-1\n"
        + f"- Worker report findings identity: {'b' * 64}\n"
    )


def test_worker_delivered_rejects_report_that_is_not_approval(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    relpath = _artifact(
        repo,
        "2026-07-28-worker-report-not-approved.md",
        _body(fresh="worker-delivered", tier=_valid_worker_report_tier(approval="approval_eligible: false")),
    )

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "approval_eligible: true" in result.stderr


def test_worker_delivered_rejects_report_without_findings_delivery(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    relpath = _artifact(
        repo,
        "2026-07-28-worker-report-not-delivered.md",
        _body(fresh="worker-delivered", tier=_valid_worker_report_tier(delivery="running")),
    )

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "findings-received" in result.stderr


def test_worker_delivered_rejects_non_sha256_report_identity(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    relpath = _artifact(
        repo,
        "2026-07-28-worker-report-bad-identity.md",
        _body(fresh="worker-delivered", tier=_valid_worker_report_tier(packet="not-a-sha")),
    )

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "lowercase SHA-256 identity" in result.stderr


def _carrier_fields(report_path: str, report_identity: str = "e" * 64) -> dict[str, str]:
    return {
        "worker report": report_path,
        "worker report identity": report_identity,
        "worker report approval": "approval_eligible: true",
        "worker report delivery": "findings-received",
        "worker report packet identity": "a" * 64,
        "worker report input identity": "c" * 64,
        "worker report parent receipt identity": "parent-receipt-1",
        "worker report findings identity": "b" * 64,
    }


_DEFAULT_REPO_ROOT = object()


def _validate_carrier(
    repo: Path,
    fields: dict[str, str],
    *,
    repo_root: Path | None | object = _DEFAULT_REPO_ROOT,
    artifact_binding_fields: dict[str, str] | None = None,
) -> None:
    _evidence.validate_worker_delivery_evidence(
        Path("artifact.md"),
        "",
        "worker-delivered",
        section_field_map=lambda *_args: fields,
        repo_root=repo if repo_root is _DEFAULT_REPO_ROOT else repo_root,
        artifact_binding_fields=artifact_binding_fields
        if artifact_binding_fields is not None
        else {
            "packet sha256": fields["worker report packet identity"],
            "identity sha256": fields["worker report input identity"],
        },
    )


def _write_report(repo: Path, content: bytes, relative: str = "report.yaml") -> Path:
    report = repo / relative
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_bytes(content)
    return report


def _approval_report(**overrides: object) -> bytes:
    payload = {
        "schema_version": "charness.reviewer_worker_report.v1",
        "execution_mode": "file-backed-worker",
        "approval_eligible": True,
        "delivery_state": "findings-received",
        "receipt_ok": True,
        "ledger_ok": True,
        "provenance_ok": True,
        "packet_identity": "a" * 64,
        "reviewed_input_identity": "c" * 64,
        "parent_receipt_identity": "parent-receipt-1",
        "findings_identity": "b" * 64,
    }
    payload.update(overrides)
    return yaml.safe_dump(payload, sort_keys=False).encode("utf-8")


def test_worker_delivered_requires_repo_root_for_report_carrier(tmp_path: Path) -> None:
    fields = _carrier_fields("report.yaml")
    with pytest.raises(_evidence.ValidationError, match="without the repository root"):
        _validate_carrier(tmp_path, fields, repo_root=None)


def test_worker_delivered_rejects_unsafe_report_path(tmp_path: Path) -> None:
    fields = _carrier_fields("../report.yaml")
    with pytest.raises(_evidence.ValidationError, match="repo-relative path"):
        _validate_carrier(tmp_path, fields)


def test_worker_delivered_rejects_missing_report_carrier(tmp_path: Path) -> None:
    fields = _carrier_fields("missing/report.yaml")
    with pytest.raises(_evidence.ValidationError, match="does not exist inside"):
        _validate_carrier(tmp_path, fields)


def test_worker_delivered_rejects_report_identity_mismatch(tmp_path: Path) -> None:
    report = _write_report(tmp_path, _approval_report())
    fields = _carrier_fields(str(report.relative_to(tmp_path)), "0" * 64)
    with pytest.raises(_evidence.ValidationError, match="SHA-256 does not match"):
        _validate_carrier(tmp_path, fields)


def test_worker_delivered_rejects_unreadable_report_yaml(tmp_path: Path) -> None:
    report = _write_report(tmp_path, b"\xff")
    fields = _carrier_fields(str(report.relative_to(tmp_path)), hashlib.sha256(report.read_bytes()).hexdigest())
    with pytest.raises(_evidence.ValidationError, match="not readable YAML"):
        _validate_carrier(tmp_path, fields)


def test_worker_delivered_rejects_non_mapping_report_carrier(tmp_path: Path) -> None:
    report = _write_report(tmp_path, b"- just-a-list\n")
    fields = _carrier_fields(str(report.relative_to(tmp_path)), hashlib.sha256(report.read_bytes()).hexdigest())
    with pytest.raises(_evidence.ValidationError, match="must contain a mapping"):
        _validate_carrier(tmp_path, fields)


def test_worker_delivered_rejects_report_without_approval_proof(tmp_path: Path) -> None:
    report = _write_report(tmp_path, _approval_report(ledger_ok=False))
    fields = _carrier_fields(str(report.relative_to(tmp_path)), hashlib.sha256(report.read_bytes()).hexdigest())
    with pytest.raises(_evidence.ValidationError, match="does not prove approval"):
        _validate_carrier(tmp_path, fields)


def test_worker_delivered_rejects_report_identity_join_mismatch(tmp_path: Path) -> None:
    report = _write_report(tmp_path, _approval_report(packet_identity="f" * 64))
    fields = _carrier_fields(str(report.relative_to(tmp_path)), hashlib.sha256(report.read_bytes()).hexdigest())
    with pytest.raises(_evidence.ValidationError, match="identity joins do not match"):
        _validate_carrier(tmp_path, fields)


def test_worker_delivered_preserves_parent_receipt_case_exactly(tmp_path: Path) -> None:
    report = _write_report(tmp_path, _approval_report(parent_receipt_identity="Parent.Receipt:1"))
    fields = _carrier_fields(str(report.relative_to(tmp_path)))
    fields["worker report parent receipt identity"] = "Parent.Receipt:1"
    fields["worker report identity"] = hashlib.sha256(report.read_bytes()).hexdigest()

    _validate_carrier(tmp_path, fields)


def test_worker_delivered_rejects_parent_receipt_case_mismatch(tmp_path: Path) -> None:
    report = _write_report(tmp_path, _approval_report(parent_receipt_identity="Parent.Receipt:1"))
    fields = _carrier_fields(str(report.relative_to(tmp_path)))
    fields["worker report identity"] = hashlib.sha256(report.read_bytes()).hexdigest()

    with pytest.raises(_evidence.ValidationError, match="identity joins do not match"):
        _validate_carrier(tmp_path, fields)


@pytest.mark.parametrize("receipt", ["", "bad receipt", "bad\nreceipt", "@bad"])
def test_worker_delivered_rejects_empty_or_malformed_parent_receipt_identity(
    tmp_path: Path, receipt: str
) -> None:
    report = _write_report(tmp_path, _approval_report(parent_receipt_identity=receipt or "placeholder"))
    fields = _carrier_fields(str(report.relative_to(tmp_path)))
    fields["worker report identity"] = hashlib.sha256(report.read_bytes()).hexdigest()
    fields["worker report parent receipt identity"] = receipt

    with pytest.raises(_evidence.ValidationError, match="parent receipt identity"):
        _validate_carrier(tmp_path, fields)


def test_worker_delivered_rejects_report_foreign_to_artifact_binding(tmp_path: Path) -> None:
    report = _write_report(tmp_path, _approval_report())
    fields = _carrier_fields(str(report.relative_to(tmp_path)))
    fields["worker report identity"] = hashlib.sha256(report.read_bytes()).hexdigest()

    with pytest.raises(_evidence.ValidationError, match="Reviewed Input Identity"):
        _validate_carrier(
            tmp_path,
            fields,
            artifact_binding_fields={"packet sha256": "f" * 64, "identity sha256": "c" * 64},
        )


def test_blocked_fresh_eye_line_may_keep_a_pending_spawn_record(tmp_path: Path) -> None:
    """The escape hatch must stay open, or the rule above buys a false claim: an
    author whose spawn was genuinely blocked records `blocked <signal>` and the
    pending spawn state is then the TRUTH, not a contradiction."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="pending-parent-spawn", delivery="pending-parent-spawn")
    body = _body(
        fresh="blocked the Agent tool is not exposed in this session",
        tier=tier,
        tail="\n## Host signal\n\nAgent tool absent from the session tool list.\n",
    )
    relpath = _artifact(repo, "2026-07-28-blocked.md", body)

    assert _validate(repo, relpath).returncode == 0


# --- C2: the artifact that dates itself out of its own floors --------------


def test_body_date_cannot_back_date_an_artifact_out_of_its_floors(tmp_path: Path) -> None:
    """`_date_from_body(text) or _date_from_filename(path)` read the author-written
    channel FIRST, and every floor grandfathers on `date < RULE_DATE` — so an
    earlier body `Date:` bought exemption from the fresh-eye, boundary-ownership,
    delivery-state and reviewed-input binding floors at once."""
    repo = tmp_path / "repo"
    body = "# Demo Critique\nDate: 2026-07-01\n\n## Decision Under Review\n\nno floors filled at all\n"
    relpath = _artifact(repo, "2026-07-28-backdated.md", body)

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "has no `Fresh-eye satisfaction:` line" in result.stderr


def test_both_channels_agreeing_pre_cutoff_is_still_grandfathered(tmp_path: Path) -> None:
    """The control: taking the LATER date must not retroactively fail genuinely
    old artifacts, which is the whole checked-in corpus."""
    repo = tmp_path / "repo"
    body = "# Demo Critique\nDate: 2026-07-01\n\n## Decision Under Review\n\nno floors filled at all\n"
    relpath = _artifact(repo, "2026-07-01-old.md", body)

    assert _validate(repo, relpath).returncode == 0


# --- C3: the floor whose trigger its own producer never emits --------------


def test_bullet_form_packet_consumed_triggers_the_binding_floor(tmp_path: Path) -> None:
    """`PACKET_CONSUMED_RE` allowed leading whitespace but not a list marker, so
    the bullet form — what 34 checked-in artifacts and the scaffold's own
    instructions write — turned the binding floor OFF while declaring a packet."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    # Where the corpus actually writes it: a metadata bullet list, not inside the
    # `## Reviewed Input Identity` section.
    body = _body(tier=tier, tail="\n## Context\n\n- Packet Consumed: `some/packet.json`\n")
    relpath = _artifact(repo, "2026-07-28-bullet.md", body)

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "packet-bound critique must declare fields" in result.stderr


def test_bullet_trigger_inside_the_identity_section_also_demands_the_fields(tmp_path: Path) -> None:
    """The same trigger placed inside `## Reviewed Input Identity` is parsed as a
    field there, so it refuses through the missing-fields branch instead. Both
    placements must refuse; only the message differs, and pinning both keeps a
    future parser change from re-opening one of them."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    body = _body(tier=tier, tail="\n## Reviewed Input Identity\n\n- Packet consumed: some/packet.json\n")
    relpath = _artifact(repo, "2026-07-28-bullet-in-section.md", body)

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "reviewed input identity missing fields" in result.stderr


def test_heading_form_packet_consumed_triggers_the_binding_floor(tmp_path: Path) -> None:
    """C3's named residual: the `## Packet Consumed` heading form, which 46 checked-in
    release critiques use and no line trigger can match — no colon, path on a later
    line.

    It stayed open because every widening of a CONTENT trigger also fires on an
    artifact that merely discusses this surface, whose remediation (produce a SHA for
    a packet that does not exist) is impossible. A heading is not prose, so the
    heading form needs no such trade: it is read as a section, and the declared VALUE
    still decides, so the corpus's `n/a` negative keeps the floor off."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    body = _body(tier=tier, tail="\n## Packet Consumed\n\n`some/packet.json`\n\n## Context\n\n- ok\n")
    relpath = _artifact(repo, "2026-07-28-heading.md", body)

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "packet-bound critique must declare fields" in result.stderr


def test_heading_form_prose_is_not_a_declared_packet(tmp_path: Path) -> None:
    """The over-block the heading widening first re-created, caught by review.

    The declared value was the first TOKEN of the section's first line, tested only
    against the `n/a` negatives — so a prose opener read as a packet path. Two
    checked-in critiques open the section exactly that way (`Transient prepare packet
    generated at ...`, `Inline brief — the review covered ...`), and one of them, a
    May artifact nobody had edited, would then have been refused for missing reviewer
    tier evidence under `--paths`. A declared packet is a PATH."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    for label, first_line in (
        ("transient-prose", "Transient prepare packet generated at `2026-07-09T11:25:12Z` for the run."),
        ("inline-brief", "Inline brief — the review covered `tests/seed_cache.py` directly."),
    ):
        tail = f"\n## Packet Consumed\n\n{first_line}\n\n## Context\n\n- ok\n"
        relpath = _artifact(repo, f"2026-07-28-heading-{label}.md", _body(tier=tier, tail=tail))
        assert _validate(repo, relpath).returncode == 0, label

    # Falsifiable counterpart on the same reader: the two path shapes the corpus
    # writes DO still declare, so requiring a path did not close the widening.
    for label, first_line in (
        ("bare-path", "charness-artifacts/critique/x-packet.md"),
        ("code-wrapped", "`charness-artifacts/critique/x-packet.json`"),
    ):
        tail = f"\n## Packet Consumed\n\n{first_line}\n\n## Context\n\n- ok\n"
        relpath = _artifact(repo, f"2026-07-28-heading-declares-{label}.md", _body(tier=tier, tail=tail))
        assert _validate(repo, relpath).returncode == 1, label


def test_a_fenced_section_heading_is_not_the_real_section(tmp_path: Path) -> None:
    """Fenced text is SHOWN, not asserted — read as the author's claim on four gates
    now, and the artifacts most likely to QUOTE a canonical `## Section` block are
    critiques of these very validators.

    The shared section reader ignores headings inside a fence, so an artifact that
    documents the `## Reviewed Input Identity` form above its own real section binds
    through the real one. Before this, the quoted example's fields won by being
    first."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    tail = (
        "\n## Context\n\nThe canonical binding block is:\n\n"
        "```markdown\n## Reviewed Input Identity\n\n- packet path: `quoted/example.json`\n"
        "- packet sha256: `deadbeef`\n- identity sha256: `cafebabe`\n```\n"
    )
    relpath = _artifact(repo, "2026-07-28-fenced-identity.md", _body(tier=tier, tail=tail))

    # The quoted block declares nothing: no packet trigger, no binding fields read,
    # so the floor stays off rather than binding to `quoted/example.json`.
    assert _validate(repo, relpath).returncode == 0


def test_heading_form_declaring_no_packet_leaves_the_floor_off(tmp_path: Path) -> None:
    """The over-block twin, on the new shape. `n/a` under the heading is the corpus's
    way of writing "no packet"; demanding three SHA256 fields for it would be a
    refusal with no possible remediation. An EMPTY section is the third case: the
    author declared nothing either way, and reading that as absence would silently
    turn the floor off, so it is not read as a declaration at all.

    Prose that merely mentions the heading is not a declaration either — this is the
    trade a line trigger could not avoid and a heading parse does not have to make.
    """
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    for label, tail in (
        ("declared-absent", "\n## Packet Consumed\n\nn/a (no adapter sections)\n"),
        ("empty-section", "\n## Packet Consumed\n\n## Context\n\n- ok\n"),
        ("prose-mention", "\n## Context\n\n- we changed the `## Packet Consumed` parse today\n"),
        ("fenced-quotation", "\n## Context\n\n```\n## Packet Consumed\n\n`some/packet.json`\n```\n"),
    ):
        relpath = _artifact(repo, f"2026-07-28-heading-{label}.md", _body(tier=tier, tail=tail))
        assert _validate(repo, relpath).returncode == 0, label


def test_no_packet_consumed_line_leaves_the_binding_floor_off(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    relpath = _artifact(repo, "2026-07-28-nopacket.md", _body(tier=tier))

    assert _validate(repo, relpath).returncode == 0


# --- C4: the declared verify command that disables the floors --------------


def test_all_sweep_still_requires_reviewer_tier_evidence(tmp_path: Path) -> None:
    """`--all` is what `.agents/surfaces.json` declares as this validator's verify
    command, and under it `selected_paths` is empty — so `require_tier_evidence`
    was False for EVERY artifact. Whether an artifact carries tier evidence is a
    property of the artifact, not of how the run reached it."""
    repo = tmp_path / "repo"
    _artifact(repo, "2026-07-28-notier.md", _body())

    result = run_script(VALIDATOR, "--repo-root", str(repo), "--all")

    assert result.returncode == 1
    assert "reviewer tier evidence missing fields" in result.stderr


def test_all_sweep_does_not_retroactively_fail_pre_cutoff_artifacts(tmp_path: Path) -> None:
    """The control that bounds the rule above, and the reason it shares the
    fresh-eye enforce-from date: 99 checked-in artifacts claim `parent-delegated`
    with no tier block, and every one of them predates that date."""
    repo = tmp_path / "repo"
    _artifact(repo, "2026-07-01-notier.md", _body(date="2026-07-01"))

    assert run_script(VALIDATOR, "--repo-root", str(repo), "--all").returncode == 0


def test_all_sweep_names_the_floors_it_did_not_evaluate(tmp_path: Path) -> None:
    """`Validated N critique artifact(s).` reads as coverage. It was equally true
    of a sweep that evaluated neither binding currency nor the cross-surface
    probe, so the run now says what it did not establish."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    _artifact(repo, "2026-07-28-scope.md", _body(tier=tier))

    result = run_script(VALIDATOR, "--repo-root", str(repo), "--all")

    assert result.returncode == 0
    assert "enforcement scope over 1 artifact(s)" in result.stdout
    assert "mode=--all" in result.stdout
    # `-check=disabled`, not `=not-evaluated`: the flag is a fact about the
    # invocation. Saying "evaluated" would assert work over artifacts that
    # declared no binding at all — the overclaim the artifact count already made.
    assert "binding-currency-check=disabled" in result.stdout


def test_scope_record_reports_a_date_channel_disagreement(tmp_path: Path) -> None:
    """Reported, not refused: the corpus carries one honest past-midnight
    off-by-one, and the exemption a disagreement could buy is already gone."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    _artifact(repo, "2026-07-28-skew.md", _body(date="2026-07-29", tier=tier))

    result = run_script(VALIDATOR, "--repo-root", str(repo), "--all")

    assert result.returncode == 0
    assert "date-channel-disagreement=1" in result.stdout


# --- C6: the probe whose "no hit" meant "never ran" ------------------------


def test_configured_probe_with_no_changed_scope_reports_not_established(tmp_path: Path) -> None:
    """`run-quality.sh` passes `--changed-ref ""` whenever `merge-base origin/main
    HEAD` fails, and an empty ref short-circuited to `False` — indistinguishable
    from "configured, resolved, no match". The #408 objective override was
    silently absent with nothing to notice.

    Uses `--paths` against a real in-repo artifact so an artifact IS in scope: run
    in `changed` mode against a clean tree this assertion passed via the
    no-artifacts fallback instead of the probe resolution, i.e. it was green
    whether or not the repair worked.
    """
    # `-packet.md` files share the date prefix but are prepare-packet renders, not
    # critique artifacts: selecting one puts ZERO artifacts in scope and the assertion
    # below fails on `not-resolved` instead of exercising the probe. The glob happened
    # to pick a real artifact until a packet sorted last on the same date.
    #
    # Nor can it be the LAST artifact by name: `--paths` enables the binding-currency
    # check, and a critique artifact's reviewed-input identity goes stale as soon as
    # any reviewed path is edited afterwards — the normal, intended end state, which
    # five of the six most recent artifacts are already in. Pinning "the newest one
    # validates" made this test fail whenever an unrelated slice touched a file some
    # recent critique had reviewed. Select one whose binding is still current instead;
    # this test is about PROBE RESOLUTION, and the artifact is only a vehicle for
    # putting something in scope.
    candidates = sorted(
        path
        for path in (ROOT / "charness-artifacts" / "critique").glob("2026-07-2*.md")
        if not path.name.endswith("-packet.md")
    )
    assert candidates, "expected at least one recent critique artifact to select"
    for candidate in reversed(candidates):
        relpath = candidate.relative_to(ROOT).as_posix()
        result = run_script(VALIDATOR, "--repo-root", str(ROOT), "--paths", relpath, "--changed-ref", "")
        if result.returncode == 0:
            break
    else:  # pragma: no cover - only when every recent artifact has drifted
        raise AssertionError(
            "no recent critique artifact still has a current reviewed-input binding; "
            "this test needs one in scope to exercise probe resolution"
        )

    assert result.returncode == 0, result.stderr
    assert "cross-surface-probe=not-established" in result.stdout


def test_zero_artifacts_in_scope_does_not_fabricate_a_probe_resolution(tmp_path: Path) -> None:
    """The scope record reproduced the class it was added to close. `on_complete`
    runs unconditionally but the probe is resolved inside `validate_factory`,
    which the shared runner calls only when artifacts exist — so a run passing a
    perfectly good `--changed-ref` and simply finding no critique artifact printed
    "no --changed-ref/--changed-path resolved", asserting a resolution that never
    ran. That is the common `run-quality.sh` path."""
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "critique").mkdir(parents=True)

    result = run_script(VALIDATOR, "--repo-root", str(repo), "--all")

    assert result.returncode == 0
    assert "cross-surface-probe=not-resolved" in result.stdout
    assert "not-established" not in result.stdout


def test_undatable_artifact_is_not_exempt_from_tier_evidence(tmp_path: Path) -> None:
    """The C4 repair keyed on `observed_date is not None and >= RULE_DATE`, so an
    artifact with no parseable date was fully exempt under `--all` — through the
    one input this module's own rule names as never fail-open. Becoming undatable
    is easy and often accidental: an undated filename, or a `Date:` written as
    `**Date:**`."""
    repo = tmp_path / "repo"
    _artifact(
        repo,
        "release-2-12-0-critique.md",
        "# Release Critique\n\n**Date:** 2026-07-28\n\n"
        "## Fresh-Eye Satisfaction\n\nparent-delegated\n\n"
        "## Boundary Ownership\n\n- Verdict: single-surface\n",
    )

    result = run_script(VALIDATOR, "--repo-root", str(repo), "--all")

    assert result.returncode == 1
    assert "reviewer tier evidence missing fields" in result.stderr


def test_markup_wrapped_stub_does_not_satisfy_the_tier_floor(tmp_path: Path) -> None:
    """`_section_field_map` strips only backticks, so testing the raw value let
    `**TODO**` through — the unedited stub wearing three characters of markup,
    which is how this surface has been defeated before. Both sibling checks in the
    same file already normalized leading markup; this one did not."""
    repo = tmp_path / "repo"
    tier = (
        "## Reviewer Tier Evidence\n\n"
        "- Requested tier: **TODO** the fresh-eye reviewer tier requested.\n"
        "- Requested spawn fields: _TBD_ the fields sent.\n"
        "- Host exposure state: requested_fields_sent\n"
        "- Application state: > TODO the host signal.\n"
        "- Delivery state: findings-received\n"
    )
    relpath = _artifact(repo, "2026-07-28-markup.md", _body(tier=tier))

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "unedited scaffold `TODO`/`TBD` placeholder" in result.stderr


def test_earlier_mention_does_not_shadow_the_declared_fresh_eye_claim(tmp_path: Path) -> None:
    """`fresh_eye_satisfaction_status` returned the FIRST line containing the
    phrase, so a sentence in an earlier section shadowed the real
    `## Fresh-Eye Satisfaction` section — silently disarming the claim-vs-record
    consistency check, whose trigger is the claim's own text, while a human reader
    saw the contradiction plainly."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="pending-parent-spawn", delivery="pending-parent-spawn")
    body = (
        "# Demo Critique\nDate: 2026-07-28\n\n"
        "## Decision Under Review\n\n"
        "Fresh-eye satisfaction: nested-delegated for the sub-slice; the parent record is below.\n\n"
        f"{tier}\n"
        "## Fresh-Eye Satisfaction\n\nparent-delegated\n\n"
        "## Boundary Ownership\n\n- Verdict: single-surface\n"
    )
    relpath = _artifact(repo, "2026-07-28-shadowed.md", body)

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "claims a completed delegation" in result.stderr


def test_fenced_quotation_of_the_claim_is_not_read_as_the_claim(tmp_path: Path) -> None:
    """Fenced text is shown, not asserted — this repo's standing lesson, and a
    critique OF this validator is exactly the artifact that quotes the canonical
    form. The honest artifact below records a blocked review; the fence must not
    turn it into a delegation claim."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="pending-parent-spawn", delivery="pending-parent-spawn")
    body = (
        "# Demo Critique\nDate: 2026-07-28\n\n"
        "## Decision Under Review\n\n"
        "The refused shape is:\n\n```\nFresh-eye satisfaction: parent-delegated\n```\n\n"
        f"{tier}\n"
        "## Fresh-Eye Satisfaction\n\nblocked the Agent tool is not exposed in this session\n\n"
        "## Host signal\n\nAgent tool absent from the session tool list.\n\n"
        "## Boundary Ownership\n\n- Verdict: single-surface\n"
    )
    relpath = _artifact(repo, "2026-07-28-fenced.md", body)

    assert _validate(repo, relpath).returncode == 0


def test_nested_delegated_claim_is_held_to_the_same_spawn_record(tmp_path: Path) -> None:
    """Both typed values assert a delegation that COMPLETED; keying only on the
    parent spelling let the same false confidence through under the other token
    the scaffold offers as a co-equal choice."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="pending-parent-spawn", delivery="pending-parent-spawn")
    relpath = _artifact(repo, "2026-07-28-nested.md", _body(fresh="nested-delegated", tier=tier))

    result = _validate(repo, relpath)

    assert result.returncode == 1
    assert "claims a completed delegation" in result.stderr


def test_declared_absent_packet_does_not_turn_the_binding_floor_on(tmp_path: Path) -> None:
    """Widening the trigger to the bullet form made `- Packet Consumed: n/a` — the
    corpus's own way of writing "no packet" — demand three SHA256 fields for a
    packet the artifact just said does not exist. The over-block twin of the hole
    the widening closed."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    body = _body(tier=tier, tail="\n## Context\n\n- Packet Consumed: n/a (no adapter sections).\n")
    relpath = _artifact(repo, "2026-07-28-nopacket-declared.md", body)

    assert _validate(repo, relpath).returncode == 0


def test_line_wrapped_and_bold_packet_declarations_trigger_the_floor(tmp_path: Path) -> None:
    """The corpus's only genuine bullet declaration wraps the path onto the next
    line, so the first widening still missed the artifact that motivated it."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    for name, form in (
        ("wrapped", "- Packet consumed:\n  `charness-artifacts/critique/p.md`."),
        ("bold", "- **Packet Consumed**: `charness-artifacts/critique/p.md`"),
    ):
        relpath = _artifact(repo, f"2026-07-28-{name}.md", _body(tier=tier, tail=f"\n## Context\n\n{form}\n"))
        result = _validate(repo, relpath)
        assert result.returncode == 1, f"{name} form did not trigger the binding floor"
        assert "packet-bound critique must declare fields" in result.stderr


def test_unconfigured_probe_is_reported_distinctly_from_unestablished(tmp_path: Path) -> None:
    """A repo that configures no probe is opt-out by design (spec DBD-4) and must
    not read the same as a configured probe handed nothing to look at."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    _artifact(repo, "2026-07-28-noprobe.md", _body(tier=tier))

    result = run_script(VALIDATOR, "--repo-root", str(repo), "--all")

    assert result.returncode == 0
    assert "cross-surface-probe=not-configured" in result.stdout


def test_bare_fresh_eye_mention_reads_the_status_off_the_following_lines() -> None:
    """A colonless `Fresh-Eye Satisfaction` mention with the status wrapped below it.

    `declared_fresh_eye_status` is `section_reader(...) or line_reader(...)`, so this
    arm is reachable ONLY when no canonical `## Fresh-Eye Satisfaction` section exists.
    The corpus writes the bare mention when the declaration lives in a prose preamble;
    reading it as absent would report an undeclared status for an artifact that
    declared one, and the fresh-eye floor keys off exactly this value.
    """
    text = (
        "# Demo Critique\nDate: 2026-07-28\n\n"
        "Fresh-Eye Satisfaction\n\n"
        "parent-delegated\n\n"
        "## Boundary Ownership\n\n- Verdict: single-surface\n"
    )

    assert _scope.fresh_eye_satisfaction_status(text) == "parent-delegated"


def test_bare_fresh_eye_mention_stops_at_the_next_section() -> None:
    """The next section's prose is not this status.

    Without the stop, the boundary-ownership verdict below is spliced into the
    fresh-eye status and the floor matches against a string the author never wrote.
    """
    text = (
        "# Demo Critique\n\n"
        "Fresh-Eye Satisfaction\n\n"
        "## Boundary Ownership\n\n- Verdict: single-surface\n"
    )

    assert _scope.fresh_eye_satisfaction_status(text) == ""


def test_blocked_packet_declaration_is_absent_not_a_binding(tmp_path: Path) -> None:
    """`Packet Consumed: blocked <reason>` is the third value the critique skill's
    own result contract teaches for an honestly skipped packet. Before #636's
    sibling fix here, the first token `blocked` was read as a consumed-packet
    path, demanding three SHA fields for a packet the artifact just declared
    absent — a validator refusing the value its own skill prescribes."""
    repo = tmp_path / "repo"
    tier = _TIER_BLOCK.format(host="requested_fields_sent", delivery="findings-received")
    body = _body(
        tier=tier,
        tail="\n## Context\n\n- Packet Consumed: blocked host denied the prepare spawn\n",
    )
    relpath = _artifact(repo, "2026-08-18-blocked.md", body)

    result = _validate(repo, relpath)

    assert result.returncode == 0, result.stderr
