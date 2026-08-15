"""Pins for `scripts/what_reads_this.py` (#599).

Three input kinds, and one negative case that matters more than the three: a
reference living only in a surface the tool cannot scan must be reported as
UNSCANNED, never as zero. The issue records both directions of that failure —
six deletion proposals refuted by a file nobody opened, and two files that look
orphaned because their consumers are an assertion on a value and a directory
glob. A search that answers "0" to the second kind is worse than no search,
because it is confidently wrong.

The fixture is a miniature tree rather than this repo: an assertion about this
repo's consumer count goes stale on unrelated commits, and re-recording the
number is not a test.
"""
from __future__ import annotations

from pathlib import Path

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]

WRT = load_script_module("what_reads_this_under_test", ROOT / "scripts" / "what_reads_this.py")

_CONSUMER = '''"""A module that reads things in three different ways."""
from helpers import listed_skill_ids

THRESHOLD = listed_skill_ids
PAYLOAD = {"listed_skill_ids": 3}


def check(compact):
    if compact.get("listed_skill_ids") != []:
        raise AssertionError("listed_skill_ids must be empty")


def load(config):
    return config.get("retry_budget") + config["retry_budget"]


def fixtures(root):
    return sorted(root.glob("*.fixture.json"))


def sources(root):
    return sorted(root.glob("skills/**/scripts/*.py"))
'''


