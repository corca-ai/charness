# Issue #560 Resolution Critique
Date: 2026-08-09
Fresh-Eye Satisfaction: parent-delegated

## Reviewer Tier Evidence

- requested tier: `bounded-reviewer` typed subagent, read-only by definition
- requested spawn fields: inherited parent model and reasoning settings; no
  per-subagent model or effort override requested; both spawned unnamed
- host exposure state: host-defaulted
- envelope note: the spawn envelope exposed Read/Grep/Glob only, and both
  reviewers independently confirmed Bash/Edit/Write/Agent were absent
- application state: spawn tool accepted both reviewer agent ids; reviewer-tier
  application details are host-hidden
- Delivery state: findings-received

## Decision Under Review

Closing `#560` on the fixture built at `2a545fe9` — `tests/quality_gates/bundle_ready_world.py`,
a repo copy seeded so the bundle plan reads a repo that is bundle-READY, plus
ready-path tests for the bundle and closeout surfaces that run against it rather
than against `ROOT`.

`#560` reported two gaps. (1) After `#537`, the bundle ready payload and render
shape were owned only by tests requiring the LIVE worktree to be clean, so while
any blocker was live ZERO tests exercised the ready path — the state where a
ready-path regression is most likely to be introduced and least likely to be
noticed. (2) `test_final_bundle_private_error_and_render_branches`, a
monkeypatch test about error branches, still read the live manifest and reddened
for manifest-integrity reasons under a name about monkeypatched branches.

The build was committed with no delegated resolution critique. This critique is
the first delegated reviewer on it and the one the closeout floor requires before
the close call. A second round then read the repairs this one demanded.

## Failure Angles

- **Does the fix deliver gap 1, or only appear to?** A fixture that inherits live
  state would re-acquire the coupling under repair, one level up.
- **Does it deliver gap 2 by the remedy the issue proposed, or a different fix
  wearing gap 2's name?** The single most likely place a closeout over-claims.
- **A test asserting what it never established** — this repo's live class.
- **Call-site exposure (`#564`)** — a repair pinned only at its own function.
- **"By construction" as a name that outruns the thing named.**

## Round 1 — Findings

Ten findings. One BLOCKER, six DISCLOSE, three CLEAR. The blocker:

**`test_final_bundle_private_error_and_render_branches` had an assertion weakened
from `==` to `<=`, justified by a comment stating a mechanism that does not
exist.** The comment claimed the equality form "also asserts that the live
manifest is otherwise valid, which made this test redden for manifest-integrity
blockers under a name about monkeypatched error branches." But
`_current_manifest_blockers` reads no manifest CONTENT at all
(`scripts/final_bundle_preflight_lib.py:84-121` checks `ls-files`,
`is_file()/is_symlink()`, and two `git diff` calls). Under the test's `drift_git`
monkeypatch every git call is patched, so the only live input is `is_file()` and
the reachable outputs are exactly `{manifest_worktree_drift,
manifest_index_drift}` or `{manifest_not_regular}`. A superset was never
producible. The weakening decoupled nothing, cost the drift-code pin, and left a
false rationale on a proof surface — where the rationale is the durable part.

Verified independently before repair by reading the library, not by trusting the
reviewer.

## Repair, and Round 2

