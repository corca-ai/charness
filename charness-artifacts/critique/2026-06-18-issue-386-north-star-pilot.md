# Resolution Critique — #386 (issue-bundle closeout; north-star pilot)

Execution: bounded fresh-eye subagents (canonical path).
Fresh-Eye Satisfaction: parent-delegated.
Target: decision premortem (the fix lands a design standard + a reviewer mandate,
not a diff-shaped gate).

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage` (design lock-in guiding a repo-wide overhaul).
- **Requested spawn fields**: none sent — this Claude Code run spawned each bounded
  reviewer (4 angles + 1 counterweight) via the Agent tool with `subagent_type:
  general-purpose` and no model/effort override; the adapter `reviewer_tiers`
  mapping was not forwarded through the Agent spawn interface.
- **Host exposure state**: `host-defaulted`
- **Application state**: `unverified-by-host` (the host does not confirm applied
  spawn fields back to the parent; reviewers ran with the host default reviewer).

## What was critiqued

The decision under review was **North Star v1**, the harness design standard that
the #386 fix pilots (`docs/design-north-star.md`). The #386 fix is the standard
applied: at the issue-bundle closeout (an irreversible boundary) the distinct
disposition reviewer must confirm each closed issue's behavior via a *different
evidence channel and observer*, never by re-reading the bundle proxy; no new gate.
Framing question: where does this philosophy fail, and is the
reversible/irreversible boundary robust enough to carry it.

## Angles (4) + counterweight (1)

- **Jackson (framing)** — the headline "trust intelligence" fought the real
  diagnosis (terminal trust at irreversible boundaries); risked steering toward
  deletion. → reframed.
- **Weinberg (diagnostic)** — #386's reviewer *already* re-examined and
  rubber-stamped, so "re-examine" alone is the cure that failed; the cure must
  use a *distinct evidence channel*. → this is the load-bearing #386 mechanism.
- **Gawande (operational)** — "re-examine" needs a captured observable distinct
  from the triggering claim, by a distinct observer, or it degrades to a
  rubber-stamp. → folded into the Rung-2 mandate.
- **Minto (durability)** — the boundary term is load-bearing and was undefined;
  the standard lacked failure signatures. → defined by blast radius; added
  Failure Signatures.

## Four-bin triage (counterweight)

- **Act Before Ship** — F1 reframe (diagnosis-first); F2 distinct-channel +
  distinct-observer; F3 blast-radius boundary definition; F7 edges + failure
  signatures. All folded into the north star and the #386 fix.
- **Bundle** — F6 stop-condition (populated evidence record + second observer
  sign) — expressed as the disposition review's bound artifact.
- **Over-Worry** — F4 "gate-removal sign-off record": rebuilds the fence the
  standard retires; dropped (kept only the cheap "count is not a metric" line).
- **Valid but Defer** — F5 per-surface observable checklists, F8 migration
  apparatus, F9 diagnosis back-test: the *overhaul plan's* job, not this fix.

## Recurrence conclusion for #386

The root cause was a *missing per-issue behavior mandate on a distinct observer
that already existed* — so it re-read the proxy. The fix closes exactly that gap:
the reviewer must now name, per closed issue, the distinct behavior channel
consulted or a non-`verified` disposition; re-reading the readback/CLOSED is
explicitly not confirmation. Deliberately **no 8th gate**: a deterministic floor
greening on self-classification would re-grant the terminal trust that caused the
bug (north star P5).

## Residual risk (named, not hidden)

The fix trusts the distinct reviewer to honor the mandate (the craken bet). A
reviewer could still under-confirm — but the *structural* gap (no per-issue
obligation at all) is closed, and the obligation is now legible and auditable in
the bound review artifact. Hardening the distinct-observer honesty further, and
the verify-closeout consumer (Direction-3), are deferred to the overhaul.

## Deliberately not doing

- Direction-3 (verify-closeout refusing on undispositioned HOTL entries) — a
  different consumer; deferred.
- A generalized per-unit-disposition gate unifying #381/#385/#386 — deferred to
  the north-star-guided overhaul.
