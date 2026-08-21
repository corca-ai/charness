# Retro Portability Boundary Debug (#685/#686)
Date: 2026-08-21

## Problem

Two current retro consumer paths mislead operators: the documented artifact-name
stem emits a warning that sounds actionable, and the installed planner advertises
a source-checkout command that is unavailable in a consumer repository.

## Correct Behavior

Given `--artifact-name <stem>`, persistence silently normalizes the name to the
documented `.md` artifact and returns the explicit persisted path. Given an
installed retro planner, every shipped skill probe is expressed through
`$SKILL_DIR`, resolves against the installed skill package, and is not hidden
inside an `ok: true` envelope when unavailable.

## Observed Facts

- `persist_retro_artifact.py --help` calls the value a filename stem without an
  extension, while `scripts/retro_persistence_lib.py` appends `.md` and prints
  `lacks .md` to stderr.
- The installed `plan_retro_run.py` emits
  `python3 skills/public/retro/scripts/check_auto_trigger.py --repo-root .`
  when run with `--repo-root /tmp`; that path is absent there while the envelope
  still says `ok: true`.
- The source and plugin copies contain the same implementation, so this is a
  shipped contract defect, not only a local checkout issue.

## Reproduction

- #685: run the documented persistence command with a temporary repo and
  `--artifact-name 2026-08-21-stem-probe`; the artifact is written, but stderr
  contains `lacks .md`.
- #686: run the installed-layout command with
  `--repo-root /tmp --changed-paths scripts/example.ts`; the `auto-session-trigger`
  packet has `available: false` for the source-layout path inside `ok: true`.

## Candidate Causes

- Persistence treats normalization as an exceptional caller error even though
  the public CLI defines a stem as the normal input.
- The planner uses a repository-relative path for a script shipped inside the
  skill package.
- Planner envelope health is based only on adapter validity and does not expose
  a missing gate packet as a failure, allowing an unavailable probe to look ready.

## Hypothesis

The primary causes are mismatched ownership contracts: the CLI owns the stem
normalization but the library leaks an internal diagnostic, and the installed
skill owns the trigger script but the planner addresses the source tree.
If normalization becomes a structured result without the warning and the
trigger packet resolves from `SKILL_ROOT` with `$SKILL_DIR`, the two reproductions
will disappear while persisted paths and source/plugin parity remain intact.
Disconfirmers: rerun both exact commands and inspect packet availability, stderr,
and artifact readback after the smallest changes.

## Verification

- Confirmed before repair: the warning is emitted only by the normalization branch;
  the planner path is hard-coded at the packet construction site, and its
  `available` bit is computed from the wrong root.
- Current status: hypothesis confirmed and repaired; source/export regression
  proof, readiness negative-branch proof, and parent focused tests are green.

## Root Cause

The two surfaces conflate a portable input/output contract with the authoring
checkout. A normal stem conversion is rendered as a warning, while a shipped
skill command is rendered as a source path. The planner's adapter-only `ok` bit
then fails to communicate the packet's path failure.

## Invariant Proof

- Invariant: a consumer-facing retro planner advertises only commands addressable
  in the consumer's current layout; persistence diagnostics distinguish refusal
  from accepted normalization.
- Producer Proof: persistence and planner packet builders are the producers.
- Final-Consumer Proof: the retro operator reads stderr, artifact path, and the
  structured planner packet; tests must exercise those channels separately.
- Interface-Shape Sibling Scan: debug/handoff planners distinguish `$SKILL_DIR`
  commands from repo-owned validators; this retro packet currently did not.
- Non-Claims: this does not prove a real host's installed cache or publication.

## Detection Gap

- Persistence tests asserted the warning, encoding the symptom instead of the
  public stem contract. Replace it with an assertion that stderr is empty.
- Planner tests checked packet presence and source-tree shape but not installed
  package resolution. Add a source/plugin-layout packet test with the exact
  portable command.

## Sibling Search

- Mental model: source checkout and installed package are interchangeable.
- same layer: debug/handoff planner commands | decision: retain their explicit
  repo-vs-skill distinction | proof: `$SKILL_DIR` command carriers in source.
- cross-file: `scripts/portable_command_carrier.py` | decision: no change; it
  audits documentation paths, not runtime planner resolution.

## Seam Risk

- Interrupt ID: retro-portability-boundary-685-686-2026-08-21
- Risk Class: external-seam, repeated-symptom
- Seam: installed skill planner -> emitted command -> consumer execution
- Disproving Observation: a fresh installed-layout packet test reports a valid
  `$SKILL_DIR` path and no unavailable required trigger probe.
- What Local Reasoning Cannot Prove: host cache refresh and real consumer execution.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-21-fresh-eye-delivery-boundary.md

## Prevention

Make shipped skill commands use one explicit skill-root carrier and test the
installed layout, while keeping repo-owned validators separately marked. Treat
normalization warnings as contract output changes requiring a consumer assertion,
not as harmless operator messaging.
