# Spec: SessionStart hook host split, AGENTS.md as canonical routing

Status: draft — F4-CONFLICT resolved by operator 2026-07-25. **The required
fresh-eye critique was not obtained** (see `## Critique`), so this contract is
not yet cleared for `impl`. · 2026-07-25

## Problem

Two always-loaded surfaces carry the same routing contract. `AGENTS.md
## Skill Routing` states it, and the SessionStart hook's `DIRECTIVE`
(`scripts/session_start_routing.py:34`) restates it in near-identical terms. Both
are injected into every session on hook-installed hosts, so the duplication buys
nothing and creates a two-surface synchronization burden that has already
drifted (the hook names `charness:handoff` and the "task governs" tiebreak; the
AGENTS.md block does not).

Separately, `AGENTS.md ## Subagent Delegation` carries Codex-only operational
detail (`gpt-5.6-terra`, `medium`, `fork_turns: "none"`, `agent_type` caution)
plus an explicit negation telling Claude Code hosts the block does not apply to
them. Every Claude session pays context for a rulebook addressed to a different
host, and for the instruction to ignore it.

The external prompt-sizing guidance gathered 2026-07-25
(`charness-artifacts/gather/2026-07-25-claude5-context-engineering-rules.md`,
"repetition -> clarity", "upfront information -> progressive disclosure") points
the same way as north star P2/P3, so this is an ordering problem, not a new
direction.

## Capability Contract

**Actor:** any agent opening a session in a charness-managed repo.

**Capability delta:** the agent gets exactly one statement of the routing
contract and only the host controls that apply to the host it is actually
running on.

**Acceptance boundary:** AGENTS.md alone is sufficient to route a session on a
host with no hook; the hook adds recency and host resolution, never content the
agent cannot otherwise reach.

## Current Slice

Invert the canonical/fallback relationship between AGENTS.md and the hook, and
split the hook payload by `--host`.

1. `AGENTS.md ## Skill Routing` becomes the sole content home for routing. Its
   self-description flips from "the hook may inject this; this block is the
   fallback" to "this block is canonical; the hook points here."
2. `session_start_routing.py` emits a **thin pointer** — direct the agent to read
   and apply `AGENTS.md ## Skill Routing` now — plus a **static per-host
   subagent contract** string selected by the existing `--host` argument.
3. Per-host subagent detail moves out of `AGENTS.md ## Subagent Delegation`
   into a committed reference under `skills/shared/references/`, one section per
   host. AGENTS.md keeps the host-neutral standing request (delegation is
   pre-approved; bounded reviewers are read-only; use the host's own subagent
   controls) plus a pointer to that reference, and drops the per-host
   model/effort table and its Claude-facing negation. The hook's per-host
   payload names the host and its section in that reference.
4. `render_skill_routing.py` and `setup_skill_routing_lib.py` are updated so the
   rendered block and its completeness signals describe the inverted
   relationship.

## Fixed Decisions

| # | Decision | Rationale |
|---|---|---|
| F1 | AGENTS.md is the canonical content home for routing | Only surface guaranteed present on hook-absent hosts; committed and reviewable in-repo |
| F2 | Hook keeps a routing **pointer**, not a restatement | Preserves the context-recency benefit #240 bought while removing duplicated content |
| F3 | Hook payload is static committed strings branched by `--host` | Zero execution cost, no repo scan, no new failure surface inside a hook that must never break a session |
| F4 | Per-host subagent contract keeps a committed in-repo content home under `skills/shared/references/`; AGENTS.md points to it and the hook injects only a host-selected pointer | Correctness must not depend on an opt-in hook (see F4-CONFLICT); still removes the always-loaded Codex table and the Claude-facing negation from AGENTS.md |
| F5 | `--host unknown` gets pointer only, no subagent contract | Emitting a host contract for an unidentified host would be a guess |

F2 and F4 were operator decisions (2026-07-25), taken over "full restatement"
and "routing removed entirely" respectively.

### F4-CONFLICT (found during spec grounding, 2026-07-25)

**The session_routing hook is opt-in and disabled by default.**
`scripts/host_hook_session_routing.py:224-227`: "Opt-in: an adapter with no
`session_routing` section leaves every host disabled, so this is a no-op until
enabled." The gate is `_routing_intent` reading the `session_routing` intent
section (`host_hook_session_routing.py:95-97`); absent section means every host
resolves to disabled.

This breaks F4's premise. F4 was chosen on the understanding that the hook is
the host-resolution layer; if the hook is off by default, moving the Codex
subagent contract *into* the payload means that on a default Codex install the
`fork_turns: "none"` gotcha and the `gpt-5.6-terra` / `medium` request reach
nobody. That is a functional regression, not a residual gap.

