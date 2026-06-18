issue(achieve): non-terminal issue-bundle closeout + design north star

Close #386.

Classification: bug (workflow-boundary propagation — terminal trust at an
irreversible boundary).

JTBD: an operator running a multi-issue closeout via achieve+hotl needs Charness
to require per-issue HOTL confirmation before an issue bundle is closed, so a
goal cannot claim "HOTL closeout" when the real evidence floor is only "local
implementation + deployment readback".

Root cause: at the issue-bundle `complete` flip (an irreversible boundary), the
distinct fresh-eye disposition review existed and ran, but had no per-issue
behavior mandate — so it re-read the bundle proxy (deployment readback + CLOSED
state) and rubber-stamped. The prose HOTL completion-audit existed but was buried
in the hotl ledger, not enforced at the achieve closeout decision. This is the
recurrence cluster's shared shape (#359/#363/#376/#381/#382/#385): a lifecycle
transition closing on aggregate/proxy proof — terminal trust at an irreversible
boundary.

Debug artifact: cite-only (causal review consumed the debug substrate cite-only;
no separate debug session).

Fix (no new gate): rather than an 8th bespoke closeout floor, this lands the
design north star (docs/design-north-star.md) — equip a capable judge; keep teeth
only where a wrong answer escapes; at irreversible boundaries success is
provisional and confirmed by a different observer and a different evidence
channel, never a terminal green — and pilots it on #386: the achieve disposition
review (Rung 2, the already-mandatory distinct observer) must now confirm each
closed issue's behavior via a channel distinct from the bundle readback/CLOSED,
or record an explicit non-verified disposition. Re-reading the proxy is not
confirmation. Rung 1 stays presence-only (no content classifier). Also clarifies
the closeout-state taxonomy (deployment[4]+CLOSED[6] do not subsume behavior[5])
and the hotl completion-audit (cite the behavior channel, not the proxy).

Why no gate: gate #8 would grant another terminal green on the agent's own
self-classification — the exact "all gates green + CLOSED = behavior proven"
equivalence that caused #386. A deterministic floor cannot make re-examination of
the same proxy honest (north star P4/P5).

Review: shaped by a 4-angle + counterweight decision premortem on the north star;
its sharpest finding — re-examination must use a distinct channel + distinct
observer, because #386's reviewer re-read the proxy — is this fix.

Siblings: causal-review four-axis scan; decision per sibling and proof level
follow. Direction-3 (verify-closeout refusing on undispositioned HOTL entries) is
a valid follow-up, deferred — a different consumer needing goal-context it does
not own. The generalized per-unit-disposition abstraction (operator-queue #381 /
blocked-matrix #385 / this) is same-class, deferred to the north-star-guided
overhaul. Proof level is static reasoning only (no runtime/provider roundtrip);
the fix is prose, verified by the closeout/achieve gate suite.

Prevention: north star P4 plus the Rung-2 per-issue distinct-channel mandate;
recurrence is caught by a sharpened distinct observer, not a new terminal green.

Critique: charness-artifacts/critique/2026-06-18-issue-386-north-star-pilot.md

Verification: skill-ergonomics sweep + 127 closeout/achieve gate tests + markdown
gate, all green. Prose-only; no code regression surface.
