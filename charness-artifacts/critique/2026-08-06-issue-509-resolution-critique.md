# Issue #509 Resolution Critique

Date: 2026-08-06

## Decision Under Review

Whether the local #509 fix should normalize implicit URL slugs in
`gather_public_url.py`, keep the strict `write_record.py` contract unchanged,
and carry the source/plugin parity plus omitted-slug execute/readback tests into
the local closeout.

## Execution

Executed: three bounded code-critique angle reviewers (Jackson, Weinberg,
Gawande), one separate counterweight reviewer, and two bounded repair-review
rounds. All were unnamed, read-only, parent-delegated fresh-eye contexts. The
first repair round returned HOLD for missing Unicode record readback; that
assertion was added before the final v3 repair round returned PASS.

## Fresh-Eye Satisfaction

parent-delegated. Parent boundary fingerprints for the angle windows,
counterweight window, and repair windows all returned `verdict: clean` with
`drift: []`.

## Packet Consumed

- JSON packet: `charness-artifacts/critique/2026-08-06-issue-509-resolution-critique-packet-v3-packet.json`
- Markdown render: `charness-artifacts/critique/2026-08-06-issue-509-resolution-critique-packet-v3-packet.md`
- JSON packet SHA256: `33f572e4469f4e0166823cc34c8cf5175a0cd076071e242e5caee6ea782a0ecb`
- Markdown render SHA256: `335f2b7d299ba0100995d0824424f8e7c97bd7be92f9d0aa3fc860d4f57bb875`
- Reviewed-input identity SHA256: `fe73530675e86d633df991655860439295cc90643db87b8399eb955b99f4fe2c`

The JSON packet digest and Markdown render digest are intentionally separate;
the JSON digest is the packet binding. The v1/v2 packets are superseded by v3.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded fresh-eye reviewer.
- Requested spawn fields: `model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`; the repo contract requested `fork_turns=none`, while this host spawn surface exposed the equivalent `fork_context=false` control and no `fork_turns` field.
- Host exposure state: metadata-hidden
- Application state: metadata-hidden — the host returned completed reviewer payloads but did not expose provider-side application metadata.
- Delivery state: findings-received.

## Target

Code critique, shaped by `skills/public/critique/references/code-critique.md`.

## Diff Scope

`gather_public_url._slug_from_url` now percent-decodes and lowercases the URL
path, emits only ASCII alphanumeric/hyphen label characters, and retains the
digest of the original URL. The generated plugin mirror was exported before
verification. One issue-shaped uppercase/encoded-space execute/readback test
and one percent-encoded non-ASCII execute/readback test cover the changed
branches.

## Capability at Stake

The local producer-to-writer contract: an implicit slug must pass the existing
writer validation and create a dated record without requiring an undocumented
explicit slug. Provider roundtrip, installed-host execution, remote CI, and
GitHub issue closure are outside this local critique.

## Angles

- Jackson / problem framing: the fix addresses the reporter's workaround-free
  `--execute` JTBD, preserves explicit slug precedence, and retains the raw URL
  digest. No adjacent broad URL policy was introduced.
- Weinberg / diagnostic boundary: the fix is at the producer that creates the
  implicit value; the generic writer remains strict. Source/plugin parity is
  byte-identical. The Unicode branch was initially under-covered and was
  repaired with a readback assertion.
- Gawande / operational checklist: normal execute creates and reads a dated
  record; existing writer tests cover dry-run, collision, and pointer behavior.
  Source-path execution plus byte parity is sufficient local evidence without a
  duplicate plugin test.

## Counterweight Triage

### Act Before Ship

- `strong` — the new ASCII-only branch required an omitted-slug,
  percent-encoded non-ASCII execute/readback regression under #509's
  “every auto-derived slug passes writer validation” acceptance. Fixed in
  `tests/test_web_fetch_support.py` and re-read by the final repair reviewer.

### Bundle Anyway

- `strong` — retain the source/plugin parity check and both digest-bearing
  filename assertions in the same slice; they are already in the changed
  surface and prevent producer/export drift.

### Over-Worry

- `strong` — query text need not become human-visible in the slug because the
  digest continues to hash the complete original URL.
- `strong` — broad provider, installed-host, live URL, or writer-contract
  refactors would move the fix away from the diagnosed producer boundary.
- `strong` — a duplicate installed/plugin execution test adds no semantic
  coverage while source/plugin files are byte-identical.

### Valid but Defer

- `moderate` — malformed percent-escape policy and broader URL canonicalization
  have no issue evidence or acceptance contract; preserve them as non-claims,
  not as implicit future behavior.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `tests/test_web_fetch_support.py:613-638` | action: fix | note: Unicode percent-encoded implicit-slug branch needed execute/readback coverage; repaired and re-reviewed PASS
- F2 | bin: bundle-anyway | evidence: strong | ref: `skills/public/gather/scripts/gather_public_url.py:43-51` and generated plugin mirror | action: document | note: keep source/plugin parity and digest-bearing filename assertions bound to the same local slice
- F3 | bin: over-worry | evidence: strong | ref: `skills/public/gather/scripts/gather_public_url.py:50` | action: defer | note: query rendering and broad URL/provider normalization are unsupported scope because the raw URL digest preserves identity
- F4 | bin: valid-but-defer | evidence: moderate | ref: `charness-artifacts/issue/2026-08-06-issue-509-causal-review.md:57-60` | action: document | note: provider, installed-host, remote, and GitHub CLOSED proof remain explicit non-claims

## Boundary Ownership

- Producer: `skills/public/gather/scripts/gather_public_url.py` produces the
  implicit slug from the source URL; the generated plugin mirror carries it.
- Consumer: `skills/public/gather/scripts/write_record.py` and
  `gather_writer_lib.validate_slug` are the final consumers that accept or
  refuse the value before persistence.
- Owning surface: gather's implicit-slug producer owns normalization; the
  generic writer owns strict validation and remains unchanged.
- Verdict: owned-correctly

## Pre-Merge Action

The required Unicode readback repair is complete. Before committing, run the
focused suite, source/plugin parity, Ruff, the local quality/critique artifact
validators, and the strongest honest slice closeout. Do not claim provider,
installed-host, remote CI, GitHub CLOSED, or push success from this local
evidence.

## Deliberately Not Doing

Do not make queries human-visible in slugs, loosen `write_record.py` to accept
uppercase or non-ASCII explicit slugs, generalize provider normalization, or
duplicate the source test for an installed plugin. Those would change the
ownership boundary or require evidence outside this slice.

## Next Move

Run the local verification and closeout gates, then record the #509 carrier and
typed local behavior disposition. Keep #509 OPEN until the single final push,
independent remote evidence, and issue adapter closeout readback are actually
performed.
