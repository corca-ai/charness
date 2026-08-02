# Issue 477 resolution
Date: 2026-08-02

## Decision Under Review

Closing #477 by REPOINTING the risk-interrupt planner to a layout-independent
path (a `skills/shared/scripts/` shim reached at equal depth in both layouts)
rather than deleting the call — and whether the closeout's root-cause and
sibling claims survive an independent read before an irreversible public close.

## Failure Angles

- **The root cause is a restatement of the symptom.** "A wrong path" explains
  nothing about why it survived authoring, review, and every gate, and a vague
  root_cause becomes permanent record at close time.
- **The fix is complete in this tree and incomplete where it ships.** Every
  check ran inside the repo, where the authoring `scripts/` is always in reach,
  so it cannot distinguish a self-sufficient package from a nearby tree.
- **The class is declared closed when only one instance was repaired.** Sibling
  sweeps that inspect rather than resolve report clean by not looking.
- **The shim is a new execution surface**: it runs whatever it finds walking up.

## Counterweight Pass

Real blockers, folded: the three-mechanism root cause; the unproven behavioural
claim; two overstated sentences in the fix's own docstring. Over-worry, raised
and NOT folded: the shim's unbounded upward walk (bounded in practice — the
correct planner is always one level up in both real layouts, so the walk
terminates immediately; recorded as a limit, not repaired). **AMENDED
2026-08-02: since repaired.** A later round on the #478 shims judged the
unbounded walk worth closing rather than tolerating, and
`authoring_script_shim._MAX_ANCESTORS` now caps it. Amended here because a
durable record naming a deferred remedy is read at slice-shaping time, and
leaving it saying "deferred" invites re-opening a closed item. and a missing
`ValidationError` handler on the shim path (no reachable raise found).

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_skill_contracts.py:203 | action: document | note: a source guard pinned the BROKEN string as REQUIRED, so fixing the path would have failed a gate — permanence, not just missed detection; folded into the ledger root_cause
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/probe/2026-08-02-477-installed-layout-plan-risk-interrupt.md | action: fix | note: the behavioural claim was unproven until run from an exported package outside this tree; the probe was produced before the close
- F3 | bin: valid-but-defer | evidence: strong | ref: skills/shared/scripts/run_plan_envelope.py:32 | action: defer | note: ten packaged-Python sites resolve in both layouts only by an exporter-flattening coincidence; recorded with a revisit trigger rather than repaired
- F4 | bin: over-worry | evidence: moderate | ref: skills/shared/scripts/authoring_script_shim.py:44 | action: fix | note: the shim's ancestor walk was unbounded upward; deferred at the time, then capped when the shared module landed (ref updated — the logic moved out of plan_risk_interrupt.py)

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (read-only typed subagent; Read/Grep/Glob only)
- Requested spawn fields: subagent_type=bounded-reviewer, unnamed one-shot spawn, session-model inheritance per the Claude Code host split
- Host exposure state: applied
- Application state: host-confirmed: the spawn returned a full findings report in-band, and the reviewer self-reported its envelope as Read/Grep/Glob only
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — a bounded `bounded-reviewer` subagent spawned by the parent
for this resolution, read-only by envelope, reporting its own context as
`parent-delegated`. Reviewer-boundary window `issue-477-causal`;
`reviewer_boundary_fingerprint.py` snapshot and verify both `clean`, no drift.
Its findings are folded below and into the closeout ledger; the two claims it
refuted were corrected rather than argued.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed: the reviewed input was the live tree at c31a6eca plus the issue body, handed to the reviewer inline. -->

## Boundary Ownership

- Producer: `export_plugin.py`, which decides the shipped tree's depth from a skill package to the package root.
- Consumer: skill prose in `impl`/`spec` that names a path relative to `$SKILL_DIR`.
- Owning surface: the shared skill-script entrypoint tier (`skills/shared/scripts/`), which is the one location at equal depth in both layouts.
- Verdict: moved-to-owner

## Why this critique exists

The repo contract runs a causal review before a bug-class close so the closeout
ledger records a mechanism rather than a restatement of the symptom, and so the
sibling sweep happens while the class is still fresh. The operator's approval
for this goal covers the DECISION to close; it never covers the evidence floor.

