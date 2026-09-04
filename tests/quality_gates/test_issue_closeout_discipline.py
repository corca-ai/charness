from __future__ import annotations

import re
from pathlib import Path

import yaml

from tests.script_loader import load_script_module

from .support import ROOT, fake_gh_env, run_script

SKILL = ROOT / "skills" / "public" / "issue" / "SKILL.md"
CLOSEOUT = ROOT / "skills" / "public" / "issue" / "references" / "closeout-discipline.md"
SHAPING = ROOT / "skills" / "public" / "issue" / "references" / "issue-shaping.md"
RESOLVE_FLOW = ROOT / "skills" / "public" / "issue" / "references" / "resolve-flow.md"
SCRIPT = "skills/public/issue/scripts/issue_tool.py"


def _read(path) -> str:
    return path.read_text(encoding="utf-8")


def _issue_plan(tmp_path: Path, *args: str) -> dict:
    result = run_script(
        SCRIPT,
        "plan",
        "--repo-root",
        str(tmp_path),
        *args,
        env=fake_gh_env(tmp_path),
    )
    assert result.returncode == 0, result.stderr
    return yaml.safe_load(result.stdout)


def test_issue_skill_pins_verified_ledger_for_new_closeout() -> None:
    skill = _read(SKILL)
    closeout = _read(CLOSEOUT)

    assert "verified" in skill
    assert "{repo, number, url}" in skill
    assert "ledger" in skill
    assert "Created-Issue Ledger" in closeout
    assert "never report a number, repo, or status not present in the" in closeout


def test_the_ledger_keys_the_docs_name_are_keys_the_create_helper_actually_emits() -> None:
    """The join no test in this repo used to make, and the reason the defect was invisible.

    `test_issue_create.py` asserted the helper's real keys. The tests above assert the
    docs' real strings. Both passed while the docs named `{repo, number, url}` and the
    helper emitted `created_number` / `created_url` — so an agent following the
    instruction literally read nulls on a create that had SUCCEEDED, and a retry would
    have filed a duplicate issue. Two correct tests, one uncovered seam between them.

    This reads the key names out of the doc text rather than restating them, so renaming
    on either side fails here instead of silently drifting apart again.
    """
    documented: set[str] = set()
    for path in (SKILL, CLOSEOUT, RESOLVE_FLOW):
        for match in re.finditer(r"\{([a-z_]+(?:,\s*[a-z_]+)+)\}", _read(path)):
            keys = {key.strip() for key in match.group(1).split(",")}
            # Only brace sets containing `repo` are the CREATE ledger. Scoping on that
            # keeps the read/verify shape (`--json number,url,state`) from being checked
            # against the create payload, which would fail on a doc that is entirely
            # correct -- and the cheapest way out of that red would be deleting the guard.
            if "repo" in keys:
                documented.update(keys)
    assert documented, "no create-ledger key set found in the issue docs; the parser is broken, not the docs"

    # Brace sets are not the only way the docs name a payload key. These are named in
    # prose and backticks, which no safe regex distinguishes from ordinary words, so they
    # are listed rather than inferred. Listing them is what makes the guard cover the keys
    # the create closeout actually reads instead of only the three in the ledger set.
    documented.update({"body_preview", "body_verified", "title"})

    emitted = _create_payload_keys()
    missing = sorted(documented - emitted)
    assert not missing, (
        f"issue docs tell the agent to report {missing}, which the create helper never emits. "
        f"Helper emits: {sorted(emitted)}"
    )


def _create_payload_keys() -> set[str]:
    """Every key `issue_create.create_issue` can put in its payload, read from the source.

    Read statically on purpose: driving the helper would need a backend, and the failure
    being guarded is a NAME mismatch, which the literal assignments already show.

    Scoped to the `payload: dict[str, Any] = {...}` literal and later `payload[...] =`
    assignments, NOT to every dict key in the file. Parsing the whole file passed today
    only because every other dict literal happens to fit on one line; a formatter wrapping
    one of them would silently widen this set and make the assertion above pass when it
    should fail.
    """
    source = (
        ROOT / "skills" / "public" / "issue" / "scripts" / "issue_create.py"
    ).read_text(encoding="utf-8")
    create_function = re.search(
        r"^def create_issue\(.*?(?=^def _emit\()",
        source,
        re.DOTALL | re.MULTILINE,
    )
    assert create_function is not None, "could not find create_issue; this guard is looking at the wrong function"
    literal = re.search(r"payload: dict\[str, Any\] = \{(.*?)\n    \}", create_function.group(0), re.DOTALL)
    assert literal is not None, "could not find the create payload literal; this guard is looking at the wrong shape"
    keys = set(re.findall(r'^\s*"([a-z_]+)":', literal.group(1), re.MULTILINE))
    keys.update(re.findall(r'payload\["([a-z_]+)"\]\s*=', create_function.group(0)))
    return keys


def test_issue_new_closeout_requires_title_body_preview_and_warning() -> None:
    skill = _read(SKILL)
    closeout = _read(CLOSEOUT)

    assert "helper-returned title" in skill
    assert "body_preview" in skill
    assert "body_verified" in skill
    assert "Created <repo>#<number>: <title> (<url>)" in closeout
    assert "Body summary: <one to three sentences from body_preview>" in closeout
    assert "warning: body was not verified" in closeout


