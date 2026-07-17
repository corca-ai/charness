# Achieve Goal: Implement the #444 deferred polish (pause-case header/footer in _format_failure plus a template-vs-regex pause-vocabulary drift test) as a real slice, and run the prove dogfood consumer prompt against that slice to promote prove's review_status to reviewed and add prove to review_required_skills.

Status: complete
Created: 2026-07-17
Activation: `/goal @charness-artifacts/goals/2026-07-17-prove-dogfood-via-444-polish.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: both slices done (`963e147c`, `b1b74e0c`); closeout in
  progress (disposition review, complete flip, closeout commit, handoff refresh).
- Current slice: closeout.
- Next action: bind the disposition review, flip `Status: complete`, commit
  the goal + retro artifacts, refresh `docs/handoff.md`.
- Verification cadence: focused pytest on the touched test files at each slice
  commit; `run_slice_closeout.py --verification-lock` with mutation coverage at
  the final mutating closeout; dogfood registry validator after the promotion
  edit.
- Slice review packet: intent, changed files (`scripts/check_issue_closeout_commit_msg.py`,
  `scripts/public_skill_dogfood_lib.py`, their `plugins/` mirrors,
  `tests/test_check_issue_closeout_commit_msg_inprocess.py`,
  `tests/quality_gates/test_public_skill_dogfood.py` — the critique-driven
  drift pin, a mid-goal scope addition — and
  `docs/public-skill-dogfood.json`/`.md`), invariants (pause-only failure text
  names the provenance remedy; mixed/normal failures keep the generic text;
  drift test reads the template, not a copied literal), proof commands, and the
  non-claims listed under `## Final Verification`.
- History boundary: keep this frame current during the active run; move
  completed detail to `## Slice Log`, `## Operator Decision Queue`,
  `## Final Verification`, and `## Auto-Retro`.

## Goal

Implement the #444 deferred polish (pause-case header/footer in _format_failure plus a template-vs-regex pause-vocabulary drift test) as a real slice, and run the prove dogfood consumer prompt against that slice to promote prove's review_status to reviewed and add prove to review_required_skills.

**Source handoff entry #1: After `charness update` + restart: run the prove dogfood consumer prompt on a real slice, promote `review_status` to `reviewed` with observed evidence, and add `prove` to `review_required_skills` (#442 recorded this as the one deferred sub-item; the substance floor is already in place)**

> After `charness update` + restart: run the prove dogfood consumer prompt on
>    a real slice, promote `review_status` to `reviewed` with observed evidence,
>    and add `prove` to `review_required_skills` (#442 recorded this as the one
>    deferred sub-item; the substance floor is already in place).

---

**Source handoff entry #3: Deferred from #444's critique (fails closed, separable): pause-case header/footer polish in `_format_failure`, and a template-vs-regex pause-vocabulary drift test**

> Deferred from #444's critique (fails closed, separable): pause-case
>    header/footer polish in `_format_failure`, and a template-vs-regex
>    pause-vocabulary drift test.

## Non-Goals

- Not a release: no plugin version bump expected.
- Do not absorb adjacent handoff entries beyond the selected chunk.

## Boundaries

- In scope: `scripts/check_issue_closeout_commit_msg.py` (`_format_failure`
  only), `scripts/public_skill_dogfood_lib.py` (`PROMPT_HINTS["prove"]` only),
  their `plugins/charness/scripts/` mirrors,
  `tests/test_check_issue_closeout_commit_msg_inprocess.py`,
  `tests/quality_gates/test_public_skill_dogfood.py` (added mid-goal for the
  critique-driven md↔json drift pin),
  `docs/public-skill-dogfood.json`, `docs/public-skill-dogfood.md` (including
  repairing the pre-existing achieve/hotl omission in its required list), and
  this goal artifact plus the closeout handoff refresh.
- Out of scope: the pause carve-out predicate itself (`_PAUSE_BRIEF_RE`,
  `evaluate`), the resolution-brief template wording, any `prove` skill body
  change, and any release/version bump.
- Portable per implementation-discipline: no host-specific assumption; the
  drift test reads the checked-in template file, not installed-plugin state.
- External writes: none. Commits stay local; push is queued in the Operator
  Decision Queue (autonomous session, no push approval in the request).
