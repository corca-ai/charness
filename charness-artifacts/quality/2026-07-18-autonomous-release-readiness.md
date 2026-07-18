# Quality Review
Date: 2026-07-18
Title: Dead-code advisory signal and autonomous release readiness

## Scope

Target boundary: dead-code advisory precision, confirmed internal helper cleanup, synchronized plugin exports, and release readiness for the cumulative unreleased range.

Ambient repo findings: D18 remains ignored. Existing near-limit files and nested CLI tests are reported but are not attributed to this slice.

## Structural Packet

- capability_needed: maintainers need a credible dead-code attention list rather than framework/source-scan conventions mixed with deletion candidates.
- current_centers: vulture primary/sweep, path/name heuristics, AST classification, and human removal judgment.
- next_center: one source parse that assigns provenance-backed runtime-external roles before findings reach human triage.
- transformation: classify observed conventions and delete repository-proven residue; do not build a general dynamic-use oracle.
- proof_boundary: positive and negative role fixtures, live inventory delta, synchronized exports, broad gates, changed-line proof, and release-range verification.
- enforcement_posture: keep this advisory; irreversible release boundaries retain separate verification teeth.
- sequencing: parse and classify once, preserve ambiguous exports for judgment, then delete only proven residue. Generative ordering optimizes evidence cost, not correctness.

## Current Gates

- Focused pytest and ruff own classifier behavior; source/plugin sync and packaging own exported parity.
- Read-only quality, locked closeout, changed-line coverage, fresh checkout probes, and public-release readback own progressively broader claims.
- The advisory does not block or declare dead code by itself.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; release-quality profile. <!-- reproduction-source -->
- runtime hot spots: this read-only release run passed 81 gates in 76.4s; pytest was 56.1s. Recent full-release latest/median was 82.6/82.2s and dead-code advisory 7.8/7.8s.
- coverage gate: focused behavior tests passed; the pre-commit consumer excluded worktree changes and is explicitly not trusted. Authoritative locked changed-line proof runs after commit.
- evaluator depth: deterministic-gates-only because AST roles, inventory counts, mirror bytes, coverage, and public release state are directly observable; Cautilus was not warranted.

## Healthy

- One AST parse per file now classifies dataclass fields, provenance-backed pytest fixtures, and `ast.NodeVisitor` dispatch methods.
- Source-scanned attention contracts are restricted to their declared path; same-named variables elsewhere remain review candidates.
- The sweep fell from 24 to 21 findings and from 9 to 2 review candidates. The two survivors are dynamic exports and remain visible for judgment.
- Three obsolete helpers and one unused setup constant had no checked-in consumers and were removed from both source and plugin mirrors.
- Ninety-one focused tests pass; the advisory itself remains about 8s and did not become a new slow gate.

## Weak

- Source-scanned membership is an exact path/name contract; future declarations require an intentional update.
- Static import provenance does not prove arbitrary runtime rebinding, so the advisory remains a triage aid rather than an oracle.

## Missing

- No general cross-module dynamic-export attribution explains the two remaining review candidates.

## Deferred

- Do not add a maintained dynamic-use registry or compatibility shims without an observed deletion error or recurring diagnosis cost.

## Advisory

- structural review result: artifact: `docs/design-north-star.md`; the next center is the existing advisory classifier, not another gate. Reversible deletion candidates stay with judgment and publication keeps distinct proof.
- prose review result: artifact: `skills/public/quality/SKILL.md`; trigger boundaries, progressive disclosure, helper ownership, dogfood pressure, and target-vs-ambient split remain healthy. Host references are intentional named-host/adapter seams, not evidence to hardcode hosts into portable logic.
- command: `check-python-lengths`; `scripts/setup_agent_docs_lib.py` remains near its warning limit at about 460/480 lines after this cleanup.
- inventory: 156 standing nested CLI test files remain ambient test-economics evidence, not a reason to weaken this slice's focused proof.

## Delegated Review

- Delegated Review: executed — diagnostic correctness and compatibility angles plus a separate counterweight ran read-only; two reviewers independently found an over-broad source-scan exemption, which was fixed and retested.
- Parent boundary fingerprints reported no worktree, index, or HEAD drift after every reviewer.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): focused fixtures are cheap; advisory and focused tests can run in parallel only outside mutation phases; broad and changed-line consumers remain distinct rather than duplicated proof.

## Commands Run

- Focused pytest: 91 passed across the selected files; focused ruff passed; `git diff --check` passed after removing trailing blank lines.
- Exact line proof: a mutant at direct-import alias binding made the new alias fixture fail, then the reverted implementation passed 20/20 advisory tests.
- Dead-code advisory: primary clean; sweep 21 total, 2 review candidates.
- Source/plugin sync completed; read-only release quality passed 81/81 in 76.4s. Release-boundary commands are recorded by the final closeout and release artifact.

## Recommended Next Quality Moves

- active retain role provenance and negative lookalike fixtures as the advisory pattern — capability_needed=credible attention; next_center=existing classifier; transformation=narrow classification; proof_boundary=focused fixtures plus live inventory; enforcement_posture=advisory.
- passive add dynamic-export attribution only after a deletion mistake or repeated manual triage cost because an unused registry would recreate the inventory it claims to simplify — capability_needed=explain ambiguity; next_center=observed consumer evidence; transformation=diagnostic enrichment; proof_boundary=real misses; enforcement_posture=no-gate.
- passive split near-limit setup helpers only when a coherent owner boundary appears because line-count-only extraction would add navigation cost — capability_needed=maintainability; next_center=owned behavior; transformation=module extraction; proof_boundary=call-site simplification; enforcement_posture=no-gate.

## History

- [Prior durable quality review](history/2026-07-14-open-issue-resolution-proof.md)
