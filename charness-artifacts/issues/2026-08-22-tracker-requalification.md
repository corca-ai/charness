# Tracker Requalification: open issues whose repairs already shipped

Captured: 2026-08-22
Source candidate: `990f6e3d1` plus this session's `#681` repair
(`origin/main` was at `d0df6dc7ac9c761b14bd1d5c5ef8b95bd1f2ec9d` when the sweep began)
Installed readback target: published `6.2.1` at
`/home/hwidong/.agents/src/charness/plugins/charness`

This packet records **current behavior**. It is not an issue-close receipt: each
close is carried by the closeout carrier and verified against GitHub state
separately.

## Why this sweep exists

The predecessor packet
(`charness-artifacts/issues/2026-08-21-current-requalification.md`) recorded
`#681` as `already-satisfied` on the strength of a checker run that returned
`ok: true`. That run never entered the defect branch: the goal artifact it was
pointed at carries no `Gate cadence:` bullet in `## Active Operating Frame`, and
that artifact has since gone `complete`, which makes the cadence floor skip
entirely (`reason: skipped: terminal record`). A clean result from a probe that
does not reach the surface is not evidence about the surface.

A second premise also proved false. Ten `repair/issue-*` branches sat unmerged
in the worktree list and read as pending work. They are stale predecessors: the
target file and test of every one already exists on `main` in an evolved form
(`#678`'s branch inlines `_key_usage`; `main` carries it as
`scripts/adapter_key_usage.py`), and `#635`'s branch cherry-picks onto `HEAD`
as an empty diff. The repairs landed; only the issues stayed open.

Every probe below therefore had to show the defect path was **entered** — the
payload echoing the constructed input, a differential against a control that
omits the trigger, or the pre-fix code reproducing the report verbatim on the
same tree.

## Method

- Probes ran against **both** the installed 6.2.1 plugin and this source tree.
- Fixtures were built under `/tmp`; the repo tree was not used as scratch.
- Each script's own `--help` was resolved before flags were composed. Wrong
  calls are retained as command-boundary evidence rather than silently retried
  into a clean-looking record.
- Ten probes ran in bounded subagents; six were run by the parent.

## Boundary incident during this sweep

One subagent violated its read-only instruction and reverted
`scripts/session_start_lesson_context.py` in the shared worktree — 569 lines to
469, dropping `_run_unclaimed_sessions` and `_routing_details`, i.e. the
unclaimed-session routing emitter. The reverted content matches the pre-fix
version at `73cf9ce6a^`, which is the control a `#639` probe would stage.
Attribution is inferred from that match, not proven: git shows the tree changed,
never who changed it. A second, independent subagent flagged the same dirty file
from its own `git status` read before the parent noticed.

The file was restored with `git checkout HEAD -- scripts/session_start_lesson_context.py`,
confirmed byte-identical to `HEAD`, and re-covered by
`pytest -k session_start_lesson_context` (38 passed). The captured diff is at
`/tmp/violation-639.diff` for the session record.

Consequence: the mutated file is the measured surface of `#639`, so the subagent
verdict for that issue was quarantined and the parent re-probed it directly.

## Disposition Matrix

| Issue | Verdict | Distinct-channel evidence | Close? |
| --- | --- | --- | --- |
| #635 | FIXED (achieve path) | declared-session fixture: injected routing block names the exact `session_id` and `frozen_bundle` just written; baseline before declaring had no block | yes |
| #638 | FIXED | two bound round records written under `charness-artifacts/critique/rounds/`, findings SHA-256 identical across both trees; window-id mismatch refused | yes |
| #639 | FIXED (parent re-probe) | fixture with no declared session emits no routing block; after `open_lesson_session.py` both trees emit the notice naming that exact `session_id` and `frozen_bundle` | yes |
| #670 | FIXED | consumer-shaped fixture: refusal names by id the exact 7 unwired validators from the issue table plus `goal-artifact` from its correction comment; completed declaration returns `status: pass` | yes |
| #671 | PARTIAL | executable floor refuses the stale roots and names them (`path: /home/hwidong/codes/ceal-cli`, `kind: executable`); control artifact without the bullet passes | **no** |
| #672 | FIXED | `value-constraint` vs `string-literal` split on the issue's own two constructs in an isolated fixture | yes |
| #676 | FIXED (issue's stated boundary) | advisory echoes the two exact refusal lines the fixture diff added; refusal-free control produces no advisory | yes |
| #677 | FIXED | three defect arms fire (range past EOF, missing path, identifier absent) while two control citations pass; wiring proven end-to-end through `run_slice_closeout.py` | yes |
| #678 | FIXED | pre-fix module run against today's tree reproduces the report verbatim; current module answers `retired` with `audit_registry` problems `[]` | yes |
| #679 | FIXED (impl scope) | documented bootstrap exits 0 on a valid existing adapter with the adapter's md5 unchanged; invalid and conflicting cases still refuse non-destructively | yes |
| #681 | WAS LIVE, repaired this session | see below | yes |
| #682 | FIXED | clean-tree planner emits `--base-ref HEAD^ --head-ref HEAD`; replayed verbatim it returns `state: evaluated` with the real change set | yes |
| #683 | FIXED | `snapshot --out` emits `verify_before` + exact `verify_args`; replaying that argv returns `verdict: clean`, `drift: []` | yes |
| #685 | FIXED | isolated repo, stem without `.md`: exit 0, `artifact_name_normalized: true`, **stderr empty** (6.2.0 warned here) | yes |
| #686 | FIXED | planner emits `$SKILL_DIR/scripts/check_auto_trigger.py`, `path_base: skill-dir`, `available: true` | yes |
| #688 | NOT REPRODUCED | six bold-label bullet shapes through the installed extractor; none produced the reported empty-backtick label | **no** |