- Stop conditions: the prove consumer run routing to a different skill or
  failing to execute (report the concrete signal, leave `review_status`
  untouched); the commit-msg hook rejecting the slice for a reason outside the
  polish scope; any validator demanding a change outside the in-scope paths.

Discuss before activation: resolved — two consequential defaults are settled by
the operator's standing directives rather than a live question. (1) Promotion
proof level: `review_status: reviewed` will claim exactly one live consumer-run
observation on this host plus deterministic validator/test evidence, with
explicit non-claims (no Cautilus run, no cross-host proof); this is the proof
shape handoff `## Next Session` item 1 itself prescribes, and the restart
precondition it named is observed satisfied (this session's installed surface
exposes `charness:prove`). (2) No push: commits stay local and the push is
queued as an operator decision, matching achieve's no-external-side-effect
default for an autonomous run. Both defaults confirmed as the standing
handoff-directed interpretation; no operator input required before activation.

## User Acceptance

- A pause-only commit-msg hook failure prints text that names the actual
  remedy (add the `AI-provenance:` line to the staged brief) instead of
  directing the author toward close keywords and the closeout ledger; mixed
  and non-pause failures keep the existing generic text unchanged.
- A future reword of the resolution-brief template's `Autonomous vs pause`
  field or its pause vocabulary breaks a checked-in test instead of silently
  decoupling the template from the hook regex.
- `docs/public-skill-dogfood.json` shows `prove` at `review_status: reviewed`
  with a dated observed-evidence list an operator can audit, and `prove`
  appears in `review_required_skills` (json) and the markdown required list.
- The observed evidence names what was actually run this session and what was
  not (non-claims preserved).

## Agent Verification Plan

- Outcome capability: a consumer repo operator hitting a pause-only hook
  failure can recover from the failure text alone; the charness maintainer can
  trust the dogfood registry's `prove` row as reviewed evidence.
- Cheap per-commit: focused
  `python3 -m pytest -q tests/test_check_issue_closeout_commit_msg_inprocess.py tests/quality_gates/test_issue_closeout_commit_msg_hook.py`,
  mirror sync (`sync_root_plugin_manifests.py` + staged-mirror gate), and
  `python3 scripts/validate_public_skill_dogfood.py --repo-root .` after the
  registry edit.
- Slice boundary: the prove consumer run itself (routing + executed workflow +
  emitted slice closeout ledger) is Slice 2's observed evidence; fresh-eye
  critique is bound by the prove flow per the repo contract.
- High-cost final: `run_slice_closeout.py --verification-lock` with
  `--produce-mutation-coverage` (Slice 1 touches a mutation-pool script),
  run after critique-driven edits settle.
- Expected proof cost: low — one focused suite, one broad locked closeout, one
  registry validator run.
- Test-duplication pressure: low — new assertions extend one existing
  in-process pin file; the drift test reads the template instead of cloning
  fixture prose.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | #444 F5+F6: pause-aware header/footer in `_format_failure` keyed on *failing* pause-triggered reports (mixed passing+failing pin included) plus the template-vs-regex pause-vocabulary drift test with loud-failure parsing; sync `plugins/` mirror | Retires the deferred #444 debt and produces the real slice the prove dogfood run needs | Focused pytest green incl. mixed-report and header-asserting pins; mirror in sync; hook behavior unchanged for non-pause failures | done (`963e147c`) |
| 2 | Add a realistic `PROMPT_HINTS["prove"]` consumer prompt (lib + mirror + registry row via scaffold); run the prove consumer flow on Slice 1's closeout; capture routing/execution/ledger observations; promote `prove` to `reviewed` + `review_required_skills` in json+md (repair achieve/hotl md drift); validators green | Handoff item 1's restart precondition is observed satisfied this session (`charness:prove` installed) | Observed-evidence list in the registry; `validate_public_skill_dogfood.py` green; slice closeout ledger emitted by the prove flow | done (`b1b74e0c`) |

## Operator Decision Queue

- Decision: push this goal's local commits (`963e147c`, `b1b74e0c`, and the
  closeout commit) to `origin/main`.
  - Owner: operator
  - Why deferred: autonomous session with no push approval in the request; the
    goal boundary declares external writes none, and all proof is local-complete.
  - Unblock action: `git push origin main` (the changed-line mutation-coverage
    marker is fresh, so the pre-push gate runs active).
  - Revisit trigger: next operator session, or the next release cut.
