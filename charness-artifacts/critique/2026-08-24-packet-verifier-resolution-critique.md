# Reviewer Packet Verifier Resolution Critique
Date: 2026-08-24

## Decision Under Review

Expose the existing reviewed-input identity owner through one public critique
command, and put that exact command in both the prepare receipt and packet
Markdown. Reviewers must consume the command's semantic verdict instead of
guessing that a domain-separated `content_sha256` is a raw `sha256sum` value.

## Failure Angles

- A new command could duplicate the identity algorithm and drift from its owner.
- Packet-byte validity could be mistaken for current reviewed inputs.
- A malformed, wrong-kind, zero-path, or stale packet could render `current`.
- Receipt and Markdown could carry different or non-executable commands.
- The source command could work while its checked-in plugin export is absent or
  stale.

## Round 1

The bounded reviewer executed the exact command printed in
`2026-08-24-packet-verifier-r1-packet.md`; it returned `ok: true`,
`status: current`, and the expected packet/input identities. The reviewer then
read the complete uncommitted surface and returned `pass` with no blocking
findings. Focused checks run by the reviewer covered six new tests, packaging,
command docs, repo-copy invariants, skill validation, and Python compilation.

Boundary window `packet-verifier-r1` verified clean after delivery:
`ok: true`, `verdict: clean`, with empty `drift`, `parent_attributed_drift`, and
`unmatched_parent_paths`.

The parent separately challenged the zero-path arm after review. The existing
owner at `scripts/reviewed_input_identity.py` already refuses it as
`declared reviewed inputs cover zero paths`; the new command delegates to that
owner and requires its reason to be `current` before exiting zero.

The closeout structural sweep then found one defect that focused behavior tests
did not: the new verifier had hand-copied a bootstrap loader instead of carrying
the repo's canonical shim. `check_bootstrap_shim_consistency.py --fix` repaired
the source, and the normal plugin sync regenerated the installed copy. Because
that repair touched the verdict command, it triggered round 2.

## Round 2

A second bounded reviewer read the whole repaired surface. The reviewer executed
the new packet's exact command (`status: current`), confirmed the source and
installed verifier match the canonical shim and each other, exercised both
entrypoints, and returned `pass` with no findings. The canonical shim gate
covered 120 files, the six focused verifier tests passed, and packaging validation
passed. Boundary window `packet-verifier-r2` verified clean after delivery with
no drift or unmatched parent paths.

The post-round-2 closeout then exposed a conflict between two structural gates:
the bootstrap gate requires every standalone skill command to carry the exact
canonical shim, while the duplicate ratchet classified the new member of that
same mandatory family (`4ea1108c10838c57`) as new clone debt. The ratchet's scoped
`--accept-family` path recorded that one exact fingerprint in its baseline; no
source was distorted to evade either gate. This changes a gate baseline after
round 2 and therefore ships `accepted-unreviewed-under-round-cap`, with the next
closeout rerun as executable evidence rather than a false third review claim.

## Counterweight Pass

- The packet Markdown is not independently hash-bound. This is not a blocker:
  the JSON packet byte digest and domain-separated reviewed-input identity are
  the proof object, while a focused first-reader test pins Markdown/receipt
  command concordance and execution.
- A malicious process that can rewrite both code and expected digests is outside
  this local freshness control. The command proves declared packet/input
  identity against the current repository; it is not a hostile-host attestation.

## Structured Findings

- F1 | bin: over-worry | evidence: moderate | ref: scripts/critique_packet_lib.py:231 | action: document | note: Markdown is not separately hash-bound, but it carries the same generated command as the receipt while the JSON packet and reviewed-input identity remain the canonical proof object

## Reviewer Tier Evidence

- Requested tier: high-leverage — this command renders verdicts on a proof surface, for both rounds.
- Requested spawn fields: model `gpt-5.6-terra`, reasoning effort `medium`, fork turns `none`; the host-required task identifier was also supplied for result retrieval, for both rounds.
- Host exposure state: requested_fields_sent
- Application state: the spawn API accepted the request; no independent runtime signal proves the effective model or effort.
- Delivery state: findings-received for both rounds

## Fresh-Eye Satisfaction

parent-delegated — distinct read-only bounded reviewers returned `pass` in both
rounds; both boundary fingerprint windows verified clean.

Fresh-eye pass: skills/public/critique/scripts/verify_packet.py — round 1 found
no verdict defect; after the canonical bootstrap-shim repair, round 2 read the
whole repaired surface and found none.

Fresh-eye pass: charness-artifacts/quality/dup-ratchet-baseline.json — skipped,
accepted-unreviewed-under-round-cap because the exact canonical-shim family was
scoped into the ratchet baseline only after the round-2 gate run.

## Dogfood And Scenario Review

The maintained `critique` dogfood prompt, routing, artifact home, counterweight
triage, and acceptance evidence remain applicable. The existing acceptance row
already requires a consumed prepare packet to bind exact packet bytes and
path-scoped reviewed inputs so stale verdicts are visible. This slice makes that
existing contract executable for the first reader; it does not change the prompt,
routing choice, durable artifact location, or scenario registry. Deterministic
first-reader tests plus two packet-bound fresh-eye rounds own the change. No live
Cautilus run or scenario-registry mutation is needed or claimed.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-24-packet-verifier-final-packet.json
- Packet path: charness-artifacts/critique/2026-08-24-packet-verifier-final-packet.json
- Packet SHA256: 704f490cafa84200d5e21bb5920a66f56a7d6999d0a39ef94373a44a0b52e21c
- Identity SHA256: 5aef9c791d68bcacb0df61219b449e04fcfb00dec22edc9760e4b841d69761ea

This final parent-consumed packet binds the post-round-2 test repair. The bounded
round-2 reviewer consumed the separately preserved `r2` packet over the repaired
verifier source and plugin surface; no reviewer consumption of this final packet
is claimed.

## Boundary Ownership

- Producer: `prepare_packet.py`, which emits one command from the finalized
  packet/input binding.
- Consumer: the human or file-backed reviewer before it trusts the packet.
- Owner: `scripts/reviewed_input_identity.py::verify_packet_binding` and
  `verify_reviewed_input_identity`.
- Verdict: owned-correctly

The public CLI translates the owner's typed outcome into YAML and an exit code;
it does not recreate packet hashing, path capture, or current-input comparison.

## Non-Claims

- Cautilus, GitHub mutation, Ceal mutation, push, release, and consumer-host
  roundtrip were not run.
- Final closeout completed 36 commands with adverse and unproven subjects empty;
  standing pytest passed in 91.3 seconds. A second closeout reused that locked
  broad proof and produced focused test coverage for the 60-test packet/identity
  suite. After commit, the committed-range gate honestly blocked on three
  uncovered verifier lines: missing-bootstrap refusal and unexpected identity-owner
  exception handling. Two direct in-process tests raised the focused verifier file
  to eight tests; the next committed-range run returned `status: clean` across all
  seven changed mutation-pool files from `origin/main..HEAD`.
- The post-round-2 duplicate-baseline disposition has no third fresh-eye review;
  the two coverage tests added after that finding are also accepted under the
  explicit two-round-cap non-claim.
