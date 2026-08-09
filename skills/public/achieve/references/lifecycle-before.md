# Achieve Lifecycle — Before

Part of achieve's three-phase lifecycle contract; see `lifecycle.md` for
the overview and `lifecycle-during.md` / `lifecycle-after.md` for the rest.

## Before

Start from prose, not from an already perfect goal. Shaping happens here, in the
Before-phase (invoked via `/achieve`), never at `/goal` activation. Interview
only until the work has enough shape to save a reviewable goal artifact.
Establish:

- desired outcome
- non-goals and boundaries
- user-visible acceptance proof
- low-cost agent verification
- high-confidence or high-cost verification
- per-slice expected proof cost and expected test-duplication pressure, so a
  slice that adds or expands tests states up front whether it is likely to push
  a broad duplicate/length/pressure gate toward its threshold
- slice sequence
- critique plan
- timebox contract, when the user gives a time budget
- when the goal resolves a tracked issue: the `debug` root-cause step for a
  bug-class issue (planned *before* the fix slice) and the closeout
  close-via-`issue` step (`Close #N` on the fix/closeout commit) — see
  `references/coordination.md` *Resolving A Tracked Issue*
- stop conditions
- reporting expectations
- closeout binding plan: semantic inputs, fixed target, fresh-eye channel, lock evidence, and terminal-record rule

Ask a small number of high-leverage questions. Do not interrogate the user for
detail that a strong default or the request wording already settles.

### Backlog Recount Before Scope

Shape scope only after recounting the tracker, and record the split in
`## Backlog Recount`: `Counted:` (how many open issues, when, by what command),
`Claims:` (issues this goal takes), `Not claimed:` (issues it deliberately
leaves, with the reason).

**Counting is not re-verifying.** A recount says how many issues are open; it
says nothing about whether they are still TRUE. An append-only backlog
accumulates issues whose premise the tree has already refuted — one was found by
hand only after a reviewer round had been spent on it, and its fix quoted its own
complaint as the reason the fix existed. Before claiming or declining an issue,
render its premise state:

```bash
python3 "$SKILL_DIR/scripts/recount_premise_state.py" --repo-root . \
  --premise-file <your judgements>.json --with-bodies \
  --exclude <the goal artifact you are shaping>
```

It emits one of `premise-holds`, `premise-refuted-clean`,
`premise-refuted-with-live-residue`, or `unverifiable-by-machine` per open issue,
**and then stops** — it never closes an issue and never recommends closing one.
Read these before trusting a verdict:

- The PREMISE judgement is yours, supplied through `--premise-file`. With no file,
  every issue renders `unverifiable-by-machine`; the tool will not invent a
  judgement you did not make.
- `premise-refuted-with-live-residue` is a REFUSAL to recommend, not a close
  candidate. A refuted premise is not a close signal: the motivating instance was
  genuinely refuted and still must not close, because a further ask was live and a
  durable record had said so.
- A residue channel that did not RUN is not a channel that came back clean. Without
  `--with-bodies`, against a wrong `--repo-root`, or where every record is
  gitignored or excluded, the tool refuses rather than reporting `clean`.
- `--exclude` the artifact you are shaping, so a marker you just wrote in it does
  not come back to you as someone else's evidence.

**Residue is STRUCTURAL, and `premise-refuted-clean` is not a claim that nobody
declined.** The tool reads exactly two signals, both of which mean one thing in
every repo and every language: an explicit `Premise-residue:` marker in a durable
record, and unchecked `- [ ]` task items in the issue body. It deliberately does
**not** infer a decline from wording. An earlier version matched hand-written
English and Korean phrase lists inside proximity windows; that was repo-specific
hardcoding in a portable skill, and its window sizes had been tuned against this
repo's own backlog until the output looked right — a verdict surface fitted to its
own test set, which is the defect this seam exists to remove.

So when a record declines to close an issue, **write the marker**; nothing infers
it for you:

```text
Premise-residue: <issue anchor> — part 2 (the automated helper) is unbuilt; do not
close on part 1 shipping alone.
```

