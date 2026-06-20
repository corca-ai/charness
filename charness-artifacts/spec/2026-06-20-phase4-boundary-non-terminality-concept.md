# Concept Spec — Phase 4: Non-terminality + Portability at the Remaining Irreversible Boundaries

Status: **locked** (S0 gating artifact — bounded fresh-eye gating critique
PASS-WITH-CONDITIONS, three blockers folded 2026-06-20, §9). Implementation
(WS-1) may proceed.
Created: 2026-06-20
Goal: `charness-artifacts/goals/2026-06-20-north-star-phase4-boundary-non-terminality.md`
Provenance (this S0 pass): direct code reads of
`skills/public/release/scripts/publish_release_execute.py`,
`publish_release_post_create.py`, `release_issue_closeout.py`;
`skills/public/issue/scripts/issue_verify_closeout_body.py`;
`scripts/proof_mismatch.py`; `skills/public/hotl/references/ledger-and-dispositions.md`;
`skills/public/achieve/scripts/goal_artifact_closeout_delegation.py`,
`goal_artifact_discussion.py`; `skills/public/achieve/references/lifecycle.md`,
`goal-artifact.md`; the pinned tests `test_goal_artifact_blocked_matrix.py`,
`test_goal_artifact_closeout_delegation.py`, `test_workflow_safety_docs.py`,
`test_proof_semantics_adapter.py`; plus the leak greps over
`skills/ scripts/ tests/ docs/ plugins/`.
Doctrine: `docs/design-north-star.md` (P1–P5). Template + proven pattern:
`charness-artifacts/spec/2026-06-20-per-unit-disposition-concept.md` (the locked
rung-1/rung-2 contract WS-1/WS-2 reuse) and the overhaul-sweep goal's S1/S2.

This spec is concept-first. It fixes the shared abstraction and the per-surface
contracts; exact diffs / test bodies are the job of the impl slices and are left
as named probes here, not pre-written.

---

## 1. The one concept (reused verbatim, not re-derived)

A **per-unit disposition** is the record a lifecycle transition leaves for each
unit it touches, as two rungs (the locked Phase-3 abstraction —
`2026-06-20-per-unit-disposition-concept.md` §1):

- **Rung-1 — presence/form floor (deterministic, P5-legitimate).** Refuses a
  transition whose record is **silent or malformed** on the per-unit obligation.
  It checks the record *contains* the required shape; **never** whether the
  content is honest. It may force the question; it may not declare completion.
  **There is no terminal green.**
- **Rung-2 — distinct-channel observer (human-audited, P4).** Judges the
  *honesty* of each unit's disposition through an evidence channel **distinct
  from** the proxy the transition rode in on. Re-reading the same proxy is not
  confirmation. Its human sign-off — not a gate's green — is the stop condition.

> **The binding invariant (never relaxed):** a rung-1 floor that **greens on
> self-classification** re-grants the terminal trust the cluster abused. Rung-1
> refuses *silence/malformation* and nothing more; *honesty* is always rung-2's
> job. "All units present ⇒ done" is the #386 anti-pattern and is forbidden. A
> typed non-`verified` disposition satisfies rung-1 **exactly as** a confirmation
> does (render-not-declare) — the obligation is to render the verdict-or-
> disposition per unit, never to gate the transition on an aggregate "all
> confirmed."

Success = **a closed escape path + a clearer / more portable concept**, never
"fewer lines / fewer gates" (a north-star failure signature). Phase 4 extends the
already-validated abstraction to three boundaries Phase 2/3 left untouched; it
invents no new abstraction.

---

## 2. WS-1 — release publish non-terminality (the real charness-owned boundary)

### The open escape (verified in code)

`publish_release_execute.py:_publish_and_finalize` (lines 156–204):

1. `git tag` + `git push` (line 156–157).
2. `create_release` — the irreversible external mutation (line 159).
3. `verify_release_visible(...)` → `release_view_result` → **`gh release view`**,
   bounded retries on the **same** channel (`publish_release_post_create.py:40-58`).
4. **`release_verified = release_verify_result.returncode == 0`** (line 163) — a
   single same-channel returncode proxy.
5. `if not release_verified:` write a recovery artifact + `fail_after_post_create_verification`
   (exit nonzero) — fires **only** when the release is not even visible (lines 173–186).
6. else: **`ensure_release_issues_closed(...)`** (line 187) — the irreversible
   issue-close boundary — runs gated **only** on the line-163 proxy.