Restored the equality and rewrote the comment to the mechanism. Round 2 read the
repair and returned REPAIR-SOUND, confirming both factual claims independently
(no content read; `base_sha` genuinely from `premise.local_head_sha`, so exactly
two of the four codes were unproducible — "exactly right, not approximately
right"). It added that `manifest_not_tracked` is unreachable under the patch
because `args[0]` is exactly `ls-files`, and that the subset form failed in the
same live-state case anyway, so the repair is a strict improvement.

Round 2's two disclosures were applied: the comment now states the durable
mechanism instead of narrating the review, and it no longer says the fixture
manifest is "valid by construction" — it is decoupled from the live manifest's
GIT state, not from the live template's JSON shape, which the fixture seeds from.
Round-2 repairs are accepted-unreviewed per the two-round cap.

## Counterweight Pass

The angle that paid was gap 2 — "a different fix wearing gap 2's name" — and it
paid exactly where predicted. The real repair (retargeting `build_plan` at the
fixture manifest) was sound and load-bearing; a cosmetic change bundled beside it
carried a false explanation.

Angles that did NOT pay, recorded so the next reviewer does not re-run them:

- **A suspected dead fixture parameter was refuted by mutation.**
  `test_final_bundle_private_error_and_render_branches` declares
  `bundle_ready_repo` and appeared not to use it; deleting the parameter fails the
  test with `NameError` at the `build_plan` call. The hypothesis was wrong, not
  the code.
- **Gap 1 is genuinely delivered for the JSON payload on both surfaces.** The
  fixture's readiness is computed over the fixture tree, and the live repro class
  (an artifact under `charness-artifacts/`) cannot reach it because the repo copy
  excludes that tree.

## What The Closeout Must Not Claim

Not: "`#560`'s ready path is now owned by a fixture that is ready by
construction, and the monkeypatch test no longer reads the live manifest." Both
halves over-claim. The fixture is ready by COPYING the live tree and is
independent only of the artifact-path and manifest-git-state classes; the
monkeypatch test still reads `ROOT / MANIFEST` for its drift assertion, by
design, and now also carries a session-fixture dependency.

Not: any claim that the ready RENDER is covered while a blocker is live. It is
not — see the disclosures below.

## Disclosures Carried Into The Closeout

1. **The human ready-render is still uncovered in the blocked window.**
   `#560` named three ready-path owners; `test_final_bundle_cli_human_renderer_is_available`
   still runs against `ROOT` and takes the blocked branch. The fixture test uses
   `--json`. Ready-render coverage in that window is a hand-built dict, not the
   preflight's own output.
2. **The monkeypatch test gained a new live-state dependency with a wider
   fan-out.** A fixture BUILD error (renamed seed input, changed critique heading,
   git failure) now errors four fixture-dependent tests at once.
3. **"Ready by construction" is overstated as a test NAME.** The fixture inherits
   the live plugin mirror, `.agents/surfaces.json`, source tree, and five seeded
   artifacts. Honest in the module docstring, not in the name that gets quoted.
4. **Four of six assertions in the new ready-path test are entailed by
   `status == "ready"`.** Not a correctness bug, but they are not independently
   pinned and the closeout must not say they are.
5. **Call-site exposure remains on three items** (`#564`'s class):
   `_restamp_reviewed_binding`'s call site is pinned by a SOURCE-TEXT read, which
   proves the string appears, not that it executes; `_rewrite_shas`' list-element
   branch is unproven at both function and call site and is latent by its own
   admission; the seed-inputs `AssertionError` is diagnostic-only and unpinned.
6. **The commit's central figure is a recorded construction, not a standing
   gate.** No gate prevents a future edit from re-coupling the fixture tests to
   `ROOT`.
7. **The spec acceptance check is implemented in part.**
   `charness-artifacts/spec/2026-08-06-final-bundle-preflight-contract.md:121`
   asks for manifest identity, artifact/surface/mirror inventories, behavior
   channel, and ordered command set. The fixture test asserts `ready`, the mirror
   and critique inventories, and the closeout entry — not the others.
8. **Slice 3 of the predecessor goal recorded ONE delegated round on a
   verdict-logic slice** where its own acceptance asked for two. This critique is
   `#560`'s resolution critique; it is NOT that slice's missing second round, and
   the closeout must not imply otherwise.

## Boundary Ownership

- Producer: `_current_manifest_blockers` in `scripts/final_bundle_preflight_lib.py`, which decides which manifest blocker codes exist.
- Consumer: `test_final_bundle_private_error_and_render_branches`, which asserts the producer's output under a monkeypatched git.
- Owning surface: the consumer. The producer is unchanged by this repair and gained no new obligation.
- Verdict: single-surface

The repair lives entirely in `tests/quality_gates/test_final_bundle_preflight.py`
— one assertion and its comment. The producer (`_current_manifest_blockers` in
`scripts/final_bundle_preflight_lib.py`) is UNCHANGED: the blocker was a consumer
asserting less than the producer guarantees, plus a false statement about the
producer's behavior. Nothing moved across the boundary, and no new obligation was
pushed onto the producer, so there is no owner to move this to. The one
producer-side fact the repair depends on — that `_current_manifest_blockers`
never reads manifest content — is now stated at the consumer where the assertion
lives, which is where a future weakener will be standing.

## Reviewer Provenance

Fresh-eye satisfaction: parent-delegated

Two bounded read-only reviewers (`bounded-reviewer`), each a distinct agent
context from the parent and from each other, spawned unnamed. Parent-side
worktree+index fingerprint snapshot/verify around both windows:
`w-20260808T222049Z-3406314` clean, `w-20260808T222720Z-3417390` clean, so both
rounds' approvals are attributable. Neither reviewer had Bash; both stated that
limit, and round 1 listed the two evidence items it could not obtain. The parent
independently re-derived the blocker from source before repairing it.

## Will The Class Recur

Partly. The repair removes one false rationale, and the restored assertion is
mutation-proven. But disclosure 6 is the honest residual: nothing prevents a
future edit from re-coupling these tests to `ROOT`, so `#560`'s class is repaired
in instance, not gated. That is a deliberate scope choice, not an oversight, and
it belongs in the record rather than in a claim of prevention.
