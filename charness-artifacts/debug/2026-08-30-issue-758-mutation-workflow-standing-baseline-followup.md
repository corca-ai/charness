# Issue #758 Standing-Baseline CI Follow-up Debug
Date: 2026-08-30
Status: diagnosed; repair deferred by explicit operator proof-policy amendment

## Problem

After the typed-content referent repair passed local full quality and provider
Quality Core, Mutation Tests run `33297693085` still failed the artifact-referent
corpus test before mutation execution. The workflow's mutation result remained
unmeasured.

## Correct Behavior

When a repo-owned gate judges whether a Git commit citation is durable, identical
tracked bytes at the same `HEAD` should not receive different verdicts merely
because an authoring clone retains an unrelated local ref or object. This is the
debugged invariant; the operator later removed hosted Mutation Tests from Goal
#744's completion proof and did not authorize this follow-up implementation.

## Observed Facts

- The run checked out exact head
  `15527e8b74348c71692afd1be290c7b940a94391`.
- `Select mutation sample` ran 8,534 passes, 6 skips, and one failure in 800.63s.
  `Run mutation` was skipped; the provider comment is
  https://github.com/corca-ai/charness/issues/758#issuecomment-5467284741.
- Local pre-push full quality on the exact commit passed the corpus gate; provider
  Quality Core run `33297678534` also passed.
- Mutation Tests already uses `actions/checkout` with `fetch-depth: 0`. Checkout
  depth was therefore a valid disconfirmer but not the remaining workflow defect.
- A depth-1 clone of the exact `HEAD` reported many valid historical ancestors as
  missing. After `git fetch --unshallow`, those disappeared and only two findings
  remained: Goal Draft lines 196 and 199, both token `d309412d6`.
- `d309412d6` exists in the authoring clone on a divergent local `main`, is not an
  ancestor of the published `HEAD`, and is not advertised by any provider ref.
  The frozen Goal Draft explicitly calls it a local commit and excluded evidence
  context rather than publication authority.
- The current resolver uses `git cat-file -t`, so the authoring clone's local
  object makes the gate pass while the provider clone correctly cannot find it.

## Reproduction

1. Run the corpus gate at exact `HEAD` in the authoring clone: it is clean because
   `git cat-file -t d309412d6` succeeds through a divergent local ref.
2. Clone provider `main` at the same `HEAD` with full history and run the same
   gate: it blocks only Goal Draft lines 196 and 199.
3. Confirm `git merge-base --is-ancestor d309412d6 HEAD` returns nonzero and
   `git ls-remote origin` advertises no ref containing that object.

## Candidate Causes

- Rejected: a remaining typed review digest. The only full-history findings are
  the explicit local Git commit.
- Rejected: the real workflow is shallow. Its checked-in checkout already sets
  `fetch-depth: 0`.
- Rejected: export materialization changes the scanned corpus. The same tracked
  bytes reproduce in a full provider clone.
- Confirmed: object existence is being treated as published-history durability.

## Hypothesis

- Falsifiable claim: a full provider clone and the authoring clone disagree only
  when the cited object is present outside published `HEAD` history; comparing
  `cat-file` with `merge-base --is-ancestor <sha> HEAD` identifies that exact
  difference.
- disconfirmer: deepen the exact shallow clone without changing tracked bytes;
  if every finding disappears, local-only object residue is not the cause.

## Verification

- Result: confirmed. The shallow/deep probe removed ancestor-transport findings;
  the full-history residual is exactly `d309412d6` at two frozen sites. Local
  object existence is true while published-HEAD ancestry and provider ref
  advertisement are false.
- Goal disposition: the operator explicitly approved ignoring Mutation Tests for
  this Goal to remove the long serial proof loop. No hosted mutation success is
  inferred from this diagnosis.

## Root Cause

The artifact-referent resolver equates “this clone has a commit object” with
“this revision's published history durably supplies that commit.” An authoring
clone retained `d309412d6` through a divergent local branch, so local quality
passed. A clean provider clone at the same tracked revision lacked the excluded
object and failed. The workflow exposed an environment-dependent gate verdict;
it did not expose a missing `fetch-depth` setting.

### Five Whys

1. Why did Mutation Tests stop before mutation? The standing corpus gate failed.
2. Why did only CI fail? CI lacked `d309412d6`; the authoring clone retained it.
3. Why did local quality accept that difference? The resolver asks object
   existence, not reachability from the reviewed `HEAD`.
4. Why was the object local-only? It belonged to excluded shaping history which
   the frozen draft records as context, not provider publication authority.
5. Why did the first local proof miss the class? It tested the same long-lived
   clone whose residual object supplied the accidental proof.

## Invariant Proof

- Invariant: identical tracked bytes and `HEAD` should produce the same durable
  commit-referent verdict regardless of unrelated local refs.
- Producer Proof: the frozen Goal Draft explicitly types `d309412d6` as local,
  excluded context.
- Final-Consumer Proof: the same-byte full provider clone blocks the two sites;
  the authoring clone passes solely because `cat-file` sees the extra object.
- Interface-Shape Sibling Scan: eight pre-cutoff worker commits in the corpus are
  also present only outside current `HEAD`; they remain reported under the
  existing dated grandfathering policy and were not changed.
- Non-Claims: no mutation ran, no mutation score exists, and the referent resolver
  was not repaired in this Goal.

## Detection Gap

- Mutation workflow standing baseline | ordinary local quality reused a clone
  with extra refs and objects | if reopened, the smallest structural check is a
  temporary repository where a side-branch-only commit exists but is not
  reachable from `HEAD`.

## Sibling Search

- cross-file: `scripts/artifact_referents.py` resolver semantics versus
  `.github/workflows/mutation-tests.yml` checkout history.
- Same layer: `git_commit_exists` / `_cached_commit_exists` — same class,
  diagnosed and intentionally deferred.
- Corpus sibling: eight worker-commit citations before the enforcement cutoff —
  already reported, nonblocking, and outside this Goal's change.
- Workflow sibling: Mutation Tests checkout — full history already configured;
  no workflow change required.
- Consumer repositories: out of scope. Their agents own Git/topology composition.

## Seam Risk

- Interrupt ID: issue-758-shallow-history-2026-08-30
- Risk Class: none
- Seam: authoring-clone object database to provider-main artifact-referent gate.
- Disproving Observation: local full-history green and exact provider baseline red.
- What Local Reasoning Cannot Prove: a hosted mutation result after any future
  resolver repair.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: `charness-artifacts/goal-runs/744/amendments/2026-08-30-ignore-mutation-test-proof.md`

## Prevention

If this gate class is reopened, bind Git durability to `HEAD` reachability and
handle any frozen local-only context through an exact structured record rather
than a prose regex or cutoff change. That implementation and its proof-surface
review are deliberately not part of Goal #744 after the operator removed
Mutation Tests from the Goal's completion proof.
