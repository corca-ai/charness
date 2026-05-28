# Retro: chunked-routing code-vs-judgment layering miss

Mode: session
Date: 2026-05-28
Trigger: user correction during push-blocker resolution exposed a real workflow miss

## Context

While clearing the `check-python-lengths` pre-push gate on the 22 unpushed commits, the
agent surfaced the `chunked_routing_lib.py` file at 886 lines (>2.4x the 360-line cap)
and the recent-lessons artifact noting it as "deferred splitting work; check_python_lengths
is informational." The agent's first instinct was a mechanical split into 5 sibling
modules. The user interrupted: "이걸 왜 코드가 하죠? 에이전트가 더 잘 할 것 같은데. 코드가
너무 많은 역할을 해서 청킹을 못할 것 같은 느낌이 듬" (≈ "Why is code doing this? An agent
would do this better. The code has too many roles, which is probably why it can't be
chunked properly.")

The user's read was correct. Three of the five subsystems —
- `propose_merges` (connected-components on token-overlap)
- `should_fire_chunker` (Korean+English regex intent classifier)
- `render_auto_draft_artifact` (markdown templating from token-derived label/objective)

— encode agent-judgment work as deterministic rules. The 886-line growth was a symptom
of the underlying layering miss, not just a code-organization problem. The file resists
clean chunking because the heuristics tangle together; agent judgment doesn't decompose
into rule sets the way data parsing does.

## Evidence Summary

- `charness-artifacts/goals/2026-05-28-handoff-chunked-routing.md` (closed
  goal artifact, 7 slices)
- `charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`
  (the originating slice closeout, which marked the file growth as deferred
  splitting and called the gate informational)
- `skills/public/handoff/scripts/chunked_routing_*.py` (the split modules, post-fix)
- Conversation turn where the user raised the layering question after the
  agent's first AskUserQuestion enumerated 5-way split as the
  "(Recommended)" option

## Waste

- The chunked-routing goal (slices 1–7, ~12 commits) shipped procedural code
  that re-implements three agent-judgment tasks. The full pipeline could be
  invoked conversationally on the parsed handoff entries — the parser is
  genuinely code-shaped, but merger + trigger + auto-draft are agents doing
  inference on natural-language context.
- The mid-session split into 5 modules (this push) cleared the length gate
  but did not address the layering miss; it locked in the procedural design
  rather than challenging it.
- The originating closeout retro said `check_python_lengths.py` is
  "informational" when it is in fact a hard gate (exit 1). That wrong
  belief flowed into recent-lessons and caused this push to discover the
  gate failure live rather than during the original closeout.

## Critical Decisions

- **Originating slice 1 spec scope**: the chunked-routing goal artifact
  defined the pipeline as parser → ranker packet → merger → auto-draft +
  a separate trigger phase. The spec did not ask "for each subsystem, is
  this code or agent work?" — it took the procedural framing as given.
- **This-push mid-session choice**: the agent chose to do the split now
  rather than walk back the design. The user accepted that, but
  explicitly asked for a retro covering both why the original design
  picked code and why the agent did not catch the layering until
  prompted.

## Expert Counterfactuals

- **Christopher Alexander — "form follows context"**: a file's length is
  a downstream signal; the upstream question is whether each subsystem's
  form matches its context. Alexander would have asked, slice-by-slice,
  whether the natural form for "decide if two handoff entries belong
  together" is a graph algorithm or a paragraph of agent reasoning. The
  answer for merger + trigger + auto-draft is the paragraph. The
  procedural form was a category error, not a sizing problem. A length-
  gate-driven split treats the symptom and locks in the bad form.
- **Don Reinertsen — "cost of delay vs. cost of poor partitioning"**: the
  closeout retro's "defer the split" decision was made on the belief that
  the gate was informational. Reinertsen would have asked what the
  cheapest possible test of that belief was. Running `python3 scripts/
  check_python_lengths.py --repo-root .` once would have refuted it in
  500ms. The originating slice paid no cost-of-delay tax, but the next
  consumer (this push) paid the full cost: 4 standing-gate failures from
  the same set of commits, cascading into a 2-hour omnibus
  gate-clearing slice.