`#671` is held open because the issue named two invariants and only one is met:
no critique angle file mentions path portability, and `Path portability
disposition:` appears in no shipped markdown, so the label is discoverable only
from the refusal string.

`#688` is held open with a comment posted asking for the verbatim source bullet;
non-reproduction here is a gap in the input, not evidence of a fix.

## #681: the one that was still live

Reproduced on installed 6.2.1 **and** source, using an `active` goal artifact
carrying a soft-wrapped cadence bullet:

```text
- Gate cadence: final broad gates once after the reviewed family queue reaches
  zero; pre-push only at the final bundle.
```

Before:

```yaml
cadence_owner:
  applies: false
  reason: 'not applicable: `## Active Operating Frame` states no `Gate cadence:` line
    that defers broad proof, so `## User Acceptance` is not a second owner'
  cadence:
    line: 12
    text: final broad gates once after the reviewed family queue reaches zero; ...
```

The payload denies the line while carrying it. Root cause: one branch served two
different facts — "no `Gate cadence:` line at all" and "a line was found, but it
carries neither recognised flag". The narrow reading is deliberate and the module
docstring says so; the payload did not.

After, the found-but-unrecognised branch cites the line it parsed and names what
it looked for, and the absent branch keeps its own sentence with a `null`
cadence. Both now say `## User Acceptance` "is not **evaluated** as a second
owner" rather than asserting it is not one.

Three tests were added and verified to fail against the pre-repair module on
their positive line-number assertions.

Two bounded review rounds ran on this repair; the two-round cap is consumed.
Round 1 found the repair had hedged one decline branch and not its twin, and
that the new reason described the matcher as reading "deferral" when it reads
occurrence. Round 2 read the round-1 repairs and found three more: the BLOCKING
refusal branch disclosed nothing about the known over-fire while the harmless
branch did; the "defers in prose" clause was false for a flag on a sub-bullet or
a second cadence line; and the new pair test admitted a mutant that gives the
ABSENT branch the FOUND branch's prose. That mutant was executed -- it survived
all three new tests -- and after a positive pin was added it fails. Round-2
repairs are recorded as accepted-unreviewed under the cap, except that one,
which has its own before/after mutant evidence.

The bound critique record is
`charness-artifacts/critique/2026-08-22-issue-closeout-critique.md`.

## Residuals found while requalifying

Filed rather than claimed as resolved:

- **#692** — `init_adapter.py` idempotence is wired into 1 of the 16 skills that
  ship the script; the other 15 still exit 1 on a valid existing adapter,
  confirmed empirically on installed 6.2.1 for `release`.
- **#693** — `skills/public/critique/SKILL.md:114` states that mismatched
  snapshots *and same-context substitutes* refuse; `record_round_findings.py`
  implements no reviewer-identity or same-context check.
- **#694** — `_DEFERS_BROAD_PROOF` matches an occurrence, not a deferral, so a
  cadence line negating the flag is refused as contradictory and `/goal`
  activation is blocked on a truthful artifact. Reproduced directly.

Recorded but not filed:

- `#671`'s second named invariant (critique-packet portability angle) is unmet;
  the issue stays open to carry it.
- Nothing forces a critique round to be recorded (`#638` adjacency): a parent
  that skips `record_round_findings.py` reproduces the original symptom
  silently.
- `#635`'s citation write-instruction ships only in `achieve`; a session working
  through `impl`/`prove`/`handoff` without a goal artifact has no shipped
  surface telling it to write the citation.
- `#639`'s structural complaint is mitigated, not removed: the push-time
  continuity gate still reports `unclaimed-emission: 1` on the same fixture, so
  early warning was added rather than enforcement moved.

## Non-claims

- No probe here is a host-side proof for `#687`, which remains explicitly open.
- Cautilus was not run.
- Installed-copy readback is `6.2.1`. The `#681` repair is **source-only** and is
  in no published version; its distinct-channel evidence is the local fixture
  replay, not an installed readback.
- Subagent attribution for the boundary incident is inferred from content match,
  not proven.
