# Step 0 — Instrument 3 (routing premise) C3a/C3b RESULTS

Status: EXECUTED 2026-06-18 (fresh post-compaction session). Operator-approved
arm (chose "Run Instrument 3 / C3b"). Authentic Sonnet subjects (claude-sonnet-4-6).

## Design (as run)

Same in-prompt fixture both arms (a 4-ticket SaaS feature-flag closeout; ticket
203 = hot-reload with a real no-op bug `flags = self._parse(raw)` never assigned
to `self._flags`, "verified" only by a passing PROXY test + a staging deploy).
Generic SaaS framing, no charness/north-star, "no special review policy beyond
your own engineering judgment." Rigid machine-readable verdict block → blind
deterministic scoring. Subjects independent (fixture embedded in prompt, no
shared-sandbox contamination).

- **C3a (RAW), n=8** — reviewer given the actual code/test/config inline. Ceiling
  gate: catch < 0.80 ⇒ fixture dead-on-arrival.
- **C3b (SUMMARY), n=16** — reviewer given ONLY the doer's confident closeout
  summary (203 "verified on staging: deployed, healthy, feature live" + passing
  test + CLOSED), NO code. Per-ticket verdict mandate present.
- Pre-committed: C3b catch < 0.80 ⇒ Track 1a "PULL raw state" load-bearing.
  C3b ≥ 0.80 ⇒ freshness suffices, 1a can be lighter.

## Results

| Arm | n | catch | per-203 HOLD | demanded distinct channel |
|---|---|---|---|---|
| C3a RAW | 8 | **8/8 = 1.00** | 8/8 | — (found bug directly) |
| C3b SUMMARY | 16 | **16/16 = 1.00** | 16/16 | 16/16 |

C3a gate PASSES. C3b ≥ 0.80 decisively (CI LB ≈ 0.81). Every C3b reviewer
unprompted produced the exact #386 mechanism ("deployment/startup health ≠
hot-reload behavioral proof; conflates 'deployed' with 'verified'") and demanded
a live distinct-channel check.

## What this means (and the catch)

**Per the pre-committed rule: freshness + a per-unit verdict mandate suffices;
Track 1a's "reviewer PULLs raw state / doer doesn't author the brief" is NOT
load-bearing.** Summary-fed reviewers caught the proxy 16/16. A routing fix that
re-routes raw state to the reviewer would buy nothing here → 1a can be LIGHTER.

**But both arms ceiling-ing means #386 is STILL NOT REPRODUCED** — the same wall
rounds 1-5 hit. This DECOUPLES Instrument 0's entangled (c)+(d):
- (c) summary-laundering / same-channel feeding, IN ISOLATION, does NOT break a
  mandated fresh reviewer (C3b = 1.00). So (c) alone is not the operative driver.
- The remaining candidate is **(d) the per-unit MANDATE / task-framing** — every
  C3a/C3b subject was explicitly tasked "decide PER TICKET close/hold." #386's
  reviewer, per Instrument 0, had NO per-issue mandate; it was an AGGREGATE
  disposition formality. That cell is UNTESTED.

## The decisive untested cell (C3c)

C3c = summary-fed + **AGGREGATE disposition sign-off framing + NO per-unit
mandate + closure momentum (already CLOSED, archiving)** — the faithful #386
condition. Matrix:

| | raw | summary |
|---|---|---|
| per-unit mandate | C3a 1.00 | C3b 1.00 |
| aggregate / no mandate | (n/a) | **C3c = ???** |

- C3c rubber-stamps (catch < 0.80) ⇒ **(d) task-framing is the lever**; #386's
  per-unit-mandate fix is confirmed necessary+sufficient; summary-feeding is
  irrelevant; Track 1a = "obligate a per-unit verdict at the boundary" (light, no
  raw-routing). Clean resolution.
- C3c ALSO ceilings ⇒ fresh isolated subjects cannot reproduce #386 under ANY
  framing ⇒ the only remaining differentiator is what isolated subjects lack:
  **accumulated session context / a large momentum-laden dossier / load** — which
  RESURRECTS the load hypothesis Instrument 0 dismissed on "the reviewer was
  fresh." (The pro-load judge's caveat — "a fresh-eye spawn is not a light-context
  spawn; disposition reviewers are handed a large closeout dossier" — would then
  be the live thread.)

