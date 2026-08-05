Close #491 — keep semantic-reference review reviewer-owned

Classification: decision-needed
Jtbd: Decide whether the three heterogeneous semantic-reference escapes need a
universal reference manifest/literal matcher or a bounded reviewer-owned control.
Critique: charness-artifacts/critique/2026-08-05-issue-491-resolution-critique.md

Decision: Keep the shared semantic-reference question as a reviewer-owned
decision aid. Do not add a universal `reference-claims` manifest, full-corpus
literal-set matcher, or semantic meta-gate. The question now requires a bounded
candidate search, first-reader/copy-paste readback when such a reference is in
scope, and an explicit `not applicable`, `insufficient evidence`, or
`unproven — defer` disposition when the boundary cannot be established.

Boundary: In scope are the three #491 claim families, their current reader-facing
references, source/plugin parity, the safe `--fields-file` example, and the
narrow regression proof. Out of scope are universal reference inventory,
mechanical semantic matching without a stable mapping, host rendering/uptake,
and reviving the historical `refilled_subkeys` report field.

Implementation: repaired both copies of `goal-artifact.md` so the actual
`append_slice_log.py` example uses a quoted JSON heredoc and `--fields-file`;
repaired both copies of `lifecycle-during.md` and `upsert_goal.py` comments to
describe current slug coercion and total-loss rejection; narrowed the shared
semantic question; and added a source/plugin plus command-shape regression
assertion. The current bootstrap report was read back as the post-#507 contract:
private `_subkey_refills` evidence is not a public `refilled_subkeys` report key.

Root Cause: behavior owners and reader-facing references were maintained in
separate surfaces without a stable mechanical ownership map; one copy-paste
example and two historical descriptions therefore survived behavior changes.

Siblings: #496 established the historical-claim supersession discipline; #507
owns the current bootstrap lifecycle report shape; #499 carries the shared
semantic reviewer-question wiring. Their decisions and focused proofs were
read during the bounded candidate search; no sibling requires a new universal
gate for this issue.

Prevention: Relevant behavior/reference changes must carry the semantic question
through the critique packet. The reviewer records candidate scope and a compact
three-row claim/readback ledger for the lifecycle, bootstrap vocabulary, and
copy-paste command families. A future stable mapping plus measured recurrence
may reopen a narrow mechanical control; this closeout does not claim corpus-wide
coverage.

Evidence: the focused achieve/reference and input-channel suite passed 37 tests;
source/plugin parity passed for the repaired references and helper; `git diff
--check` passed; the current issue read was OPEN with zero comments before this
closeout. The quality record is
`charness-artifacts/quality/2026-08-05-issue-491-semantic-reference.md`.

Claim/readback ledger:

| Claim family | Current owner/readback | Disposition |
| --- | --- | --- |
| `pursue_readiness` scope/refusal claims | `lifecycle-before.md`; fences, `unreadable:`, and current `scope_not_checked` were read back | updated/current; reviewer-owned semantic check, no universal mapping |
| bootstrap status vocabulary / historical `refilled_subkeys` | `bootstrap-posture.md`, `quality_bootstrap_lifecycle.py`, and private `_subkey_refills` implementation were read back | current `augmented` contract retained; historical key explicitly not reintroduced |
| `append_slice_log.py` invocation | `goal-artifact.md` source/plugin first-reader block and helper input channel were read back | updated to `--fields-file`; narrow command-shape test added |

Behavior #491: verified — distinct reader/reference readback channel: a
standalone extraction of both first-reader source/plugin blocks confirmed the
safe `--fields-file` invocation and absence of lossy prose flags, while direct
helper help/readback confirmed the corresponding flag exists. This is not a
claim that every repository reference or host-rendered reader path was tested.

AI-provenance: agent-drafted decision and carrier; delegated bounded fresh-eye
review findings and post-review repairs are recorded in the linked critique.