## What the review changed

It did not ratify the fix. Three things in the closeout are the reviewer's, not
the implementer's:

1. **The root cause went from one mechanism to three.** The implementer's account
   was "a layout-dependent `../` count that no gate resolved". The reviewer added
   the two that explain permanence rather than occurrence:
   - `check_doc_links.COMMAND_TARGET_RE` has no `$` in its target character
     class, so a `$SKILL_DIR`-prefixed command was **never parsed at all** — not
     exempted by the placeholder rule, simply unreadable — and `DOC_GLOBS` never
     scans `plugins/`, so nothing resolved anything in the shipped layout.
   - `check_skill_contracts.PACKAGE_CONTRACTS` pinned the BROKEN string as a
     REQUIRED snippet. **An author who fixed the path would have failed a gate.**
     The repo did not merely fail to detect this; a green gate was conditional on
     the defect persisting.
2. **Two claims were pushed back on and are corrected in the ledger.** The fix's
   own docstring said it "resolves the layout ambiguity"; the reviewer showed it
   removes ONE instance of a class still live at roughly ten other sites. And the
   docstring's rejection of a two-candidate probe argued that `check_doc_links`
   would misread it — that gate structurally cannot read the form at all.
3. **The behavioural verdict was called unproven.** Every check to that point ran
   inside this tree, where the authoring `scripts/` is always in reach; the
   reviewer said that cannot distinguish "the shipped package is self-sufficient"
   from "the authoring tree was nearby", and demanded an out-of-tree channel. It
   was produced:
   [the installed-layout probe](../probe/2026-08-02-477-installed-layout-plan-risk-interrupt.md).

## Sibling sweep — decision and proof

Four axes swept. Proof is per-axis resolution in BOTH layouts, not inspection.

| axis | result | decision |
| --- | --- | --- |
| other `$SKILL_DIR/../../../`+ escapes in shipped prose | none live | closed |
| path-bearing source guards in `check_skill_contracts.py` | all five resolve in both trees | closed |
| `\|\| true` swallows in Bootstrap fences | every one wraps a baseline tool or is `command -v`-guarded | closed |
| hard-coded depth walks in packaged Python | ten sites resolve in both layouts **only because the exporter's kind-flattening cancels the `plugins/<pkg>` prefix** | recorded, not repaired |

The fourth is the one that matters. `parents[3]` / `parents[2]` at seven planner
sites plus three `gather` scripts, and a latent wrong `parents[4]` fallback at
`skill_runtime_bootstrap.py:103`. Decision: **do not repair in this closeout** —
they are correct today, repairing ten call sites is a slice of its own, and the
honest record is the revisit trigger. Revisit trigger: any change to
`export_plugin.py`'s skill-tier layout turns all ten into this same bug at once.

Also recorded: the four `$SKILL_DIR/../../shared/` commands in
`fresh-eye-subagent-review.md` are resolved by no gate in any layout, because
shared-tier prose is deliberately skipped (`$SKILL_DIR` is whichever skill
included it). Correct today, verified by hand. A decidable rule exists — resolve
shared prose against the package's carried `authoring_root` — and is the named
follow-up rather than a repair here.

## Recurrence judgement

The new blocking gate closes mechanism (1): `SKILL_DIR_RE` anchors on the
literal instead of lexing after `python3`, and it resolves against the shipped
layout. Verified it fired on this defect while live — the two sites sat in
`KNOWN_SHIPPED_FINDINGS` and the set is now empty.

It does **not** close mechanism (3): nothing connects a source-guard literal to
that resolver, so a future guard can pin an unresolvable path again with the
same effect. And its shipped-layout catch currently depends on `plugins/scripts/`
not existing; the robust form refuses any `$SKILL_DIR/...` resolving outside the
package's `authoring_root`. Both are carried into the ledger's `prevention`
field as stated limits rather than left implicit.

## Non-claims

- This critique reviewed the fix's REASONING and swept for siblings. It did not
  re-derive the planner's own verdict logic, which is out of scope for #477.
- The out-of-tree probe is an EXPORT, not a host install; it proves the package
  is self-sufficient for this command, not that a host installer works.
