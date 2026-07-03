# Concept Ideation
Date: 2026-07-03

Concept name: **Portable concept-boundary / ownership discipline for gather (and lifecycle skills)**

Source issues: #417 (gather credentialed-provider boundary — concrete ship target),
#414 (portable skills lack a repo-owned concept-boundary checkpoint), #416 (portable
skill boundary drift observed during Ceal incident), #408 (prevent symptom-driven
prompt/core fixes from bypassing ownership-boundary review). Operator steer 2026-07-03:
ship the gather cleanup through push+release so the Ceal consumer can drop its local
quarantine and resume; **no Ceal-coupled implementation may enter charness.**

## World Model

- **Actor:** an agent running an installed, portable charness `gather` in a consumer
  repo (Ceal is the reporting consumer, but charness must not know Ceal).
- **Job:** turn an external source into a durable local knowledge asset.
- **Status quo failure:** generic `gather` discovery surfaces (SKILL.md default steps,
  find-skills inventory, references, and `docs/gather-provider-ownership.md`) advertise
  credentialed provider-CLI routes (`gather-slack`, `gather-notion`, `gws`/Google
  Workspace, Drive) as if they were generic gather behavior. Consumer workers keep
  *discovering* those stale routes and reasoning about provider CLIs, forcing the
  consumer to carry a local quarantine/sanitize stopgap — policy that belongs upstream.
- **Conflicting internal doc:** `docs/gather-provider-ownership.md` currently frames
  Slack/Notion as **charness-owned provider runtime** (near-term follow-up #2). #417's
  operator direction redraws this: plain `gather` = credentialless/public by default;
  credentialed org data flows through the **consuming runtime's** first-class capability
  CLI/connector, described as a host/runtime-owned boundary, never a prescribed provider CLI.

## Verified Facts

- #417 operator direction (verbatim intent): "plain `gather` should mean sources that do
  not require credentials. Credentialed Slack, Notion, Google Workspace, Drive ... should
  be reached through the consuming runtime's first-class capability CLI/connector surface."
  Non-goal: "Do not encode Corca/Ceal-specific command names into Charness."
- #416/#414: charness is a portable skill/plugin surface and must not learn a consumer's
  `core/runtime/connector/workflow/instance` taxonomy; charness owns only the lifecycle
  discipline that *asks for* the repo-owned boundary signal and carries it through.
- `docs/gather-provider-ownership.md` (read in full) is the doc most in tension with #417
  and is named in #417's re-read obligation.
- gather is also touched by the live reference-compaction churn via #411 (gather
  claim-fidelity floor redesign). Same surface, two intents — coordinate edits.

## Decision (RESOLVED — operator away, proceeding on recommendation)

**Option A — Reframe + gate.** Redraw the concept so generic `gather` advertises only
credentialless/public sources by default. Move credentialed Slack/Notion/GWS out of
generic discovery (SKILL.md default, find-skills inventory, references) and describe them
as a **host/runtime-owned capability boundary** — no prescribed provider CLI names in
generic guidance. Keep any existing provider runtime available behind an **explicit
credential/grant-gated** path (not deleted → reversible). This fully removes the
consumer's discovery pain, satisfies #417 portably, and avoids an irreversible deletion.

Rejected now:
- **Guidance-only** — smaller, but leaves credentialed runtime advertised anywhere a
  worker looks past the top-level prose; weaker guarantee for the consumer.
- **Deprecate/remove runtime** — most literally matches "move credentialed out of
  gather," but it is a destructive, irreversible (north-star P4/P5) removal that breaks
  grant-based consumers and is a heavier release than the problem requires. Can be filed
  as a follow-up if the boundary proves it should not exist at all.

## The general checkpoint (#414/#416/#408) — frame, not this ship

The portable, repo-owned concept-boundary checkpoint is the *generalization*: charness
lifecycle skills (impl/critique/issue/quality/spec/achieve) should carry a neutral
"boundary ownership" prompt — who PRODUCES this fact, who CONSUMES it — and a closeout
section for cross-surface fixes, **parameterized by an adapter-provided owner vocabulary**
so charness never hardcodes a consumer's nouns. The gather fix is the first concrete
instance of that discipline; the general checkpoint is deferred to its own spec pass.

## Structured Questions

- Q1 | urgency: must-resolve | depends-on: null | action: spec | note: RESOLVED as Option A (reframe + gate); operator may still override on return.
- Q2 | urgency: probe-in-impl | depends-on: Q1 | action: impl | note: does any provider runtime physically remain to gate, or is it already only guidance? (map pass answers this)
- Q3 | urgency: probe-in-impl | depends-on: Q1 | action: impl | note: coordinate the gather edits with #411's claim-fidelity floor redesign so the same surface is not rewritten twice with divergent intent.
- Q4 | urgency: defer | depends-on: Q1 | action: spec | note: the general #414/#416/#408 adapter-owned boundary checkpoint is a separate downstream spec, not this ship.

## Open Questions

- How much of `docs/gather-provider-ownership.md` gets rewritten vs superseded? (It is the
  doc #417 flags; likely a targeted correction of the credentialed-ownership framing.)
- Does find-skills' capability inventory advertise `gather-slack`/`gather-notion` as
  generic routes, and does removing them from generic discovery need a support-skill
  metadata change vs a prose change? (map pass answers this.)

## Next Step

Route to **impl** on the gather boundary cleanup (Option A), scoped portably (no Ceal
nouns), then verify → commit → push → release with an irreversible-boundary confirmation
(distinct observer + distinct evidence channel) at publish. General checkpoint
(#414/#416/#408) is filed as a follow-up spec. Waiting on the surface-map pass to pin
exact file:line edit targets before mutating.

## Resolution (implemented 2026-07-03)

Option A implemented. The discovery leak was mechanism-level, not just prose: with no
adapter, `resolve_adapter.py` defaulted ALL sources to `direct-cli`, so `advise_slack_path.py`
handed workers `support/gather-slack/scripts/export-thread.sh`. Fix flips the DEFAULT for the
two credentialed org providers that ship a charness-owned wrapper (`slack`, `notion`) to
`none`; `github` (dev tooling) and `google_workspace` (no repo-owned CLI → already routes to
host/export/browser) stay `direct-cli`. Credentialed access is now an explicit adapter opt-in
(`host-mediated` or `direct-cli`). Support runtimes kept (no deletion). RCF floor references
(source-priority/capability-contract/browser-mediated-private-sources) untouched.

Changed: resolve_adapter.py, advise_slack_path.py, gather/SKILL.md, references/gather-provider.md,
adapter.example.yaml, docs/gather-provider-ownership.md, + 2 test files pinned to the new
posture, + regenerated plugins/ mirror. Verified: full pytest suite 3980 passed;
check_skill_contracts, validate_public_skill_dogfood, skill-ergonomics, claim-fidelity specs,
packaging-install-surface all green. Fresh-eye subagent review run before commit.

Deferred follow-up (own spec): the general #414/#416/#408 adapter-owned concept-boundary
checkpoint. Also note: gather is the surface #411 (claim-fidelity floor redesign) also touches —
coordinate when Slice 7 reaches gather.