The pre-publish critique gate (`release/references/closeout-critique-gate.md`)
runs *before* the published state exists; the only post-publish check is the
**same `gh release view` channel re-read**. There is **no distinct-channel
observer and no per-surface verdict record** between "release visible per gh" and
"close the GitHub issues." That single same-proxy returncode is exactly the P4
re-examination failure at an irreversible boundary.

### The wire (what WS-1 lands) — additive, not a delete-migration

- **Rung-2 distinct-channel observer** (new helper in
  `publish_release_post_create.py`, e.g. `confirm_release_via_distinct_channel`):
  after `release_verified` is true, confirm the published release through a
  channel **distinct from `gh release view`**. Default distinct channel = an
  **HTTP fetch of the public `expected_release_url`** (different transport,
  different auth path, observes the *public* artifact, not the `gh` CLI's view);
  an adapter may declare an install/download probe instead. The observer records
  one of:
  - a **distinct-channel confirmation** (status + the evidence: HTTP status, a
    body/asset fingerprint, the URL fetched), or
  - a **typed non-`verified` disposition** when the distinct channel cannot run
    (`skipped — <reason>`, or a HOTL status such as `blocked-needs-operator` /
    `blocked-needs-capability`). Never a second `gh release view` standing in for
    confirmation; never a silent green.
- **Rung-1 per-surface presence floor** (deterministic): **before**
  `ensure_release_issues_closed`, refuse the transition when the payload carries
  **no** per-surface behavioral-verdict record (neither a distinct-channel
  confirmation nor a typed non-`verified` disposition). Presence/form only — it
  refuses *silence*. It does **not** declare the release "verified": the line-163
  `gh` proxy stays **necessary-but-not-sufficient**, and a typed disposition
  passes the floor exactly as a confirmation does (render-not-declare).
- **Rung-2 honesty (human audit)** is a **durable post-publish disposition
  review** of the recorded distinct-channel observable + any typed disposition.
  **It is NOT the existing release critique gate** (gating-critique Blocker 1,
  code-verified): `enforce_release_critique_gate`
  (`release/references/closeout-critique-gate.md`) runs **pre-publish** — "before
  any version bump… A refusal here leaves the working tree untouched" — so it
  cannot audit a state that does not yet exist. The post-publish observer is the
  release's durable closeout artifact (`charness-artifacts/release/latest.md` +
  the recovery/closeout record), audited by a human / the next session's
  disposition review. WS-1 makes rung-1 *demand the record exists* so that human
  observer has captured observables to audit.

**Non-terminality check (LOAD-BEARING — gating-critique Blocker 1, folded).** The
irreversible issue-close (`ensure_release_issues_closed`,
`release_issue_closeout.py:87-131`, which posts a manual-fallback `gh issue
close`) runs **inside the same automated `_publish_and_finalize` call** at
`publish_release_execute.py:187`; the human rung-2 audits **afterward**. So the
rung-1 floor's presence-only nature is not decorative:

> **Fixed (F2a):** issue-close advances on **rung-1 record-presence only** — a
> distinct-channel confirmation **or** a typed non-`verified` disposition pass it
> *equally*. The automated distinct-channel confirmation (HTTP-200 / asset
> fingerprint) is a **recorded observable for the human rung-2 audit, NEVER an
> automated gate-condition that advances issue-close.** Wiring an automated
> "distinct-channel-confirmed ⇒ proceed" would relocate the #386 / P4
> re-examination anti-pattern (`design-north-star.md:93-94`) onto a new channel —
> forbidden. A typed `skipped`/`blocked` disposition makes the gap **legible**
> (recorded, not silent) for the rung-2 sign-off.

The current `release_verified` proxy is **supplemented, not deleted** — WS-1 is
*additive* (like the issue-closeout floors), so the migration-discipline "delete
old surface" step is **N/A by design**; the "seeded-proof-before-relying-on-the-
floor" step still binds.

### WS-1 proof (local, by goal contract)

Seeded published-release fixture (a fake backend where `create_release` succeeds
and the distinct channel is controllable):
- a payload **silent** on the per-surface verdict **FAILS the rung-1 floor before
  `ensure_release_issues_closed` runs** (the replacement catches the seeded
  silent case);
- a payload whose only post-publish evidence is the same `gh release view`
  re-read (no distinct channel) **does not pass** the rung-1 floor as a
  confirmation — it must carry the distinct-channel record or a typed disposition;
- a distinct-channel confirmation **or** a typed non-`verified` disposition
  **PASSES** rung-1;
