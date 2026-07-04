# Systemic Context-Tax Measurement — Design (2026-07-04)

Serves [intent.md](./intent.md) §"Held open": single-run capture cannot see the
systemic dumbing — the context tax a skill's overhead levies on unrelated
reasoning across a whole session, and the ritual-following it may train. This is
the DESIGN for measuring it. Nothing is built in this session; the intent's own
warning (the measurement apparatus is itself the overhead disease) is the
binding constraint on every choice below.

## Current evidence, stated honestly

The systemic-tax hypothesis rests on ONE pre-effort anecdote (the 2026-07-02
founding symptom in intent.md). Every audit run since has come back cold on
adjacent questions: [apparatus-floor-audit.md](./apparatus-floor-audit.md)
found faithful runs are NOT forced into runtime ritual by doc-open floors, and
[churn-sweep-completion.md](./churn-sweep-completion.md) found real churn
genuinely rare and already fixed. No new symptom instance has been logged
since. Pieces 2–3 below are therefore designed **in case**, not
demand-confirmed; only piece 1 is evidence-first.

## The decomposition that makes it tractable

Sessions do not share model weights. Whatever "systemic" effect exists cannot
accumulate inside the model across sessions — on the agent/harness side it can
only live in two places:

- **T1 — in-session tax:** context displacement (harness tokens crowding
  task-relevant attention), reasoning interruption (gates firing mid-chain),
  and in-context ritual priming (a procedure-heavy opening shaping later
  unrelated answers) — all within one session window.
- **T2 — surface-encoded ritual pressure:** the standing written surfaces
  (CLAUDE.md, skill bodies, refs, gate stdout, carried artifacts like handoff
  and lessons) that *instruct* compliance-shaped behavior into every fresh
  session. The static skill/ref inventory side is already auditable — the
  [skill-anatomy-map](./skill-anatomy-map.md) and
  [rationale-accuracy-audit](./rationale-accuracy-audit.md) are that
  substrate. The *dynamic* side — handoff/lessons prose written by a
  possibly-taxed session and read by the next (a T1→artifact→T1 loop) — is
  NOT covered by those audits and is a first-class citable surface below.

So the open problem reduces to: **an instrument for T1 at session scale**, plus
a way to connect T1 evidence back to the T2 surface that induced it.

## Rejected designs (each fails the intent's own tests)

- **Standing session-scale A/B (harness-on/off):** the pre-built apparatus
  disease by name; doubles cost per data point; standing infra to answer a
  question that arises rarely.
- **In-session sentinel probes / canary questions:** the measurement *is*
  injected overhead — it contaminates the session it measures.
- **Scalar tax metric as a standing gate or target:** proxy-metric ban
  (Goodhart); the intent's only test is "그게 정말 최선인가?", applied by a
  reader, not a threshold.
- **Cross-session observational regression (overhead share vs outcome):**
  hopelessly confounded — harder tasks invoke more skills — and n is tiny.
- **Within-session early-vs-late comparison:** confounded by task ordering and
  natural long-context degradation independent of harness overhead.

## The design: three pieces, zero standing apparatus

1. **Symptom ledger (detector, near-zero cost).** The operator's own "에이전트가
   멍청해진 것 같다" perception is the primary sensor — it started this whole
   effort and it is the only detector aimed at the real target. Give it a
   durable landing place: one line per firing (date · session · the moment ·
   what felt dumb), appended to
   [symptom-ledger.md](./symptom-ledger.md). No form, no template, no gate.
   Trigger rule, stated honestly: the operator (or an agent hearing the
   symptom mid-session) appends the line; the operator reviews the ledger and
   requests an audit by name — **no automatic threshold, no read cadence.**
   The one-sentence pointer wiring this into session discipline lives in
   [operating-contract.md](../../docs/conventions/operating-contract.md);
   a pointer is not a gate — without it the ledger silently no-ops.
