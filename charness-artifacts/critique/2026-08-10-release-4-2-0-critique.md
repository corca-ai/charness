# Release critique — charness 4.2.0
Date: 2026-08-10
Target: 4.1.0 → 4.2.0 (minor)
Range: `0db174c4..c8ce7ea7` (pushed and hosted-readback confirmed before this critique)

## Scope

Seven commits. What a CONSUMING repo installs:

- `achieve` — new `recount_premise_state.py` CLI plus `recount_premise_lib` /
  `recount_residue_lib` (backlog re-verification), documented in
  `references/lifecycle-before.md`.
- `achieve` — `release_triggered` now recognises ecosystem-standard release
  surfaces instead of four of this repo's own script names, plus an
  adapter-declared `release_surface_tokens`.
- `issue` — a sixth closeout classification `consolidated` with its own floor,
  four backend readbacks, and a close-reason refusal in `issue_close`.
- `issue` — `issue_critique_observer` negation matching: 24-character window →
  clause-scoped, with object-negation excluded.
- `issue` — `issue_closeout_ledger_counts` gained `unif*` and dropped a fitted
  80-character clause cap.
- `quality` — two reference-data entries in `attention-state-visibility.json`.

Repo-local, NOT shipped: the `check-seed-fixture-budget` relevel in
`.agents/quality-adapter.yaml`.

## Bump rationale, stated because it is debatable

`minor`. The version policy reserves `major` for changed INVOCATION expectations
and FORCED MIGRATION. Three floors now fire where they did not, which is the
argument for `major`, and it loses on three grounds:

1. No invocation changed — same commands, same flags, same artifact shapes.
2. Each floor's published contract already claimed the scope; only the
   implementation was narrower. `achieve`'s coordination reference has always
   said "when the run touches a release surface (version bump / install
   manifest)". This is a repair, not a new demand.
3. No migration step is forced. Each escape is one line in a section that already
   exists, and each refusal message names it.

Precedent: `2026-07-26-v2.9.0-notes.md` shipped "`check-seed-fixture-budget` can
now fail your push" as a minor, leading with the warning. Same class, same
handling — and the notes for this release owe the same leading warning.

## Bounded fresh-eye critique

One bounded read-only reviewer, unnamed, boundary-verified clean via
`reviewer_boundary_fingerprint.py` (window `w-20260809T215942Z-1792976`,
verdict `clean`). Verdict: **SHIP-WITH-FIXES**, three fixes, all applied before
this artifact was written.

### Fix 1 (must) — the observer refused the commonest honest phrasing

MEASURED, then repaired. Clause-scoped negation demoted
`Fresh-eye satisfaction: parent-delegated bounded review found no blockers` to
`undelegated`, which REFUSES an issue close — with a message quoting a value that
contains `parent-delegated`. That is an arbitrary refusal at an irreversible
boundary, which is how a gate earns a route-around, and `found no blockers` is
how a reviewer writes a clean result.

Repair: `no` / `none` deny only when they sit BEFORE the token, where they negate
the review rather than its findings. `not`, `never`, `nothing`, `without`,
`failed to`, `unable to` still deny anywhere in the clause. Ten cases pinned in
both directions.

Honest note on evidence strength: the reviewer could not produce a
currently-checked-in field value this demoted — it was latent, not a measured
corpus regression. It was repaired anyway, because the phrasing is the default
one and the cost of being wrong is a blocked public close.

### Fix 2 (must) — the release notes must declare the newly-firing floors

Applied in the notes: each of the three, with its escape, led rather than
buried, plus an explicit statement that `consolidated` has not been exercised
end-to-end against a live tracker.

### Fix 3 (should) — `release_surface_tokens` was advertised and DEAD

The module comment told consumers to declare bespoke release surfaces in the
adapter; the resolver read them; the tests exercised `release_triggered`
directly — and `apply_coordination_floors`, the only production caller, passed no
repo root, so nothing a consumer declared was ever consulted. This is the same
silent inertness the token list itself was being repaired for, one layer up.

Repaired: `repo_root` threaded through, pinned by a test that asserts the floor
fires through `apply_coordination_floors` rather than through the library
function. Documented in `references/adapter-contract.md` beside
`discussion_deploy_vocab`. `consolidated` also gained a section in
`issue/references/closeout-discipline.md`, which `issue_plan.py` declares a
required read for it and which previously said nothing about it.

## Evidence the reviewer could not fetch, resolved by the parent

- `--reason` in `issue_close`'s close template is NOT new in this range; the diff
  adds only the consolidated-close refusal. No backend-version note is owed.
- `skills/public/issue/adapter.example.yaml` is untouched by this range, so its
  unknown-placeholder defect is pre-existing and out of scope. Filed as `#581`
  rather than folded in, so the notes do not claim a fix this version does not
  contain.
- `diff -r skills/public plugins/charness/skills` is byte-identical except
  `.gitkeep`. Generated-surface parity confirmed, not inferred.

## Open risks and non-claims

- `consolidated` ships UNEXERCISED end-to-end: no umbrella filed, no member
  closed against a live tracker. Its blast radius is contained — every new path
  is gated on `classification == "consolidated"`, so a consumer who never selects
  it cannot regress — and the first consumer who does gets a refusal-heavy path
  rather than a permissive one. Stated in the notes rather than gated.
- The chain check in the consolidation readback is near-inert against real
  chains: a consolidated destination is CLOSED, so check 2 catches what check 4
  claims to. Recorded, not repaired.
- `recount_residue_lib` hardcodes `charness-artifacts` and two `docs/` paths. It
  FAILS CLOSED for a consumer with a different layout (absent root becomes a
  channel gap, never a clean verdict), but its gap message says "check
  --repo-root", which misdiagnoses that consumer. Not repaired in this release.
- The observer's negation vocabulary remains English-only, stated in the module.
- No consumer repo was inspected. Every claim here is about this repo's tree and
  this repo's tests.

## Reviewer Tier Evidence

- Requested tier: bounded read-only fresh-eye reviewer (`bounded-reviewer`), unnamed and synchronous.
- Requested spawn fields: subagent_type=bounded-reviewer, run_in_background=false, no host addressing name.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer returned findings in-band, and `reviewer_boundary_fingerprint.py verify --window-id w-20260809T215942Z-1792976` reported `ok: true, verdict: clean` with empty drift, so the read-only envelope held.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated bounded review returned three fixes (two must, one should); all three were applied before this artifact was written, and the reviewer's two unfetchable evidence items were resolved by the parent and recorded above.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed: the reviewed input was the pushed commit range 0db174c4..c8ce7ea7 plus the worktree, cited by SHA in the Scope section rather than by packet digest. -->

## Boundary Ownership

- Producer: the `achieve` and `issue` public skills, which emit the closeout verdicts and the coordination-floor triggers this release changes.
- Consumer: a consuming repo's closeout run — the agent or maintainer whose goal flip or issue close these floors permit or refuse.
- Owning surface: the public skill packages under `skills/public/**`, mirrored to `plugins/charness/**`; the repo-local `.agents/quality-adapter.yaml` budget relevel is deliberately NOT part of the shipped surface.
- Verdict: owned-correctly