- normal publication still records verified public release state; the existing
  `test_release_publish.py` post-create-verification tests stay green.
- **No live GitHub release this run** (Operator Decision Queue; local seeded proof
  is the closeout default; any live run is operator-approved + phase-scoped).

Reuse: `charness-artifacts/spec/release-post-create-verification-suppression.md`
(the partial post-create verification implementation) is genuinely extensible —
its `verify_release_visible` / recovery-artifact scaffolding is where the
distinct-channel observer and the rung-1 record attach.

---

## 3. WS-2 — Direction-3: refuse-on-undispositioned-HOTL-entry on `verify-closeout`

### The gap (verified in code)

`issue_verify_closeout_body.py` got the rung-1 **behavioral-verdict** floor
(`evaluate_behavioral_verdict`, lines 224–258) and the **AI-provenance** floor
(`evaluate_ai_provenance`, 261–273) in the prior goal's S1. `evaluate_behavioral_verdict`
accepts, per closed issue, a `Behavior #N:` line whose *value* may **name** a
HOTL status — but it enforces only that *a substantive line exists per issue*. It
**reads no HOTL carrier disposition**: a carrier that lists a HOTL loop **entry**
without one of the typed HOTL statuses (or `local-only-by-contract`) is not
refused. That is the second #386 consumer — an undispositioned HOTL entry can
ride `CLOSED` to "done."

### The wire (what WS-2 lands) — reuse the `proof_mismatch.py` template

`scripts/proof_mismatch.py` is the structural template (repo-root `scripts/`, not
`skills/public/issue/scripts/` — the goal's implied path was loose; the file is
real and is *already* folded by both achieve and issue closeout via
`apply_proof_mismatch_floor`). Its shape WS-2 copies:

- **Presence-gated, no over-fire, no date gate needed.** `proof_mismatch` fires
  only on a present `## Proof Ledger`; WS-2's floor fires only when the carrier
  **presents a HOTL entry/section** (the carrier-body per-issue HOTL disposition
  block). A carrier with no HOTL entry is inert — internal-only / no-live closes
  stay exempt, exactly like the source-preservation floor's "externally sourced
  iff a `Source origin:` marker is present."
- **Per-entry typed-disposition floor.** Each presented HOTL entry must carry one
  of the typed HOTL statuses **or** `local-only-by-contract`; an entry present
  **without** one is refused (the `_GAP_DISPOSITION_KINDS` analogue). The HOTL
  status vocabulary (`hotl/references/ledger-and-dispositions.md` §Statuses):
  `verified`, `blocked-needs-operator`, `blocked-needs-capability`,
  `deferred-by-operator`, `issue`, `accepted-risk`, `out-of-scope` — plus
  `local-only-by-contract`. **This typed vocabulary becomes *newly enforced* by
  WS-2's floor** (gating-critique Blocker 2, code-verified): today
  `local-only-by-contract` lives **only in the `evaluate_behavioral_verdict`
  docstring** (`issue_verify_closeout_body.py:231`) — **no code recognizes it as
  a typed token**; the existing floor "passes" it only incidentally because it
  accepts any substantive `Behavior:` value. WS-2's floor is the **first typed
  HOTL-status recognizer** — an impl slice must not assume a recognizer exists.
- **Presence/form only — rung-1.** The floor refuses an **undispositioned** entry
  (silence/malformation on the typed status). Whether the chosen disposition is
  *honest* is the **resolution critique** (rung-2 — the doctrine already mandates
  it; no new rung-2 is added here).
- **Adapter-portable.** The HOTL ledger schema/path is adapter-owned
  (`ledger-and-dispositions.md` §Ledger tooling ownership). The floor reads the
  **carrier-body** per-issue disposition (presence/form), **never** a fixed ledger
  file path. It **extends the `evaluate_behavioral_verdict` family** in
  `issue_verify_closeout_body.py` — one more sibling evaluator, not a new parallel
  gate where one suffices.