2. **Session tax audit (detector→case triage, on-demand).** A
   counterfactual-by-judge: a fresh-eye subagent reads one session's record
   against a fixed symmetric rubric of ≤1 page:
   - (a) *tax moments* — a harness-mandated step displaced or interrupted
     productive reasoning with no downstream payoff; span-cited;
   - (b) *ritual-shaped responses* — checklist/ceremony answers to non-ritual
     asks; span-cited;
   - (c) *paid-off overhead* — mandated steps that visibly improved the
     outcome; span-cited (the symmetry guard: a judge sent to find tax will
     find tax, so it must also collect the defense);
   - (d) *net counterfactual* — what a body-only agent would plausibly have
     done differently at each cited moment, and whether that is better or
     worse.
   Output is a **case list, never a score**, landing at
   `charness-artifacts/reference-compaction/tax-audit-<date>.md` (dated file
   only; a `latest.md` pointer is deliberately skipped for a rare on-demand
   instrument). Every tax case must name the inducing surface — a gate, ref,
   contract line, **or a carried artifact entry (handoff/lessons)** — the
   T1→T2 bridge that feeds the per-surface compaction machinery (carried-
   artifact cases have no standing machinery; remediation is a manual edit).
   **Open sub-problem, not assumed solved:** no existing renderer turns a
   real session record (observed 0.5–13MB jsonl, ~484k tokens) into a
   judge-readable transcript — the only renderer today
   (`run_skill_efficiency_ab.py` `_write_transcript`) caps at 20K chars and
   strips tool results. Choosing the preprocessing is part of the pilot's
   first work and must itself pass the anti-apparatus test.
3. **Escalation contrast (decision-grade, rare).** When prune-vs-keep for a
   specific surface is contested — *however* that contest was surfaced (a tax-
   audit case, census cross-check, or direct capture inspection): ONE
   with/without contrast on the same task via the existing A/B harness,
   `scripts/run_skill_efficiency_ab.py --run <config> --judge-cmd ...`
   (+ `grade_skill_outcome.py`). Governance note: that harness carries its own
   self-test-first / judge-spend opt-in gate and is SEPARATE from the cautilus
   `plan_cautilus_proof.py` ask-before-run contract — do not route it through
   the wrong gate. Nothing new is built. Its verdict is one input about one
   surface on one task — never a harness-wide "smarter or dumber" verdict.

Piece 2 is the **triage** instrument (is there a tax case worth escalating?);
piece 3 is the **decision** instrument for a named surface. Neither answers
"is the agent net smarter with charness?" — that question stays open and would
need its own deliberate, operator-approved experiment design.

## Deliberately NOT doing

- No standing A/B infrastructure, no scheduled audits, no dashboard.
- No in-session probes of any kind.
- No per-skill or per-session tax scalar; audit output stays case-shaped.
- No token-accounting script: an overhead-share trend line is a cost proxy,
  not an effectiveness measure — deferred until a real decision needs trend
  data, and advisory-only even then.
- No standing ledger trigger cadence or automatic audit threshold — a human
  decides when the case list is worth an audit.
- No transcript-compaction tooling built ahead of the pilot; the pilot names
  its preprocessing and defends it against the anti-apparatus test.
- No third confound-tracker for operator-perception drift: the ledger records
  a perception, not a measurement, and is never cited as one (covered by the
  selection-bias clause below).

## Validity threats, named honestly

- **Judge counterfactual is speculative.** Mitigation: span citations required
  (source-bound-records discipline); contested calls escalate to piece 3,
  which replaces opinion with an executed contrast.
- **Confirmation bias.** Mitigation: the symmetric rubric — (c) is mandatory,
  and the audit's judgment is net, not gross.
- **Selection bias.** Symptom-triggered audits sample bad sessions, and the
  symptom itself is operator perception (which can drift independently of any
  real tax). Accepted: this is a diagnostic instrument, not an average-effect
  estimator, and must never be cited as one.
- **Instrument bloat (the meta-risk).** If the rubric grows past a page, audits
  become standing, or a score creeps in, the disease has recurred inside its
  own cure. The bound is part of the design, not a style preference.
- **Hollow audits.** If the pilot below yields vague, non-actionable prose,
  shelve the instrument rather than tune it — a measurement that changes no
  decision is pure overhead.

## Smallest next slice (build only when triggered, with operator approval)

1. Precondition: the ledger produces ≥1 NEW entry (post-2026-07-02). Do not
   hand-pick a convenient closed session — the pilot session must trace to a
   real ledger entry AND carry a currently open or contested decision, so a
   null result is a genuine negative rather than an artifact of timing.
2. Write the ≤1-page audit rubric (portability call at build time: it likely
   generalizes, so its home is a shared/skill reference) and name the
   transcript preprocessing.
3. Run ONE pilot audit and judge it on TWO separate gates:
   - *instrument validity* — did it produce span-cited, falsifiable cases
     (including paid-off ones), not vague prose?
   - *decision utility* — did a case change at least one live
     prune/keep/keep-as-is call?
   Valid-but-no-decision-changed keeps the instrument shelved-ready (the
   session may honestly contain no tax); invalid output shelves it outright,
   recording the held-open item as "measured indirectly via compaction +
   symptom ledger only."