- Decision: file-or-apply the dogfood scaffold fallback-prompt warning (a
  scaffold-time signal when a row's prompt equals the skill description
  because `PROMPT_HINTS` lacks an entry — the gap that left `prove` with an
  unrealistic prompt until this goal).
  - Owner: operator (or the next session with issue-write scope)
  - Why deferred: this goal's boundary excludes external writes and scopes the
    lib to `PROMPT_HINTS["prove"]` only.
  - Unblock action: file a charness issue (novel; structural pattern: scaffold
    silently reuses producer metadata as consumer input) or apply the warning
    in `public_skill_dogfood_lib.py` with a matching test.
  - Revisit trigger: the next new public skill's dogfood row, or the next
    quality pass over the dogfood registry.

## Slice Log

### Slice 1: Slice 1: #444 F5/F6 pause failure-text polish + drift guard

- Objective: Make pause-only commit-msg failures name the AI-provenance remedy and pin the template<->regex pause vocabulary with a loud-failure drift test
- Why this approach: Smallest real slice retiring the #444 deferred debt; doubles as the genuine slice the prove dogfood run observes
- Commits: 963e147c
- What changed: scripts/check_issue_closeout_commit_msg.py (+ plugins mirror, byte-identical), tests/test_check_issue_closeout_commit_msg_inprocess.py (3 new pins)
- Alternatives rejected: Keying the swap on all reports (rejected: a passing non-pause report would wrongly suppress the remedy); hardcoding template vocabulary in the test (rejected: circular copy defeats the drift guard)
- Targeted verification: 33 focused tests green; live CLI demo of pause-only and overlap paths; run_slice_closeout --verification-lock --refresh-broad-pytest-proof green with focused mutation-coverage producer
- Test duplication pressure: check_dup_ratchet --json: ok=true, block=false, boy_scout_block=false (no new family from the 3 added pins)
- Critique: full bounded-reviewer slice review (aed11f4ced72e56b9): no blocker; footer overlap-condition wording folded; fingerprint drift-free before and after
- Off-goal findings: none this slice (md required-list drift already dispositioned in ## Off-Goal Findings)
- Lessons carried forward: Live CLI demo caught nothing the pins missed but cost <1s; keep it in the pause-path verification recipe
- Metrics:

### Slice 2: Slice 2: prove dogfood live run + promotion to reviewed

- Objective: Observe a live prove consumer run on Slice 1's closeout, then promote the registry row to reviewed and wire prove into review_required_skills
- Why this approach: The dogfood run wraps a genuine slice closeout instead of a synthetic exercise; promotion follows the observation, never precedes it
- Commits: b1b74e0c
- What changed: scripts/public_skill_dogfood_lib.py (+mirror) PROMPT_HINTS[prove]; docs/public-skill-dogfood.json (reviewed + evidence + required list); docs/public-skill-dogfood.md (mirrors json, repairs achieve/hotl omission); tests/quality_gates/test_public_skill_dogfood.py (md-json drift pin)
- Alternatives rejected: Keeping the description-fallback prompt (rejected by plan critique: routing evidence would overclaim); filing an issue for the md drift guard instead of applying it (rejected: 11-line local test is cheaper than the issue round-trip and external writes are out of scope this goal)
- Targeted verification: validate_public_skill_dogfood green (20/20); pytest dogfood suites green; locked closeout rerun green after the drift-pin addition (broad + focused mutation producer)
- Test duplication pressure: check_dup_ratchet --json: ok=true, block=false (one 11-line pin added; no clone family)
- Critique: full bounded-reviewer promotion review (a4cd9fa1bd39a3287): PASS, no blocker; evidence citations traced to repo state; drift-guard gap applied same-slice; fingerprint drift-free
- Off-goal findings: none new (md required-list drift already dispositioned; guard now applied)
- Lessons carried forward: Launching the locked closeout before the slice critique risked one wasted broad run; the discipline order critique-then-lock exists for exactly this — the drift-pin addition forced the rerun
- Metrics:

## Context Sources

- Source: handoff entry #1 (After `charness update` + restart: run the prove dogfood consumer prompt on a real slice, promote `review_status` to `reviewed` with observed evidence, and add `prove` to `review_required_skills` (#442 recorded this as the one deferred sub-item; the substance floor is already in place)) — see [docs/handoff.md](../../docs/handoff.md).
- Source: handoff entry #3 (Deferred from #444's critique (fails closed, separable): pause-case header/footer polish in `_format_failure`, and a template-vs-regex pause-vocabulary drift test) — see [docs/handoff.md](../../docs/handoff.md).
- Cited issue: #442
- Cited issue: #444

## Interview Decisions

- Mode: implementation-continuation (not artifact-only). Family considered:
  artifact-only draft vs execute-once-activated. The operator's opening
  request ("리포 자율 개선" — autonomous repo improvement) plus the handoff
  Workflow Trigger settle execution intent; no operator is present to
  interview mid-run, so the assumed mode is stated here instead of asked.
  single-point: the request wording itself.
- Slice pairing (chunker merge of handoff entries 1 and 3): family considered
  was synthetic-demo slice vs real backlog slice for the prove dogfood run.
  Chosen: the #444 deferred polish as the real slice, so the dogfood evidence
  observes genuine work. Rejected: a synthetic slice (weaker evidence),
  affordance-convergence (compatibility-sensitive, wrong size).
  single-point: this goal's pairing only.
- Subagent model/effort: the repo's standing `gpt-5.6-terra`/`medium` request
  is axis: host — this host's Agent tool exposes no such model override
  (enum sonnet/opus/haiku/fable); typed `bounded-reviewer` spawns proceed
  host-defaulted and the limitation is stated, per the CLAUDE.md contract.
- Promotion evidence scope: axis: host — the consumer run observes THIS host's
  installed surface only; the registry evidence must say so rather than claim
  cross-host routing proof.

## Plan Critique Findings

- Reviewer provenance: one bounded fresh-eye `bounded-reviewer` plan critique
  (agent ac87480d048c93622, read-only Read/Grep/Glob envelope),
  boundary-fingerprint snapshot/verify wrapped (`drift: []`), host-defaulted
  model per the Interview Decisions axis note. Verdict: no activation blocker.
- Folded (worth-folding): (1) the checked-in prove registry prompt is the
  frontmatter-description scaffold fallback (`PROMPT_HINTS` has no `prove`
  entry), so Slice 2 adds a realistic consumer prompt to
  `public_skill_dogfood_lib.py` + mirror and re-scaffolds the row — otherwise
  the "routes the prompt" evidence would overclaim; (2) the F5 condition is
  pinned to *failing* reports with `trigger == "pause-brief"` (a passing
  non-pause report beside a failing pause report must NOT suppress the pause
  remedy text) plus a mixed-report and header-asserting test; (3) the drift
  test asserts the placeholder was found, anchors extraction to the fenced
  template block (Persistence prose also contains the vocabulary), and
  asserts exactly two `|` alternatives; (4) `docs/public-skill-dogfood.md`'s
  required list pre-dates this goal in omitting achieve/hotl — repaired in
  the same md edit and recorded under Off-Goal Findings.
- Over-worry raised, not folded: missing-`ok`-key misfire (production reports
  always carry `ok`); drift-test circularity (producer/consumer surfaces are
  independently owned, so the cross-read is the guard, not a tautology);
  promotion-evidence overclaim relative to peers (planned evidence exceeds the
  static-only `achieve` precedent once folding 1 lands).

## Off-Goal Findings

- Pre-existing drift found by the plan critique: `docs/public-skill-dogfood.md`
  "Current Required Reviewed Skills" omitted `achieve` and `hotl` while the
  json `review_required_skills` carries both, and no validator checks the md
  list. Disposition: repaired inline in Slice 2's md edit (one-line list fix,
  same file already in scope; prefer deleting drift over documenting drift).

