"""Two readers refuse an unhonored adapter declaration instead of surveying the wrong
thing and reporting it as fact.

Rows 19-20 of slice 5.

`map_sources` produces a map OF THE REPO'S OWN narrative sources, so an unhonored
declaration does not degrade the output — it maps a different set of documents and says
nothing about the substitution. Measured at `724fe8a55`: a repo declaring
`source_documents: [docs/mine-narrative.md]` under `version: 9` reported
`source_documents: [README.md]`, the inferred default, exit 0. The census row notes the
emitted payload does not even carry an adapter validity field, so no consumer of the map
could tell.

`survey_verification` is the "a read is not a check" shape stated as plainly as it gets.
`adapter["valid"]` was ALREADY in the emitted payload and never branched on: a repo
declaring `verification_tools: [mytool]` under `version: 9` emitted `adapter_valid: false`
BESIDE `tool_checks: []`, exit 0 — the survey reporting the repo configured no
verification tools, in the same breath as reporting that it could not read the file that
says otherwise. The flag was printed, not used.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from .support import run_script

# Literal, so the coverage mapper can bind these tests to their sources by name.
MAP_SOURCES = "skills/public/narrative/scripts/map_sources.py"
SURVEY_VERIFICATION = "skills/public/impl/scripts/survey_verification.py"

# The shapes each contract actually reads — `optional_string_list` for both, not the
# richer mapping forms an earlier stimulus in this slice guessed at and got wrong twice.
NARRATIVE = """version: {v}
repo: demo
remote_name: upstream
source_documents:
  - docs/mine-narrative.md
mutable_documents:
  - docs/mine-narrative.md
"""
IMPL = """version: {v}
repo: demo
verification_tools:
  - mytool
"""


def _repo(tmp_path: Path, name: str, adapter: str | None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / f"{name}-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(rel: str, repo: Path) -> subprocess.CompletedProcess:
    return run_script(rel, "--repo-root", str(repo))


@pytest.mark.parametrize("version", ["9", "!!int 9"], ids=["unspeakable", "unparseable"])
def test_map_sources_refuses_rather_than_mapping_the_default_set(
    tmp_path: Path, version: str
) -> None:
    repo = _repo(tmp_path, "narrative", NARRATIVE.format(v=version))
    result = _run(MAP_SOURCES, repo)
    assert result.returncode != 0, result.stdout
    if version == "9":
        assert "narrative-adapter.yaml" in result.stderr, result.stderr
        assert "does not speak" in result.stderr, result.stderr
    else:
        # CONVERGED by `#673`: the five bare-loader libraries route through
        # `adapter_lib.read_declared_adapter`, so every resolver RECORDS a parse refusal
        # instead of raising and this door renders one verdict shape everywhere.
        assert "Traceback" not in result.stderr, result.stderr
        assert "narrative-adapter.yaml" in result.stderr, result.stderr
        assert "could not be parsed" in result.stderr, result.stderr
    # The substituted document set must not be reported alongside the refusal.
    assert "README.md" not in result.stdout


@pytest.mark.parametrize("version", ["9", "!!int 9"], ids=["unspeakable", "unparseable"])
def test_survey_verification_refuses_rather_than_echoing_the_flag_it_ignores(
    tmp_path: Path, version: str
) -> None:
    repo = _repo(tmp_path, "impl", IMPL.format(v=version))
    result = _run(SURVEY_VERIFICATION, repo)
    assert result.returncode == 1, result.stdout
    # `impl` routes through `simple_skill_adapter_lib`, so BOTH doors render the same
    # message shape here. The asymmetry with `map_sources` above is the resolver's, not
    # the guard's, and is measured rather than assumed: ten of sixteen resolvers record a
    # parser refusal in `errors` and six let it out.
    assert "impl-adapter.yaml" in result.stderr
    # The precise defect: `adapter_valid: false` printed beside an empty survey.
    assert "adapter_valid: false" not in result.stdout
    assert "tool_checks: []" not in result.stdout


def test_a_speakable_version_surveys_what_the_repo_declared(tmp_path: Path) -> None:
    """The polarity control, and the arm that failed to fail twice earlier in this slice
    when a fixture declared a shape the contract ignores. Each expectation appears ONLY
    when the declaration was honored."""
    narrative = _repo(tmp_path / "n", "narrative", NARRATIVE.format(v="1"))
    mapped = _run(MAP_SOURCES, narrative)
    assert mapped.returncode == 0, mapped.stderr
    assert "docs/mine-narrative.md" in mapped.stdout
    assert "README.md" not in mapped.stdout

    impl = _repo(tmp_path / "i", "impl", IMPL.format(v="1"))
    surveyed = _run(SURVEY_VERIFICATION, impl)
    assert surveyed.returncode == 0, surveyed.stderr
    assert "spec: mytool" in surveyed.stdout
    assert "adapter_valid: true" in surveyed.stdout


def test_no_adapter_at_all_is_not_a_refusal(tmp_path: Path) -> None:
    """Opt-in surfaces. `map_sources` infers a default document set for a repo that
    declared none, which is the correct answer for it — it is only wrong over a repo that
    declared something else."""
    assert _run(MAP_SOURCES, _repo(tmp_path / "n", "narrative", None)).returncode == 0
    assert _run(SURVEY_VERIFICATION, _repo(tmp_path / "i", "impl", None)).returncode == 0


@pytest.mark.parametrize(
    ("rel", "name", "adapter", "honored"),
    [
        (MAP_SOURCES, "narrative", NARRATIVE, "docs/mine-narrative.md"),
        (SURVEY_VERIFICATION, "impl", IMPL, "spec: mytool"),
    ],
    ids=["map_sources", "survey_verification"],
)
def test_an_ordinary_invalid_field_is_not_refused(
    tmp_path: Path, rel: str, name: str, adapter: str, honored: str
) -> None:
    """The polarity a round-1 bounded review found unpinned for these two rows.

    `valid: false` from one bad field beside honored ones must NOT refuse — widening the
    predicate to `not valid` would break every consumer with a typo'd unrelated key. The
    honored value is asserted too, so the test cannot pass by a guard that refuses nothing
    AND a resolver that honors nothing.
    """
    text = adapter.format(v="1").replace("repo: demo", "repo: demo\npreset_version: 3")
    result = _run(rel, _repo(tmp_path, name, text))
    assert result.returncode == 0, result.stderr
    assert honored in result.stdout, result.stdout


@pytest.mark.parametrize(
    ("rel", "name"),
    [(MAP_SOURCES, "narrative"), (SURVEY_VERIFICATION, "impl")],
    ids=["map_sources", "survey_verification"],
)
def test_a_silently_dropped_declaration_splits_on_the_resolver(
    tmp_path: Path, rel: str, name: str
) -> None:
    """The third door, and the two rows now land on the SAME side of it.

    They did not. `impl` routed through `simple_skill_adapter_lib`, which records a dropped
    line in WARNINGS, so `declarations_dropped` saw it and the run refused; `narrative`
    called `adapter_lib.load_yaml_file` bare, discarded that sink, and proceeded on the
    inferred default. `#673` routed narrative through `read_declared_adapter`, so this is
    the deliberate test change the previous version asked for — and the `impl` arm, which
    was already correct, still guards against regressing the half that worked.
    """
    repo = _repo(tmp_path, name, "version: 1\nrepo: demo\n  remote_name: upstream\n")
    result = _run(rel, repo)
    assert result.returncode == 1, result.stdout
    assert "could not interpret" in result.stderr, result.stderr