def _fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "evals").mkdir(parents=True)
    (repo / "skills" / "public" / "demo" / "scripts").mkdir(parents=True)
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)

    (repo / "scripts" / "consumer.py").write_text(_CONSUMER, encoding="utf-8")
    (repo / "scripts" / "helpers.py").write_text("listed_skill_ids = ['a', 'b']\n", encoding="utf-8")
    (repo / "evals" / "contract.fixture.json").write_text("{}\n", encoding="utf-8")
    (repo / "skills" / "public" / "demo" / "scripts" / "run.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / ".agents" / "demo-adapter.yaml").write_text("version: 1\nretry_budget: 3\n", encoding="utf-8")
    (repo / "docs" / "guide.md").write_text("The adapter reads `retry_budget` from YAML.\n", encoding="utf-8")
    return repo


def _payload(repo: Path, **kwargs: object) -> dict[str, object]:
    return WRT.build_payload(repo, **kwargs)


def _kinds(payload: dict[str, object]) -> dict[str, int]:
    return payload["reference_kinds"]


def _files(payload: dict[str, object]) -> list[str]:
    return payload["files_with_references"]


def test_a_symbol_answer_separates_definition_import_and_assertion_on_value(tmp_path: Path) -> None:
    """The grouping is the contribution.

    `listed_skill_ids` is the recorded case: its real consumer is a string
    literal inside an assertion (`scripts/eval_setup.py` raises when the value
    is not empty), and a reader scanning a flat grep for `def` or a call site
    does not see it. The fixture carries that same shape — an assertion on the
    value, not merely a dict key — so the test measures the trap it names."""
    payload = _payload(_fixture_repo(tmp_path), target_kind="symbol", target="listed_skill_ids")

    assert set(_files(payload)) == {"scripts/consumer.py", "scripts/helpers.py"}
    kinds = _kinds(payload)
    assert kinds["definition"] >= 1
    assert kinds["import"] >= 1
    assert kinds["string-literal"] >= 1


def test_a_path_answer_finds_a_consumer_that_never_names_the_path(tmp_path: Path) -> None:
    """`evals/contract.fixture.json` is opened by `root.glob("*.fixture.json")`.

    Nothing in the tree contains the string `contract.fixture.json`, so a plain
    grep returns nothing and the file reads as deletable."""
    repo = _fixture_repo(tmp_path)
    payload = _payload(repo, target_kind="path", target="evals/contract.fixture.json")

    assert "scripts/consumer.py" in _files(payload)
    assert _kinds(payload)["basename-glob"] >= 1


def test_a_path_answer_reports_an_anchored_glob_as_the_stronger_kind(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    payload = _payload(repo, target_kind="path", target="skills/public/demo/scripts/run.py")

    assert "scripts/consumer.py" in _files(payload)
    assert _kinds(payload)["glob-consumption"] >= 1


def test_an_extension_only_glob_is_not_reported_as_a_consumer(tmp_path: Path) -> None:
    """`*.json` matches the fixture and says nothing about it.

    Counting it produced 175 matches for one query against this repo — an answer
    as unusable as the grep the tool replaces, in the opposite direction."""
    repo = _fixture_repo(tmp_path)
    (repo / "scripts" / "generic.py").write_text('def all_json(root):\n    return root.glob("*.json")\n', encoding="utf-8")

    payload = _payload(repo, target_kind="path", target="evals/contract.fixture.json")

    assert "scripts/generic.py" not in _files(payload)
    assert any("extension-only globs" in line for line in payload["unscanned_surfaces"])


def test_a_config_key_answer_separates_declaration_from_lookup(tmp_path: Path) -> None:
    payload = _payload(_fixture_repo(tmp_path), target_kind="config-key", target="retry_budget")

    assert set(_files(payload)) == {".agents/demo-adapter.yaml", "docs/guide.md", "scripts/consumer.py"}
    kinds = _kinds(payload)
    assert kinds["key-declaration"] >= 1
    assert kinds["lookup"] >= 1


def test_a_zero_result_carries_the_unscanned_surfaces_and_a_caveat(tmp_path: Path) -> None:
    payload = _payload(_fixture_repo(tmp_path), target_kind="symbol", target="nothing_reads_this_name")

    assert payload["reference_count"] == 0
    assert payload["files_with_references"] == []
    assert payload["unscanned_surfaces"]
    assert "not 'nothing reads this'" in str(payload["zero_result_caveat"])


def test_a_reference_only_in_an_unscanned_surface_is_unscanned_not_zero(tmp_path: Path) -> None:
    """The negative case the acceptance check names.

    The mirror is excluded by default for a good reason — it reads what the
    source reads, so counting it doubles every answer — but "excluded" must never
    read as "absent". The default answer is zero WITH the mirror named, and the
    flag that includes it finds the reference."""
    repo = _fixture_repo(tmp_path)
    mirrored = repo / "plugins" / "charness" / "scripts"
    mirrored.mkdir(parents=True)
    (mirrored / "only_consumer.py").write_text("from x import mirror_only_symbol\n", encoding="utf-8")

    default = _payload(repo, target_kind="symbol", target="mirror_only_symbol")
    assert default["reference_count"] == 0
    assert any("plugins/**" in line for line in default["unscanned_surfaces"])
    assert default["zero_result_caveat"] is not None

    included = _payload(repo, target_kind="symbol", target="mirror_only_symbol", include_mirrors=True)
    assert "plugins/charness/scripts/only_consumer.py" in _files(included)
    assert not any("plugins/**" in line for line in included["unscanned_surfaces"])


def test_the_unscanned_list_is_printed_on_a_non_zero_answer_too(tmp_path: Path) -> None:
    """A caveat shown only on failure reads as an apology, not as scope."""
    payload = _payload(_fixture_repo(tmp_path), target_kind="symbol", target="listed_skill_ids")

    assert payload["reference_count"] > 0
    assert payload["unscanned_surfaces"]
    assert payload["zero_result_caveat"] is None


def test_a_non_git_tree_says_so_rather_than_implying_a_tracked_listing(tmp_path: Path) -> None:
    payload = _payload(_fixture_repo(tmp_path), target_kind="symbol", target="listed_skill_ids")

    assert payload["listing"] == "filesystem-walk"
    assert any("git could not list this tree" in line for line in payload["unscanned_surfaces"])


def test_an_undecodable_file_is_declared_rather_than_skipped_silently(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    (repo / "scripts" / "binary.py").write_bytes(b"\xff\xfe\x00listed_skill_ids")

    payload = _payload(repo, target_kind="symbol", target="listed_skill_ids")

    assert any("could not read" in line for line in payload["unscanned_surfaces"])


def test_a_reference_only_in_an_unscannable_extension_is_unscanned_not_zero(tmp_path: Path) -> None:
    """The acceptance check's negative case, against a surface the tool truly cannot scan.

    The mirror is flag-includable, so proving the case there proves it for a
    surface the tool CHOOSES not to scan. The extension allowlist is the one it
    genuinely cannot: a tracked `.jsonl` ledger is valid UTF-8, is never read,
    and a reference living only there must be reported as unscanned."""
    repo = _fixture_repo(tmp_path)
    (repo / "charness-artifacts").mkdir(parents=True)
    (repo / "charness-artifacts" / "ledger.jsonl").write_text(
        '{"anchor": "ledger_only_symbol"}\n', encoding="utf-8"
    )

    payload = _payload(repo, target_kind="symbol", target="ledger_only_symbol")

    assert payload["reference_count"] == 0
    assert payload["zero_result_caveat"] is not None
    assert any("text allowlist" in line for line in payload["unscanned_surfaces"])


def test_the_declared_allowlist_caveat_matches_the_code() -> None:
    """The caveat names `.jsonl` and `.html` as NOT scanned.

    It is static prose, so it goes false the moment either extension is added to
    `_TEXT_SUFFIXES`. Pinning the relation keeps the declaration honest rather
    than merely present."""
    assert ".jsonl" not in WRT._TEXT_SUFFIXES
    assert ".html" not in WRT._TEXT_SUFFIXES