It is also internally inconsistent with F1. F1's reasoning — put content in the
surface guaranteed to be present, because the hook may be absent — applies with
*more* force to the subagent contract than to routing, since routing at least
degrades to model judgment while `fork_turns` is a silent-failure gotcha
(caller-provided model/reasoning overrides are rejected under the default
`fork_turns: "all"`).

**Resolution (operator-confirmed 2026-07-25, now recorded as F4):** apply F1's principle
uniformly. The per-host subagent contract keeps a committed in-repo content home
— a reference doc under `skills/shared/references/` — that AGENTS.md's one-liner
points to. The hook's per-host payload then carries the same thing routing does:
a pointer plus recency, naming the host and its reference section. This still
removes the Claude-facing negation and the always-loaded Codex table from
AGENTS.md (the stated goal), without making correctness depend on an opt-in
hook.

Under this resolution F3 (static committed strings, no repo scan) is unchanged,
and A4/A5 shift from asserting contract *content* in the payload to asserting
the correct host *pointer* in the payload.

## Deliberately Not Doing

- **Not** moving routing content into the hook exclusively. Rejected on
  coverage: hook-absent hosts (clean installs without the opt-in
  `session_routing` intent, third-party agents that honor AGENTS.md, CI
  runners) would lose routing entirely. Note the auditability objection does
  *not* hold — the payload lives in a committed script and only the wiring is
  machine-local.
- **Not** making the hook dynamic (scanning installed skills or probing tool
  availability). Rejected on hook-safety: `session_start_routing.py` is written
  to fail silently and never break a session; adding I/O and latency to it
  trades a real risk for accuracy the agent can obtain on demand via
  `charness catalog list`.
- **Not** deleting `## Subagent Delegation` from AGENTS.md. The standing
  delegation request and the read-only reviewer boundary are host-neutral
  contract and stay.

## Reversal Note (load-bearing)

This slice **reverses the 2026-07-04 session-start-routing revision**, which
deliberately moved the routing rule text out of a pointer and into the directive
itself. That decision is recorded in `scripts/host_hook_session_routing.py:1-13`
and asserted by `tests/test_session_start_routing.py:25-47`, whose docstring
states the directive "now states the routing rule directly, not just a pointer"
and frames that as carrying #240's protections.

The reversal is intentional and narrow: #240's protection was *routing
reliability via front-loaded recency*, and a pointer that names the section and
says to read it now still front-loads. What the 2026-07-04 revision added beyond
recency was duplicated content, which is what this slice removes. The
corresponding assertions must be **rewritten to pointer-integrity assertions**,
not deleted — a silent test deletion here would erase the only durable record of
why the directive was expanded.

## Probe Questions

- **P1 — Does a pointer hold routing reliability as well as a restatement?**
  Not decidable by unit test; it is a cross-session behavioral property. Probe
  by running the existing prompt-mutation / routing-behavior harness
  (`charness-artifacts/prompt-mutation/`) if it covers session-open routing, and
  otherwise carry this as an accepted risk with a named rollback (restore the
  full directive) rather than claiming it proven.
- **P2 — Does `skill_routing_semantically_complete` need a new signal set, or
  only edited strings?** Its current signals require `sessionstart` and
  `context-only` in the AGENTS.md section. Determine during implementation
  whether the inverted sentence should still be a required signal or whether the
  canonical-home claim replaces it.

## Non-Goals

- Rightsizing the 199-file / 18.4K-line `skills/**/references/` surface.
- Adding a repo-owned prompt-size auditor, or adopting `/doctor` into contract.
- Any change to host auto-memory posture (`recent-lessons.md` stays repo-owned).

## Constraints

- The hook must remain context-only and must never raise into a host session.
- The hook payload must stay in committed repo source, not host settings.
- No host-specific file locations or template choices enter skill bodies.
- Changes to AGENTS.md, the renderer, and the completeness validator ship in one
  slice; a renderer that disagrees with AGENTS.md is a drift bug by definition.

## Success Criteria

1. Routing contract text appears in exactly one content home; the hook names
   that home instead of restating it.
2. A session on a hook-absent host can still route from AGENTS.md alone.
3. A Claude Code session receives no Codex-specific subagent instruction and no
   instruction to ignore one.
4. A Codex session receives the Codex subagent contract it previously read from
   AGENTS.md.
5. The 2026-07-04 reversal is recorded in-repo, not only in this artifact.

## Acceptance Checks

