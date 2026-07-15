# Session Routing Catalog CLI Debug
Date: 2026-07-15

## Problem

A consumer-repository agent attempted a removed CLI name and reported that it
could not inspect skills. The supported inventory command then failed in the
installed global CLI with `ModuleNotFoundError: No module named 'scripts'`.

## Correct Behavior

Given an ordinary task, when a Charness session opens, then the agent starts
the matching workflow from installed metadata and judgment. Given an unclear
hidden-availability question, when it needs inventory, then it runs exactly
`charness catalog list --repo-root <repo> --json`; a nonzero result is reported
as a command failure, not as unavailable skills.

## Observed Facts

- `charness --help` lists `catalog` and no `find-skills` subcommand.
- The copied CLI in `/home/hwidong/.local/bin/charness` reported a managed
  checkout through `charness version --json`, yet `catalog list` failed to
  import `scripts`.
- Its loader selected `Path(__file__).parent` when no colocated package
  manifest existed, so it added the bin directory rather than the managed
  checkout to `sys.path`.
- The session hook and setup renderer named the catalog command but did not
  make the ordinary-task action and nonzero-result action equally explicit.

## Reproduction

- Copy `charness` to `<home>/.local/bin/charness`, copy the repository to
  `<home>/.agents/src/charness`, set `HOME=<home>`, then run the copied CLI's
  `catalog list --repo-root <consumer> --json` command. Before the fix it
  imports from the bin directory and fails; the focused subprocess regression
  reproduces the installed layout.

## Candidate Causes

- A live session still carried a historical prompt surface.
- The routing wording left ordinary-task behavior under-specified.
- The copied CLI used its bin directory instead of the managed checkout for
  its catalog backend.

## Hypothesis

- The standalone CLI fails because its catalog loader substitutes the script
  directory for the checkout; using `resolve_repo_root(default_home_root(),
  None)` will load the managed checkout. Disconfirmer: a copied-CLI subprocess
  still fails after that change.

## Verification

- result: confirmed — the copied-CLI regression passed after the loader uses
  the managed checkout; `20 passed` covered the catalog, session-hook, and
  setup-renderer focused suites.

## Root Cause

The loader's standalone fallback was inconsistent with the rest of the CLI:
version and lifecycle commands resolve the managed checkout, while catalog
used the copied executable's directory. Separately, the positive routing
replacement did not say when ordinary work should bypass inventory or how to
report an inventory failure.

## Invariant Proof

- Invariant: a copied CLI loads the catalog backend from its managed checkout;
  ordinary routing begins from metadata, with inventory reserved for unclear
  hidden availability.
- Producer Proof: `_load_catalog_lib` resolves the managed checkout before
  importing `scripts.capability_catalog`; hook and renderer emit the direct
  action sequence.
- Final-Consumer Proof: the subprocess test executes the copied CLI against a
  consumer repository and receives a read-only inventory payload.
- Interface-Shape Sibling Scan: `catalog refresh` shares the repaired loader;
  focused in-process dispatch coverage remains in the existing catalog test.
- Non-Claims: the currently installed binary and an already-open host session
  were not rewritten or rerun by this source slice.

## Detection Gap

- catalog loader test | reused an already imported backend after changing the
  fallback | add the copied-CLI subprocess regression.

## Sibling Search

- Mental model: a replacement contract must state the next action and its
  failure interpretation across runtime and generated guidance.
- same layer: `scripts/session_start_routing.py` | decision: same waste, fix now | proof: direct-action and nonzero-result assertions
- abstraction up: `skills/public/setup/scripts/render_skill_routing.py` and `AGENTS.md` | decision: same waste, fix now | proof: renderer assertion and source guidance update
- specialization down: `charness` catalog refresh | decision: diagnostic-only | proof: it shares the repaired `_load_catalog_lib`
- cross-file: `tests/charness_cli/test_codex_cache_refresh.py` | decision: same waste, fix now | proof: copied-CLI subprocess regression

## Seam Risk

- Interrupt ID: installed-cli-catalog-backend
- Risk Class: none
- Seam: none
- Disproving Observation: the copied-CLI subprocess would still raise an
  import error after the repair.
- What Local Reasoning Cannot Prove: a released update has replaced every
  operator's already installed CLI and restarted every host session.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep direct-action routing concise, retain the copied-CLI regression as the
install-boundary proof, and sync the hook and setup-generated guidance from
their source paths before validation.
