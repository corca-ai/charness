# Validator Contract Coupling Debug
Date: 2026-07-18

## Problem

`validate_quality_artifact.py` accepted a quality record whose gitignored
evidence citation placed `<!-- reproduction-source -->` on the following line,
but the locked broad suite later failed `check_spec_evidence_durability.py`
because that validator requires the marker on the citation line.

## Correct Behavior

Given a scaffolded artifact with a reproduction-only citation, when its owning
author-time validator passes, then the same artifact should not first reveal an
undocumented formatting dependency in a much later broad gate.

## Observed Facts

- The quality validator and critique validator passed before locked closeout.
- The broad suite failed 1 of 4,718 tests on an exact line-local marker rule.
- Moving the marker onto the citation line made all 4,718 tests pass.
- The failure is repo-specific; web search is not useful for a local validator
  message whose source and tests are available directly.

## Reproduction

- Put `.charness/quality/runtime-signals.json` on one quality-artifact line and
  `<!-- reproduction-source -->` on the next; quality validation passes while
  `check_spec_evidence_durability.py --repo-root .` fails.

## Candidate Causes

- The quality validator may not compose the repo-wide evidence-durability rule.
- The durability checker may be overly line-local even when a following marker
  unambiguously annotates the preceding wrapped bullet.
- The quality scaffold/guidance may expose a valid shape, but manual wrapping
  may create an undocumented coupling that no author-time check owns.
- The closeout command plan may schedule the cheap durability checker only
  inside broad pytest instead of before the 95-second suite.

## Hypothesis

- The main cause is detection-order coupling: the owning quality validator does
  not invoke a shared artifact evidence check, and slice closeout does not run
  the existing cheap durability checker before broad pytest. If true, a minimal
  invalid fixture passes quality validation and the closeout plan lacks the
  checker as an early command. disconfirmer: inspect the checker and test whether
  the allegedly invalid marker is actually inside the same semantic Markdown
  list item before adding or moving a gate.

## Verification

- disconfirmed in its scheduling form — the durability gate is intentionally a
  repo-wide boundary scan, and the closeout manifest already runs changed-surface
  checks before broad pytest. Copying its parser into every artifact validator or
  moving the full scan into the structural sweep would add duplicate ownership.
- confirmed in a narrower semantic form — `iter_citation_lines` treated physical
  lines as the annotation boundary even when CommonMark indentation made the next
  line part of the same bullet. A focused fixture reproduced this exact mismatch.
- implemented — the checker now accepts an immediately following indented marker
  for a citation bullet, rejects an unindented next-line marker, and validates all
  316 current durability-scoped documents.

## Root Cause

The durability owner modeled evidence annotations as raw-line properties while
authors and Markdown renderers model wrapped list items semantically. Its test
suite protected against unrelated markers but had no wrapped-bullet case, so a
format-only wrap changed the verdict. A separate interface sibling duplicated
the entire CLI command path list in `render_cli_reference.py`; its only drift
detector was a later three-way pytest assertion rather than the renderer itself.

## Invariant Proof

- Invariant: an artifact author-time pass must not hide a deterministic repo-wide
  citation failure until the broad suite.
- Producer Proof: focused durability fixtures prove indented continuation and
  unindented unrelated marker behavior; command-docs YAML supplies help commands.
- Final-Consumer Proof: `check_spec_evidence_durability.py` passes all 316 scoped
  docs, and regenerated `docs/generated/cli-reference.md` is byte-identical.
- Interface-Shape Sibling Scan: quality/debug validators, scaffolds, closeout
  planning, command-docs YAML, CLI parser, command registry, and renderer inspected.
- Non-Claims: an owning validator need not absorb unrelated repo-wide policy;
  the repair should reuse or schedule the shared owner rather than duplicate it.

## Detection Gap

- durability checker tests | no wrapped-list-item fixture | add paired indented
  pass and unindented fail cases without duplicating the checker elsewhere.
- CLI reference renderer | maintained a private full command list | derive paths
  and order from the parser and help commands from command-docs; fail on mismatch.

## Sibling Search

- Mental model: passing an artifact's schema validator implies all deterministic
  artifact rules relevant to that file have run.
- same layer: quality/debug validators | decision: intentional schema-only
  boundary | proof: source inspection; repo-wide durability remains separately owned.
- abstraction up: physical-line annotations inside semantic Markdown blocks |
  decision: same bug, fix now | proof: paired local payload fixtures.
- specialization down: unindented or preceding markers unrelated to a citation |
  decision: intentional plain-text or non-rendering boundary | proof: negative fixtures.
- mental-model sibling: `render_cli_reference.py` private command list |
  decision: same bug, fix now | proof: parser/contract mismatch now fails in renderer.
- cross-file: `scripts/check_spec_evidence_durability.py` and
  `scripts/render_cli_reference.py`.

## Seam Risk

- Interrupt ID: artifact-validator-contract-coupling
- Risk Class: contract-freeze-risk
- Seam: scaffold -> owning validator -> repo-wide durability gate -> closeout.
- Disproving Observation: an indented continuation marker still fails, an
  unindented marker passes, or parser/command-docs drift renders silently.
- What Local Reasoning Cannot Prove: external Markdown dialects beyond the
  repo's CommonMark-compatible checked-in artifacts.
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/debug/2026-07-18-debug-review.md

## Prevention

Made evidence-marker scope follow the smallest semantic Markdown unit that
caused the incident, added positive/negative fixtures, and removed the renderer's
private CLI command path list. Kept repo-wide durability in its existing owner
instead of coupling every artifact validator to a spec-named parser.
