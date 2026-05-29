# Resolution Critique — issue #246

- **Issue**: corca-ai/charness#246 — handoff chunker tells the operator to `/goal`
  an unshaped auto-draft, skipping the achieve Before-phase.
- **Target reference**: code-critique (code + doc fix).
- **Decision artifact**: fix commit `f2dcc7d` + this close ledger.
- **Prepare packet consumed**: `charness-artifacts/critique/2026-05-29-034133-packet.md`.
- **Framing question**: what would let this class (a producer surfacing the
  run verb for an unshaped artifact) — and the siblings from causal review —
  come back?

## Prior context (causal review, cite-only)

Root cause = missing producer→consumer contract: the chunker reused the goal
artifact's `Activation:` field (`/goal`) as the operator's next move, surfacing
the run verb for an artifact it had just written with placeholder User
Acceptance / Agent Verification Plan / Slice Plan. Boundary honored by the fix:
the artifact's `Activation:` line stays `/goal` (a correct goal-artifact field);
only the operator next-move guidance changed. Detection gap: no gate asserted
producer next-move consistency with placeholder state. Sibling decision: no
other producer emits a run verb across a mandatory shape gap (proof: static
scan only).

## Angles (3 bounded fresh-eye reviewers, parent-delegated)

1. **Surface completeness / recurrence sweep** — found the fix consistent across
   chunked-routing.md step 4/5, SKILL.md, the drafter payload, and the plugin
   mirror, BUT flagged `docs/handoff.md:43` still showing `→ /goal` for the
   in-flight unshaped chunk-1 draft (same #246 pattern, in the chunker's own
   parse target).
2. **Contract correctness** — confirmed the new test is load-bearing (reverting
   to bare `/goal` fails it); raised portability of the `/achieve @file` token
   and whether achieve guarantees a draft-status→Before-and-stop branch.
3. **Cross-surface consistency** — independently flagged `docs/handoff.md:43`
   (HIGH); confirmed terminology consistency, plugin-mirror parity, and that the
   shape-before-activate contract is documented (not code-only); judged no
   reciprocal achieve edit forced.

## Counterweight triage (four bins)

- **Act Before Ship**: reconcile `docs/handoff.md:43` to route through
  `/achieve` (shape) before `/goal` (activate). DONE in the fix commit set.
- **Bundle Anyway**: none (the one cheap edit was promoted to Act-Before-Ship).
- **Over-Worry**: `/achieve @file` literal token is the established repo
  convention (matches `/goal @file` usage throughout SKILL.md/references), so it
  is not a new portability sin; the dual-command payload is self-mitigated by the
  `next_step` prose + the reference instructing the agent to surface `next_step`.
- **Valid but Defer**: add an explicit draft-status→Before-phase branch to
  `skills/public/achieve/references/lifecycle.md` so the shape-and-stop behavior
  is guaranteed rather than inferred. Current inference ("read it first and
  continue its lifecycle" + "Start from prose, not an already perfect `/goal`")
  is sound, so this is a separate achieve-lifecycle hardening, not a #246 blocker.

## Decision and proof

- **Decision**: ship after the Act-Before-Ship `docs/handoff.md` reconcile
  (applied); over-worry items dropped; the lifecycle-branch item deferred.
- **Proof**: deterministic local gates — full repo-python pytest (1664 passed,
  4 skipped), validate_skills / validate_packaging(_committed) / check_doc_links
  / check-markdown / check-secrets / validate_cautilus_proof / ruff /
  validate_public_skill_{validation,dogfood} / validate_rca_ledger, plus the new
  `test_cli_next_step_routes_through_achieve_before_phase`. No live/provider
  proof was run (not applicable to this doc/payload change).

## Fresh-Eye Satisfaction

parent-delegated (3 angle subagents + 1 separate counterweight subagent).
