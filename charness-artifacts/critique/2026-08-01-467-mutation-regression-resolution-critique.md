# Resolution Critique — issue #467, mutation test regression on main

Date: 2026-08-01
Issue: corca-ai/charness#467
Classification: bug
Fresh-eye satisfaction: parent-delegated

## What the issue actually was, versus what it looked like

The report is titled a mutation regression and leads with six survived mutants,
so the obvious reading is "kill six mutants". That reading is wrong, and acting
on it would have closed the issue without touching the failure.

The `Status: FAIL` came from ONE signal: `changed-line coverage`, on
`scripts/skill_gate_report_render.py:31`. The mutation SCORE passed at 94.9%
against an 80% threshold. The six mutants are reported under
`## Survived Mutants` as detail, and are explicitly not the blocking signal —
the report says so in its own words ("Blocking signal: changed lines were left
test-uncovered before mutation").

A resolution that killed all six mutants and left the changed line uncovered
would have satisfied the issue's most visible content and none of its verdict.

## The failure mode this resolution had to avoid

The goal that produced this closure names it: closing on a shrunken denominator.
`989a1134` is the SHA this issue measured. Between then and now, 31 commits
landed. If the resolution had re-measured against a NEW base, the changed set
would no longer contain `skill_gate_report_render.py`, the gate would report
`blocking: []`, and the issue would appear resolved — while nothing had been
proven about the line that failed.

That is why the closing comment quotes a run whose `base_sha` is literally
`989a1134f24836f5da8c7766f8570fb90edef8ce`. Same base, same denominator, now
clean. The distinct-channel confirmation (CI run 30702242447) is a second
observer on a second channel, per the north star's P4, rather than a re-run of
the same local command.

## The reviewer caught the closure asserting the defect it was closing

**This section exists because the first version of this critique, and the comment
that closed the issue, were WRONG on the load-bearing claim.** Recorded rather
than quietly amended, because the error is the interesting part.

The closing comment cited CI run `30702242447` as the distinct-channel
confirmation that the blocking signal was resolved "at the same base `989a1134`".
The bounded reviewer read `quality-core.yml` and found that job's base is
`github.event.before` — and run `30702242447` is the **second** push, so its base
is `9ea738bb`, not `989a1134`. It analyzed a three-file range that does not
contain `skill_gate_report_render.py` at all. It could not corroborate anything
about that file.

Checking that pulled a bigger thread. The FIRST push's run (`30701478239`) does
carry `"base_sha": "989a1134..."`, and its `blocking` list contains only
`ci_local_gate_parity_lib.py` — but its `changed_pool_files` (51 entries)
**does not contain `skill_gate_report_render.py` either**. The file had not been
modified in `989a1134..HEAD`; it was in the MUTATION workflow's range, which is
computed from a different base. So `blocking: []` did not mean the line was
covered. It meant the file was no longer in the changed set.

That is precisely the outcome the governing goal declared inadmissible for this
closure — "the push cannot kill a mutant, and closing on a shrunken denominator
would be the zero-denominator class committed at an irreversible boundary" — and
the closure committed it anyway, in the goal whose purpose was closing that class.

**Measured directly rather than inferred:** `scripts/skill_gate_report_render.py`
had **no test of any kind** (`grep` across `tests/` returns nothing) and measured
**0% (lines 10-34 uncovered)**. Line 31, the line #467 named, is
`blocked = status == "blocked"` — the default-derivation branch — and BOTH
production callers (`check_skill_surface_preflight.py:238`,
`skill_issue_anchor_scan.py:98`) pass `blocked` explicitly. It is public API
reachable only by a direct call: exactly the shape a changed-line gate flags and
a caller-driven suite never reaches.

Resolved for real by `tests/quality_gates/test_skill_gate_report_render.py`,
which covers both directions of the default derivation, both directions of the
explicit override, and the `Iterable` contract. Re-measured: **100%, 0 lines
missed.**

## Where this resolution is weaker than it looks

- **The local gate that produced the original evidence is itself defective**, and
  its `blocking: []` is now known to have been the wrong evidence entirely (see
  above). It printed `analyzed only 49 of 51 changed mutation-pool file(s)` and
  returned PASS; that instrument is filed as #469. The closure no longer rests on
  it: the blocking signal is settled by direct line coverage of the named line,
  which is a claim about the code rather than about a gate's range.
- **Five of six mutants were refuted, not killed.** Four of those refutations
  (the `indent` mutants) rest on a claim about consumers — that nothing parses
  this script's stdout — established by grep, which cannot see a consumer that
  builds the path dynamically. The refutation is honest but not exhaustive, and
  it is the weakest link in the closure.
- **One refutation is contingent.** The line-65 `ensure_ascii` equivalence holds
  only while `check_chunk_contract`'s message set stays ASCII-only. That is why
  a guard test pins the premise instead of the conclusion. Without it, a future
  edit would silently invalidate a written verdict in a closed issue.

## What stops this class from recurring

The recurrence risk is not "mutants survive again" — that is the workflow doing
its job. It is **closing a mutation-workflow issue on the wrong signal**: reading
the survived-mutant list as the verdict when the verdict is a separate line, or
re-measuring against a moved base.

Two things now stand against it, and only one is structural:

1. Structural: the changed-line gate binds proof to `base_sha` in its own JSON
   payload, so a resolution that re-based is visibly re-based in the evidence it
   quotes. This closure demonstrates the pattern — quote the payload including
   `base_sha`, not a summary of it.
2. Not structural, recorded honestly: the "read the blocking signal, not the
   sample list" discipline lives in this critique and in the closing comment. No
   gate enforces it. A future agent that skips both will make the same mistake.

## Sibling search

- `mutation-tests.yml` files these issues on a 12-hourly cron with an
  OPEN-issue dedupe marker. Closing #467 frees that marker. Accepted
  deliberately: a fresh issue means a fresh regression, and keeping #467 open to
  suppress a future true positive would trade a real signal for a tidy backlog.
- The same "verdict vs sample" confusion is available in any report that leads
  with examples and buries its status line. No other such report was audited
  this run; that is a non-claim, not a clean finding.

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (the repo's typed read-only reviewer agent).
- Requested spawn fields: `subagent_type: bounded-reviewer`, no host addressing/team `name` (an addressed spawn routes onto a teammate protocol whose retrieval tool is not exposed here), `run_in_background: false`. No model/effort override requested: on a Claude Code host the per-host contract uses session-model inheritance.
- Host exposure state: host-defaulted
- Application state: host-confirmed: the spawn returned findings inline in this session; the reviewer reported its own envelope as Read/Grep/Glob only.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewer was given an inline brief naming the issue, the five resolution claims, and six questions. The binding floor is therefore off by design, and this critique does not claim packet-bound identity. -->

## Boundary Ownership

- Producer: `skills/public/hitl/scripts/check_chunk_contract.py` (the JSON verdict payload) and `scripts/skill_gate_report_render.py` (the shared gate-report string).
- Consumer: an operator reading stdout, plus this repo's own test suite, which parses the payload with `json.loads`.
- Owning surface: each script owns its own output contract; the tests own its proof.
- Verdict: single-surface


Producer: `skills/public/hitl/scripts/check_chunk_contract.py` (the JSON verdict payload)
and `scripts/skill_gate_report_render.py` (the shared gate-report string).
Consumer: an operator reading stdout; plus this repo's own test suite, which parses the
payload with `json.loads`.
Owning surface: each script owns its own output contract; the tests own the proof.

Verdict: single-surface

Corrected from the first version, which said "the resolution touches one surface:
`check_chunk_contract.py` and its test file". `check_chunk_contract.py` was **not
modified at all** — the Lane C work is test-only — and the resolution also touches
`scripts/skill_gate_report_render.py`'s new test. The verdict stands, but the inventory
behind it was wrong.

Also corrected: the claim "no other module consumes that stdout programmatically". The
repo's own test suite parses it six times with `json.loads`. The `indent` equivalence
survives for a **stronger** reason the first version did not state: `json.loads` is
whitespace-insensitive, so `indent=2 → 1/3` changes no consumer's parse. That is the
premise a future editor needs, and it is not the one that was written down.

The one boundary question that arose beyond that was resolved by not crossing it: killing the
line-65 `ensure_ascii` mutant would have required changing `check_chunk_contract` in
`scripts/hitl_review_artifact_lib.py` to echo chunk text into its messages. That is a
different surface, owned by the library rather than the CLI, and the change would have
been a defect written to satisfy a mutant. Refuted in writing instead, with a guard test
pinning the premise the refutation rests on.
