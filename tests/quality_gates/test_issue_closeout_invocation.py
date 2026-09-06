"""Artifact layout must not change the issue owner's complete carrier invocation."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.quality_gates.issue_closeout_support import load_verify_module
from tests.quality_gates.test_issue_bundled_closeout import (
    NUMBERS,
    REPO,
    _assert_two_group_success,
    _bundle_artifact,
    _bundle_body,
)
from tests.quality_gates.test_issue_closeout_commit_msg_hook import hook
from tests.quality_gates.test_prepush_close_keyword_guard import _finding

BUG_PATH = "charness-artifacts/issue/bug.md"
FEATURE_PATH = "charness-artifacts/issue/feature.md"
BUG_ARTIFACT = "Closes #42.\nClassification: bug\n"
FEATURE_ARTIFACT = "Closes #43.\nClassification: feature\n"


def _consume(root: Path, body: str, files: dict[str, str], consumer: str) -> dict:
    if consumer == "pre-push":
        result = _finding(root, body, files)
        assert result is not None
        return result
    message = root / "message.txt"
    message.write_text(body, encoding="utf-8")
    return hook.evaluate(
        root, message, REPO,
        list_paths=lambda _root: list(files),
        read_file=lambda _root, path: files[path],
    )


@pytest.mark.parametrize("consumer", ["commit-msg", "pre-push"])
@pytest.mark.parametrize("partition", ["separate", "artifact-plus-bare", "combined", "bare"])
def test_one_delivered_citation_survives_every_artifact_partition(
    tmp_path: Path, consumer: str, partition: str,
) -> None:
    _bundle_artifact(tmp_path)
    body = _bundle_body()
    files = {
        "separate": {BUG_PATH: BUG_ARTIFACT, FEATURE_PATH: FEATURE_ARTIFACT},
        "artifact-plus-bare": {BUG_PATH: BUG_ARTIFACT},
        "combined": {BUG_PATH: body},
        "bare": {},
    }[partition]

    result = _consume(tmp_path, body, files, consumer)

    assert result["ok"] is True
    assert len(result["reports"]) == 1
    report = result["reports"][0]
    _assert_two_group_success(report)
    assert report["source_artifacts"] == {
        number: [path for path, artifact in files.items() if f"#{number}" in artifact]
        for number in NUMBERS
    }
    assert report["bare_close_numbers"] == [
        number for number in NUMBERS if not report["source_artifacts"][number]
    ]


@pytest.mark.parametrize("consumer", ["commit-msg", "pre-push"])
@pytest.mark.parametrize("mutation", ["duplicate", "global", "disagree", "partial", "foreign"])
def test_message_only_classification_conflicts_remain_visible(
    tmp_path: Path, consumer: str, mutation: str,
) -> None:
    original = _bundle_body()
    body = original
    if mutation == "duplicate":
        body += "\nClassification #42: feature\n"
    elif mutation == "global":
        body += "\nClassification: feature\n"
    elif mutation == "disagree":
        body = body.replace("Classification #42: bug", "Classification #42: feature")
    elif mutation == "partial":
        body = body.replace("Classification #43: feature", "")
    else:
        body += "\nClassification #44: feature\n"

    with pytest.raises(RuntimeError, match="classification"):
        _consume(tmp_path, body, {BUG_PATH: original}, consumer)


@pytest.mark.parametrize("consumer", ["commit-msg", "pre-push"])
def test_conflicting_overlapping_artifacts_are_not_last_writer_wins(
    tmp_path: Path, consumer: str,
) -> None:
    with pytest.raises(RuntimeError, match="conflicting artifact classifications for #42"):
        _consume(
            tmp_path, _bundle_body(),
            {BUG_PATH: BUG_ARTIFACT, FEATURE_PATH: "Closes #42.\nClassification: feature\n"},
            consumer,
        )


@pytest.mark.parametrize("consumer", ["commit-msg", "pre-push"])
def test_artifact_authority_remains_valid_without_message_declarations(
    tmp_path: Path, consumer: str,
) -> None:
    _bundle_artifact(tmp_path)
    body = "\n".join(
        line for line in _bundle_body().splitlines()
        if not line.startswith("Classification ")
    )
    result = _consume(
        tmp_path, body,
        {BUG_PATH: BUG_ARTIFACT, FEATURE_PATH: FEATURE_ARTIFACT}, consumer,
    )
    _assert_two_group_success(result["reports"][0])


@pytest.mark.parametrize("consumer", ["commit-msg", "pre-push"])
def test_matching_overlapping_artifacts_preserve_every_source(
    tmp_path: Path, consumer: str,
) -> None:
    _bundle_artifact(tmp_path)
    result = _consume(
        tmp_path, _bundle_body(),
        {BUG_PATH: BUG_ARTIFACT, FEATURE_PATH: BUG_ARTIFACT}, consumer,
    )
    report = result["reports"][0]
    _assert_two_group_success(report)
    assert report["source_artifacts"][42] == [BUG_PATH, FEATURE_PATH]
    assert report["source_artifacts"][43] == []


def test_supplied_classifications_do_not_suppress_global_body_disagreement() -> None:
    verifier = load_verify_module()
    with pytest.raises(RuntimeError, match="conflict"):
        verifier._resolve_closeout_classifications(
            "Classification: feature", [42], None, {42: "bug"},
        )
    assert verifier._resolve_closeout_classifications(
        "No classification declaration.", [42], None, {42: "feature"},
    ) == {42: "feature"}