def test_issue_skill_pins_target_durability_on_retry() -> None:
    skill = _read(SKILL)
    closeout = _read(CLOSEOUT)
    resolve_flow = _read(RESOLVE_FLOW)

    assert "durable workflow state" in skill
    assert "target_unavailable" in skill
    assert "Target Durability" in closeout
    assert "do not re-walk the fallback ladder" in closeout
    assert "never silently fall through" in closeout
    assert "durable workflow state" in resolve_flow


def test_issue_shaping_requires_external_source_identity() -> None:
    shaping = _read(SHAPING)
    closeout = _read(CLOSEOUT)
    skill = _read(SKILL)

    assert "source identity" in shaping
    assert "Slack thread" in shaping
    assert "preserve the original user context" in shaping
    assert "External-Source Identity" in closeout
    # Field forms live in the describe script, not recopied in closeout prose.
    describe = _read(ROOT / "skills/public/issue/scripts/describe_closeout_draft_shape.py")
    assert "Source origin:" in describe
    assert "Re-read obligation:" in describe
    assert "Source origin:" in shaping
    assert "Re-read obligation:" in shaping
    assert "source identity/preservation" in skill


def test_issue_skill_guardrails_block_silent_retarget_and_chat_memory_closeout() -> None:
    skill = _read(SKILL)

    assert "Target repo is durable workflow state" in skill
    assert "target_unavailable" in skill
    assert "stale local note" in skill
    assert "source identity/preservation" in skill


def test_issue_planner_requires_closeout_discipline_for_new_and_resolve(tmp_path: Path) -> None:
    new_plan = _issue_plan(tmp_path, "--intent", "new")
    resolve_plan = _issue_plan(tmp_path, "--intent", "resolve", "--", "42")

    assert "references/closeout-discipline.md" in {ref["path"] for ref in new_plan["required_reads"]}
    assert "references/closeout-discipline.md" in {ref["path"] for ref in resolve_plan["required_reads"]}


def test_issue_resolve_prefers_autoclose_carriers_before_manual_close() -> None:
    skill = _read(SKILL)
    skill_flat = " ".join(skill.split())
    closeout = _read(CLOSEOUT)
    resolve_flow = _read(RESOLVE_FLOW)
    brief = _read(ROOT / "skills" / "public" / "issue" / "references" / "resolution-brief.md")

    # The compact skill keeps only routing; the detailed auto-close contract lives in
    # the closeout and resolution references below.
    assert "auto-close preference" in skill_flat
    assert "Resolve Auto-Close Linkage" in closeout
    assert "PR body" in closeout
    assert "commit body" in closeout
    assert "auto-close the normal closeout path" in resolve_flow
    assert "PR body or direct-to-default commit body" in brief
    assert "preferred closeout carrier" in brief
    assert "re-read GitHub state after comment plus close" in closeout
    assert "command success alone is not closeout" in closeout


def test_issue_closeout_draft_validation_runs_before_mutation(tmp_path: Path) -> None:
    plan = _issue_plan(tmp_path, "--intent", "resolve", "--", "42")
    closeout = _read(CLOSEOUT)

    gate_commands = {gate.get("id"): gate.get("command") for gate in plan["gate_packets"]}
    assert "validate-closeout-draft" in gate_commands["closeout-draft"]
    assert "Before a PR body, direct commit body, or manual close comment is published" in closeout
    assert "fails before any GitHub mutation" in closeout


def test_issue_closeout_draft_gate_names_the_stub_producer_not_only_the_validator(tmp_path: Path) -> None:
    """The closeout shape must be HANDED to the author at the gate, not discovered
    by failing the validator. The `closeout-draft` packet names its validator; it
    must also name `describe_closeout_draft_shape.py` (+ `--stub`), the producer
    that renders the enforced shape live from the verifier constants."""
    plan = _issue_plan(tmp_path, "--intent", "resolve", "--", "42")

    packet = next(gate for gate in plan["gate_packets"] if gate["id"] == "closeout-draft")
    assert "describe_closeout_draft_shape.py" in packet["shape_command"]
    assert packet["stub_command"].endswith("--stub")
    assert "describe_closeout_draft_shape.py" in packet["stub_command"]
    assert "before drafting" in packet["shape_run_when"]
    assert (ROOT / "skills/public/issue/scripts/describe_closeout_draft_shape.py").is_file()


def test_issue_closeout_covers_release_helper_issue_verification() -> None:
    closeout = _read(CLOSEOUT)
    publication_boundary = _read(ROOT / "skills" / "public" / "release" / "references" / "publication-boundary.md")

    assert "Release-driven direct-to-default work follows the same linkage" in closeout
    assert "--close-issue" in closeout
    # The PARSER, not a substring of the file that builds it. As a source-text check this
    # survived deleting the flag it guards: `--close-issue` still occurs in `--close-issue-repo`
    # and in five help strings, so the assertion stayed green while the promised flag was gone.
    parser_module = load_script_module(
        "publish_release_args_closeout_discipline",
        ROOT / "skills/public/release/scripts/publish_release_args.py",
    )
    options = {
        option
        for action in parser_module.build_parser()._actions
        for option in action.option_strings
    }
    assert "--close-issue" in options
    assert "payload.distinct_channel_verification" in publication_boundary


def test_issue_closeout_separates_carrier_from_lifecycle_publication() -> None:
    closeout = _read(CLOSEOUT)

    assert "Issue-resolution carrier publication" in closeout
    assert "separate publication surfaces" in closeout
    assert "do not require a second issue" in closeout
