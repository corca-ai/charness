# v1.3.0 Release Critique

Date: 2026-07-17
Verdict: APPROVE minor (1.2.0 → 1.3.0)

## Decision Under Review

Cut charness 1.3.0 carrying four local commits (`963e147c` pause-only
commit-msg failure-text polish + template↔regex drift test; `b1b74e0c` prove
dogfood promotion to reviewed + `review_required_skills` + md/json drift pin;
`4a23d5d9` goal closeout artifacts + handoff refresh; `c0d807b7` per-host
subagent contract split + dogfood scaffold `prompt_fallback` advisory), then
push and publish per the operator's "푸시 릴리즈" instruction.

## Fresh-Eye Satisfaction

parent-delegated bounded release critique in a different agent context
(bounded-reviewer a2d67bb1234497080, read-only Read/Grep/Glob envelope);
zero-drift reviewer boundary fingerprint verified around the review.

## Reviewer Tier Evidence

- Requested tier: high-leverage (release critique class).
- Requested spawn fields: per-host contract (AGENTS.md `Subagent Delegation`,
  split 2026-07-17) — Claude Code host convention applies: typed
  `bounded-reviewer`, session-model inheritance.
- Host exposure state: host-defaulted
- Application state: read-only envelope asserted by agent type (Read/Grep/
  Glob); parent-side boundary fingerprint verify returned `drift: []`.

## Failure Angles

- Bump honesty (patch vs minor vs major) against the release version policy.
- Consumer breakage: `prove` joining `review_required_skills`; new
  `prompt_fallback` field/warnings; hook failure-text change on installed
  hosts.
- Install-surface integrity (generated manifests, mirror parity, drift).
- Release-notes truthfulness (non-claims for the prove promotion).
- Push/publish blockers (secrets, placeholders, shouldn't-ship artifacts).

## Structured Findings

- F1 | bin: over-worry | evidence: strong | ref: scripts/public_skill_dogfood_validation_lib.py | action: document | note: the tightened `review_required_skills` is registry data resolved from the target repo's own `docs/public-skill-dogfood.json`; the exported plugin ships no registry, so consumer repos are unaffected — only charness's own gate tightened, and its registry satisfies it (20/20).
- F2 | bin: valid-but-defer | evidence: strong | ref: scripts/public_skill_dogfood_lib.py | action: fix | note: consumer-visible output changes (new `--json` field `prompt_fallback`, stdout WARNING lines, stderr advisory; pause-only hook failure text) must be named in the release notes — folded into the notes below.
- F3 | bin: valid-but-defer | evidence: strong | ref: docs/public-skill-dogfood.json | action: fix | note: notes must not claim cross-host, multi-run, or evaluator-backed proof for the prove promotion (single Claude Code session observation with explicit non-claims) — folded into the notes.
- F4 | bin: valid-but-defer | evidence: strong | ref: docs/handoff.md | action: fix | note: the handoff baton ("v1.2.0 remains the published surface"; "push … or fold into the next release") goes stale at publish; the release flow's baton reconcile must update it to 1.3.0 — completed as part of this release's closeout.
- F5 | bin: over-worry | evidence: strong | ref: packaging/charness.json | action: defer | note: all version-carrying surfaces read 1.2.0 with no drift and no hand-edited generated manifests; `.agents/plugins/marketplace.json` carrying no version field is its schema, not drift.
- F6 | bin: over-worry | evidence: strong | ref: charness-artifacts/goals/2026-07-17-prove-dogfood-via-444-polish-host-log-probe.json | action: defer | note: committed probe artifact embeds $HOME paths and session UUIDs, consistent with six prior committed probe artifacts (established artifact policy); noted, not a blocker.

## Release Notes Basis (truthful bullets)

- Commit-msg closeout hook: pause-only failures now print the one-line
  `AI-provenance:` remedy instead of the generic close-keyword/ledger text;
  mixed and non-pause failures keep the existing text; exit/JSON semantics
  unchanged. New drift test pins the hook's pause regex to the
  resolution-brief template vocabulary.
- Dogfood scaffold: rows carry an advisory `prompt_fallback` flag; both
  suggest CLIs warn (non-blocking stderr; stdout WARNING in human mode) when
  a row's prompt is the frontmatter-description fallback. `--json` payload
  gains the field.
- `prove` promoted to `reviewed` on one live Claude Code consumer-run
  observation (explicit non-claims: single host, no Cautilus run) and joined
  `review_required_skills`; realistic `PROMPT_HINTS["prove"]` prompt added.
- `docs/public-skill-dogfood.md` required list now mirrors the json under a
  checked-in drift pin (repairs a pre-existing achieve/hotl omission).
- Authoring contract (repo prose, no installed behavior change): subagent
  model/effort request split into per-host contracts (Codex vs Claude Code).

## Deliberately Not Doing

- No issue closes at release time (nothing pending closure).
- No major bump: no rename, removal, or invocation break in any shipped
  surface.

## Boundary Ownership

- Verdict: owned-correctly

Release mechanics stay in the repo-owned publish helper; registry/list
ownership stays with the dogfood validator pair; hook text stays in the
consumer hook with the producer template pinned by the drift test.

## Packet Consumed

none — release-boundary critique over the four commits listed above (packet
sections not declared for this ad hoc release scope; changed surfaces
enumerated inline).
