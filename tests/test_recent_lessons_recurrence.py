"""Back-test for lesson concept identity and the re-derived selection weighting.

The defect these pin: `_normalize_lesson_key` keys lesson identity on the first 14
words of the bullet's surface text, so re-wording a lesson reset its recurrence count
to 1. Measured on the live corpus, 1594 of 1596 candidates sat at
`source_count == 1`, making the recurrence multiplier exactly 1.0 and
selection pure recency -- while one concept held 7+ rows across 6 dates and never won
a digest slot.

Both halves are tested against the SHIPPED constants, not against locally fixed ones:
a test that pins its own alpha would keep passing after someone reverted the
re-derivation, which is the exact vacuous-test failure mode this file exists to avoid.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.lessons import recent_lessons_lib as lib  # noqa: E402

RETRO_DIR = "charness-artifacts/retro"


def _seed_retro(repo: Path, *, name: str, date: str, waste: list[str]) -> Path:
    artifact = repo / RETRO_DIR / name
    artifact.parent.mkdir(parents=True, exist_ok=True)
    body = [f"# Session Retro: {name}", f"Date: {date}", "Mode: session", "", "## Waste", ""]
    body.extend(f"- {item}" for item in waste)
    body.extend(["", "## Persisted", "", f"Persisted: yes: {RETRO_DIR}/{name}", ""])
    artifact.write_text("\n".join(body), encoding="utf-8")
    return artifact


def _index(repo: Path) -> list[dict]:
    payload = lib.build_lesson_selection_index(
        repo_root=repo,
        output_dir=repo / RETRO_DIR,
        summary_path=repo / RETRO_DIR / "recent-lessons.md",
    )
    return payload["candidates"]


def _by_class(candidates: list[dict], slug: str) -> dict | None:
    return next((c for c in candidates if c.get("recurrence_class") == slug), None)


# --- concept identity -------------------------------------------------------


def test_reworded_lessons_sharing_a_class_group_into_one_candidate(tmp_path: Path) -> None:
    """The whole point: re-wording must not reset the count."""
    repo = tmp_path / "repo"
    for index, (day, wording) in enumerate(
        [
            ("2026-05-01", "batch source edits before regenerating a derived surface"),
            ("2026-05-20", "regenerate the derived surface once, not once per edit"),
            ("2026-06-10", "stop re-running the sync helper after every single edit"),
        ]
    ):
        _seed_retro(
            repo,
            name=f"{day}-demo-{index}.md",
            date=day,
            waste=[f"{wording} (recurrence-class: derived-surface-batching)"],
        )
    entry = _by_class(_index(repo), "derived-surface-batching")
    assert entry is not None
    # Three differently-worded bullets, one concept, three independent observations.
    assert entry["source_count"] == 3


def test_untagged_reworded_lessons_stay_separate(tmp_path: Path) -> None:
    """Control: without a class tag the historical surface-text key still applies.

    This is what leaves the already-frozen retro corpus scored exactly as before.
    """
    repo = tmp_path / "repo"
    _seed_retro(repo, name="2026-05-01-a.md", date="2026-05-01", waste=["batch edits first"])
    _seed_retro(repo, name="2026-05-20-b.md", date="2026-05-20", waste=["regenerate once only"])
    candidates = _index(repo)
    assert all(c["source_count"] == 1 for c in candidates)
    assert all(c["recurrence_class"] is None for c in candidates)


def test_class_groups_across_sections_not_just_within_one(tmp_path: Path) -> None:
    """One concept seen as Waste here and a Next Improvement there is ONE class.

    Grouping only within a section would still split the measured 7-rows-across-
    6-dates concept, since it appeared in both.
    """
    repo = tmp_path / "repo"
    _seed_retro(
        repo,
        name="2026-05-01-a.md",
        date="2026-05-01",
        waste=["re-ran the helper per edit (recurrence-class: derived-surface-batching)"],
    )
    artifact = repo / RETRO_DIR / "2026-05-20-b.md"
    artifact.write_text(
        "# Session Retro: b\nDate: 2026-05-20\nMode: session\n\n"
        "## Next Improvements\n\n"
        "- workflow: batch the edits (recurrence-class: derived-surface-batching)\n\n"
        f"## Persisted\n\nPersisted: yes: {RETRO_DIR}/2026-05-20-b.md\n",
        encoding="utf-8",
    )
    entry = _by_class(_index(repo), "derived-surface-batching")
    assert entry is not None
    assert entry["source_count"] == 2
    # The class renders in the section of its NEWEST observation (the Next
    # Improvements bullet dated 2026-05-20), not of whichever filename sorted
    # first. Artifact order is lexicographic, so "first seen" was never
    # chronological and the digest cites the latest source path.
    assert entry["kind"] == "next_improvement"
    assert entry["lesson"] == "batch the edits"
    assert entry["latest_source_path"].endswith("2026-05-20-b.md")


def test_class_candidate_id_is_keyed_on_the_class_not_the_wording(tmp_path: Path) -> None:
    """A tagged class must not collide with an untagged bullet that opens the same way.

    Forgetting the tag on one copy is the expected authoring slip; if the id were
    still hashed on (kind, first-14-words) the two candidates could share an id.
    """
    repo = tmp_path / "repo"
    _seed_retro(
        repo,
        name="2026-05-01-a.md",
        date="2026-05-01",
        waste=["batch the edits first (recurrence-class: derived-surface-batching)"],
    )
    _seed_retro(repo, name="2026-05-20-b.md", date="2026-05-20", waste=["batch the edits first"])
    candidates = _index(repo)
    tagged = _by_class(candidates, "derived-surface-batching")
    untagged = next(c for c in candidates if c["recurrence_class"] is None)
    assert tagged is not None
    assert tagged["candidate_id"] != untagged["candidate_id"]
    assert tagged["candidate_id"].startswith("class:")


def test_class_display_follows_the_newest_wording(tmp_path: Path) -> None:
    """The digest cites the newest source, so it must show the newest wording."""
    repo = tmp_path / "repo"
    _seed_retro(
        repo,
        name="2026-05-01-a.md",
        date="2026-05-01",
        waste=["the old phrasing (recurrence-class: shared-concept)"],
    )
    _seed_retro(
        repo,
        name="2026-05-20-b.md",
        date="2026-05-20",
        waste=["the current phrasing (recurrence-class: shared-concept)"],
    )
    entry = _by_class(_index(repo), "shared-concept")
    assert entry is not None
    assert entry["lesson"] == "the current phrasing"


def test_class_marker_is_stripped_from_the_displayed_lesson(tmp_path: Path) -> None:
    """The tag is machine identity, not prose the next operator should read."""
    repo = tmp_path / "repo"
    _seed_retro(
        repo,
        name="2026-05-01-a.md",
        date="2026-05-01",
        waste=["batch the edits first (recurrence-class: derived-surface-batching)"],
    )
    entry = _by_class(_index(repo), "derived-surface-batching")
    assert entry is not None
    assert "recurrence-class" not in entry["lesson"]
    assert entry["lesson"] == "batch the edits first"


# --- re-derived weighting ---------------------------------------------------


def test_recurring_class_outranks_a_same_day_one_off(tmp_path: Path) -> None:
    """The retro's required acceptance: 5x over 50 days beats a 0-day one-off.

    Runs the real index builder with the SHIPPED constants. Under the previous pair
    (alpha 0.35, half-life 14) the class scored ~0.20 against 1.00 and lost.
    """
    repo = tmp_path / "repo"
    # 5 observations of one class, spread across 50 days ending 50 days before as_of.
    for index, day in enumerate(
        ["2026-05-01", "2026-05-13", "2026-05-25", "2026-06-06", "2026-06-08"]
    ):
        _seed_retro(
            repo,
            name=f"{day}-recurring-{index}.md",
            date=day,
            waste=[f"observation {index} (recurrence-class: long-running-trap)"],
        )
    # A brand-new one-off dated 50 days after the class's latest observation; the
    # newest date in the corpus is as_of, so this candidate sits at age 0.
    _seed_retro(repo, name="2026-07-28-fresh.md", date="2026-07-28", waste=["a brand new one-off"])

    candidates = _index(repo)
    recurring = _by_class(candidates, "long-running-trap")
    one_off = next(c for c in candidates if c["lesson"] == "a brand new one-off")

    assert recurring is not None
    assert recurring["source_count"] == 5
    assert recurring["age_days"] == 50
    assert one_off["age_days"] == 0
    assert recurring["selection_weight"] > one_off["selection_weight"], (
        f"recurring class {recurring['selection_weight']} must outrank the fresh "
        f"one-off {one_off['selection_weight']}"
    )
    # The class must also actually WIN, i.e. sort ahead of it, not merely score higher.
    assert candidates.index(recurring) < candidates.index(one_off)


def test_a_stale_recurring_class_still_decays_out(tmp_path: Path) -> None:
    """Recurrence must not become a permanent slot.

    The counterweight to the test above: a class that stopped recurring long ago
    loses to a fresh observation, so the boost cannot pin a dead concept forever.
    """
    repo = tmp_path / "repo"
    for index, day in enumerate(
        ["2026-01-01", "2026-01-05", "2026-01-09", "2026-01-13", "2026-01-17"]
    ):
        _seed_retro(
            repo,
            name=f"{day}-old-{index}.md",
            date=day,
            waste=[f"ancient observation {index} (recurrence-class: dead-trap)"],
        )
    _seed_retro(repo, name="2026-07-28-fresh.md", date="2026-07-28", waste=["a brand new one-off"])

    candidates = _index(repo)
    stale = _by_class(candidates, "dead-trap")
    one_off = next(c for c in candidates if c["lesson"] == "a brand new one-off")
    assert stale is not None
    assert stale["age_days"] > 180
    assert stale["selection_weight"] < one_off["selection_weight"]


def test_selection_policy_reports_the_shipped_constants(tmp_path: Path) -> None:
    """The index self-describes its policy, so a reader can audit the weighting."""
    repo = tmp_path / "repo"
    _seed_retro(repo, name="2026-05-01-a.md", date="2026-05-01", waste=["something"])
    payload = lib.build_lesson_selection_index(
        repo_root=repo,
        output_dir=repo / RETRO_DIR,
        summary_path=repo / RETRO_DIR / "recent-lessons.md",
    )
    policy = payload["selection_policy"]
    assert policy["alpha_base"] == lib.LESSON_SELECTION_ALPHA_BASE
    assert policy["recency_half_life_days"] == lib.LESSON_SELECTION_HALF_LIFE_DAYS


def test_the_derivation_invariant_holds_for_the_shipped_constants() -> None:
    """Guard the constants directly, independent of corpus construction.

    If someone reverts alpha or the half-life, this fails with the arithmetic in the
    message rather than as a confusing ranking change three tests away.
    """
    from datetime import date, timedelta

    as_of = date(2026, 7, 1)

    def weight(n: int, age: int) -> float:
        # Call the LIBRARY's own alpha and recency functions rather than
        # re-deriving them here: a re-implementation would keep passing after
        # someone changed the real formula, guarding the constants but not the
        # behavior they feed.
        alpha = lib.adaptive_lesson_alpha(n)
        _age_days, recency = lib._recency_weight(as_of - timedelta(days=age), as_of)
        return recency * (1 + alpha * max(0, n - 1))

    recurring = weight(5, 50)
    one_off = weight(1, 0)
    assert recurring > one_off, f"5x@50d={recurring:.3f} must exceed 1x@0d={one_off:.3f}"
    # Guard the MARGIN too: a pair that only barely satisfies the invariant flips
    # silently the next time anything about the corpus or the formula moves.
    assert recurring / one_off > 1.25, f"margin too thin: {recurring / one_off:.3f}"
    # And the decay end, so raising alpha alone cannot satisfy the test above.
    assert weight(5, 180) < one_off
