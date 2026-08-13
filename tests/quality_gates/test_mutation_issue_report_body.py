"""Execute the `Open or update mutation issue` script body, in every checked-in copy.

Until now this script existed only inside a workflow YAML string. No test, linter, or
type checker read it, and the step runs only when the pipeline is ALREADY red — so a
scheduled green could never exercise it, and two of its defects survived a repair that
claimed to fix them:

- **B** — the run-log tail was attached only when the summary file was ABSENT. In the
  runs that motivated the repair a summary DID exist and described a collateral symptom,
  so the branch never fired and the actual failing baseline output never reached the
  issue. A summary that exists is not a summary that explains.
- **D** — `clampBody` was defined and never applied. GitHub rejects a body over 65536
  characters and the throw kills the whole reporting step, so the runs with the most
  diagnostic output were the ones that filed nothing at all.

Both are behaviours of the JS, not of the YAML, so they are driven here through `node`
with `github`/`context` stubbed, rather than asserted as substrings. The parametrization
over `_workflow_copies()` is the other half: the repair reached this repo's live
workflow but not the shipped consumer templates, so every install kept the defect the
issue title names.
"""
from __future__ import annotations

import json
import os
import subprocess
import textwrap
from pathlib import Path

import pytest
import yaml

from .support import ROOT

STEP_NAME = "Open or update mutation issue"

HARNESS = """\
const calls = [];
// Rejections are drivable because the shipped script's ONLY failure handling is its two
// `error.status` arms, and stubs that can never reject leave both of them dead: an
// unconditional `throw` in either would keep every test green while, in production, the
// ordinary path failed the reporting step after the comment had already landed.
const reject = (name) => {
  const status = process.env[`HARNESS_${name}_ERROR_STATUS`];
  if (!status) return null;
  const error = new Error(`stubbed ${name} failure`);
  error.status = Number(status);
  return error;
};
const github = {
  // Records its route and params: the listing contract (state/labels/per_page) is part
  // of what "execute the shipped code" has to mean, and a discarding stub asserts none.
  paginate: async (route, params) => {
    calls.push({ op: 'paginate', route, params });
    return JSON.parse(process.env.HARNESS_OPEN_ISSUES || '[]');
  },
  rest: {
    issues: {
      listForRepo: 'listForRepo',
      createLabel: async (args) => {
        calls.push({ op: 'createLabel', args });
        const error = reject('CREATE_LABEL');
        if (error) throw error;
      },
      createComment: async (args) => { calls.push({ op: 'createComment', args }); },
      create: async (args) => { calls.push({ op: 'create', args }); },
      removeLabel: async (args) => {
        calls.push({ op: 'removeLabel', args });
        const error = reject('REMOVE_LABEL');
        if (error) throw error;
      },
    },
  },
};
const context = {
  repo: { owner: 'acme', repo: 'widget' },
  serverUrl: 'https://github.test',
  runId: '4242',
  sha: 'cafebabe',
};
const core = { info: () => {}, warning: () => {}, setFailed: () => {} };
(async () => {
%(script)s
})().then(
  () => require('node:fs').writeFileSync(process.env.HARNESS_OUT, JSON.stringify(calls)),
  (error) => { console.error((error && error.stack) || String(error)); process.exit(1); },
);
"""


def _workflow_copies() -> list[Path]:
    """Template, plugin mirror, AND this repo's hand-customized live instance.

    Reuses `test_quality_mutation_testing`'s list rather than restating it: two copies of
    the same three paths is how a fourth copy gets added to one and silently missed by
    the other, which is the very "one copy kept the defect" failure this file exists to
    close."""
    from .test_quality_mutation_testing import _mutation_workflow_copies

    return _mutation_workflow_copies()


def _copy_ids() -> list[str]:
    return [path.relative_to(ROOT).as_posix() for path in _workflow_copies()]


def _issue_script(workflow: Path) -> str:
    document = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    steps = [step for job in document["jobs"].values() for step in job["steps"]]
    matching = [step for step in steps if step.get("name") == STEP_NAME]
    assert len(matching) == 1, f"{workflow}: expected exactly one {STEP_NAME!r} step"
    return matching[0]["with"]["script"]


