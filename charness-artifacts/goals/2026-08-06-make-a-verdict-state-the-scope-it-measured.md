# Achieve Goal: Stop a surface from returning success its own evidence contradicts

Status: draft
Created: 2026-08-06
Activation: `/goal @charness-artifacts/goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md` after confirming the draft is
  still intended.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue

Both shaping decisions were RESOLVED by the operator on 2026-08-05 and are folded
into `## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

1. **What is the unit of the goal?** Family considered: {#487+#488 only, as the
   operator first said; add #489; add the unreachable-file cluster}. **Chosen by
   the operator 2026-08-05: #488 + #489 + #487.** #488 and #489 are genuinely the
   same class and share a ruler, so splitting them would stand the same reviewer
   up twice; and leaving #489 out strands the residue the previous goal's own fix
   created. The unreachable-file cluster was rejected as a second, heterogeneous
   family that would put the timebox at risk. Anti-anchoring: `axis: three
   symptoms in one session is evidence of a class only if the MECHANISMS match —
   check before unifying`. That check is why #487 is carried but explicitly not
   folded into the class.
2. **#489's direction.** Family considered: {let `deliberately_absent` name dotted
   sub-keys; report an honest status; decide after replaying the merge}. **Chosen
   by the operator 2026-08-05: report an honest status first** — `augmented` plus
   the refilled sub-keys, instead of `preserved`. The false statement is the part
   that misleads a reader, and removing it needs no schema change and breaks
   nothing. The dotted vocabulary was rejected FOR NOW as a larger verification and
   ambiguity surface, not as wrong. Anti-anchoring: `axis: the smallest honest
   change is the one that stops the surface from asserting something untrue, not
   the one that makes the feature complete`.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
