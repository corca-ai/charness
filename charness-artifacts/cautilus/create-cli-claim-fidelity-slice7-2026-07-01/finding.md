# create-cli claim-fidelity capture — 2026-07-01 (reference-compaction Slice 7)

## Verdict

**FLOOR PASS (n=1, first live baseline).** Slice 7 moves the create-cli
claim-fidelity floor off the re-read proxy `requiredCommandFragments` doc-open of
`command-conventions.md` to an emitted-token floor
`requiredSummaryFragments=["version"]`. A fresh ask-before-run capture of the
pinned multi-command agent-CLI design prompt **emits the canonical `version`
lifecycle verb in its closeout** — the RSF floor MATCHES, and the three retained
RCF floors (`intent-first-grammar.md`, `command-surface.md`, `quality-gates.md`)
all opened. The token was **observed, not assumed**: `version` is NOT in the
prompt (`list/plan/capture/score/doctor`), so the run demonstrably ADDED the
canonical version surface from `command-conventions.md`'s flagship rule ("treat
`version` as the canonical version surface"). This is also create-cli's FIRST
live claim-fidelity capture (previously a HYPOTHESIS floor with thresholds
omitted).

## What ran

`/charness:create-cli` with the spec's pinned concrete slice (design a
claim-fidelity capture CLI: `list / plan(prep) / capture(execute) / score /
doctor`, agent-facing `--json`). Isolated-worktree capture at
`HEAD`=975715ff (`base-commit.txt`), exit **0 (NATURAL completion)**, **177065ms**
wall, 1.12M tokens, tool profile Bash=7 Skill=1. The run produced a full CLI
DESIGN (not code — the prompt scoped "설계해줘"), then stopped at three open
decisions awaiting the operator. No files were mutated (design-only), so there is
no `outputs/` set and no substance judge (create-cli has no
`outcome-assertions.json`).

## Floor: PASS, graded against the authoritative stream.jsonl

`build-skill-execution-observation.mjs --spec` over the capture's `stream.jsonl`
→ `outcome=passed | coverage=5/10`. The closeout literally emits:

- `claim-fidelity version   # cheap startup probe for agents` as a distinct
  command in the proposed surface — the RSF `version` token, matched.
- Justified via the convention: "`version` is the stable read-only probe for
  agents doing repeated startup checks; `-v` stays `verbose`" — a verbatim
  application of `command-conventions.md`'s version/verbose rules.
- Coverage 5/10 opened: `intent-first-grammar.md`, `command-surface.md`,
  `command-conventions.md`, `quality-gates.md`, `machine-readable-state.md`; the
  5 unopened are all on-demand refs (case-studies / code-shape /
  external-capability-clis / install-update / version-provenance).

## Why command-conventions.md is DEPTH, not a floor (the Move-C thesis for create-cli)

The observed run DID open `command-conventions.md` — but its flagship content
(the lifecycle verb enum `init/doctor/update/reset/uninstall/version` + "version
as the canonical version surface") is **already inlined verbatim in
`create-cli/SKILL.md` step 2 (lines 44-46)**, so the doc-open was not required to
apply the convention (the run had the verbs from always-loaded core). What
`command-conventions.md` uniquely owns — probe-surface list, `-v`=verbose rule,
version/help flag conventions, product-shaped-divergence rationale — is genuine
DEPTH the run opened for slice detail, not an every-run floor. So the doc stays
DECLARED with `classTag DEPTH` (like impl's `verification-ladder.md` after Slice
5); the floor moves from "did the run open the doc" to "did the run emit the
canonical verb." A future create-cli run that applies the verb convention from
core WITHOUT opening the doc would (correctly) still pass the emitted-token floor
— the exact wasteful-re-read relief Move C is for.

## Honest-reading guard (recorded, not softened)

- `version` also occurs incidentally in the closeout (a JSON `schema_version`
  field), so RSF `version` is a FORM floor, weakly discriminating on its own.
  Mitigation: create-cli keeps THREE doc-open RCF floors
  (intent-first-grammar/command-surface/quality-gates), so a shallow run that
  only echoes `schema_version` without a real design still fails routing. If a
  later capture shows the token passing on a hollow run, RE-PIN to a stronger
  emitted phrase (e.g. the version/verbose convention application) — never soften
  the matcher or re-add the doc-open proxy.
- create-cli has no substance judge, so this FORM floor is the only automated
  signal beyond routing; the honest closeout categorization is not machine-graded
  for create-cli (unlike impl).

## Also landed this slice (Slice-5 critique follow-up)

`references/quality-gates.md` said the `Lint Gate` status enum is "defined in"
`impl/references/verification-ladder.md "Lint Gate Closeout Shape"`. After Slice
5 that section forwards to `impl` SKILL.md `## Closeout Vocabulary`, so the prose
was stale; reworded to "live in `impl` SKILL.md `## Closeout Vocabulary`, to
which ... 'Lint Gate Closeout Shape' now forwards." (`create-cli/SKILL.md`
line 137-141's "owned by ... Lint Gate Closeout Shape" is left as-is — that
section legitimately owns the closeout-field SHAPE and forwards the enum.)

## Threshold

`thresholds.max_duration_ms=360000` set from this first PASSING baseline
(177065ms) at ~2x headroom (the hitl/retro model); advisory degrade signal, not
pass/fail.
