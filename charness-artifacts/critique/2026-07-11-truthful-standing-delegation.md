# Truthful Standing Delegation
Date: 2026-07-11

## Decision Under Review

Preserve repo-owner standing delegation and independent fresh-eye review while
removing the false claim that repo instructions override higher-priority
system, developer, or host prohibitions. Route the two reviewed host references
to their actual integration owners without suppressing findings.

## Failure Angles

- Instruction hierarchy: `THIS SECTION WINS` could induce an agent to violate
  an active higher-priority prohibition instead of reporting the constraint.
- Review integrity: hierarchy truth must not regress into asking for consent a
  second time or permitting a same-agent substitute when spawning is allowed.
- Portability and UX: intentional setup-policy and config-search paths must stay
  concrete and visible; only their review context changes.

## Counterweight Pass

- The hierarchy inversion and literal-phrase re-consent detector were real
  blockers; both changed before the verification lock.
- The host paths, markdown-preview precedence, and all lexical findings remain.
  No generic host API, new blocking gate, or count target was introduced.
- Greenfield consent provenance remains a watch item until consumer evidence
  shows that setup-generated wording manufactures authorization.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/setup/references/agent-docs-policy.md | action: fix | note: replace false precedence claims with a truthful standing request bounded by higher-priority prohibitions.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/setup_agent_docs_fresh_eye_lib.py | action: fix | note: detect semantic future re-consent phrases while accepting truthful hierarchy acknowledgements.
- F3 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/scripts/skill_text_quality_lib.py | action: fix | note: route setup policy and dual-host config paths to their real review owners without suppressing hits.
- F4 | bin: bundle-anyway | evidence: strong | ref: AGENTS.md | action: fix | note: align dynamic-workflow wording without forbidding ordinary single-agent continuation when orchestration is unavailable.
- F5 | bin: over-worry | evidence: strong | ref: skills/support/markdown-preview/SKILL.md | action: document | note: do not remove intentional config paths, change lookup precedence, add a generic host API, or optimize the lexical count.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: adapter mapping `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: host-defaulted
- Application state: the host accepted parent-delegated reviewers, but did not expose provider-side application metadata.

## Fresh-Eye Satisfaction

parent-delegated — permission-hierarchy and portability reviewers disagreed
productively; a separate counterweight fixed the scope, and the final diff
review found four concrete defects before passing the corrected source/mirrors.
Packets consumed: `2026-07-11-101842-packet.md` and
`2026-07-11-103004-packet.md`. Rail-1 verification reported zero drift after
every review boundary.

## Boundary Ownership

- Producer: setup policy produces standing delegation guidance; host config
  resolvers produce concrete compatibility paths; quality only annotates hits.
- Consumer: repo operators and agents deciding whether review may spawn and
  whether a host reference is portable prose or an intentional integration.
- Owning surface: setup policy/inspector for authorization, runtime config
  owners for lookup paths, quality inventory for non-dispositive routing.
- Verdict: moved-to-owner