A marker needs a reason, and one inside a fenced block is skipped and reported —
so this example cannot become a live disposition.

The Before phase used to shape outcome, non-goals, boundaries, acceptance and a
slice sequence without ever opening the tracker, and `--pursue-ready` — the
surface that decides a goal may activate — validated headings, placeholders and
closeout-plan fields, so a goal whose scope contradicted the tracker passed
cleanly. A floor cannot catch what the contract never asks for. The measured
cost in one run: a duplicate issue filed, the issue the whole run was fixing
left open and unreferenced, and a known issue re-discovered and worked around
instead of linked. None of those is a judgement failure in the moment; each is
what happens when the shaping phase has no reason to open the tracker.

The floor is **presence-only, deliberately**. It never grades WHICH issues a
goal claims, because that judgement is the operator's and a floor grading it
would be a new false-verdict surface inside the tool built to stop them — it
would have to answer "should this goal have claimed that one", which nothing can
decide from the artifact. Presence makes the reasoning visible; a human or a
bounded reviewer grades it.

`Claims: none` and `Not claimed: none` are legal answers — a goal may genuinely
claim nothing tracked — but the word has to be written. An empty `Claims:` line
tells the next session exactly as much as no line at all while LOOKING
satisfied, so both are refused identically.

Scope and grandfathering, so the rule does not redden the corpus it lands in.
Two axes, and each fails CLOSED:

- **Status.** The floor is skipped only for a RECOGNISED non-shaping status —
  `active`, `blocked`, `complete` — because those artifacts' scope was set before
  the rule existed and cannot be re-decided. A missing `Status:` line,
  `Status: Draft`, or `Status: draft — slice 2 in flight` all still evaluate. It
  is deliberately not `== "draft"`: that spelling made the floor removable by
  deleting one line, and it disarmed the closeout-binding-plan gate in the same
  edit. Both now share one predicate.
- **`Created:` date.** A goal dated before the rule date is grandfathered off —
  and the report says NOT EVALUATED rather than reading as a satisfied floor. A
  missing or malformed `Created:` line evaluates.

So "the floor cannot be removed by deleting one line" is true of both axes, not
just the date.

### Mode disambiguation

One mode question is high-leverage often enough to call out: is this an
**artifact-only** goal draft (shape and save, then stop) or an
**implementation-continuation** run (the user expects slices to execute once
activated)? When the selector or prose is genuinely ambiguous between the two,
ask at least one question to resolve it before saving — a wrong assumption here
either strands a draft the user wanted executed or starts executing a draft the
user wanted only reviewed. When a strong default settles it (the prose names the
mode), state the assumed mode in the artifact and the response instead of
asking. The mode is a shaping-time intent question only; it never licenses
auto-execution, because `/goal` (pursue) and `/achieve` (shape) are separate
operator actions. This is the before-phase question-discipline contract.

### Anti-anchoring probe

For each value confirmed by the user, inherited from issue framing, or
pulled from prior session memory, test whether the value is one of a known
system axis (host, provider, environment, profile, locale, runtime, tier)
before locking the design. Record the result on each value:

- `axis: <name>` when the system already varies on that axis somewhere
  else (adapter, preset, profile, integration manifest), or
- `single-point: <reason>` when the value really is a singleton.

A confirmed value with neither record is over-anchored. This preserves the
confirmed-input over-anchoring lesson: one confirmed model name must not become
a global default when the repo runs on multiple hosts.

When the repo is known to vary on a host/provider/environment axis, do
**not** offer an `AskUserQuestion` that frames the value as a global
`confirm <value-X>` vs `defer to host` binary. Offer the family shape
instead (one option per axis instance), or ask the axis question first.

A `critique` Before-phase pass may pick the
[`confirmed-input over-anchoring`](../../critique/references/confirmed-input-over-anchoring.md)
angle to verify the probe ran honestly.

### Portability self-test

A goal artifact must be readable by a fresh session without the saving
session's working memory. Before saving the artifact at status `draft`,
the Before-phase records three durable sections inline (already present
in the template):