## Coordination Cues

- Routing: handoff (chunked-routing pickup) → achieve (goal lifecycle) →
  prove — selected from installed skill metadata for the Slice 1 closeout
  consumer flow (`impl` owns building, `quality` owns the standing bar,
  `critique` owns the reviewer substrate); the same selection is recorded as
  Slice 2's observed routing evidence. Fresh-eye reviews routed to typed
  `bounded-reviewer` spawns per the repo Subagent Delegation contract.
- Gather: n/a — no external source was consumed; all context came from
  checked-in repo surfaces and the live session.
- Release: n/a — no release-surface token in this goal's recorded work; the
  promotion rides the existing v1.2.0 installed surface.
- Issue closeout: n/a — #442 and #444 were already closed before this goal;
  both are cited as context only and no close keyword is carried.

## Final Verification

- Self-verification: Slice 1 — 33 focused tests green, live CLI demonstration
  of the pause-only remedy text and the close-keyword-overlap generic text,
  locked `run_slice_closeout.py --verification-lock --refresh-broad-pytest-proof
  --produce-mutation-coverage` completed (broad standing pytest green, focused
  mutation-coverage producer). Slice 2 — `validate_public_skill_dogfood` green
  (20 cases, 20 required), dogfood suites green, locked closeout rerun green
  after the drift-pin addition. Plugin mirrors byte-identical (`cmp`).
