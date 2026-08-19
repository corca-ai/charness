# issue 673 resolution critique
Date: 2026-08-19

## Decision Under Review

The resolution of [#673](https://github.com/corca-ai/charness/issues/673): routing the five
adapter libraries that called `adapter_lib.load_yaml_file` bare through a shared
`read_declared_adapter`, so `adapter_version_verdict.parse_refused` and
`declarations_dropped` stop being structurally dead for their consumers.

## Failure Angles

- **Changing HOW a surface fails changes what its consumers observe.** Five resolvers move
  from raising to returning; anything keyed on the raise, or on the exit code that followed
  it, silently takes a different path.
- **The issue's own diagnosis could be stale.** It names six resolvers and a "non-zero exit"
  acceptance; both were written before a sibling repair landed.
- **Convergence produces duplication.** Routing five libraries through one loader makes their
  bodies near-identical, which is `#550`'s subject — and the cheap response is to classify it
  away rather than extract it.
- **A module split can hide a behavior change** behind a re-export.

## Counterweight Pass

REAL BLOCKERS, all folded before close:

- A REGRESSION THIS RESOLUTION CAUSED. Making five resolvers exit 0 instead of tracebacking
  removed `scripts/resolve_artifact_path.py`'s only protection — its subprocess return code —
  and it began resolving `charness-artifacts/quality/latest.md` over a repo that declared
  `docs/mine-q`, at exit 0. Guarded on the CONDITION now, with a three-door test.
- Twelve claim defects on surfaces someone reads to decide, including
  `adapter_version_verdict` telling readers in three places that six resolvers are blind when
  zero are, and a swallow-arm justification refuted by a live exit-0 bypass this very change
  closed.
- The split's first cut broke every skill script that path-loads `adapter_lib` with nothing
  on `sys.path`, and its registration left a half-initialised module in `sys.modules` on
  failure — the second-error-hides-the-first shape its own comment names.

OVER-WORRY, raised and not folded: normalising the sixteen exit codes, which the issue's
acceptance asks for. The divergence is not what made a guard blind, and changing it is a
behavior change for every caller that branches on the code. Pinned in `NON_ZERO_EXIT_SKILLS`
so a move in either direction is a diff rather than a silence.

MEASUREMENT CORRECTIONS to the issue itself: FIVE resolvers tracebacked, not six
(`announcement` was repaired by the predecessor), and the exit codes are a third
inconsistency the issue does not name.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/resolve_artifact_path.py | action: fix | note: this resolution removed the consumer's only protection and it began resolving a charness default over a repo that declared otherwise
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/adapter_version_verdict.py | action: fix | note: the consumer-guard module documented a hole it no longer has, in three places, and justified its swallow arm with a claim a live bypass refutes
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/adapter_lib.py | action: fix | note: the module split broke path-loading from skill scripts and left a failed parser registered, hiding its own cause
- F4 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/quality/dup-review.json | action: document | note: convergence surfaced #550; resolve_adapter_payload was EXTRACTED for four libraries and only the residue classified, each with its own reason
- F5 | bin: over-worry | evidence: moderate | ref: tests/quality_gates/test_every_resolver_answers_a_refused_document.py | action: defer | note: uniform exit codes, asked for by the issue and deliberately not delivered; the split is pinned instead
## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (this repo's read-only typed subagent).
- Requested spawn fields: subagent_type=bounded-reviewer, no host addressing name, read-only tools (Read, Grep, Glob), one bounded packet per round naming intent, changed files, invariants, non-claims and out-of-scope lines.
- Host exposure state: applied
- Application state: host-confirmed: three reviewer reports were returned to the parent across two rounds, each naming the tools it actually used and the findings it could not construct.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; each round's packet was authored inline in the spawn prompt and is reproduced in the goal's `## Slice Log` slice 2 critique field. -->

## Boundary Ownership

- Producer: `scripts/adapter_lib.read_declared_adapter` — the one owner of what a resolver reports about a document it could not fully read.
- Consumer: every `skills/public/*/scripts/resolve_adapter.py`, and through them `scripts/adapter_version_verdict`'s three predicates in each skill's guards.
- Owning surface: adapter resolver contract.
- Verdict: owned-correctly
