---
name: retro
description: "Use after a meaningful work unit or when the user asks for a retrospective. Reviews what happened, what created waste, which decisions mattered, which named expert lens or direct counterfactual would have changed the next move, and which workflow/capability/memory improvements should make the next session better. One retro shape; scale the depth to the work unit under review."
---

# Retro

Use this after a meaningful unit of work completes or when the user asks for a
retrospective.

If the user correctly points out a missed issue, broken assumption, or missing
gate that the current workflow should likely have caught, run a short
`session` retro before continuing. Keep it bounded to the miss that was just
revealed; do not turn every correction into a long postmortem.

## Bootstrap

Resolve the adapter and run the planner before gathering evidence or writing the
artifact. Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`,
then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/plan_retro_run.py" --repo-root .
python3 "$SKILL_DIR/scripts/scaffold_retro_artifact.py" --repo-root .
```

The planner names the work-class counterfactual lens brief, required
reads (incl. `references/expert-lens.md` for the briefed lens), gate packets, and
the next action. Open the `required_reads` before writing; expert-lens.md is an
unconditional read because the counterfactual is mandatory and its lens catalog is
not inlined here. For a first run with no adapter, run `init_adapter.py` then
`prepare_packet.py --prepared-for "<label>"` before relying on adapter paths.

Adapter policy:

- If the adapter is missing and the request is session-like, continue with
  inferred defaults.
- If the adapter is missing and the request is metrics-heavy or explicitly asks for
  durable artifacts, create `<repo-root>/.agents/retro-adapter.yaml` first, then continue.
- If the adapter is invalid, repair it using `references/adapter-contract.md`
  before relying on adapter-defined paths or metrics.
- Never block a `session` retro solely because the adapter is missing.

## Workflow

1. Scale the retro to the work unit under review.
2. Gather evidence in this order.
   - current thread, current task, changed files, recent commits
   - existing handoff or prior retro artifacts when they matter
   - the most recent durable retro under `output_dir` when a trend line matters
   - adapter-defined `evidence_paths`
   - for host-log-derived efficiency signals, prefer `$SKILL_DIR/scripts/probe_host_logs.py`
     (`--repo-root .`) before claiming turns, tokens, or tool-call counts, and
     the optional `$SKILL_DIR/scripts/audit_codex_session.py` when Codex session
     logs are available — both are evidence sources, not portable prerequisites
     or waste conclusions. Pass `--session-id <id>` or
     `--session-file <path>` to read the full session JSONL directly. The probe
     reports generic host metrics; it does not attach Goal Draft windows or
     execution identity.
     The measured / proxy / unavailable signal distinctions live in
     `references/phase-aware-efficiency.md`.
   - adapter-defined `metrics_commands` only when they sharpen a real claim
   - recurring waste signals from adapter-defined evidence sources
   - if the adapter declares `packet_sections`, run
     `$SKILL_DIR/scripts/prepare_packet.py` once and read the markdown packet
     before writing lessons; see `references/prepare-packet.md`
   - consumer rework is observed through the operator's own issue filing, not a
     gate: issues labelled `rework` carry a `Causing skill:` line
     (`../issue/references/issue-shaping.md` owns that filing shape). When the
     adapter declares the `rework-issues-by-causing-skill` packet section, the
     packet already holds the per-skill attribution for the period; read it
     and name the causing skills in `Evidence Summary` and `Trends vs Last
     Retro`. A section body that starts with `Rework issues UNAVAILABLE` means
     the read did not happen; say so instead of reporting zero rework
3. Write the core retro.
   - `Context`: what unit of work is being reviewed and what matters next
   - `Window`: the span of work being reviewed
   - `Evidence Summary`: which durable artifacts, commands, or metrics actually informed the retro
   - `Waste`: where time, clarity, or trust was lost
   - `Critical Decisions`: which decisions changed outcome or constrained later work
   - `Trends vs Last Retro`: compare against the last durable retro when one exists
   - `North Star Alignment`: required; see `references/section-guide.md`
   - `Expert Counterfactuals`: what 1-2 counterfactual lenses, named experts
     when useful, would likely have done differently
   - `Next Improvements`: concrete changes for the next session
   - `Persisted`: whether the retro was written to a durable artifact, and if
     not, why not
   - for token, tool-call, broad exploration, or efficiency claims, apply
     `references/phase-aware-efficiency.md` before labeling work as waste
