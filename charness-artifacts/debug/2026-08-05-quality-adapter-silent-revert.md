# Debug: the quality bootstrap reverts a customized adapter toward the preset
Date: 2026-08-05

Issue: [#481](https://github.com/corca-ai/charness/issues/481) — root cause found
and fixed.

## Problem

Running `quality` in a repo whose `.agents/quality-adapter.yaml` had already been
customized rewrote it. Measured in the reporter's tree: 47 -> 62 lines, comment
lines 14 -> 0, and keys naming paths that do not exist there 0 -> 3
(`scripts/coverage-floor-exemptions.txt`, `lefthook.yml`,
`.github/workflows/*.yml`).

## Correct Behavior

A bootstrap re-run over an already-customized adapter leaves the operator's
decisions intact: a field the operator deleted stays deleted, and anything the tool
cannot preserve is announced rather than silently overwritten.

## Observed Facts

- `gate_commands: [npm run gate]` survived, so the writer merges rather than
  blindly overwriting.
- Every comment line died; exactly the deleted preset keys came back.
- `SKILL.md` calls the bootstrap as standard procedure, so this repeats every run.

## Reproduction

- Fixture RECONSTRUCTED from the posted before/after, since the reporter's tree is
  not visible from this session: Svelte + TypeScript `package.json`,
  `tsconfig.json`, `README.md`, and a 24-line adapter with 12 comment lines,
  `gate_commands: [npm run gate]`, `preset_lineage: [typescript-quality]`, and
  `coverage_floor_policy` / `coverage_fragile_margin_pp` /
  `recommendation_defaults_version` / `public_spec_section_exemptions` /
  `preflight_commands` / `security_commands` deleted. Run
  `bootstrap_adapter.py --repo-root <fixture>` and diff before/after.
- The first replay did NOT reproduce: `adapter_status: unchanged`, nothing written.
  That negative result is what found M3 below.
- Adding `charness-artifacts/quality/latest.md` — present in any repo that has run
  `quality` before, so present in the reporter's — reproduced it immediately:
  `adapter_status: updated`, 24 -> 56 lines, 12 comments -> 0, and the reporter's
  three nonexistent-path keys back.

## Candidate Causes

- A blind overwrite that discards the existing file.
- A merge whose absence rule cannot tell never-set from deliberately-removed.
- A re-serializer that drops comments, which have no representation in its data.
- A write-suppression heuristic that fails open when anything else changes.

## Hypothesis

- Falsifiable claim: if this is a blind overwrite, every operator value dies; if it
  is a merge with a bad absence rule, PRESENT values survive and only DELETED ones
  return. `gate_commands` surviving predicts the second. | disconfirmer: replay on
  the fixture and check whether a present custom value survives while a deleted
  preset key returns.

## Verification

- Result: confirmed — `gate_commands` survived and only the deleted preset keys
  returned, disconfirming the blind-overwrite candidate. Three further isolating
  runs then separated the mechanisms below.

## Root Cause

Three mechanisms, each isolated by a controlled run so a single "the file did not
change" assertion could not hide one behind another.

**M1 — comment destruction.** `render_bootstrap_adapter` re-serializes from a data
dict; comments have no representation in it. Isolated with a run carrying comments
and ZERO deleted keys, forced to write by one benign one-line `concept_paths`
augmentation: comments 2 -> 0, data diff exactly one line. Independent of M2.

**M2 — key resurrection.** `field in explicit_fields` is the only absence signal in
`_add_adapter_policy_fields` / `_add_prompt_and_runtime_fields`, and absent
unconditionally means refill-with-default, so "never set" and "deliberately
removed" are indistinguishable. Isolated with a run carrying deleted keys and ZERO
comments: every defaulted key resurrected. Independent of M1.

**M3 — the trigger, which the report did not name.** `diff_is_defaulted_only()`
suppresses the write only when the ENTIRE diff is defaulted-only, so any single
unrelated legitimate merge unblocks the full rewrite and drags every defaulted key
in with it. In the reporter's repo that unblocking change is created BY THE QUALITY
RUN ITSELF, because its own artifact is a `detect_concept_paths` candidate.

M3 is why the existing guards did not help: the existence guard and `--dry-run`
protect the FILE, while what was lost was the operator's INTENT inside it — and the
de-facto protection for that intent, `diff_is_defaulted_only`, FAILS OPEN.

Fix: tightening `diff_is_defaulted_only` was the obvious move and the wrong one,
because suppression is not representation. Instead a hand-authored
`deliberately_absent` field maps a field name to the reason it is gone, so the merge
has something to look at, and the rationale lives in that same field because the
comment that held it is destroyed by the very rewrite it explains. Comments are
still not preserved — a recorded operator decision, with `ruamel.yaml` rejected as a
dependency and refusing-to-rewrite rejected because the operator does not hand-edit
adapters — so the loss is ANNOUNCED instead.

## Invariant Proof

- Invariant: a field the operator removed from the adapter stays removed across a
  bootstrap run.
- Producer Proof: `render_bootstrap_adapter` filters declared fields out of the
  rendered items; `tests/quality_gates/test_quality_bootstrap_absence.py:45`.
- Final-Consumer Proof: NOT established — `quality_adapter_lib` resolution still
  re-defaults on absence, so the invariant holds at the file and not at the resolved
  adapter. Escalated as #485 rather than claimed.
- Interface-Shape Sibling Scan: 4 render-and-write helpers measured; only this one
  merges into an existing file, the rest refuse or warn.
- Non-Claims: nothing here is verified in the reporter's tree.

## Detection Gap

- `diff_is_defaulted_only` write-suppression | did not fire: it was the de-facto
  protection for operator intent and fails open, suppressing only when the ENTIRE
  diff is defaulted-only | smallest change: represent the intent as data so
  suppression stops being what carries it.
- the bootstrap report | did not fire: it reported `updated` without stating what
  the update cost | smallest change: `comments_dropped` plus a stderr WARN naming
  the remedy.

## Sibling Search

- Mental model: a generator that merges into a hand-authored file must be able to
  represent "absent on purpose", or it will keep refilling deletions.
- axis: other render-and-write helpers | location: scripts/ + skills/, ruler = calls
  `render_yaml_mapping`/`write_adapter_scaffold` and writes | decision: no fix owed
  to the other 3 | proof: `adapter_lib.py:517` raises on an existing file;
  `markdown_preview_bootstrap_lib.py:107,:151` return `preserved-existing` and warn;
  `hitl/bootstrap_review.py:96` writes machine-only session state.
- axis: the same conflation in the CONSUMER | location: `quality_adapter_lib.py` |
  decision: escalate, do not fix here | proof: it starts from
  `infer_quality_defaults` and overlays only present fields, so absence is
  re-defaulted at resolution; filed as #485.
- cross-file: `scripts/adapter_lib.py` — the shared serializer carried two more
  instances of the same silent-drop class, both fixed here: a trailing ` # ...` was
  swallowed into the scalar (so `margin: 2.0  # widened` parsed as a string, the
  default won, and the report still said `preserved`; worst case a `key:  # note`
  line dropped its ENTIRE nested block), and a string equal to `true`/`123`
  reloaded as a bool/int.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: none
- Disproving Observation: none
- What Local Reasoning Cannot Prove: whether the reporter's own tree is fixed
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/critique/2026-08-05-issue-481-resolution-critique.md

## Prevention

`tests/quality_gates/test_quality_bootstrap_absence.py:45` names the reporter's
three resurrected keys and fails if the render filter is reverted; `:102` fails if
the announcement is removed; `:74` pins idempotence. The deeper prevention is the
vocabulary itself: a deletion is now sayable, so it no longer has to survive as an
absence that every default-on-absence rule will refill.

Residue, filed not folded: [#485](https://github.com/corca-ai/charness/issues/485)
(resolution still re-defaults on absence) and
[#486](https://github.com/corca-ai/charness/issues/486) (the announcement goes
silent once an adapter has no comments left, which this fix's own first run
guarantees).
