# WS-3a Critique — Tier-1 `ceal-dev` consumer-name portability deleak

Date: 2026-06-20
Slice: WS-3a of `charness-artifacts/goals/2026-06-20-north-star-phase4-boundary-non-terminality.md`
Concept lock: `charness-artifacts/spec/2026-06-20-phase4-boundary-non-terminality-concept.md` §4a + §4c
Scope: governing-surface edit (achieve `lifecycle.md` / `goal-artifact.md`) + a
fixture/docstring rename + the public-skill validation review for `achieve`.

## What changed

Removed the `ceal-dev` consumer-**NAME** leak from charness's portable achieve
doctrine/examples (`ceal-dev` → neutral `instance`), preserving the illustrative
`apply/restart` verbs (WS-3b's concern). Sites L1–L5 + the `plugins/` mirror:
`lifecycle.md:342` (prose) + `:353` (example lane), `goal-artifact.md:219`
(example lane), `goal_artifact_blocked_matrix.py:7` (docstring),
`test_goal_artifact_blocked_matrix.py:38` (`_RUNNABLE_LANE` fixture).

**Protected, left byte-unchanged** (stripping any deletes a guard / a legit
adapter example): P1 `docs/runtime-capability-contract.md:117`, P2
`docs/capability-resolution.md:140,143`, P3 `tests/charness_cli/test_capability_resolution.py`
(all `slack.ceal-dev` capability-resolution examples), **P4
`tests/quality_gates/test_proof_semantics_adapter.py:244`** (the `ceal-dev` inside
`test_core_module_is_domain_blind()`'s `forbidden` tuple — a domain-blindness
GUARD), P5 `docs/public-skill-dogfood.json:76` (frozen historical dogfood log).

## Acceptance (S0 §4a + User Acceptance)

`grep -rn "ceal-dev" skills/ scripts/ tests/` returns **only the two protected
classes**: P3 (`test_capability_resolution.py`, `slack.ceal-dev`) and P4
(`test_proof_semantics_adapter.py:244`, the domain-blindness guard). No
portable-core doctrine/taxonomy/fixture leak remains.

## Bounded fresh-eye critique — PASS (folded)

A bounded fresh-eye reviewer (distinct agent context, read-only) verified every
angle **against the actual staged code with its own greps + git diffs + pytest**
(distinct evidence channel), not the slice author's summary. **Verdict: PASS, no
blockers.**

CONFIRMED: (A1 under-clean) the acceptance grep returns exactly the 6 protected
hits, zero remaining `ceal-dev` in achieve skill/script; `docs/` P1/P2/P5 and the
`plugins/` mirror have no stray leak. (A2 over-fire) `git diff --cached HEAD` for
the protected files = 0 lines — P3/P4/P5 byte-unchanged. (A3 guard works) 46
tests pass — `_RUNNABLE_LANE` is still `preauthorized-runnable` and the floor
fires on it unchanged (the literal `ceal-dev` was incidental — the tests key on
the classification token); the P4 guard still asserts (and the passing test
proves) the portable core contains no `ceal-dev`. (A5) the `plugins/` mirror is
byte-identical to source (staged) — `staged-plugin-mirror-drift` will not fire.
(A6) the floor-script diff has zero lines beyond the docstring swap — no gate
logic, no `CLOSEOUT_STATE_LEVELS`/taxonomy token, no `goal_artifact_discussion.py`
regex (those are WS-3b); the `achieve` consumer contract is unchanged.

Over-worries dismissed (NOT folded): the P4 guard token "looks like a missed
leak" (it is the opposite — the guard that enforces the deleak); P3 `slack.ceal-dev`
remaining (a legit protected adapter example); dropped backticks around `instance`
in the lifecycle.md:342 prose (cosmetic — "instance" reads as a common noun, not a
code token; re-fencing would be churn); the `apply/restart` verbs untouched
(in-spec — WS-3b's vocabulary concern, not the consumer name).

## Public-skill validation decision (cautilus `next_action: none`, ask-before-run)

Cautilus `run_mode: ask`, `next_action: none` — no live evaluator run; deterministic
validation + this recorded fresh-eye review own the closeout. `achieve` is the only
changed public skill; its consumer contract is unchanged (a doc/fixture rename, no
gate/behavior change). `achieve` dogfood case refreshed (`reviewed_on` +
observed-evidence). Closeout proceeds with `--ack-cautilus-skill-review`.

## Non-claims

- This is a portability deleak, not boundary-hardening — charness owns no
  prod-apply boundary (the goal's framing correction).
- WS-3b (the `applied-restarted` taxonomy rename + the
  `goal_artifact_discussion.py` deploy-vocab adapter seam + the Post-Apply heading)
  is the verb-vocabulary deleak; it is a separate slice, not done here.
