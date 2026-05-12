from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Callable


def issue_sibling_fixture_results(workspace: Path) -> dict[str, object]:
    return {
        "issue-146-mental-model-sibling-search": {
            "observationStatus": "observed",
            "blockerKind": "",
            "summary": "The causal review must name the mental model and scan structural sibling patterns beyond keyword and proximity matches.",
            "entryFile": str(workspace / "AGENTS.md"),
            "loadedInstructionFiles": [
                str(workspace / "skills/public/issue/SKILL.md"),
                str(workspace / "skills/public/issue/references/causal-review.md"),
            ],
            "loadedSupportingFiles": [],
            "routingDecision": {
                "selectedSkill": "issue",
                "bootstrapHelper": "none",
                "workSkill": "issue",
                "selectedSupport": "none",
                "firstToolCall": "none",
                "reasonSummary": "The issue skill requires mental model sibling search beyond keyword or proximity matching.",
            },
        },
        "issue-148-mental-model-sibling-search": {
            "observationStatus": "observed",
            "blockerKind": "",
            "summary": "The issue resolution requires recurrence-focused review, names the mental model, and scans structural sibling patterns beyond keyword and proximity matches.",
            "entryFile": str(workspace / "AGENTS.md"),
            "loadedInstructionFiles": [
                str(workspace / "skills/public/issue/SKILL.md"),
                str(workspace / "skills/public/issue/references/causal-review.md"),
            ],
            "loadedSupportingFiles": [],
            "routingDecision": {
                "selectedSkill": "issue",
                "bootstrapHelper": "none",
                "workSkill": "issue",
                "selectedSupport": "none",
                "firstToolCall": "none",
                "reasonSummary": "The recurrence-focused review must preserve mental model structural sibling search beyond keyword/proximity matches.",
            },
        },
    }


def run_issue_sibling_search_concept_fixtures(
    root: Path,
    *,
    run_command: Callable[..., object],
    expect_success: Callable[[object, str], None],
) -> None:
    with tempfile.TemporaryDirectory(prefix="charness-eval-issue-sibling-concepts-") as tmpdir:
        tmp = Path(tmpdir)
        workspace = tmp / "workspace"
        workspace.mkdir()
        fixture_results_path = tmp / "fixture-results.json"
        fixture_results_path.write_text(
            json.dumps(issue_sibling_fixture_results(workspace), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        for fixture in (
            root / "evals" / "cautilus" / "issue-146-sibling-search.fixture.json",
            root / "evals" / "cautilus" / "issue-148-sibling-search.fixture.json",
        ):
            result = run_command(
                [
                    "node",
                    "scripts/agent-runtime/run-local-eval-test.mjs",
                    "--repo-root",
                    str(root),
                    "--workspace",
                    str(workspace),
                    "--cases-file",
                    str(fixture),
                    "--output-file",
                    str(tmp / f"{fixture.stem}.observed.json"),
                    "--artifact-dir",
                    str(tmp / f"{fixture.stem}.artifacts"),
                    "--backend",
                    "fixture",
                    "--fixture-results-file",
                    str(fixture_results_path),
                ],
                cwd=root,
            )
            expect_success(result, f"{fixture.name} concept assertions")
