# Proof-Surface Repair Retro

Date: 2026-08-13
Scope: session

## Context

Four rows a bounded closeout review had pulled back from the cohort carrier
(#597, #607, #590, #609) were repaired, reviewed in two bounded rounds each,
closed through the `issue` floor, and read back. The release-resume ergonomics
gap named by the claims-review contract was closed in the same slice.

This is the second retro dated 2026-08-13; the earlier
`2026-08-13-session-retro.md` covers a different session and is not superseded.

## Window

Start: the `docs/handoff.md` pickup naming the four held-back rows.
End: `verify-closeout --expect-state CLOSED` returning `verified` for all four,
confirmed by an independent `gh issue list` inventory (17 open remain).
Commits: `dd473642`, `dfb29e0e`, `b0eb51d5`, `022dded4`, `ff6eff4c`, `9be0e946`,
`32f9a637`, `ae118905`, `23f0735f`.

## Evidence Summary

- Two review windows, three bounded reviewers each, both
  `reviewer_boundary_fingerprint.py` verifies `clean` with empty
  `parent_declared`, each run before the first parent write.
- Two-round critique:
  `../critique/2026-08-13-four-proof-surface-repairs-two-round-critique.md`.
- Round 1 found a live defect on every surface. **Round 2 found a defect inside a
  round-1 repair on every surface** — the headline number of this session.
- Four issues closed with per-issue behavioral verdicts through channels distinct
  from the fix and from `CLOSED`: the exported plugin copies for #607 and #609,
  the live repo corpus for #597, and production GitHub state for #590 (issue
  #612, filed by a real scheduled CI run).
- Three residues filed rather than implemented: #610, #611, #613.

## Waste

- **Two full producer/consumer cycles were spent discovering a local/CI gate
  disagreement.** The local pre-push lane SKIPPED `check-changed-line-mutation-coverage`
  non-blocking (no fresh producer marker), while CI ran it and blocked. The push
  went out green and CI came back red on three lines. Cost: one red CI run plus
  two locked closeout reruns.
- **Three validator round-trips on hand-authored carrier bodies**, all from line
  WRAPPING: a `Proof:` or `population:` that landed at the start of a wrapped
  line was parsed as a new ledger field and silently removed from the field it
  belonged to. The rendered shape (`describe_closeout_draft_shape.py`) documents
  the fields; it does not warn that they are line-anchored.
- **One carrier commit was refused and its staged edit silently rode into the
  next commit.** The `#607` commit failed the commit-msg hook (classification
  inferred as `bug`), and because the loop's `git add` was file-scoped, the
  orphaned edit was swept into the `#590` carrier. Recovered, but the mechanism
  is a real hazard: a refused closeout commit leaves its staging behind.
- Not waste, and worth separating: the six reviewer spawns and their wall-clock.
  Round 2 alone caught two fail-opens and one reopened class. That is the rule
  paying for itself, not overhead.

## Critical Decisions

- **Refuse rather than silently narrow, for the `output_dir` blindness (#613).**
  Threading the record path through the claims module was the real fix and was
  too large to land unreviewed at the round-2 cap. A loud refusal blocks affected
  consumers from publishing at all — a real behaviour change — but they were
  previously publishing with no claims review, so the refusal is strictly safer.
- **Do not bundle the four closeouts into one carrier.** A bundle would force a
  single `Root Cause:` across four different defects. Four commits, four honest
  ledgers, one push.
- **Record #590's behavioral verdict as PARTIAL rather than claiming or
  declining it.** Live CI confirmed the `## Step outcomes` half in production;
  the log-tail and clamp branches are unreachable until the pipeline is red. Both
  facts are in the carrier.
- **State the claims-review residual at its real size.** Round 2 established that
  deleting the marker line and amending skips the floor entirely — an order of
  magnitude cheaper than forging a record. The non-claim now says so, rather than
  advertising a strength the floor does not have.

## Trends vs Last Retro

The prior retro's lesson was *conservative static verdicts*: keep dynamic values
`unknown` unless a parser proves them. This session is the same class one level
deeper — the repair that implemented that lesson fabricated verdicts three more
ways, and its own repair fabricated a fourth. The trend is not "static scanners
are hard"; it is that **a hand-written scanner's blast radius is unbounded until
something bounds it**. The newline bail that limits a mis-parse to one line is
the first structural answer this repo has to that.

## North Star Alignment

P4/P5 held at every irreversible boundary: four issue closes each carry a
behavioral verdict through a distinct channel or a typed non-verified
disposition; the push was granted per phase and confirmed by `ls-remote` and CI;
no release occurred. The one place the north star was nearly violated is the
`unproven` verdict — a state that exists precisely so a machine cannot be forced
to declare completion it has not observed.

## Expert Counterfactuals

**Douglas Engelbart — design Tool, Language, and Method together.** The
mandated second review round is a Method with no Tool behind it: nothing
mechanically records that a proof-surface slice owes round 2, and nothing
records that round 2 ran. This session's round 2 found blockers on three of
three surfaces, so the Method is earning its cost — but its enforcement is a
sentence in a contract file that an agent must remember to read. The
system-improving move is to make the obligation legible where the work happens:
the closeout already detects newly-added proof-surface FILES and demands a
`Fresh-eye pass:` line; the same detector could demand a round-2 marker for a
CHANGED verdict surface. That is the T that would make this L and M reliable.

**Falsification-first operator lens.** A green local gate and a green CI gate are
two different observers, and this session learned it the expensive way: the local
lane skipped the check that CI blocked on, and "91 passed, 0 failed" was true and
useless for the question actually being asked. The next move is not "run more
gates locally" but "before treating a local green as push evidence, ask which
checks the local run SKIPPED" — the runner already prints its skip policy, and
nobody read it.

## Sibling Search

- same layer: `skills/public/quality/scripts/surface_marker_lib.py`
  `nested_cli_files` | decision: intentional boundary | proof: it reads raw text
  and is deliberately wider than the seam scanner; the two counts answer
  different questions and the docstring now says they are not reconciled.
- abstraction up: the `check-changed-line-mutation-coverage` local/CI parity gap
  | decision: same waste, fix now | proof: recorded as a Next Improvement below
  with the runner's own skip-policy line as the check; not a code change this
  session because the gate's skip-when-stale behaviour is deliberate.
- specialization down: `scripts/check_quality_tool_fixtures.py` `_contained` and
  the digest branches | decision: intentional boundary | proof: every refusal
  branch already `continue`s past both counters, verified per-branch in-process.
- mental-model siblings: `skills/public/release/scripts/publish_release_post_create.py`
  distinct-channel probe | decision: intentional boundary | proof: it already
  pairs a recorded observer identity with a mechanical channel check, which is
  the shape the claims repair copied rather than duplicated.

Structural-follow-up destination: applied: the newline bail bounding scanner
mis-parses, the claims-lane preconditions moved to their owning module, and the
in-process coverage for every subprocess-only refusal; tracked issue: #610, #611,
#613.

## Next Improvements

- **workflow**: Before treating a local green as push evidence, read which checks
  the local run SKIPPED — `run-quality.sh` and the closeout both print their skip
  policy, and a skipped gate is not a passed gate. This session pushed on a green
  that had skipped the check CI blocked on.
  (recurrence-class: skipped-is-not-passed)
- **capability**: A hand-written text scanner needs a blast-radius bound before
  it needs more cases. The newline bail on `'`/`"` literals turns any future
  mis-parse from a file-wide desync into one corrupted line; prefer that shape
  over enumerating more syntax.
  (recurrence-class: conservative-static-verdicts)
- **memory**: When authoring a closeout carrier by hand, keep ledger field names
  off the start of a wrapped line — the parser anchors on line starts, so a
  wrapped `Proof:` silently leaves the field it belonged to. Three round-trips
  this session came from exactly that.
  (recurrence-class: line-anchored-ledger-fields)

## Packet Consumed

none — continued from `docs/handoff.md` Next Session, not a prepared packet.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-13-proof-surface-repair-retro.md