| # | Criterion | Check | Type |
|---|---|---|---|
| A1 | 1 | `build_additional_context(host)` output contains no restatement of the pickup/catalog rule: asserts absence of `charness catalog list` and presence of an `AGENTS.md` + `Skill Routing` pointer | unit |
| A2 | 1 | Renderer output and AGENTS.md agree that AGENTS.md is canonical; `render_skill_routing.py --repo-root .` reports `leave_as_is` against the updated AGENTS.md | unit |
| A3 | 2 | `agents_skill_routing_semantically_complete(AGENTS.md)` is true with the hook uninstalled, and the section names the pickup, metadata-judgment, and catalog routes without depending on hook text | unit |
| A4 | 3 | `render_output("claude")` `additionalContext` contains no `gpt-5.6-terra`, no `fork_turns`, and no "not-exposed limitation" negation | unit |
| A5 | 4 | `render_output("codex")` `additionalContext` names the Codex section of the subagent reference; the Codex model/effort/`fork_turns` contract itself is asserted present in that committed reference | unit |
| A6 | 4 (regression guard) | With the hook uninstalled, the Codex model/effort/`fork_turns` contract is still reachable from AGENTS.md by following its pointer — assert the reference file exists and AGENTS.md links it | unit |
| A7 | 5 (negative) | `render_output("unknown")` emits the pointer with no host subagent contract and no JSON wrapper | unit |
| A8 | — (negative) | Hook still exits 0 and emits usable stdout when stdin is empty or malformed | unit |
| A9 | 5 | Reversal note referencing the 2026-07-04 revision is present in the rewritten test's docstring or module comment | manual |

A1 and A4 are the two checks that would have caught this slice being applied
half-way (hook edited, AGENTS.md not, or vice versa). A6 is the check that
would have caught the F4-CONFLICT regression had it shipped.

## Boundary Ownership

Reversible. All changes stay in committed repo source and this session's
editable state; no external write, no release publish, no issue close. The
irreversible-boundary safeguards (P4/P5) do not arm for this slice. The one
propagation risk is that installed machines pick up a changed payload on next
plugin update — handled by the ordinary release path, not by this slice.

## Critique

**Status: NOT OBTAINED.** Three bounded `bounded-reviewer` subagents were
spawned (two split by angle, one retry covering all four). All three returned
idle notifications without delivering findings, and this session has no
retrieval path — `SendMessage` is not exposed and `TaskList` is empty. Per repo
contract a same-agent pass is not a substitute, so the review is left unproven
rather than simulated. Reviewer boundary integrity was verified clean around
both rounds (`reviewer_boundary_fingerprint.py verify` → `drift: []`), so the
failure is result delivery, not reviewer misbehavior.

F4-CONFLICT above was found by direct code reading during spec grounding, not by
a reviewer; it does not count toward this requirement.

Focus angles still owed to a reviewer:

1. **Likely implementer misread** — does "thin pointer" get implemented as a
   pointer so thin the agent has no reason to act on it before the user's first
   message?
2. **Overstated acceptance** — A1–A7 are all unit checks against string content.
   Do they actually establish criterion 2, or only that the strings changed?
   Criterion 1's real claim (single content home) is not fully unit-testable.
3. **Hidden sequencing** — the AGENTS.md edit, the renderer, and the
   completeness validator must land together; is there an ordering where the
   validator rejects the very AGENTS.md the renderer produces?
4. **Coverage residual** — F4-CONFLICT is resolved on paper by giving the
   subagent contract an in-repo home. Does the revised F4 actually close it, or
   does the AGENTS.md pointer just relocate the same reachability question one
   hop away?
5. **Did the spec's own author bias the questions?** The operator's three
   decisions were taken against options this spec's author composed, and one of
   those options (original F4) rested on an unchecked premise about hook
   default state. Are the other two decisions resting on unchecked premises too?

## Canonical Artifact

This file. It supersedes chat-only discussion of the hook/AGENTS.md split.

## First Implementation Slice

Order matters (constraint 4):

1. Create the per-host subagent reference under `skills/shared/references/`,
   moving the Codex model/effort/`fork_turns` contract there verbatim. This
   lands **first** so no intermediate commit loses the content (F4-CONFLICT).
2. Rewrite `AGENTS.md ## Skill Routing` as canonical, and reduce
   `## Subagent Delegation` to its host-neutral core plus the pointer from (1).
3. Update `setup_skill_routing_lib.py` signals and `render_skill_routing.py`
   rendered block to match, resolving P2.
4. Split `session_start_routing.py` `DIRECTIVE` into `DIRECTIVE_BY_HOST` with a
   shared pointer prefix; keep `render_output`'s host-format logic unchanged.
5. Rewrite `tests/test_session_start_routing.py` assertions to pointer-integrity
   form, carrying the reversal note, and add A6 as the regression guard.
6. Run the repo validators, then close through `prove`.

Per the repo's "write the violation before writing the guard" lesson, A6 should
be demonstrated failing against the pre-change tree before step 1 lands.
