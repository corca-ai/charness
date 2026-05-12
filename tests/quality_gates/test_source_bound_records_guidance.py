from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_source_bound_records_guidance_is_scoped_across_public_skills() -> None:
    create_skill = (ROOT / "skills" / "public" / "create-skill" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    source_bound = (ROOT / "skills" / "shared" / "references" / "source-bound-records.md").read_text(
        encoding="utf-8"
    )
    command_surface = (
        ROOT / "skills" / "public" / "create-cli" / "references" / "command-surface.md"
    ).read_text(encoding="utf-8")
    spec_text = (ROOT / "skills" / "public" / "spec" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    impl_text = (ROOT / "skills" / "public" / "impl" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    create_skill_flat = " ".join(create_skill.split())
    assert "source/principal binding drift" in create_skill_flat
    assert "multiple source items" in source_bound
    assert "external, irreversible, expensive, or hard-to-dedupe" in source_bound
    assert "read-only summaries or ordinary multi-document synthesis" in source_bound
    assert "SourceRecord" in source_bound
    assert "ExtractionCandidate" in source_bound
    assert "ValidatedIntent" in source_bound
    assert "CommitResult" in source_bound
    assert "source-bound, not row-bound" in source_bound
    assert "duplicate candidate envelopes for the same source" in source_bound
    assert "generic batch intake schema" in source_bound
    assert "JSON report artifact" in source_bound
    assert "destination evidence" in source_bound and "ledger lookup" in source_bound
    assert "source-bound records" in command_surface
    assert "../../shared/references/source-bound-records.md" in spec_text
    assert "../../shared/references/source-bound-records.md" in impl_text