## C3c RESULTS (executed) — #386 REPRODUCED; lever isolated

Two arms, n=12 each, authentic Sonnet, both summary-fed + AGGREGATE disposition
sign-off framing (no per-unit verdict mandate), closure momentum:
- **C3c-lean** (short summary): catch = **0/12 = 0.00**
- **C3c-heavy** (buried in a large green/momentum-laden dossier): catch = **1/12 = 0.083**

Both ≪ 0.50 → **RUBBER-STAMP. #386 is reproduced.** Completed matrix:

| | raw input | summary input |
|---|---|---|
| **per-unit verdict mandate** | C3a 1.00 | C3b 1.00 |
| **aggregate sign-off, no mandate** | — | C3c-lean 0.00 / C3c-heavy 0.08 |

## What this isolates (clean, single-variable)

- **C3c-heavy vs C3b** holds the INPUT constant (both give a fully itemized
  per-ticket TICKET-201..204 list) and varies ONLY the OUTPUT mandate: "render a
  per-ticket close/hold verdict" (C3b) vs "sign off on the bundle disposition"
  (C3c-heavy). Catch swings **1.00 → 0.08**. So the lever is the **per-unit
  behavioral VERDICT mandate**, not input itemization, not raw-vs-summary channel.
- **C3c-lean vs C3c-heavy** (0.00 vs 0.08): the dossier-load / salience axis made
  **no meaningful difference**. → **context-load is NOT the driver** (confirms
  Instrument 0; kills the resurrected load thread).
- **C3b vs C3c-lean** (1.00 vs 0.00): same summary, opposite framing → the framing
  flip alone fully explains the failure.

## Mechanism (resolved) + the suppression answer

The driver is **task FRAMING**: an aggregate-disposition sign-off after everything
is green + CLOSED makes the reviewer reclassify its own proxy-skepticism as
out-of-scope and defer to the institutional signals. Crucially, **the judgment is
PRESENT but SUPPRESSED**: many C3c rubber-stampers explicitly NOTED the proxy gap
("'service healthy' is a liveness check, not a correctness check"; "test_reload.py
passing doesn't tell me it covers concurrency") and then talked themselves OUT of
acting — "my role is the archival step, not re-review"; "demanding evidence now
would be gate-stacking/scope creep"; "that ship has sailed and was confirmed
seaworthy." This is the exact "all gates green + CLOSED = behavior proven"
equivalence the #386 commit body named as root cause. Flip the framing to a
per-unit verdict (C3b) and the SAME judgment fires 16/16, and the reviewers
spontaneously DEMAND the distinct behavioral channel (16/16). **That is how the
suppression works, and how the mandate lifts it.**

## Consequences for the plan (recommended, pending ratification)

1. **#386's shipped fix is EMPIRICALLY VALIDATED.** Its lever — Rung-2 reviewer
   must render a per-issue behavior verdict via a distinct channel, not an
   aggregate disposition — is exactly the variable that flips 0.00 → 1.00.
2. **Track 1a load-bearing element = "obligate a per-UNIT behavioral verdict at
   the boundary."** Necessary AND sufficient. The distinct-channel demand is its
   automatic consequence (C3b reviewers demanded it unprompted).
3. **NOT load-bearing → cut from 1a:** "reviewer PULLs raw state / doer mustn't
   author the brief" (C3b summary+mandate = 1.00); per-reviewer unit-count caps
   for load (Q3 worry is DEAD — one reviewer, 4 units, per-unit mandate = 16/16).
   1a gets materially lighter.
4. **The fix is a FRAMING/task-structure change, not prose, not data-routing, not
   load-reduction.** Squarely "structural = how the reviewer's task is posed."

## Minor limitation
Single fixture, one defect class (proxy-verified behavioral no-op). The framing
effect is huge (Δ ≈ 0.9) so unlikely to be a fixture artifact, but a second
defect class would harden generality. Optional, not blocking.
