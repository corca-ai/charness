# Session Retro: Lifecycle Feedback and Quality Truthfulness
Date: 2026-07-14

## Mode

session

## Context

The north-star improvement slice added deterministic lifecycle follow-through
for successful issue close and release publish operations, separated objective
lifecycle evidence from human satisfaction, reconciled the current quality
artifact with the already-published v1.0.5 release, and repaired the shared
`SKILL_DIR` bootstrap contract after a consuming-repo failure report. The
configured retro trigger fired because installed release and skill surfaces
changed.

A follow-up consumer report then showed that the reviewer-boundary contract
still named Charness source paths from the consuming repository. The requested
outcome was explicit first-class consumption by both Claude and Codex, rather
than a Claude-only packaging repair.

## Evidence Summary

- The canonical spec is
  `charness-artifacts/spec/2026-07-14-lifecycle-feedback-and-quality-truthfulness.md`.
- The implementation added `scripts/lifecycle_usage_capture.py`, wired issue
  close and release publish producers, synchronized the plugin mirror, and made
  lifecycle-capture status visible in the release artifact.
- Focused verification passed 163 tests. Packaging, skills, integrations,
  attention visibility, dogfood, critique, spec durability, documentation, and
  boundary checks passed before this retro.
- Two bounded critique angles and a separate counterweight passed reviewer
  boundary verification. Their actionable findings were resolved in
  `charness-artifacts/critique/2026-07-14-lifecycle-feedback-and-quality-truthfulness-critique.md`.
- No Cautilus evaluation or installed-behavior rerun was performed or claimed;
  this slice changes deterministic repository behavior rather than model
  routing behavior.
- The locked standing suite exposed and then verified a test-environment
  isolation repair: 4,603 tests passed under read-only quality mode.
- `sh`, `bash`, and `zsh` reproduced the reported command-scoped assignment
  failure; source and synchronized plugin debug resolvers then ran from an
  unrelated temporary repository using one persistent export/invocation block.
- A clean consumer Git repository now invokes the reviewer fingerprint through
  the installed skill directory. The plugin exporter carries Claude's bounded
  reviewer envelope under `agents/`, while Codex uses a documented native
  `explorer` mapping rather than a false claim that it loads Claude markdown.
- Two independent fresh-eye angles and a counterweight confirmed the consumer,
  host-mapping, and proof boundaries; parent-side fingerprints remained clean.

## Waste

The first implementation treated `released` and `closed_issue` as satisfaction
signals. Fresh-eye critique caught that metrics-gaming risk, but defining the
signal taxonomy in the spec before wiring the producers would have avoided the
repair. Attention-state declaration and refreshed public-skill dogfood evidence
also arrived during pre-lock rehearsal instead of the mutation/sync phase,
requiring two extra closeout passes.

The shared bootstrap reference also conflated an agent-visible skill locator
with an exported shell variable. Its non-exported examples invited a plausible
environment-prefix command, and focused proof initially missed both aggregate
quality-mode inheritance and source-cwd/shell-lifetime first-reader traps.

The reviewer-boundary portability seam was already recognized as deferred, but
the earlier closeout did not turn it into a consumer-path acceptance check. That
left an ordinary installed use path free to cite a source checkout until the
operator reported the failure.

## Critical Decisions

- Use the exact deterministic delivery/feedback identity, one append-mode write
  under the shared lock, replay no-op behavior, and explicit partial/conflict
  outcomes; do not guess a latest event or backfill ambiguous history.
- Keep lifecycle capture best-effort after independently verified external
  success, so telemetry cannot overturn a completed issue close or release.
- Count `released` and `closed_issue` as objective lifecycle follow-through,
  while reserving satisfaction for `accepted` and `human_confirmed`.
- Defer installed-behavior smoke and validator refactors until behavior work or
  a measured failure justifies them; line count alone is not a north-star need.
- Treat path discovery, exported shell state, current directory, and shell
  lifetime as separate interfaces: use an absolute skill path outside the
  source root and keep export plus dependent expansion in one tool invocation.
- Treat the helper path and host discovery path as separate consumer contracts:
  package Claude's envelope where Claude loads it, map Codex to its native
  reviewer, and do not substitute shared markdown for a Codex custom agent.

## Expert Counterfactuals

- Douglas Engelbart's system-improving lens would design the tool, method, and
  language together: the capture helper is the tool, the verified-producer
  sequencing is the method, and the objective-lifecycle/satisfaction split is
  the language. Applying that frame at the spec boundary would have exposed the
  semantic mismatch before implementation and made the attention/dogfood
  visibility surfaces part of the initial change list.
- The same lens applied to bootstrap work makes the shared instructions, the
  escape-prevention validator, and unrelated-directory proof one system. That
  framing avoids fixing only the reported command while leaving agents another
  first-run path or shell-lifetime failure.
- A direct evidence-discipline counterfactual asks which wrong answer could
  escape: the dangerous outcome was a green dashboard that mislabeled machine
  lifecycle completion as human satisfaction. That question correctly makes
  taxonomy separation a release-worthy fix, while leaving reversible cleanup
  and speculative smoke work deferred.
- Applied to the reviewer seam, the same question would have required a clean
  consumer repository to exercise every command named in the policy before the
  earlier repair was considered complete. That is now the portability test's
  detection point.

## Sibling Search

- lifecycle-producing integrations: issue close and release publish | decision: both in-scope siblings now use the shared deterministic capture helper and expose explicit outcomes | proof: focused producer tests plus synchronized plugin copies | follow-up: none

## Next Improvements

- workflow: applied in this slice — producer wiring, attention-state visibility,
  public-skill dogfood evidence, and durable artifact status are one mutation
  checklist before pre-lock proof.
- capability: applied in this slice — objective lifecycle follow-through has a
  separate report count and rate instead of inflating satisfaction.
- memory: persist this retro and refresh `recent-lessons.md`; no new handoff item
  is needed for lifecycle behavior smoke or behavior-led validator splits; the
  handoff now explicitly owns the unpublished bootstrap/reviewer-boundary fix's
  later authorized release/update boundary.

- workflow: applied in this follow-up — a known deferred portability seam is
  not complete until a clean consumer test covers the named installed command,
  its host asset, and the truthful host mapping.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-14-session-retro.md