4. Make `Next Improvements` concrete.
   - `workflow`: change the sequence, gate, or review habit
   - `capability`: add or adjust a skill, tool, adapter, preset, or automation
   - `memory`: write the lesson into a durable artifact so it is not relearned
   - when a lesson names a *transferable* waste pattern (one that could recur in
     another skill, script, doc, or workflow), scan for siblings before
     declaring the lesson learned and record the result in a `## Sibling Search`
     section of the per-session artifact; narrowly local waste uses the
     `n/a — trivial fix; no plausible siblings` short-circuit. The four-axis
     scan, four-decision taxonomy, follow-up identifiers, and the section-gated
     validator are owned by `references/waste-sibling-scan.md`
   - when the pattern could improve arbitrary consuming repos, add a compact
     `## Portable Candidate`: abstract pattern, triggering evidence, intended
     consumer/repo shape, destination `create-skill` (or `not portable — <reason>`),
     and one first-prompt acceptance claim. This is a judgment route, not a rule
     that every lesson must become a public skill.
   - when an improvement is headed for an issue, classify it on two axes — a
     generalized `Structural pattern:`+`Triggering instance(s):` and a
     `Destination:`, owned by `../../shared/references/retro-issue-destination-split.md`
   - the lesson ledger is optional memory and selection state; do not create a
     second lesson-specific artifact beside it
   - when a lesson keeps changing actions across sessions, or a person asks to
     promote one, route it through
     `../../shared/references/lesson-graduation.md`: a standing `docs/` page
     takes ownership of the rule and the lesson leaves the working set.
     Graduation is settled with the person and is not performed inside the retro
5. Persist when there is a durable home.
   - if `output_dir` exists or the adapter defines one, persist the retro artifact with `$SKILL_DIR/scripts/persist_retro_artifact.py` instead of ad hoc file writes; for Goal Run evidence use the owning Goal Run identity contract; the helper stamps the `## Persisted` line with the real durable path it writes, so do not hand-edit that line afterward
   - if the adapter defines `summary_path`, `$SKILL_DIR/scripts/persist_retro_artifact.py` should refresh the compact lesson digest automatically from the written durable artifact; where the repo keeps a lesson ledger it also seeds a transition for every newly tagged `(recurrence-class: <id>)` and records the outcome as a `Seeding:` line under `Persisted:` — those transitions land uncommitted for review, and a budget refusal is reported there rather than failing the persist
   - on the first retro after a legacy hand-curated `recent-lessons.md` (file exists, `output_dir` has no prior `*.md` artifacts), the persistence helper preserves the existing summary instead of replacing it with an empty-stub digest. Pass `--force-empty-summary` only after confirming the legacy content is safe to drop.
   - otherwise still give the user a concise retro in chat
   - when the retro names an RCA-class event (a bug, repeated correction, or
     weak-proof finding) and the repo maintains the conversion ledger, append
     one RCA event (`--source retro`) per
     `../../shared/references/rca-ledger-append.md`; this is a silent no-op in
     repos without the ledger
   - never stop without stating `Persisted: yes: <path>` or `Persisted: no: <reason>`

## Output Shape

The result should usually include:

- `Context`
- `Window`
- `Evidence Summary`
- `Waste`
- `Critical Decisions`
- `North Star Alignment`
- `Trends vs Last Retro` when prior evidence exists
- `Expert Counterfactuals`
- `Next Improvements`
- `Sibling Search` when a transferable waste pattern is named (opt-in;
  `n/a — trivial fix; no plausible siblings` short-circuit otherwise)
- `Portable Candidate` when the sibling scan finds a cross-repo capability
- `Persisted`
- `Packet Consumed` when a retro prepare packet was produced, or
  `n/a (no adapter sections)` when no sections are declared

## Auto-Retro Trigger

Trigger a short `session` retro automatically when a user correction exposes a
real miss. Consume the planner packet and read `state` before
`triggered`; its basis and the full trigger/skip taxonomy live in
`references/trigger-and-persistence.md`. Keep the retro bounded and include
`Persisted`.

## Expert Counterfactual Rule

Every retro includes at least one counterfactual lens. The planner classifies the
work under review and briefs the fitting lens as a `required_read` of
`references/expert-lens.md` (for harness/skill/workflow/eval/contract work, the
Engelbart `system-improving-itself` lens); open it and apply the briefed lens —
the catalog and sub-agent flow are not inlined here. Use named experts only when
the name sharpens a *different* changed action (never decoration); when sub-agents
are available and the session warrants depth, up to two distinct-lens expert
sub-agents, otherwise write the counterfactuals inline.

## Guardrails

- Separate observed facts from proposed improvements.
- Do not fabricate metrics when the adapter does not provide a real source.
- Do not label broad exploration as waste solely because it was broad; identify
  phase intent and the triage lock first.
- A retro may stay narrative without metrics, but must say so explicitly.
- If no prior retro exists, say so instead of implying a trend line.
- Capability suggestions exist to reduce future waste, not to show tool awareness.
- Do not let the retro turn into a generic postmortem when the user asked for a
  short session review.
- Do not claim persistence implicitly; name the durable path or the reason it
  remained chat-only.
- Do not invent hidden machine formats or write hidden telemetry; the retro only
  reads explicit evidence sources.
- If no improvement is proposed, explain why the current workflow should remain
  unchanged.

## References

- `references/adapter-contract.md`
- `references/section-guide.md`
- `references/phase-aware-efficiency.md`
- `references/expert-lens.md`
- `references/trigger-and-persistence.md`
- `references/waste-sibling-scan.md`
- `references/prepare-packet.md`
- `../../shared/references/retro-issue-destination-split.md`
- `../debug/references/sibling-search.md`
- `../../shared/references/rca-ledger-append.md`
- `../../shared/references/lesson-graduation.md`