- **Closest in-file structural template (gating-critique Blocker 3):**
  `evaluate_source_preservation` (`issue_verify_closeout_body.py:159-194`) is a
  *stronger* precedent than the cross-file `proof_mismatch.py` for the exact shape
  WS-2 builds — it is **presence-gated on a carrier-body marker** ("externally
  sourced iff a substantive `Source origin:` marker is present"), requires **one
  of a typed form-set**, reads the **carrier body never a path**, and is a
  sibling evaluator. WS-2 mirrors its `external_sourced`/`forms_present`/`missing`
  structure with the HOTL-entry/typed-status/undispositioned analogue;
  `proof_mismatch.py` remains the reference for *degrade + fail-closed*.
- **Degrade + fail-closed**, mirroring `proof_mismatch`: an unreadable/ambiguous
  HOTL block is treated as needing a disposition rather than passing silently.

### WS-2 proof (local)

Seeded carrier with an **undispositioned HOTL entry** (an entry present, no typed
status, no `local-only-by-contract`) **FAILS `verify-closeout` before `CLOSED`
can green**; the same carrier with a typed HOTL disposition (or
`local-only-by-contract`) **PASSES** (render-not-declare). A carrier with **no**
HOTL entry is inert (existing `bug`/`feature` closes unaffected). New locked
tests under `tests/quality_gates/`; the locked `test_issue_closeout_verifier.py`
stays green.

---

## 4. WS-3 — prod-apply portability deleak (charness owns NO prod-apply boundary)

The portability axis: `apply` / `restart` / `deploy` / `applied-restarted` /
`ceal-dev` are **consumer-axis** values, NOT charness singletons. WS-3 makes the
irreversible-external-write boundary **vocabulary-neutral** and
**adapter-fillable**. This is portability deleak, **not** boundary-hardening
(charness owns no prod-apply boundary to harden).

### 4a. Tier-1 — remove the `ceal-dev` consumer-NAME leak

**Leak sites (deleak these — replace with vocabulary-neutral, adapter-named lane
examples):**

| # | Site | Form |
| --- | --- | --- |
| L1 | `skills/public/achieve/references/lifecycle.md:342` | prose "(a repo-preauthorized `ceal-dev` apply/restart)" |
| L2 | `skills/public/achieve/references/lifecycle.md:353` | example lane `- Lane: ceal-dev apply/restart \| …` |
| L3 | `skills/public/achieve/references/goal-artifact.md:219` | example lane `- Lane: ceal-dev apply/restart \| …` |
| L4 | `skills/public/achieve/scripts/goal_artifact_blocked_matrix.py:7` | docstring "(e.g. a repo-preauthorized ``ceal-dev`` apply/restart)" |
| L5 | `tests/quality_gates/test_goal_artifact_blocked_matrix.py:38` | fixture `_RUNNABLE_LANE = "- Lane: ceal-dev apply/restart \| …"` |
| L6 | `plugins/charness/skills/achieve/...` mirror copies of L1–L4 | regenerated by `sync_root_plugin_manifests.py` |

**Protected `ceal-dev` sites (do NOT touch — these are the seam working as
intended; stripping them deletes a guard or a legitimate adapter example):**

| # | Site | Why protected |
| --- | --- | --- |
| P1 | `docs/runtime-capability-contract.md:117` | `slack.ceal-dev` profile-id capability-resolution **example** |
| P2 | `docs/capability-resolution.md:140,143` | `slack.ceal-dev` capability-resolution **example** |
| P3 | `tests/charness_cli/test_capability_resolution.py:35,37,56,66,68` | `slack.ceal-dev` capability-resolution **tests** |
| **P4** | **`tests/quality_gates/test_proof_semantics_adapter.py:244`** | **`ceal-dev` inside `test_core_module_is_domain_blind()`'s `forbidden` tuple — a domain-blindness GUARD asserting the portable core contains NO `ceal-dev`. Removing it deletes a guard. (NEW: missed by the plan critique's protected set.)** |
| P5 | `docs/public-skill-dogfood.json:76` | a frozen **historical dogfood log** of issue #385's scenario — records what happened at the time, not live doctrine a new consumer reads as guidance. Out of the acceptance grep scope (`skills/ scripts/ tests/`). Leave as history. |

**Acceptance-grep correction (S0 → goal):** the goal's User-Acceptance grep
`grep -rn "ceal-dev" skills/ scripts/ tests/` should, after WS-3a, return **two
protected classes**, not one: (i) `tests/charness_cli/test_capability_resolution.py`
(`slack.ceal-dev`), AND (ii) **`tests/quality_gates/test_proof_semantics_adapter.py:244`**
(the domain-blindness guard). The goal's acceptance text names only class (i); S0
adds class (ii) so WS-3a does not over-fire and strip a guard.

**Neutral replacement shape (probe finalized in WS-3a):** the lane examples
become consumer-agnostic — e.g. `- Lane: instance apply/restart | classification:
preauthorized-runnable | …` or an explicitly adapter-named placeholder
`- Lane: <adapter deploy lane> | …`. The *operational verbs* "apply/restart" in a
**lane-example** are illustrative of the boundary class and may stay (they are
not a consumer *name*); the **consumer name `ceal-dev` must go.** WS-3a removes
the name; the verb-vocabulary deleak is WS-3b's job (§4b).

