# Handoff auto-draft stale-citation markers (F9)
Date: 2026-07-27

## Decision Under Review

The chunked-routing auto-draft writer now marks stale citations: `_render_boundaries`
excludes a `missing_paths` path from `- In scope:` and adds a `NOT asserted in scope:`
bullet, and `_render_context_sources` appends `MISSING` / `CLOSED` / `UNRESOLVED`
markers to stale citations. Closes deferred finding F9 — the staleness facts were
computed correctly and then dropped at the last operator-facing surface, so a goal
artifact asserted a moved path was in scope. Out of scope: the parser/staleness layer,
acting on staleness (dropping entries), and every other `## Next Session` item.

## Failure Angles

- **Jackson (problem framing).** Is this the named problem or an adjacent one? Found
  the diff genuinely F9-shaped, but flagged that Boundaries converts a pure
  file-existence fact into a scope verdict, which misfires on an entry whose work is
  to *create* the cited path.
- **Weinberg (diagnostic).** Is the fix at the right layer? Traced the top-level
  `staleness` block ({paths_checked, issue_states_checked}) and found it dies at
  `materialize_chunk_proposal_response` and the ranker packet — `ChunkCandidate`
  has no staleness field, so the drafter structurally cannot know whether a check ran.
- **Gawande (checklist/operational).** What operator step changes? Judged marker
  wording actionability, draft-time signal on the drafter's stdout, rollback safety
  against `check_goal`, and staleness of the operator-consulted contracts.

## Counterweight Pass

The counterweight rejected six of ten concerns and corrected a factual premise I had
accepted from the Weinberg angle: the path check runs on *every* invocation where a
repo root resolves (`parse_handoff_entries.py:148-152`); only the issue-state check is
gated behind `--with-issues`. I verified this directly before acting on the triage.
That narrows the residual false-freshness gap to issue citations alone and is why the
proposed unconditional "citation freshness" caveat bullet was rejected as a
false-in-the-common-case hedge rather than folded in.

It also rejected C1's restructure: the `NOT asserted in scope` wording already says
"re-target or **confirm**", which is the correct branch for a to-be-created path, and
collapsing the branches would re-introduce the conflation the docstring refuses.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: docs/handoff-chunked-routing.md:337-345 | action: fix | note: owning implementation contract still documented the pre-change Boundaries/Context Sources seeding; updated with the exclusion rule, the NOT-asserted bullet, the three markers, and the non-empty-fact-only rule
- F2 | bin: bundle-anyway | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_auto_draft.py:176-179 | action: fix | note: UNRESOLVED marker was a prohibition with no action verb unlike its two siblings; now names "check the issue before planning from it"
- F3 | bin: bundle-anyway | evidence: moderate | ref: tests/test_handoff_chunker_auto_draft.py:287-294 | action: fix | note: the all-paths-missing branch empties the In-scope path list and was never run through check_goal; assertion added
- F4 | bin: bundle-anyway | evidence: moderate | ref: skills/public/handoff/references/chunked-routing.md:84-91 | action: fix | note: pre-existing drift — unresolved_issues was undocumented on every reference surface while the renderer branches on it; added to the vendored reference and the HandoffEntry listing
- F5 | bin: valid-but-defer | evidence: contested | ref: skills/public/handoff/scripts/chunked_routing_types.py:114-122 | action: defer | note: the parser's staleness block never reaches ChunkCandidate, so the drafter cannot distinguish "issue states checked, none closed" from "never asked"; residual is issue citations only, and threading it through MergeProposal/ranker-packet/ChunkCandidate is its own slice — carried as Next Session item 1
- F6 | bin: over-worry | evidence: weak | ref: skills/public/handoff/scripts/chunked_routing_auto_draft.py:113-141 | action: document | note: to-be-created path is already covered by the "confirm" branch; restructure would re-conflate live and absent paths
- F7 | bin: over-worry | evidence: weak | ref: skills/public/handoff/scripts/draft_goal_from_chunk.py:175-195 | action: document | note: a stale_citations stdout block would duplicate facts needing permanent sync, for an operator whose shape_command routes straight into /achieve, which reads the artifact
- F8 | bin: over-worry | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_coordination_floors.py:44-56 | action: document | note: the floor regexes need `issue #N` and `close #N`; the rendered `- Cited issue: #451` colon has never matched, before or after this diff
- F9 | bin: over-worry | evidence: weak | ref: skills/public/handoff/scripts/chunked_routing_auto_draft.py:130-135 | action: document | note: markers need no self-clearing clause; draft scaffolding is overwritten by the Before-phase interview and no gate would enforce a delete-me instruction
- F10 | bin: over-worry | evidence: weak | ref: skills/public/handoff/scripts/chunked_routing_types.py:63-87 | action: document | note: the JSON round-trip is single-constructor-owned via asdict/from_dict and already covered by two CLI subprocess tests; a third would re-prove that a tuple copies