def _run(workflow: Path, tmp_path: Path, env: dict[str, str], open_issues: list[dict] | None = None):
    # Safe only while every template literal in the step is single-line: indenting would
    # otherwise inject two spaces into a multi-line backtick STRING and test a program
    # that differs from the shipped one.
    script = textwrap.indent(_issue_script(workflow), "  ")
    harness = tmp_path / "harness.js"
    harness.write_text(HARNESS % {"script": script}, encoding="utf-8")
    out = tmp_path / "calls.json"
    result = subprocess.run(
        ["node", str(harness)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        env={
            # Inherit the parent environment. A hardcoded PATH resolves `node` against
            # the PASSED env, so an nvm/asdf/homebrew node — and the CI runner's pinned
            # `actions/setup-node` toolcache prepend — both vanish, turning every case
            # into a bare FileNotFoundError on a host where node is installed.
            **os.environ,
            # The harness's OWN control keys, neutralized before `**env` may set them.
            # Inheriting the environment re-armed them: an exported
            # HARNESS_CREATE_LABEL_ERROR_STATUS made the propagate test throw at the
            # wrong stub while both its assertions still held, so a broadened
            # `removeLabel` catch would have shipped green. One repair re-arming what
            # another disarmed is the class this whole file exists to catch.
            "HARNESS_CREATE_LABEL_ERROR_STATUS": "",
            "HARNESS_REMOVE_LABEL_ERROR_STATUS": "",
            "HARNESS_OUT": str(out),
            "HARNESS_OPEN_ISSUES": json.dumps(open_issues or []),
            "ISSUE_TITLE": "Mutation testing failures",
            "ISSUE_LABEL": "mutation",
            "MARKER_TOKEN": "mutation-auto",
            **env,
        },
    )
    assert result.returncode == 0, result.stderr
    return json.loads(out.read_text(encoding="utf-8"))


def _posted_body(calls: list[dict]) -> str:
    posts = [call for call in calls if call["op"] in {"create", "createComment"}]
    assert len(posts) == 1, calls
    return posts[0]["args"]["body"]


def _write(tmp_path: Path, name: str, text: str) -> str:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


@pytest.fixture(params=_workflow_copies(), ids=_copy_ids())
def workflow(request) -> Path:
    return request.param


def test_a_failing_run_headlines_collateral_and_attaches_the_log_despite_a_summary(
    workflow: Path, tmp_path: Path
) -> None:
    """Defect B, precisely: the summary EXISTS. The predecessor's absence-only condition
    therefore never fired, and the run log — the only artifact naming the real failure —
    never reached the issue."""
    calls = _run(
        workflow,
        tmp_path,
        {
            "SUMMARY_PATH": _write(tmp_path, "summary.md", "## Summary\nno mutation report found"),
            "SAMPLE_PATH": _write(tmp_path, "sample.md", "## Sample\nfile.py"),
            "RUN_LOG_PATH": _write(tmp_path, "run.log", "baseline failed: ImportError\n"),
            "RUN_OUTCOME": "failure",
            "SUMMARY_OUTCOME": "failure",
            "SAMPLE_OUTCOME": "success",
        },
    )
    body = _posted_body(calls)
    assert "COLLATERAL" in body
    assert "## Run log tail (last 80 lines)" in body
    assert "baseline failed: ImportError" in body


def test_a_skipped_run_says_the_commands_never_ran(workflow: Path, tmp_path: Path) -> None:
    """`Run mutation` has no `always()`, so a failing sample step SKIPS it. A two-way
    branch reported "the mutation commands completed" for a run in which they never
    started."""
    calls = _run(
        workflow,
        tmp_path,
        {
            "SUMMARY_PATH": _write(tmp_path, "summary.md", "no report"),
            "SAMPLE_PATH": _write(tmp_path, "sample.md", "none"),
            "RUN_LOG_PATH": str(tmp_path / "absent.log"),
            "RUN_OUTCOME": "skipped",
            "SUMMARY_OUTCOME": "failure",
            "SAMPLE_OUTCOME": "failure",
        },
    )
    body = _posted_body(calls)
    assert "NEVER RAN" in body
    assert "- `Select mutation sample`: **failure**" in body
    # The verdict line's own literal, not the bullet list: `split("\n\n")[1]` was the
    # three bullets, which can never say "completed" under ANY verdict logic, so the
    # assertion could not discriminate the reassuring branch it names. Binding to the
    # literal keeps it discriminating without coupling to fixture text (a realistic
    # runner summary may legitimately contain the word).
    assert "The mutation commands completed" not in body


def test_a_successful_run_attributes_the_verdict_to_the_summary(
    workflow: Path, tmp_path: Path
) -> None:
    """The narrowing half: a genuine summary verdict must NOT be relabelled collateral,
    and must not drag an irrelevant log tail into the issue."""
    calls = _run(
        workflow,
        tmp_path,
        {
            "SUMMARY_PATH": _write(tmp_path, "summary.md", "score 61% below break 70%"),
            "SAMPLE_PATH": _write(tmp_path, "sample.md", "file.py"),
            "RUN_LOG_PATH": _write(tmp_path, "run.log", "irrelevant log\n"),
            "RUN_OUTCOME": "success",
            "SUMMARY_OUTCOME": "failure",
            "SAMPLE_OUTCOME": "success",
        },
    )
    body = _posted_body(calls)
    assert "the summary's own verdict" in body
    assert "Run log tail" not in body
    assert "COLLATERAL" not in body


def test_an_unset_run_outcome_is_reported_unexplained(workflow: Path, tmp_path: Path) -> None:
    """An outcome the step cannot read is not a success. The default must not silently
    become the reassuring branch."""
    calls = _run(
        workflow,
        tmp_path,
        {
            "SUMMARY_PATH": _write(tmp_path, "summary.md", "something"),
            "SAMPLE_PATH": _write(tmp_path, "sample.md", "file.py"),
            "RUN_LOG_PATH": str(tmp_path / "absent.log"),
            "RUN_OUTCOME": "",
            "SUMMARY_OUTCOME": "",
            "SAMPLE_OUTCOME": "",
        },
    )
    body = _posted_body(calls)
    assert "UNEXPLAINED" in body
    assert "- `Run mutation`: **unknown**" in body
    assert "- `Summarize mutation report`: **unknown**" in body


def test_an_oversized_body_is_clamped_before_it_is_posted(workflow: Path, tmp_path: Path) -> None:
    """Defect D. In the live workflow `clampBody` was defined and never called; in the two
    shipped templates it did not exist at all. Either way the body posted was the raw one,
    and GitHub rejects a body over 65536 characters — the throw kills the reporting step,
    so the runs with the most diagnostic output filed nothing."""
    calls = _run(
        workflow,
        tmp_path,
        {
            "SUMMARY_PATH": _write(tmp_path, "summary.md", "S" * 200_000),
            "SAMPLE_PATH": _write(tmp_path, "sample.md", "sample"),
            "RUN_LOG_PATH": _write(tmp_path, "run.log", "\n".join("L" * 200 for _ in range(400))),
            "RUN_OUTCOME": "failure",
            "SUMMARY_OUTCOME": "failure",
            "SAMPLE_OUTCOME": "success",
        },
    )
    body = _posted_body(calls)
    assert len(body) < 65536, "a body GitHub would reject reached the API"
    assert "body truncated at 60000 characters" in body
    # The D repair must not disable the B repair. `clampBody` truncates from the FRONT,
    # so with the log tail last a large summary consumed the whole budget and the tail
    # was sliced away — for exactly the population B is about: the runs with the most
    # diagnostic output, whose summary describes a collateral symptom.
    assert "## Run log tail (last 80 lines)" in body
    assert "## Step outcomes" in body


def test_the_run_log_tail_is_clamped_by_characters_not_only_lines(
    workflow: Path, tmp_path: Path
) -> None:
    """80 lines of 200 characters is ~16000 characters. This does not demonstrate a
    breach of the 65536 limit on its own — it demonstrates that the CHARACTER clamp
    fires, which a line-only clamp would not, and that the tail lands inside the body's
    budget rather than consuming it. The bound below is set under the unclamped size so
    removing the character clamp fails here."""
    calls = _run(
        workflow,
        tmp_path,
        {
            "SUMMARY_PATH": _write(tmp_path, "summary.md", "short"),
            "SAMPLE_PATH": _write(tmp_path, "sample.md", "sample"),
            "RUN_LOG_PATH": _write(tmp_path, "run.log", "\n".join("L" * 200 for _ in range(400))),
            "RUN_OUTCOME": "failure",
            "SUMMARY_OUTCOME": "failure",
            "SAMPLE_OUTCOME": "success",
        },
    )
    body = _posted_body(calls)
    assert "truncated to the last 8000 characters" in body
    assert len(body) < 12000


def test_the_clamped_body_reaches_an_existing_issue_too(workflow: Path, tmp_path: Path) -> None:
    """Two post sites, and the repair has to land on both. The comment path is the one a
    long-running failure actually takes, since the issue already exists by then."""
    marker = "<!-- acme/widget-mutation-auto -->"
    calls = _run(
        workflow,
        tmp_path,
        {
            "SUMMARY_PATH": _write(tmp_path, "summary.md", "S" * 200_000),
            "SAMPLE_PATH": _write(tmp_path, "sample.md", "sample"),
            "RUN_LOG_PATH": str(tmp_path / "absent.log"),
            "RUN_OUTCOME": "failure",
            "SUMMARY_OUTCOME": "failure",
            "SAMPLE_OUTCOME": "success",
        },
        open_issues=[{"number": 11, "body": f"{marker}\nolder report"}],
    )
    posts = [call for call in calls if call["op"] in {"create", "createComment"}]
    assert [call["op"] for call in posts] == ["createComment"]
    assert posts[0]["args"]["issue_number"] == 11
    assert len(posts[0]["args"]["body"]) < 65536
    assert "body truncated at 60000 characters" in posts[0]["args"]["body"]


def test_every_copy_carries_the_outcome_environment_the_body_reads(workflow: Path) -> None:
    """The behaviour above is only reachable if the step is handed the outcomes. A copy
    that drops these `env:` lines still runs — and reports `unknown` for every step,
    silently — so the wiring is pinned separately from the JS that consumes it."""
    document = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    steps = [step for job in document["jobs"].values() for step in job["steps"]]
    step = next(step for step in steps if step.get("name") == STEP_NAME)
    assert step["env"]["RUN_OUTCOME"] == "${{ steps.run.outcome }}"
    assert step["env"]["SUMMARY_OUTCOME"] == "${{ steps.summary.outcome }}"
    assert step["env"]["SAMPLE_OUTCOME"] == "${{ steps.sample.outcome }}"
    assert step["env"]["RUN_LOG_PATH"] == "${{ steps.adapter.outputs.run_log }}"


def test_an_empty_run_log_says_so_instead_of_showing_an_empty_fence(
    workflow: Path, tmp_path: Path
) -> None:
    """`Run mutation` creates the log with `tee` before the command runs, so a command
    that dies at process launch leaves a 0-byte file. An empty fenced block reads as "we
    looked and the run produced nothing", which a triager cannot tell from "the tail
    branch is broken again" — the exact ambiguity defect B was filed about."""
    calls = _run(
        workflow,
        tmp_path,
        {
            "SUMMARY_PATH": _write(tmp_path, "summary.md", "no report"),
            "SAMPLE_PATH": _write(tmp_path, "sample.md", "sample"),
            "RUN_LOG_PATH": _write(tmp_path, "run.log", ""),
            "RUN_OUTCOME": "failure",
            "SUMMARY_OUTCOME": "failure",
            "SAMPLE_OUTCOME": "success",
        },
    )
    body = _posted_body(calls)
    assert "the run log exists but is empty" in body
    assert "```\n```" not in body


def test_a_blank_tail_over_a_nonempty_log_does_not_claim_the_run_was_silent(
    workflow: Path, tmp_path: Path
) -> None:
    """The narrower claim. A whole-file emptiness statement drawn from the last 80 lines
    is the same overclaim the step exists to remove: the real failure can sit above the
    blank tail, and "the mutation commands produced no output" sends the triager away
    from it."""
    calls = _run(
        workflow,
        tmp_path,
        {
            "SUMMARY_PATH": _write(tmp_path, "summary.md", "no report"),
            "SAMPLE_PATH": _write(tmp_path, "sample.md", "sample"),
            "RUN_LOG_PATH": _write(
                tmp_path, "run.log", "baseline failed: ImportError\n" + "\n" * 200
            ),
            "RUN_OUTCOME": "failure",
            "SUMMARY_OUTCOME": "failure",
            "SAMPLE_OUTCOME": "success",
        },
    )
    body = _posted_body(calls)
    assert "the last 80 lines of the run log are blank" in body
    assert "produced no output" not in body
    assert "mutation-report" in body


def test_a_pre_existing_label_and_a_missing_recovery_label_are_swallowed(
    workflow: Path, tmp_path: Path
) -> None:
    """The two `error.status` arms are the script's ONLY failure handling, and they are
    reached on the ORDINARY path: the label usually already exists (422), and an issue
    that never went green carries no recovery-candidate label to remove (404). An
    unconditional re-throw would fail the reporting step after the comment had already
    landed, re-alarming a run that had already reported."""
    marker = "<!-- acme/widget-mutation-auto -->"
    env = {
        "SUMMARY_PATH": _write(tmp_path, "summary.md", "no report"),
        "SAMPLE_PATH": _write(tmp_path, "sample.md", "sample"),
        "RUN_LOG_PATH": str(tmp_path / "absent.log"),
        "RUN_OUTCOME": "failure",
        "SUMMARY_OUTCOME": "failure",
        "SAMPLE_OUTCOME": "success",
        "HARNESS_CREATE_LABEL_ERROR_STATUS": "422",
        "HARNESS_REMOVE_LABEL_ERROR_STATUS": "404",
    }
    calls = _run(workflow, tmp_path, env, open_issues=[{"number": 11, "body": marker}])
    assert [call["op"] for call in calls if call["op"] in {"create", "createComment"}] == [
        "createComment"
    ]


@pytest.mark.parametrize(
    ("variable", "status", "stub"),
    [
        ("HARNESS_CREATE_LABEL_ERROR_STATUS", "500", "CREATE_LABEL"),
        ("HARNESS_REMOVE_LABEL_ERROR_STATUS", "500", "REMOVE_LABEL"),
    ],
)
def test_an_unexpected_label_error_is_propagated_not_swallowed(
    workflow: Path, tmp_path: Path, variable: str, status: str, stub: str
) -> None:
    """The narrowing half: a broadened `catch` that swallowed everything would hide a real
    API failure behind a green step."""
    marker = "<!-- acme/widget-mutation-auto -->"
    script = textwrap.indent(_issue_script(workflow), "  ")
    harness = tmp_path / "harness.js"
    harness.write_text(HARNESS % {"script": script}, encoding="utf-8")
    result = subprocess.run(
        ["node", str(harness)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        env={
            **os.environ,
            "HARNESS_CREATE_LABEL_ERROR_STATUS": "",
            "HARNESS_REMOVE_LABEL_ERROR_STATUS": "",
            "HARNESS_OUT": str(tmp_path / "calls.json"),
            "HARNESS_OPEN_ISSUES": json.dumps([{"number": 11, "body": marker}]),
            "ISSUE_TITLE": "t",
            "ISSUE_LABEL": "mutation",
            "MARKER_TOKEN": "mutation-auto",
            "SUMMARY_PATH": _write(tmp_path, "summary.md", "no report"),
            "SAMPLE_PATH": _write(tmp_path, "sample.md", "sample"),
            "RUN_LOG_PATH": str(tmp_path / "absent.log"),
            "RUN_OUTCOME": "failure",
            "SUMMARY_OUTCOME": "failure",
            "SAMPLE_OUTCOME": "success",
            variable: status,
        },
    )
    assert result.returncode == 1
    # Names the stub, so the two parametrizations cannot be satisfied by the same throw.
    assert f"stubbed {stub} failure" in result.stderr


def test_the_issue_listing_is_scoped_to_open_issues_carrying_the_label(
    workflow: Path, tmp_path: Path
) -> None:
    """`listForRepo` selects the candidate set the marker is then matched against. A stub
    that discards its params asserts nothing about that scoping, so dropping `state` or
    `labels` — which would make the script scan unrelated issues — stayed green."""
    calls = _run(
        workflow,
        tmp_path,
        {
            "SUMMARY_PATH": _write(tmp_path, "summary.md", "no report"),
            "SAMPLE_PATH": _write(tmp_path, "sample.md", "sample"),
            "RUN_LOG_PATH": str(tmp_path / "absent.log"),
            "RUN_OUTCOME": "failure",
            "SUMMARY_OUTCOME": "failure",
            "SAMPLE_OUTCOME": "success",
        },
    )
    listings = [call for call in calls if call["op"] == "paginate"]
    assert len(listings) == 1, calls
    assert listings[0]["route"] == "listForRepo"
    assert listings[0]["params"]["state"] == "open"
    assert listings[0]["params"]["labels"] == "mutation"
    assert listings[0]["params"]["owner"] == "acme"
    assert listings[0]["params"]["repo"] == "widget"