### 4b. Tier-2 — neutralize the consumer-VERB vocabulary

**(b-i) Rename the `applied-restarted` closeout-taxonomy token → a neutral term.**

Sites:

| # | Site | Form |
| --- | --- | --- |
| T1 | `skills/public/achieve/references/lifecycle.md:809,813` | taxonomy level 4 definition + cross-ref |
| T2 | `skills/public/achieve/references/goal-artifact.md:266,277` | example + vocabulary list |
| T3 | `skills/public/achieve/scripts/goal_artifact_closeout_delegation.py:21,40` | docstring + `CLOSEOUT_STATE_LEVELS` tuple |
| T4 | `docs/prescribed-skill-closeout-contract.md:227` | governing contract-doc vocabulary list **(NEW: missed by the plan)** |
| T5 | `tests/quality_gates/test_goal_artifact_closeout_delegation.py:101` | fixture token (incidental — gate is token-agnostic) |
| T6 | `plugins/charness/skills/achieve/...` mirror copies of T1–T3 | re-synced |

**Decision: straight rename, NO grandfathered alias.** Verified-safe because:
- the gate `_item_resolved` (`goal_artifact_closeout_delegation.py`) is
  **resolution-based and token-agnostic** — it never reads the literal token (it
  matches `verified` / `skipped:` / `issue #N`);
- the drift test `test_closeout_state_levels_are_documented_in_lifecycle`
  (`:213`) asserts **membership** (each `CLOSEOUT_STATE_LEVELS` member appears in
  lifecycle.md), not the literal — a synced rename of constant + doc passes;