## Why The Layering Miss Was Not Caught Earlier

- The agent treated the file-size symptom (886 lines) as the problem
  shape and routed to the standard "split into siblings" answer. That
  routing skipped the "should this be code at all?" question because
  the existing `critique` Before-phase angles focus on bundle-anyway,
  act-before-ship, and confirmed-input-over-anchoring — none of them
  flag code-encoding-judgment.
- The closeout retro for the originating goal called the gate
  "informational" without checking. The agent inherited that claim from
  recent-lessons rather than verifying.
- During the in-flight push-blocker resolution, the agent surfaced the
  question to the user as "how to split" not "should this exist". The
  user's intervention reframed it. The reframing is the lesson.

## Next Improvements

- **workflow**: extend `critique` Before-phase with an explicit
  "code-vs-judgment boundary" angle for any slice that introduces or
  grows a `*_lib.py` in a public skill. The angle should fire when the
  slice plan names verbs like *classify*, *propose*, *rank*, *draft*,
  *render*, *trigger*, *infer* on natural-language input. The reviewer's
  job is to ask: could an agent doing this conversationally on the
  parsed input produce a better answer than the procedural encoding?
  Bundle this with `references/confirmed-input-over-anchoring.md`'s
  axis-probe under a new
  `skills/public/critique/references/code-vs-judgment-boundary.md`.
- **capability**: add an advisory pre-impl scan in `impl`'s Before phase
  that surfaces new `*_lib.py` files in `skills/public/*/scripts/` and
  flags whichever ones match the verb pattern above. Output is a single
  pre-impl note: "consider whether <function> is judgment-shaped". Not
  a gate, a prompt.
- **memory**: this retro file is the persistent record. Add a short
  recent-lessons entry naming the trap so the next handoff inherits the
  warning. The lesson is *not* "split big files earlier" — that is the
  surface-level read. The lesson is *"when a public-skill helper grows
  past the soft cap because of heuristics-on-natural-language, the
  underlying smell is code doing agent work; consider walking back
  before splitting."*
- **memory (correction)**: the prior closeout retro
  ([2026-05-28-handoff-chunked-routing-closeout](2026-05-28-handoff-chunked-routing-closeout.md))
  asserted `check_python_lengths.py` is informational. It is not.
  Fixed-in-place updates to retro files are not the right move; this
  retro's record of the correction is the durable fix. recent-lessons
  should carry the correction so it does not propagate again.

## Sibling Search

Transferable waste pattern: **code-encoding-judgment in public-skill
helpers**. Quick scan for similar patterns (functions matching
`classify_*`, `propose_*`, `should_fire_*`, `auto_draft_*` in
`skills/public/*/scripts/`):

| Candidate | Decision | Proof |
|---|---|---|
| `chunked_routing_merger.propose_merges` | same pattern, fix now (out of scope this push) | filed as part of this retro's next-improvements; redesign deferred to its own slice |
| `chunked_routing_lib.should_fire_chunker` | same pattern, fix now | same as above |
| `chunked_routing_auto_draft.render_auto_draft_artifact` | same pattern, fix now | same as above |
| `quality/ci_local_gate_parity_lib.classify_step` | intentional boundary | classifies structured CI step records by `type` field; rule-based on enums, not on natural-language input |
| `quality/skill_ergonomics_lib.classify_finding` | intentional boundary | classifies validator findings by path-pattern + message-prefix; structured input |
| `quality/propose_mutation_testing.classify` | intentional boundary | classifies a structured adapter payload; not natural-language inference |
| `quality/propose_mutation_testing` (proposer) | intentional boundary | "proposes" a runner configuration from structured detection signals, not a natural-language draft |

Conclusion: the layering pattern is concentrated in the chunked-routing
module. The quality skill's `classify_*`/`propose_*` helpers operate on
structured input and do not match the smell. Redesign of the three
chunked-routing subsystems is the only sibling action; it stays out of
this push's scope and will be handled as its own slice with the new
`code-vs-judgment-boundary` critique angle.

## Persisted

Persisted: yes [charness-artifacts/retro/2026-05-28-chunked-routing-layering-miss.md](2026-05-28-chunked-routing-layering-miss.md)