- `## Context Sources` — retros, prior goal artifacts, issue numbers,
  recent-lessons surfaces; what a fresh session follows first.
- `## Interview Decisions` — for each user question: the family
  considered, the chosen value, and the rejected-alternatives reason.
  This applies the anti-anchoring lesson to the artifact itself.
- `## Plan Critique Findings` — blockers folded into Boundaries /
  Verification / Slice Plan, over-worry raised but not folded, and
  reviewer provenance. Preserves the reasoning so a fresh session does
  not have to re-run critique to verify the folded revisions.

`check_goal_artifact.py` enforces these on every goal regardless of
size. A goal that genuinely has nothing for a section keeps the heading
and writes `N/A — <reason>`. The old size/marker exemption was removed:
its full-text `Single-slice goal:` scan was poisoned by prose merely describing
the marker, and the template already seeds all three headings, so the exemption
was both unsafe and redundant.

When shaping an auto-drafted skeleton, overwrite its
`To be filled by the achieve Before-phase` placeholder lines with the real
content — a leftover marker leaves the goal reading as unshaped to the
pursue-readiness check, which would make `/goal` fail-fast on an
actually-shaped goal.

Save the artifact with `upsert_goal.py` at status `draft`. Tell the user the
file is inert until they run the activation command. The skill does **not** start
executing slices on its own — activation is the user's explicit decision.

### Drafting does not consume the host goal slot

The Before-phase is artifact-only. Saving a draft must never consume the host's
active-goal slot: while shaping, do **not** call any host goal-creation or
goal-tracking tool (`/goal`, the Codex `update_goal`/`get_goal` thread-goal
surface, or the host equivalent). The host active-goal slot is host-owned — the
Claude `/goal` Stop-hook, the Codex thread-goal slot — and `achieve` coordinates
it without reimplementing it; the slot is consumed **only** at `/goal @artifact`
pursuit, the operator's explicit pursue action.

This is the symmetric counterpart of the After-phase rule that host-level goal
completion is downstream of the artifact. A draft artifact is planning/shaping
work, not the goal being pursued, so it must not register itself as host-active:
otherwise the next goal creation trips a "goal still active" slot conflict until
the operator manually clears the slot — exactly the friction this boundary
removes.

Host-runtime residual (honest boundary): the portable contract above is uniform
across hosts and needs no adapter knob, because the rule is always "never consume
the slot while drafting." If a host treats mere artifact creation as goal
activation regardless of the agent's tool calls, that is a host-runtime
limitation outside `achieve`'s control — record it as a non-claim and raise it
with the host rather than faking a portable fix.

### Activation-closeout clarity

The before-phase response must make activation impossible to miss. Close it with
an explicit checklist the operator can act on without rereading:

- `Goal file:` — the saved artifact path under `charness-artifacts/goals/`.
- `Activation:` — the exact `/goal @<path>` line to run.
- the inert-until-`/goal` status stated in one sentence (nothing runs until
  the user activates).

`check_goal_artifact.py` already fails closed when the artifact body is missing
its `Activation:` line; this closeout checklist is the response-side counterpart
so the operator-facing handoff is as clear as the artifact contract.

### Activation = Pursue Only

`/goal @<artifact>` is **pure pursue**: it runs the During loop on the goal as
given and never shapes. Shaping is the Before-phase's job (invoked via
`/achieve`); whoever runs `/goal` is responsible for handing it a shaped goal.