- an **existing consumer goal artifact** that literally wrote `applied-restarted —
  verified: …` still **resolves on `verified`**, so no artifact breaks → the
  grandfathered-alias machinery the goal hedged about is **unnecessary insurance**
  (the plan critique's over-worry, confirmed). Adding an alias would be the
  over-engineering the migration discipline warns against.

**Neutral token constraint:** the goal's success criterion (c) names `apply` /
`restart` / `deploy` as words that should **leave the portable core**, so the
replacement token must **not** reintroduce any of them. Proposed: **`instance-synced`**
("the running instance is synced to the change" — parallels `pushed-ci`: surface +
past-participle, no apply/restart/deploy verb). The exact token is a naming call
the **gating critique may adjust**; S0 locks the *constraint* (no apply/restart/
deploy) + the *decision* (straight rename, all 6 sites in sync, mirror re-synced)
and proposes `instance-synced` as the default so impl is mechanical.

**(b-ii) Make `goal_artifact_discussion.py` detection vocabulary adapter-provided.**

Sites: `goal_artifact_discussion.py:18` (`production_or_live_proof` trigger) and
`:22` (`irreversible_side_effect` trigger) hardcode the English deploy-verb
alternation `apply/restart|restart|deploy` inside the portable trigger regex.

**Decision (S0 recommendation — gating critique to confirm): Option A,
behavior-preserving adapter seam.** Keep the **generic, charness-neutral**
concepts (`prod`/`production`, `live proof`, `irreversible`, `external side
effect`, `production contact`, `real github lookup`) as the portable trigger
default, and move the **consumer-deployment-verb** alternation (`apply/restart`,
`restart`, `deploy`) into an **adapter-provided vocabulary slot with the current
English words as the default**. No adapter → byte-identical trigger behavior (no
guard lost); a non-ceal / differently-worded / non-English consumer declares its
own deploy-verb vocabulary. This is the same "ship a default, adapter overrides"
pattern as `proof_semantics_adapter` and honors the north-star's *"adapter-named,
vocabulary-neutral seam"* — the consumer-verb axis becomes **explicit and
fillable**, not hardcoded-only.

> **Rejected — Option B (drop the English defaults entirely; deploy-verbs only via
> adapter).** Cleaner against the literal "deploy leaves the core" phrasing, but it
> **loses a guard** for an unconfigured consumer (a goal that only says "deploy"
> stops triggering) — a north-star failure signature (the goal's own Non-Goals
> forbid "losing a guard"). The honest reading of success criterion (c) is "leave
> the **hardcoded-only** core ⇒ become adapter-fillable," which Option A satisfies.

**(b-iii) Rename the `Post-Apply Checkpoint Classification` heading.**

Sites: `skills/public/achieve/references/lifecycle.md:540` (the `###` heading) +
`:278` (cross-reference) + **`tests/quality_gates/test_workflow_safety_docs.py:14`**
(pins the literal heading string `"Post-Apply Checkpoint Classification"` —
**NEW: missed by the plan; the rename MUST update this test in the same slice**) +
mirror copies. Neutral target (probe): `Post-Checkpoint Commit Classification` or
`Runtime-Checkpoint Commit Classification` — the section is about classifying
commits *after a behavioral checkpoint* as `runtime-affecting` / `test-only` /
`audit-doc-only`; "Apply" is the consumer verb to drop. The body's "live apply,
restart, deployment smoke" examples (line 542) may stay as *illustrative
examples* (not a hardcoded singleton) — S0 keeps them; gating critique may flag.

### 4c. WS-3 migration discipline (binding, every surface)

Name failure-mode → land replacement → **seeded-instance proof** the replacement
catches the seeded case → only then delete the old surface + a one-line rollback
ref. Stage surface-by-surface. **Every WS-3 slice re-syncs the `plugins/` mirror
via `sync_root_plugin_manifests.py` BEFORE verify** — the `staged-plugin-mirror-drift`
gate fails an unsynced rename (plan-critique blocker C). The pinned producer tests
(`test_goal_artifact_producers.py`), closeout-delegation tests, the blocked-matrix
fixture test, and `test_workflow_safety_docs.py` must stay green.

**Honest defer-with-cause hatch:** if any WS-3 surface proves genuinely
contract-pinned or the rename genuinely lossy, land what is safe + defer the rest
with cause. S0's verdict from the code reads: **no genuine contract-pin or lossy
surface found** — WS-3a and WS-3b(b-i/b-iii) are mechanical (token-agnostic gate,
membership drift test, incidental fixtures, doc + test updates in-slice);
WS-3b(b-ii) is the one genuine *design* call (Option A vs B), locked above. So
the hatch is **insurance, expected unused** — but it stays open for any surface a
slice discovers to be load-bearing in a way this S0 pass missed.

**Risk ordering (plan critique, confirmed):** WS-3a (Tier-1) is the **riskier**
slice (it can over-fire — strip a protected `slack.ceal-dev` or the P4
domain-blindness guard — or under-clean — miss the `test_goal_artifact_blocked_matrix.py:38`
fixture), **not** WS-3b. The protected-set table (§4a) and the acceptance-grep
correction exist to keep WS-3a from over-firing.

---

## 5. Fixed Decisions (locked at S0, pending critique)

- **F1.** The shared abstraction is the Phase-3 two-rung concept, reused
  verbatim. Phase 4 invents no new abstraction.
- **F2.** No terminal-green gate is added anywhere; the §1 invariant binds. Every
  new rung-1 floor (WS-1 release presence floor; WS-2 HOTL-entry floor) is
  presence/form-only; honesty is rung-2 (WS-1 **durable post-publish disposition
  review** of the recorded observable — NOT the pre-publish release critique gate;
  WS-2 resolution critique).
- **F2a (gating-critique Blocker 1, LOAD-BEARING).** WS-1 issue-close advances on
  **rung-1 record-presence only** (a distinct-channel confirmation or a typed
  non-`verified` disposition pass it equally). The automated distinct-channel
  confirmation is a **recorded observable for the human rung-2 audit, never an
  automated proceed-gate** — an automated "confirmed ⇒ close issues" wiring would
  relocate the #386/P4 anti-pattern onto a new channel (forbidden).
- **F3.** WS-1 is **additive** (supplement the line-163 proxy, do not delete it);
  the migration "delete old surface" step is N/A, the seeded-proof step binds.
- **F4.** WS-2 **extends the `evaluate_behavioral_verdict` family** (one sibling
  evaluator); the closest in-file template is **`evaluate_source_preservation`**
  (presence-gated carrier-body marker → typed form-set), with `proof_mismatch.py`
  the reference for degrade/fail-closed; reads the **carrier body** (never a fixed
  ledger path). WS-2's floor is the **first typed HOTL-status recognizer** —
  `local-only-by-contract` + the 7 HOTL statuses are *newly enforced* (today only
  docstring prose, accepted incidentally), not an existing recognizer.
- **F5.** WS-3b token rename is a **straight rename, no grandfathered alias** (gate
  is token-agnostic; drift test is membership-based; existing artifacts resolve on
  `verified`). Neutral token must avoid `apply`/`restart`/`deploy`; default
  proposal `instance-synced`.
- **F6.** WS-3b(b-ii) discussion-vocabulary is **Option A** (adapter-provided with
  behavior-preserving English default), **not** Option B (drop defaults — loses a
  guard).
- **F7.** The protected set is **5 classes** (P1–P5), including the **newly
  surfaced** P4 domain-blindness guard and P5 historical dogfood log; the
  acceptance grep recognizes **two** protected test classes.
- **F8.** Every WS-3 slice re-syncs `plugins/` before verify; sequencing
  S0 → WS-1 → WS-2 → WS-3a → WS-3b → S4 (no cross-workstream merge hazard:
  release/issue surfaces don't overlap the achieve taxonomy/regex surfaces).
- **F9.** Success = closed escape (WS-1 + WS-2) + a more portable, vocabulary-
  neutral boundary seam (WS-3) with **no guard lost**; never line/gate count.

## 6. Probes (decided during impl, not pre-wired here)

- **P-a (WS-1).** Exact distinct channel: HTTP fetch of `expected_release_url`
  (default) vs an adapter install/download probe — decide in WS-1 by the adapter's
  declared post-publish probe; default HTTP fetch when none.
- **P-b (WS-1).** Surface placement of the rung-1 record + floor (new field on the
  release payload + a check before `ensure_release_issues_closed`) — decide in
  WS-1 by the additive-before-the-issue-close pattern.
- **P-c (WS-2).** Exact HOTL-entry carrier grammar the floor reads (a
  `## HOTL` / per-issue HOTL block vs a `HOTL #N:` line) — decide in WS-2 by the
  carrier shape `issue_verify_closeout_body` already parses; presence-gated either
  way.
- **P-d (WS-3b).** Final neutral token (`instance-synced` default) + final
  `Post-Apply Checkpoint Classification` heading rename — gating critique may
  adjust; impl finalizes.
- **P-e (WS-3a).** Final neutral lane-example wording (consumer-agnostic vs
  explicit `<adapter deploy lane>` placeholder) — decide in WS-3a.

## 7. Success Criteria (testable)

- **S0:** this spec exists; the rung-1/rung-2 split is explicit per workstream; no
  terminal-green gate is specced; the complete `ceal-dev` leak inventory + the
  5-class protected set (incl. P4/P5) are enumerated; the WS-3b straight-rename +
  Option-A decisions are locked; a bounded fresh-eye gating critique returns PASS
  folded into §9.
- **WS-1:** on a seeded published-release fixture, a payload silent on the
  per-surface verdict FAILS the rung-1 floor before `ensure_release_issues_closed`;
  a distinct-channel confirmation **or** typed non-`verified` disposition PASSES;
  a same-channel-only re-read does not stand in as confirmation; existing release
  tests green.
- **WS-2:** on a seeded carrier, an undispositioned HOTL entry FAILS
  `verify-closeout` before `CLOSED` greens; a typed HOTL disposition (or
  `local-only-by-contract`) PASSES; a no-HOTL carrier is inert; existing
  issue-closeout tests green.
- **WS-3a:** `grep -rn "ceal-dev" skills/ scripts/ tests/` returns only the two
  protected classes (capability-resolution tests + the P4 domain-blindness guard);
  doc-link/markdown gates green; mirror-drift green; blocked-matrix fixture test
  green; fresh-eye.
- **WS-3b:** the neutral token replaces `applied-restarted` in all 6 sites in sync;
  `goal_artifact_discussion.py` deploy-vocabulary is adapter-provided with a
  behavior-preserving default; the heading rename updates `test_workflow_safety_docs.py`;
  producer / closeout-delegation / drift tests green; mirror-drift green; rollback
  refs; fresh-eye.
- **Bundle:** gate suite green (broad pytest); honest non-claims; live-proof levels
  named (WS-1 live release = `skipped:` unless operator-approved).

## 8. Rejected Alternatives

- **Bulk gate deletion / "fewer gates" as metric** — north-star failure signature
  (Non-Goals).
- **An Nth terminal-green gate that greens on self-classification** — the #386
  anti-pattern (F2, §1 invariant). WS-1's rung-1 is presence-only; WS-2's is
  presence-only.
- **WS-1 as a delete-and-replace migration** — rejected: it is additive; the
  line-163 proxy stays as the necessary first check, supplemented by the distinct
  channel.
- **WS-3b grandfathered alias for `applied-restarted`** — rejected: gate is
  token-agnostic, drift test is membership-based, existing artifacts resolve on
  `verified`; the alias is unnecessary insurance / over-engineering (F5).
- **WS-3b Option B (drop the English deploy-verb defaults)** — rejected: loses a
  guard for an unconfigured consumer (F6).
- **Hardening a charness-owned prod-apply boundary** — rejected: charness owns
  none; WS-3 is portability deleak, not boundary-hardening.
- **Rewriting the historical dogfood log (P5) to scrub `ceal-dev`** — rejected:
  it is a frozen record of a past scenario, not live guidance.

## 9. S0 Gating Critique — Folded (PASS-WITH-CONDITIONS, 2026-06-20)

A bounded fresh-eye reviewer (a distinct agent context, read-only in the shared
parent worktree) verified this spec's load-bearing claims against the **actual
code** (a distinct evidence channel — direct `Read` + independent leak greps +
read-only `pytest`, not a re-read of this artifact). **Verdict:
PASS-WITH-CONDITIONS.** The locked architecture (F1–F9), the leak/protected/test
inventories, and the core safety decisions (F5 straight-rename, F6 Option A) were
**all code-verified sound; nothing was refuted.** Three blockers tighten WS-1's
non-terminality wiring and correct two WS-2 false-precedent claims — none reopen
the concept.

**Claims CONFIRMED against code (selected):** WS-1 terminal-green
(`publish_release_execute.py:159-187`; `publish_release_post_create.py:35-58`
same-channel re-read); WS-2 gap (`issue_verify_closeout_body.py:224-258` binds on
any substantive value, no typed check); `proof_mismatch.py` presence-gated /
typed-disposition / degrade+fail-closed; HOTL vocabulary byte-exact
(`ledger-and-dispositions.md:14-20`); **WS-3b token-agnosticism** (the gate
`_item_resolved` matches only `verified`/`skipped:`/`issue #N`; the drift test
`:213-219` asserts membership) — so the straight-rename (F5) is verified safe;
leak inventory **exactly L1–L6 / T1–T6 / P1–P5 + all `plugins/` mirrors, no site
missed**; **P4 domain-blindness guard real** (stripping it deletes a guard);
`instance-synced` collision-free + verb-free; the 4 pinned WS-3 tests green
(59 passed).

**Blockers folded:**

1. **WS-1 §2/F2a (LOAD-BEARING).** Issue-close runs *inside* the same automated
   `_publish_and_finalize` call; the human rung-2 audits afterward — so the rung-1
   floor must gate issue-close on **record-presence only**, never on an automated
   distinct-channel HTTP-200, else the #386/P4 anti-pattern relocates to a new
   channel. Folded into §2's "Non-terminality check" + new **F2a** + the corrected
   rung-2 location (durable post-publish disposition review, NOT the pre-publish
   release critique gate).
2. **WS-2 §3/F4.** `local-only-by-contract` is **only docstring prose**
   (`issue_verify_closeout_body.py:231`), recognized by no code today; WS-2's floor
   is the **first typed-vocabulary recognizer**. Folded into §3 + F4 so no impl
   slice assumes a recognizer exists.
3. **WS-2 §3/F4.** `evaluate_source_preservation` (`:159-194`) is the **closest
   in-file structural template** (presence-gated carrier-body marker → typed
   form-set), stronger than the cross-file `proof_mismatch.py`. Folded into §3 +
   F4.

**Over-worries dismissed by the counterweight pass (do NOT re-add):** the WS-1
two-rung shape re-creating terminal-green *as an architecture objection*
(dismissed — it is exactly P5's mandated stop condition; only automated-proceed
wiring violates P4, which F2a forbids); the `applied-restarted` grandfathered
alias (over-engineering — straight rename correct); Option B for the discussion
vocabulary (loses a guard); ±1–2 test line-number drift (non-load-bearing —
symbol/assertion-kind/class all correct); scrubbing the P5 dogfood log or the
`apply/restart` verbs in lane examples (frozen history / illustrative class, not
a consumer name); a missing "deletions" boundary (Phase-4 plan-of-record scope,
not a gap).

**Reviewer provenance:** bounded fresh-eye subagent, read-only (no Edit/Write, no
index/worktree-mutating git ops); distinct evidence channels = direct reads of
the release/issue/achieve code + `design-north-star.md` + the 4 pinned tests,
independent leak greps over `skills/ scripts/ tests/ docs/ plugins/`, and a
read-only `pytest` baseline (59 passed).

**Gate result: S0 spec LOCKED. Implementation (WS-1) may proceed.**