- Broad gate attestation: gate=run_slice_closeout(--verification-lock) |
  outcome=completed | state_ref=.charness/closeout/broad-pytest-proof.json
Retro: charness-artifacts/retro/2026-07-17-prove-dogfood-via-444-polish-goal-session-retro.md

Host log probe: charness-artifacts/goals/2026-07-17-prove-dogfood-via-444-polish-host-log-probe.json

Disposition review: charness-artifacts/critique/2026-07-17-prove-dogfood-via-444-polish-disposition-review.md
- Residual risks: the prove routing observation is a single utterance on one
  host — a paraphrased consumer prompt could route differently and that is
  explicitly not claimed; the pause-only header keys on report shape produced
  by `evaluate`, so a future report-shape refactor must keep the
  `trigger`/`ok` fields (pinned by the mixed-report test).
- Non-claims: no Cautilus evaluation ran (ask-before-run contract; no
  scenario-registry mutation); no cross-host or installed-machine re-proof of
  the promoted row beyond this session's live run; commits are local — no
  push, release, or provider write occurred.

## User Verification Instructions

- `python3 -m pytest -q tests/test_check_issue_closeout_commit_msg_inprocess.py tests/quality_gates/test_issue_closeout_commit_msg_hook.py tests/quality_gates/test_public_skill_dogfood.py` — all pins green.
- Stage a pause brief without an `AI-provenance:` line and run
  `python3 scripts/check_issue_closeout_commit_msg.py --repo-root . --commit-msg-file <msg>`:
  the failure text names the provenance remedy, not close keywords.
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .` — 20 cases,
  20 required; inspect the `prove` row's observed evidence and non-claims in
  `docs/public-skill-dogfood.json`.
- `git log --oneline -3` — `963e147c` (F5/F6 polish), `b1b74e0c` (promotion),
  plus the closeout commit; push is queued in the Operator Decision Queue.

## Auto-Retro

Retro dispositions: applied: md↔json required-list drift pin
(`tests/quality_gates/test_public_skill_dogfood.py::test_dogfood_markdown_required_list_mirrors_json`),
from the promotion review's finding 5 — the drift class had recurred once.

Retro dispositions: applied: pause footer overlap-condition wording folded
from the slice-1 fresh-eye review (commit `963e147c`).

Retro dispositions: applied: recent-lessons refresh from this goal's session
retro (`refresh_recent_lessons.py` updated
`charness-artifacts/retro/recent-lessons.md`, carrying the
host-version-dependent reviewer-polling correction AND the
critique-before-locked-closeout workflow lesson — the retro's first Next
Improvement — into the Next-Time Checklist).

Retro dispositions: none — workflow item on critique-then-lock ordering: the
rule is already owned by `docs/conventions/implementation-discipline.md`;
this run's violation was a recorded gamble against a known rule, not a
contract gap, and the recent-lessons line above is the persistence.

Retro dispositions: out-of-scope: capability item on the dogfood scaffold
fallback-prompt warning — this goal's boundary excludes external writes and
scopes the lib to `PROMPT_HINTS["prove"]` only; queued with an owner, two
unblock paths, and a revisit trigger in the Operator Decision Queue.

Structural follow-up: none — the one transferable pattern (scaffold reuses
producer metadata as consumer input) is queued as an Operator Decision Queue
item with a named unblock action because this goal's boundary excludes the
external issue write; the drift-pin `applied:` above already covers the
md-list recurrence class.