Before pursuing, confirm the goal is shaped with
`check_goal_artifact.py --pursue-ready --goal-path <artifact>`. If it is
**unshaped** (the Before-phase placeholder marker is still present — e.g. a raw
handoff-chunker auto-draft that was never `/achieve`'d), **fail-fast**: refuse to
pursue and route the operator to the Before-phase (`/achieve @<artifact>`). Do
**not** shape the goal inside `/goal` — that would put shaping back into the
pursue path, the exact responsibility blur this boundary removes.

Unshaped has **two** forms, and the second is the one that reads as ready. A
placeholder marker means the sections exist and were not filled; an artifact
whose sections were never WRITTEN carries no marker at all, so marker-absence is
not shaping-presence. `--pursue-ready` therefore also requires every required
and portability H2 heading to be present, and refuses with
`incomplete: N required section heading(s) absent (...)` naming each one. This
is the only gate in front of `/goal`, and the sections it would otherwise skip
(`Boundaries`, `Slice Plan`, `User Acceptance`) are exactly what bounds an
autonomous run — a goal with no `Boundaries` section has no recorded
external-side-effect scope and no stop conditions.

A third refusal guards the heading reading itself. Fence masking **fails open**
on an unclosed fence and hands back the raw text, so every `## Heading` inside
that fence would count as present — an artifact with all of them fenced away and
no real sections would otherwise read as complete. On an unbalanced document the
gate refuses with `unreadable: ...` naming the unclosed fence, the same bytes `check_goal` already refuses, rather than
rendering a heading verdict over a reading nobody established. The payload
carries `fences_balanced` and `sections_reading_established` so a machine caller
can see which reading the heading facts came from.

The mode stays deliberately narrower than the full `check_goal` sweep, so it
carries `scope_not_checked` in its payload naming what its verdict does **not**
establish (status validity, activation-line shape, closeout evidence, and the
CONTENT under each heading). Read the scope from the answer; a green here is a
claim about markers, headings, fences, and operator discussion — not about what
is written under the headings. `reason` names **every** refusal clause, not only
the first, so fixing the one it named does not surface a second on the next
attempt, and the PASS sentence states its own scope too.

### Consequential Discussion Before Activation

Structural readiness is not enough when the goal contains consequential
defaults. Before reporting an artifact as ready for `/goal`, surface a
non-empty `Discuss before activation:` summary when `Non-Goals`, `Boundaries`,
`Agent Verification Plan`, `Interview Decisions`, or `Plan Critique Findings`
contain decisions about live/prod proof, issue close/split, broad bundled scope,
irreversible side effects, or proof-level non-claims. The deterministic
`--pursue-ready` gate distinguishes this from placeholder shaping: such a goal
is shaped, but not operator-ready, until the discussion summary is visible before
the Slice Log and explicitly marked resolved, confirmed, or approved. A visible
summary is a floor, not completion: before offering activation or reporting the
goal ready, bring those items into the transcript and resolve or explicitly ask
about them. Helper output separates `shape_ready` from `activation_ready`;
`pursue_ready` is the activation-ready signal and must be false while
consequential discussion is only surfaced.

### Timebox Mode

When the user gives a fixed work budget ("for 3 hours", "exactly 2 hours",
"spend the next slice"), shape the goal as **timebox mode** instead of only a
macro-outcome checklist. The artifact records:

- `Timebox: <duration>` — the work budget, e.g. `3h` or `180m`.
- `Activation time: <ISO>` — the timestamp the active run started.
- `Closeout reserve: <duration>` — time reserved for final proof, artifact
  update, critique, commit, and user closeout; default to `20m` unless the user
  chose a different reserve.
- `Done-early policy: continue_next_improvement` — if the macro goal finishes
  before the closeout reserve window, immediately choose another safe
  improvement instead of closing because the first backlog item ended.

This field set makes a time budget operational: it tells the next session when
the clock started, how much closeout time to protect, and what to do if the
first slice finishes early. A timebox goal may still stop early when continuing
would be unsafe or needs a user decision, but that is evidence, not vibes. Before
the closeout reserve window, a one-line `No safe next slice:` or
`Early close rationale:` is not enough: under `## Final Verification`, record
one early-close reason, at least two candidate ledger lines, and an outcome
sufficiency check. `references/goal-artifact.md` *Timebox Fields* owns the exact
ledger form, the valid decision/sufficiency enums, and the required
`Early close report: <path>` line — this is the only place that form is written
out; the report is required even when the early stop is correct, because
correctness does not remove the communication duty.
