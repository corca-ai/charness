# S4 — Track 2 Standing-Surface Audit (north-star overhaul)

Status: **complete (read-only).** Slice S4 of
`charness-artifacts/goals/2026-06-18-north-star-overhaul.md`. Date: 2026-06-18.

Success metric (goal Design lens): **learnability/discoverability**, not line
count. Compression = concept-separation/deletion (north-star P2), never
line-shaving to dodge a cap. The orthogonality lens: *is this surface the Nth
redundant way to say X, or orthogonal and composable?*

## Measurement

### Always-on host surface (PUSH)

- `AGENTS.md` = **70 lines**; `CLAUDE.md` → symlink to `AGENTS.md`. The whole
  always-on host instruction surface is this one 70-line file.
- It is already fairly lean, but carries two clear PUSH→PULL / de-duplication
  targets (below). The file *itself* states the principle it then violates:
  L31 "Keep this block short. Detailed routing belongs in installed skill
  metadata and `find-skills` output, not in a long checked-in catalog."

### Skill bodies pinned at the cap (own-concept bloat)

The binding constraint is `MAX_CORE_NONEMPTY_LINES = 160` (core = body minus
frontmatter and pressure-exempt sections). Bodies at/near the cap:

| core | left | skill |
| --- | --- | --- |
| 160 | 0 | retro |
| 159 | 1 | issue |
| 158 | 2 | impl |
| 157 | 3 | debug |
| 156 | 4 | achieve, create-skill |
| 155 | 5 | create-cli, hitl |
| 154 | 6 | find-skills |
| 153 | 7 | release (after S3 slim) |
| 152 | 8 | announcement |

**14 public bodies sit within 8 core lines of the cap.** This is the
"skill bodies pinned at the length cap" the north-star diagnosis named as the
*cost of meeting the recurrence with bespoke prose*. All share the same shape
(Bootstrap / Workflow / Output Shape / Guardrails / References); the bulk is in
Workflow + Guardrails (own-concept restatement), matching the Phase-0 finding
that bloat is ~68% own-concept, not boilerplate.

## Bloat classification (what to cut vs keep)

Per the Step-0 RESOLVED finding — *agents possess proxy-vs-behavior and most
task judgment intrinsically; more prose does not add it* — the cut target is
**intrinsic-judgment restatement**; the keep target is **non-intrinsic
repo-specific info** (exact commands, gate names, file paths, adapter contracts,
the irreducible observable lists at irreversible boundaries — north-star P3
exception).

### AGENTS.md — two PUSH→PULL / orthogonality targets

1. **Cautilus block (L11) — the single biggest PUSH→PULL win.** ~10 always-on
   lines enumerating cautilus surfaces, the planner-consult contract, the
   wrapper, and refusal rules. The **full detail already lives** in
   `skills/public/quality/references/cautilus-on-demand.md` (the canonical home),
   and the *safeguard is enforced by tooling* (`run_cautilus_eval.py` refuses
   without a justification log; the slice-closeout cautilus plan gates skill
   reviews). So the always-on surface needs only a 1–2 line pointer
   ("Cautilus is eval-only and ask-before-run; consult the planner and refuse
   `next_action:none` before any eval — see cautilus-on-demand.md"). **No
   safeguard lost** (tooling + reference hold it); ~8 always-on lines reclaimed.
2. **Skill Routing section (L17–31) substantially DUPLICATES Start Here** — the
   non-orthogonality the Design lens targets. find-skills bootstrap L19 = L8;
   gather routing L27 = L10; quality-validation routing L29 = L15. Two sections
   saying the same routing forces the "which block governs?" overhead the
   *capabilities-over-features* page critiques. Collapse the duplicated routing
   into Start Here (or a single short routing block), keeping only the
   non-duplicated nouns (L23 capability-noun → find-skills recommendation).
   ~6–8 lines reclaimed, **discoverability improved** (one obvious routing home).

   *Keep (non-intrinsic / safeguard):* the north-star pointer (L7), the
   Subagent Delegation override block (L33–41, a host-default override safeguard),
   Phase Rules (L43–49), and the Work Phase Map / Policy Index / Contract Map
   pointers (already PULL). The Contract Map (L64–70) is a catalog the file's own
   L31 principle would push to find-skills/handoff — a *secondary* candidate, but
   it is already pointer-only (low always-on cost), so defer unless S5 has room.

### Skill bodies — own-concept SRP-split (the long tail)

The 14 capped bodies each need a concept *separated* into a reference (not
line-shaved). The seam is consistent: a coherent Workflow sub-phase or an
over-long Guardrails list lifts to `references/`, leaving the body a sharp
worked example + the principle (north-star P2/P3). Highest-bloat pilot
candidate: **`retro` (160/160, at the cap)** — its Workflow (L46–115, ~70 lines)
and the `Auto-Retro Trigger` / `Expert Counterfactual Rule` sections are
separable own-concepts.

## S5 plan (proportional, two patterns demonstrated)

1. **AGENTS.md PUSH→PULL (primary — the always-on surface shrinks measurably).**
   Cautilus block → pointer; collapse Skill Routing duplication into Start Here.
   Target: ~70 → ~55 lines, **no boundary safeguard lost or made unread.** This
   is its own fresh-eye critique boundary (goal Boundaries): reviewer question =
   "was any safeguard lost or pushed into unread overflow?", not "fewer lines?".
2. **One SRP-split pilot (`retro`)** to demonstrate the own-concept compression
   pattern on the most-over-cap body, with the same fresh-eye check.

## Spin-out sizing (Operator Decision Queue revisit)

The **AGENTS.md PUSH→PULL + one SRP pilot** is a contained S5 slice that
satisfies the goal's Done criterion ("standing prose surface shrinks measurably
without losing a boundary safeguard"). The **remaining 13 capped skill-body
SRP-splits are a genuine long tail** — each is prompt-affecting (triggers a
dogfood/scenario review) and high-volume. **Recommendation: keep Track 2's
AGENTS.md PUSH→PULL + retro pilot in this goal (S5); spin out the
remaining-13-body SRP sweep as its own follow-up goal** (it is a mechanical,
repeatable, separable program — exactly a spin-out shape). This honors the
operator's "revisit spin-out at S4 sizing" trigger: the *core* Track-2
deliverable stays bundled; the *bulk sweep* spins out.

## Non-claims

- Read-only audit; classification by reasoning against the Step-0 finding +
  north-star P2/P3, not behaviorally re-run.
- The "intrinsic-judgment restatement vs repo-specific" split is a judgment call
  per line; S5's fresh-eye reviewer is the check that no repo-specific safeguard
  is cut as "restatement."
- Line-count targets above are direction, **not** the success metric
  (learnability is); they will not be hit by shaving.
