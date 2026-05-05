from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_prescribed_path_self_test_guidance_is_wired_to_authoring_and_impl() -> None:
    create_skill = (ROOT / "skills" / "public" / "create-skill" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    impl = (ROOT / "skills" / "public" / "impl" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    reference = (
        ROOT
        / "skills"
        / "public"
        / "create-skill"
        / "references"
        / "prescribed-path-self-test.md"
    ).read_text(encoding="utf-8")

    assert "references/prescribed-path-self-test.md" in create_skill
    assert "../create-skill/references/prescribed-path-self-test.md" in impl
    assert "checked or installed `SKILL.md`" in reference
    assert "raw provider response" in reference
    assert "producer-composed smoke test" in reference
    assert "no-op result" in reference
    assert "author's free-form smoke test" in create_skill
    assert "author-composed smoke probe" in impl
