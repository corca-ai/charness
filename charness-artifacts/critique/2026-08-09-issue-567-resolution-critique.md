# Issue #567 Resolution Critique
Date: 2026-08-09
Fresh-Eye Satisfaction: parent-delegated

## Reviewer Tier Evidence

- requested tier: `bounded-reviewer` typed subagent, read-only by definition
- requested spawn fields: inherited parent model and reasoning settings; no
  per-subagent model or effort override requested; spawned unnamed
- host exposure state: host-defaulted
- envelope note: the spawn envelope exposed Read/Grep/Glob only; the reviewer
  confirmed Bash/Edit/Write/Agent were absent and listed the evidence it could
  not obtain rather than inferring it
- application state: spawn tool accepted the reviewer agent id; reviewer-tier
  application details are host-hidden
- Delivery state: findings-received

## Decision Under Review

Closing `#567` on `ca83a119`, whose message states "the repair for #567" and
which is slice 1 of the proof-surfaces goal. The issue reported two problems.

Problem 1: `plan_handoff_run.py` was the only planner in the repo branching on
natural-language keyword matching. It asked the MODEL to retype the user's
message into `--invocation-text`, then keyword-matched that retyping. Two pattern
lists disagreed about the same word, and the single Korean entry matched only the
spaced form because Hangul is `\w` and Korean attaches particles directly — "two
misses cancelling is not the same as working".

Problem 2: the docs surface was the only gated surface with no
rules-before-authoring mode, so an author got no constraints up front AND a
checker that needed the mistake to exist first — one rework cycle structurally
guaranteed.

`#567` also WITHDREW a third claim in its own body (that `gate_packets` omitted
`check_doc_links.py`); the planner pointed at the wrapper, which was correct.

The parent's initial reading was that problem 1 was fixed and problem 2 was
unverified. Measurement corrected that: problem 2 is implemented too, which is
what moved the disposition from re-scope to close.

## Failure Angles

- **Relocated, not closed.** The issue's comment names a deeper root cause: the
  same classification rule implemented three times for three executors. Deleting
  the planner's copy fixes one.
- **A rules mode that recites instead of deriving** would be this repo's live
  defect class rather than a fix for it.
- **A new gap introduced by the removal** — dangling callers, stale fixtures,
  shipped prose still naming a deleted flag.

## Findings

Twelve. One BLOCKER, five DISCLOSE, five CLEAR, one evidence request.

**BLOCKER (finding 11): the repo's own pickup surface still instructed the next
session to re-scope `#567`.** `docs/handoff.md` carried "re-scope `#567`" as Tier
0 pre-work and again as a next action — lines this session wrote hours earlier.
Closing without rewriting them would leave the next session working a closed
issue, the exact stale-next-action class the handoff exists to prevent, and a
durable record would still say the correct disposition was re-scope. Repaired:
both lines now state the close and its actual blocking condition (an unpushed
carrier), and the closeout says why close supersedes re-scope.

**CLEAR (1): problem 1 is genuinely gone from the planner.** Routing resolves
only from `--intent` / `--invoked-directly`; `--invocation-text` is absent from
the parser; `should_fire_chunker` is deleted with a note where it lived. Tests
pin the repaired behavior including the refusal-to-guess arm. The plugin export
is in sync.

**CLEAR (4): problem 2(a) is closed to a high bar.** `scripts/doc_authoring_rules.py`
renders every rule by PROBING the owning validator — link forms through
`validate_link`, backtick classes through the gate's own remedy constants, the
length cap live from the owning module constant, and the regenerable-facts
headline by making the real validator raise it. Its tests pin derivation rather
than text. This is not a recited hardcoded list, which is the standard the issue
held the goal-closeout describer to.

**CLEAR (6, 7): problem 2(b) and 2(c).** The handoff SKILL now says the
authoring-rules preflight is the one to run BEFORE writing, and the planner
emits it as a `required_reads` entry with the rules-mode command while keeping
the content check as a separate gate packet.

