# Issue 619 JSON Shim Deletion Debug
Date: 2026-08-14

## Problem

`charness init` exits non-zero at HEAD. The installed-operator entry point is
broken on the commit awaiting publication, so anything published from this state
ships a non-zero install path.

## Correct Behavior

Given a public helper whose flag surface changes, when the change lands, then
every caller in every carrier kind — Python argv lists, adapter YAML command
lists, surface-manifest command strings, docs, and tests — is migrated with it,
or a standing gate refuses the change until they are.

## Observed Facts

- `charness:488-496` passes `--json` to
  `skills/public/setup/scripts/render_skill_routing.py` and `json.loads` the
  result. That script declares only `--repo-root` and `--detail`, and `--detail`
  emits YAML. Two faults stacked: the flag exits 2, and the format no longer
  matches the parser.
- Six more sites of the same class, none previously filed:
  `draft_dup_ratchet_triage.py:249-257` and `:258-270`,
  `.agents/surfaces.json:179` and `:180`, `.agents/release-adapter.yaml:72`
  (a release-phase instruction), `docs/deferred-decisions.md:1083-1084`
  (D46's own regeneration instruction), plus the half-migrated
  `tests/control_plane/test_integrations_validation.py:386`, which already
  parses with `yaml.safe_load` while still passing `--json`.
- `draft_dup_ratchet_triage.py` fails in its DEFAULT mode. Its `run()` has zero
  coverage: `tests/quality_gates/test_dup_ratchet_triage_draft.py:243-254`
  monkeypatches `triage.run` away.
- Commit `311844e23` removed `add_argument("--json")` from 13 public surfaces:
  2 documented (`inventory_adapter_gate_design.py`, `seed_dup_review.py`) and 11
  hidden `argparse.SUPPRESS` aliases. One of the hidden ones is
  `summary_output_lib.add_output_args`, which propagates to 27 `quality`
  scripts in a single edit.
- The planners' `--json` was not redundant, contrary to the 2026-07-18 record:
  the removed hunk shows `if args.json: print(json.dumps(...))` beside
  `yaml_output.emit_yaml(plan)`. It selected a serialization.
- `scripts/check_documented_command_flags.py` exists for exactly this class but
  `build_report` iterates `iter_docs(root)` — markdown only.
- `BACKTICK_CONTENT_RE` (`scripts/check_doc_links.py:52`) excludes newlines, and
  the multi-line join applies only inside fences on a trailing backslash, so a
  backticked command wrapping across a prose line break forms no carrier and is
  not counted as skipped.

## Reproduction

```
$ python3 scripts/run_standing_pytest.py --repo-root . --mode full --include-release-only
3 failed, 9028 passed, 21 errors in 119.06s

$ python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json
check_dup_ratchet.py: error: unrecognized arguments: --json          # exit 2
$ python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --json
inventory_doc_duplicates.py: error: argument --json-out: expected one argument
$ python3 skills/public/quality/scripts/draft_dup_ratchet_triage.py --repo-root .
check_dup_ratchet.py: error: unrecognized arguments: --json          # exit 2
```

## Candidate Causes

- The hidden `--json` alias was deleted without enumerating the caller
  population it had been carrying.
- The gate built for this class scans markdown only, so no non-markdown carrier
  was ever eligible to be checked.
- The only tests exercising `charness init` are marked `release_only`, and the
  standing lane appends `-m "not release_only"`.
- Wrapped backtick spans form no carrier at all, so a broken command inside the
  gate's own scan scope stays invisible.

## Hypothesis

- Extending the gate to Python argv lists, `.agents/*.json` and `.agents/*.yaml`
  command strings, and `tests/**`, and stopping the silent drop of wrapped
  backtick spans, will name every residue site before any of them is fixed;
  disconfirmer: it names fewer than the seven measured sites, or reports a
  finding on a healthy call site.

## Verification

- confirmed — the extended gate, copied into a pristine `git archive HEAD` tree,
  exits 1 and names all eight residue sites with zero false positives:
  `.agents/release-adapter.yaml:72`, `.agents/surfaces.json:179`, `:180`,
  `charness:489`, `docs/deferred-decisions.md:1083`,
  `draft_dup_ratchet_triage.py:250`, `:259`,
  `tests/control_plane/test_integrations_validation.py:380`.
- confirmed — after the migration to `--detail`, the same gate reports 1164
  invocations over 299 argparse surfaces with 0 findings and 324 typed skips.
- confirmed — against a scratch target repo, HEAD `charness` raises
  `CharnessError ... exit code 2`, while the repaired `charness` returns
  `status: required` with `skill_routing` as a dict.

## Root Cause

The July 2026 YAML migration drew its ownership boundary at the `charness`
executable and deliberately kept a hidden `--json` alias "for parser
compatibility" to carry every caller outside that boundary. The same record
declined to build an enumerating gate, judging that "a narrow source assertion
in the focused migration tests is enough; do not add a broad prose classifier."
`311844e23` then deleted the alias. Deleting a compatibility shim is safe only
under an enumeration of what it was carrying, and the prior decision guaranteed
no such enumeration existed.

## Invariant Proof

- Invariant: a documented or invoked command flag must be a flag the named
  script accepts, in every carrier kind the repo actually uses.
- Proof: the gate now resolves invocations in Python argv lists, adapter YAML,
  surface-manifest JSON, docs, and tests, probes each target's real `--help`,
  and reports typed skips so a pass cannot over-claim coverage. A wrapped
  backtick span is no longer silently absent from both findings and skips.

## Detection Gap

Three gaps stacked, each individually survivable. The flags gate was
markdown-scoped, so six of seven sites were out of scope by construction. The
`release_only` marker kept the one failing test out of the standing lane, and
`run-quality.sh` sets `--include-release-only` only under `--release`. And
`.agents/surfaces.json` verify commands are never executed by any gate —
`scripts/validate_surfaces.py` validates schema and globs, then prints a count.

## Sibling Search

- Mental model: a refactor is complete when the symbol is gone from the tree.
- same layer: the remaining `--json` residue sites | decision: same bug, fix now
  | proof: gate run over a pristine HEAD tree naming all eight.
- cross-file: `scripts/check-markdown.sh` and five sibling shell gates resolving
  a package root as a git root (#618) | decision: same class, fix now | proof:
  mirror invocation refuses with exit 1 and `core.hooksPath` unchanged.
- cross-file: `check_auto_trigger.py` / `check_boundary_escalation.py` reporting
  `triggered: false` for unconfigured and errored probes (#622) | decision: same
  class, fix now | proof: seven fixture states, each with its own state word and
  exit byte.
- abstraction up: the lesson lifecycle's read/score half has zero production
  callers, so the digest that would have carried this lesson could not rank it
  (#621) | decision: valid follow-up inside this slice | proof: ledger-backed
  selection surfaced `premise-not-checked-against-source` from the uncertainty
  bucket | follow-up: deferred docs/handoff.md#next-session

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: public helper flag surface to its callers across five carrier kinds.
- Disproving Observation: the extended gate reports a finding on a healthy call
  site, or misses a residue site a manual sweep finds.
- What Local Reasoning Cannot Prove: whether a consuming repo scripted against
  the removed flags; that is a release-note obligation, not a gate.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Critique Scope: gate carrier coverage, skip-reason honesty, and the runtime
  cost the widened scan adds to a standing lane.
- Next Step: impl
- Handoff Artifact: this record.

## Prevention

Delete a compatibility shim by owner cohort only after proving current-state
capability equality for its callers, and enumerate those callers with an
executable gate rather than a sweep of the identifier. The ledger already
carried this as `premise-not-checked-against-source` before the breaking commit
landed; it had never been scored, so the flat digest could not rank it into
view.
