# Step 0 experiment design v2 (post design-critique)

Status: FOR OPERATOR APPROVAL. Execution post-compaction. Reflects 3 fresh-Opus
methodology critics who converged that the v1 toy design was substantially flawed.

## Why v1 was scrapped (convergent critique)

- **Ask-to-verify / task-scope confound (blocker).** v1's C1 ("decide if it can close")
  made verification the task; C2 (changelog/notes) did not — so C1-vs-C2 swapped ~5
  factors and a C2<C1 result could mean "never asked to verify," not "salience decayed
  under load." Uninterpretable.
- **A fresh subagent cannot instantiate context LOAD (blocker).** 8 tickets = breadth,
  not depth/accumulation/fatigue. v1 would measure instruction-salience and mislabel it as
  load — the one variable H names is the one the apparatus could not create.
- **Underpowered + no pre-committed numeric rule (blocker).** n=8-10 binary: a noisy null
  is the default, so the STOP-on-null rule would FALSELY falsify H.
- **C3 rescue foregone + tests the wrong failure mode.** Fresh sole-task catch is already
  ~100% (5 prior rounds). The real routing risk is SUMMARY-LAUNDERING: production reviewers
  read the doer's "verified" claims, not raw state — exactly how #386's fresh reviewer was
  fed. v1's clean re-framed C3 cannot reproduce that.
- Plus: serial-position uncontrolled; entangled-doer/sunk-cost absent; caught-but-silent
  not separated from didn't-catch.

## Revised instruments (lead with cheapest + most faithful)

### Instrument 0 — real-history mining (LEAD)
charness HAS the real #386 + recurrence-family long sessions; the failure exists in the
wild. Mine the actual closeout artifacts, `charness-artifacts/metrics/rca-ledger.jsonl`,
commit bodies, and any captured reviewer output for #386 and its family
(#359/#381/#382/#385 + the mutation-CI family) for the proxy-trust signature:
closed-on-readback / CLOSED-state, no behavioral exercise, reviewer re-reads the same
channel, doer's summary asserted "verified." Classify the OPERATIVE mechanism per instance:
{context-load/fatigue | entangled-doer/sunk-cost | summary-laundering | never-asked-to-
verify | other}. Output = base rate + dominant mechanism. Faithful by definition; may
directly answer the question (collapsing the toy) or redirect the hypothesis (our
"load/salience" guess may be wrong; the real driver could be summary-laundering).

### Instrument 1 — salience-mechanism contrast (only if mining warrants isolating salience)
Hold the verification DUTY constant; vary ONLY salience.
- **C2-non-salient:** sprint wrap-up; deliverable = per-ticket closeout row
  {changelog line, point total, close-readiness READY/HOLD}; the READY/HOLD call buried
  last; closure a side-effect; no priming.
- **C2-salient:** identical, but the READY/HOLD call is the FIRST named deliverable.
- **C1 (ceiling-sanity GATE only):** isolated "decide if SVC-4471 can close." Gate: if
  C1 catch < 0.80, the fixture is dead-on-arrival — fix it before interpreting anything.
- Controls: target serial-position varied (early/mid/last); blind raters + kappa +
  pre-registered "catch" rubric (subject outputs HOLD / flags missing behavioral
  verification for SVC-4471 specifically); identical post-hoc elicitation across cells
  ("any ticket you would NOT close? why?") to separate didn't-catch from caught-but-silent.
- **Pre-commit BEFORE running.** n ≥ 16-20/arm. CONFIRM: catch(C2-non-salient) <
  catch(C2-salient) by ≥ 0.40 absolute AND 95% CI of the difference excludes 0.
  FALSIFY: catch(C2-non-salient) ≥ catch(C2-salient) − 0.15. INCONCLUSIVE: between, or CI
  too wide → re-run / escalate load; do NOT narrate a winner. If n < 16, downgrade ALL
  results to "directional pilot, not a falsification."

### Instrument 2 — load axis (optional; only if salience confirmed and depth matters)
Drive ONE agent through N genuine prior multi-step turns before the identical closeout;
vary N (0 / ~30 / ~80); measure catch vs DEPTH. Real accumulated context IS testable via
multi-turn driving (contra "structurally impossible") — but costly. Alternative: instrument
the MAIN agent at a real long closeout.

### Instrument 3 — routing premise (separate; where Track 1a lives or dies)
- **C3a:** fresh reviewer + RAW end-state → ceiling check (assumed ~100%, small n).
- **C3b:** fresh reviewer fed the DOER's summary/changelog claims ("SVC-4471 verified")
  instead of raw state. If C3b catch < 0.80 → a routing fix that lets the reviewer read
  doer artifacts INHERITS the rubber-stamp → Track 1a's "reviewer PULLs raw state, doer
  does not author the brief" is load-bearing and must be enforced. If C3b ≥ 0.80 →
  freshness alone suffices and 1a can be lighter.

## Sequencing
0 (mining) → (if warranted) 1 (salience) → (if warranted) 2 (load). 3 (routing premise)
runs independently to settle whether Track 1a's PULL-raw-state requirement is load-bearing.

## Honest note
If Instrument 0 shows the real mechanism is NOT load/salience (e.g., summary-laundering or
entangled-doer), the whole v2 plan's "fresh sole-task reviewer restores judgment" premise
is wrong as stated and must be re-derived from the real mechanism. Instrument 0 can
invalidate the hypothesis cheaply — which is the point.