## Reviewer Tier Evidence

- Requested tier: `high-leverage` (adapter `reviewer_tiers.high-leverage`), realized as the host's typed `bounded-reviewer` agent with session-model inheritance.
- Requested spawn fields: `subagent_type: bounded-reviewer`, no host addressing/team `name` (#458), one angle per spawn. The adapter's `model: gpt-5.6-terra` / `reasoning_effort` / `fork_turns` / `service_tier` fields are Codex-host fields; per the CLAUDE.md per-host split they do not apply on this Claude Code host and their omission is contract-conformant, not a degradation.
- Host exposure state: host-defaulted
- Application state: host exposed typed read-only agents; all four reviewers self-reported Read/Grep/Glob only with no Bash/Edit/Write/Agent.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. Four bounded reviewers ran in separate agent contexts — three
angles (Jackson, Weinberg, Gawande) plus one separate counterweight pass, never
collapsed into an angle. All four returned findings directly to the parent.

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-27-f9-auto-draft-packet.json
- Packet SHA256: 2d52e8d61fc151ed004365505c31f50db0a44e155daf484d8515cfd420df39b3
- Identity SHA256: 0ece08a736c49385ca38c40f5ce8e8ee8f4569fc7f90b883586bd38152ee1b58

**Rebind non-claim.** The binding above is scoped with `--reviewed-path` to the six
code/doc/test surfaces under review; the default working-tree capture also swept the
critique artifact and the packet files themselves, so every edit to this document
staled its own binding; it is captured with the six paths already staged, because
the identity also covers the staged/unstaged patch split and `git add` moves it.
The reviewers consumed the *pre-fix* state of these six paths
(packet identity `eeb09390006550df77492e30c55b1c8ef1415787a5f128a1c19f73ac657a1d2c`);
applying the act-before-ship and bundle-anyway fixes correctly staled that capture, and
the bullets above rebind to the final state. No reviewer saw the post-fix tree: F1–F4
are fixes derived from their findings, not re-reviewed by them.

**Boundary fingerprint non-claim.** The rail-1 snapshot was taken before the spawns,
but I ran `verify` only after applying my own post-review fixes, so it reported drift
it cannot attribute. Every drifted path is accounted for by a parent action: the two
packet files were written by `prepare_packet.py` before the spawns, and
`docs/handoff-chunked-routing.md` plus both `chunked-routing.md` copies were edited by
me after the reviews returned. The independent evidence that no reviewer mutated the
tree is the typed envelope — `bounded-reviewer` exposes Read/Grep/Glob only. I am not
claiming a clean verify; I am claiming the drift is parent-caused and the reviewers had
no write capability. Next time, bracket the review window tightly and verify before
editing.

## Boundary Ownership

- Producer: `chunked_routing_staleness.annotate_entries` / `staleness_summary`, invoked from `parse_handoff_entries.py`.
- Consumer: the achieve Before-phase reader of the auto-drafted goal artifact (and, separately, the ranking agent, which already receives both halves via the chunk-proposal packet).
- Owning surface: the handoff auto-draft renderer owns *rendering* producer-supplied facts; the ChunkCandidate/ranker-packet carriage owns *transporting* the run-level checked-ness fact.
- Verdict: owned-correctly

## Deliberately Not Doing

- No unconditional "citation freshness" caveat bullet: it would disclaim the path check that actually ran in the common case, and trains readers to skip the section.
- No `stale_citations` block on the drafter's stdout: a second copy of the same facts requiring permanent sync, for a consumer that reads the artifact anyway.
- No self-clearing "delete once resolved" clause on markers: invents a contract no gate enforces.
