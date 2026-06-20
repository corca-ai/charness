# WS-2 Critique — Direction-3 HOTL-disposition floor on `issue verify-closeout`

Date: 2026-06-20
Slice: WS-2 of `charness-artifacts/goals/2026-06-20-north-star-phase4-boundary-non-terminality.md`
Concept lock: `charness-artifacts/spec/2026-06-20-phase4-boundary-non-terminality-concept.md` §3 + F4
Scope: governing-surface edit (`issue/references/closeout-discipline.md`) + a
`verify-closeout` behavior change (new rung-1 floor) + the public-skill
validation review for the changed `issue` skill.

## What changed

Closed the Direction-3 gap: `issue_verify_closeout_body.py`
`evaluate_behavioral_verdict` accepted a HOTL status only as an **opaque**
`Behavior #N:` value and read **no** HOTL carrier disposition — an undispositioned
HOTL entry could ride `CLOSED` to "done." WS-2 adds a sibling rung-1 floor:

- **`evaluate_hotl_dispositions(text, classification)`** — presence-gated (a
  carrier with no `HOTL #N:`/`HOTL:` entry is inert), modeled on the in-file
  `evaluate_source_preservation`. A presented HOTL entry's value must carry one of
  the typed HOTL ledger statuses (`hotl/references/ledger-and-dispositions.md`) or
  `local-only-by-contract`; an entry present without one is *undispositioned* and
  refused. It is the **first typed HOTL-status recognizer**. Reads the carrier body
  (never a fixed ledger path → adapter-portable); fails closed; presence/form only.
- Folded into `verify_closeout`'s `ok` aggregation + result; `validate-closeout-draft`
  inherits it by reuse (parity).

## Bounded fresh-eye critique — PASS (folded)

A bounded fresh-eye reviewer (distinct agent context, read-only in the shared
parent worktree) verified every contract clause + adversarial angle **against the
actual staged code** (`git diff --cached` / `Read` / live in-process exercise of
`evaluate_hotl_dispositions` over ~25 adversarial inputs / read-only `pytest`),
not a re-read of the spec. **Verdict: PASS, no blockers.**

CONFIRMED: presence-gating (no-HOTL ⇒ inert, fenced HOTL inert); the typed
vocabulary byte-matches `ledger-and-dispositions.md:14-20` + `local-only-by-contract`;
fail-closed (TODO/TBD/bare-"blocked" ⇒ refused); regex longest-alternant ordering
(bare "blocked"/"deferred" do not shadow-pass); **A1** the typed-vocabulary check
is legitimately rung-1 **form** (token-presence), with the direct precedent
`scripts/proof_mismatch.py` `_GAP_DISPOSITION_KINDS` — it never greens on
self-classification (`status: verified` stays necessary-not-sufficient; honesty is
the rung-2 resolution critique). Floors are **orthogonal**: a `Behavior:` line that
merely names a HOTL status does NOT trip the HOTL floor (it gates on `HOTL:` line
presence). Integration correct (`hotl_dispositions["ok"]` in the `ok` chain;
draft parity). Tests non-tautological: undispositioned ⇒ rc 2 with
`behavioral_verdict.ok=True` (failure isolated to the HOTL floor); typed /
`local-only-by-contract` ⇒ pass; no-entry ⇒ inert. Broad issue/closeout sweep
382 passed; plugin mirror in sync.

Over-worries dismissed (NOT folded): stray `HOTL <word>:` lines failing closed
(fail-closed is the spec mandate; the documented grammar is `HOTL #N:`/`HOTL:`;
mirrors the sibling `_BEHAVIOR_LINE_RE` free-target grammar); `issue` as a common
word passing a thin value (spec delegates honesty to rung-2 — render-not-declare,
identical to `evaluate_source_preservation`'s present-but-thin pass).

## Public-skill validation decision (cautilus `next_action: none`, ask-before-run)

Cautilus planner reported `run_mode: ask`, `next_action: none` (eval-only /
ask-before-run — no live `cautilus evaluate` run; the deterministic validation +
this recorded fresh-eye scenario review own the closeout). `issue` is the only
changed public skill; its *consumer contract* (routing → `issue`, closeout
discipline) is unchanged — this is an additive internal floor that extends the
existing `evaluate_behavioral_verdict` family. The `issue` dogfood case is
refreshed (`reviewed_on` + an observed-evidence line). Closeout proceeds with
`run_slice_closeout.py --ack-cautilus-skill-review`.

## Non-claims (Honest Proof Discipline)

- Proof is local + seeded carrier fixtures (no live GitHub close). The floor is
  exercised through `verify-closeout` on committed/`--body-file` carriers, not a
  live issue close.
- The floor recognizes a typed-status *token*; whether the disposition is
  *honest* (a real `verified`, a justified `accepted-risk`) is explicitly the
  rung-2 resolution critique's job, not proven here (by design).