**CLEAR (10): nothing else consumes the removed surfaces.** No live caller, hook,
preset, doc instruction, or test asserts the removed behavior. The only hits are
deliberate deletion notes, a negative assertion, historical artifacts, and an
eval spec that labels its prior sentences as HISTORY.

**DISCLOSE (2): the keyword list survives as two hand-maintained prose copies,
and they have already diverged.** `skills/public/handoff/references/chunked-routing.md`
and `docs/handoff-chunked-routing.md` both retype the rule, and they disagree
today: the reference hardcodes the literal token `docs/handoff.md` while the docs
copy names the artifact path indirectly and adds a case-variant clause the
reference lacks. The reference is the copy that ships to consumers, and it
hardcodes a path the adapter can override — so a consumer with `output_dir`
overridden ships a token list naming a file it does not have. Mitigating: both
say the signals are examples, not a closed list, so a judge can generalize. The
"same rule, three implementations" count is now two, not one.

**DISCLOSE (3): the specific Korean miss is not repaired in the surviving prose.**
The reference still lists only the spaced form. What fixed the defect is the
deletion of the matcher, not any repair to the list.

**DISCLOSE (5): the rules mode has one real carve-out.** markdownlint is not
rendered without a target — the list-marker and trailing-space class an author
trips first is still discover-by-failing. The output is honest about this; a
claim of "the full constraint list before a line exists" would not be.

**DISCLOSE (7, caveat): the rules read is emitted only when the next action is a
writing action.** A plain pickup and an undeclared run get none. Deliberate, and
tested.

**Repaired here (finding 9): the availability probe checked one file while the
emitted command imports two.** The probe gated on
`scripts/check_doc_authoring_preflight.py` existing, but the rules mode imports
`scripts/doc_authoring_rules.py` at runtime — so a partially vendored repo got a
command that dies on import, advertised as an available read. Worse, the test
seeded exactly that partial state and asserted the read WAS emitted, blessing it.
The probe now covers both files, and the test asserts that deleting the
runtime-imported half SUPPRESSES the read. Mutating the fix back to the
one-file probe fails that test, so the repair has teeth.

**Filed, not fixed (finding 8): `#570`.** `run_chunked_routing` is in
`WRITING_ACTIONS` and gets briefed with `--as-surface handoff`, but a
chunked-routing run must never write the handoff, and the file it does write is
produced by a generator — the category the set's own comment excludes two lines
above. Filed rather than fixed because choosing among the three remedies is a
judgment call about what such a run authors, and no test pins the arm in either
direction.

## Counterweight Pass

The angle that paid was "relocated, not closed", and it paid in a form the parent
would not have found: not in code, but in this repo's own handoff, which the
parent had itself written and would have shipped contradicting the close.

The angle that did NOT pay was "a rules mode that recites instead of derives".
The reviewer checked it against the strongest available standard and found the
implementation probes the owning validators throughout. Recorded so the next
reviewer does not re-run it.

## Boundary Ownership

- Producer: `scripts/check_doc_authoring_preflight.py`, which owns whether a
  rules-without-target answer exists and what it contains.
- Consumer: `plan_handoff_run.py`, which decides whether to advertise that
  command as an available read.
- Owning surface: the consumer, for the availability question repaired here. The
  producer's dependency on `doc_authoring_rules` is its own business; what was
  wrong was the consumer probing a narrower set than the command it emits needs.
- Verdict: owned-correctly

The repair lands on the consumer because the defect was a consumer-side claim
("this read is available") made from an incomplete probe of the producer. Nothing
was pushed onto the producer, and the deeper runtime chain — the emitted command
also needs the bootstrap module and the link checker — is deliberately NOT
probed: that is owned by the producer's own tests, and duplicating it in the
consumer would recreate the drift this issue is about.

## Will The Class Recur

Partly, and the honest residual is finding 2. `#567`'s root cause as stated in
its own comment is one rule with several implementations. The Python copy is
gone; two prose copies remain, already divergent, one of them shipped to
consumers. That is a smaller and more legible version of the same shape, not its
elimination, and it is named as a non-claim in the closeout rather than papered
over.
