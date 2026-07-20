# Critique Review
Date: 2026-07-20

## Decision Under Review

A self-initiated structural improvement following the `.mjs` test-discovery fix:
a new advisory quality inventory (`inventory_hardcoded_discovery.py` +
`discovery_filter_scan_lib.py`) that flags portable constants hardcoding a
**polyglot** (2+ code-language-family) test/source-file discovery list — the
measurement-contract divergence class where a baked-in list omits a language the
consuming repo actually uses. Each flagged site must be adapter-owned or carry an
inline `# discovery-boundary: <reason>` marker.

A broad first cut flagged 71 sites (mostly benign docs `*.md` / config `*.json` /
single-language `*.py` globs) — proof a pure lexical "hardcoded glob" lint is
noise. Narrowing to name-advertised extension/pattern constants spanning 2+
families in a fixed CODE_LANGUAGE_FAMILIES map reduced it to exactly 2 live sites,
both now marked: the adapter test-discovery default (genuinely adapter-owned) and
the lint-ignore suffix set (language-syntax-scoped boundary). Registered as an
opt-out quality inventory (consumer-fields, catalog, dispatch), plugin mirror
synced.

Two distinct-lens bounded fresh-eye reviewers ran (scope/false-negatives;
marker-honesty/disposition/gate-fit) with an in-lens counterweight; rail-1
reviewer-boundary fingerprint verified clean around the pass.

## Failure Angles

- Scope correctness & false negatives: does the narrow definition miss real
  divergences, and are the limits honestly disclosed?
- Marker honesty & disposition: is the presence-only marker a rubber stamp, and
  are the two live dispositions honest?
- Gate fit: registration parity, advisory-interpretation-contract compliance.

## Counterweight Pass (four-bin triage)

- K1 | bundle-anyway (fixed): the INTERPRETATION `blind_spots` did not disclose
  the two narrow-scope limits — intra-family omission (a JS-only list missing
  `.mjs`, the founding-bug shape at finer grain, reads as single-family and is
  not flagged) and extensions outside the fixed family map reading as non-code.
  Now disclosed, with a regression test asserting the disclosure and that a
  single-family omission is out of scope.
- K2 | bundle-anyway (fixed): the marker window (same line or directly above)
  was implicit; the docstring now states a gapped marker does not silence. Added
  `ValueError` to the `ast.parse` guard (null-byte source) so the scan degrades,
  never crashes.
- K3 | over-worry (confirmed sound, no change): presence-only marker is the
  correct advisory floor, not a rubber stamp — `MARKER_RE` requires a non-empty
  reason, marked sites stay in output for audit, and the marker is greppable; a
  schema would add brittleness for negligible gain on a reversible advisory. The
  marker line-window off-by-one was verified correct.
- K4 | valid-but-defer: widening to inline `.rglob`/`git ls-files` pathspec
  discovery (reintroduces the 71-site noise — disclosed, deferred); expanding the
  family map (php/cs/swift/scala/elixir) on consumer relevance; making lint-ignore
  suffix discovery adapter-owned like test discovery (a legitimate sibling of the
  `.mjs` fix, out of this gate's scope). `run_dead_code_advisory.py`'s Python-only
  `*.py` scan is a genuine intentional boundary, confirming the causal review's
  earlier call — not a missed undercount.

## Recurrence Verdict

The gate is a preventive tripwire: it reads 0 unmarked on charness today and
flags the next unmarked polyglot discovery list before it ships. Its own blind
spots (intra-family omission, finite family map, inline/dynamic discovery) are
now self-declared honestly rather than hidden, so a consumer knows exactly what
it does and does not catch.

## Boundary Ownership

- Verdict: owned-correctly

The gate is a cross-surface generic: the `quality` skill PRODUCES the advisory
and the marker convention; each portable script that holds a discovery list
CONSUMES it and owns its own `# discovery-boundary:` disposition in-code. The
advisory lives in the quality inventory suite where measurement-contract concerns
belong; the marker is an author-owned in-code opt-out, not a central allowlist —
no producer/consumer inversion.

## Reviewer Tier Evidence

<!-- allowed Host exposure state enums only -->
- Requested tier: high-leverage
- Requested spawn fields: none — Claude Code host, typed `bounded-reviewer` (Read/Grep/Glob) with session-model inheritance per the repo per-host subagent contract; no Codex model requested on this host, so the omission is contract-conformant, not a degradation.
- Host exposure state: host-defaulted
- Application state: the host spawned the typed `bounded-reviewer` agent by name for both critique-angle reviewers; the read-only envelope bound and the rail-1 reviewer-boundary fingerprint verified clean (no index/worktree drift) after both reviewers returned, so approvals are valid and reviewers ran on the parent's session-inherited model.

## Fresh-Eye Satisfaction

parent-delegated — two distinct-lens resolution reviewers with an in-lens
counterweight; rail-1 reviewer-boundary fingerprint verified clean.
