<!-- charness-work-item-key: closeout-carrier -->
# A multi-issue closeout is forced into repeated reviews and classification partitions

## Problem and capability

In #798, closing #800 and #803 required separately repackaged final reviews. The shared checker requires one scalar packet label to prefix-match every issue. The commit hook then dispatches one classification for all bare close targets, forcing bug/feature separation. Support direct consumption of one genuinely scoped review and one mixed carrier without dropping per-issue evidence.

Classification: bug
Causing skill: issue, critique

## Fixed decisions and ownership

- No dependencies. Shared code owns generic packet/result/delivery identity; issue owns target membership, per-target classification, behavioral verdict and its closeout policy.
- Existing singleton carriers remain valid. A structured exact target set is the candidate direction, not permission to accept free-text substring membership or weaken old refusals.
- A semantic review may cross caller formatting only if its bound inputs and actual observations cover every requested claim and the consuming owner accepts that scope. A release-state review alone does not prove issue behavior.

## First action and probes

Use debug to reproduce scalar-target and mixed-classification failures against the final issue/hook consumer, then causal review before repair design. Inspect `skills/shared/scripts/reviewer_worker_carrier_support.py`, `skills/public/issue/scripts/issue_critique_observer.py`, and `scripts/gates/check_issue_closeout_commit_msg.py` plus their producer schemas and tests. Freeze legacy migration, ambiguous/missing classification handling and target equality rules in the living contract before code.

## Success criteria and checks

- One source-bound review covering two different issues is consumed without a second semantic review solely for format. A mixed bug/feature carrier exercises both existing evidence floors through draft validation and hook dispatch.
- Negative controls: omitted/extra/duplicate/foreign/swapped target; stale source; wrong packet/result/parent; an uncovered issue added to an otherwise passing bundle; a bug mislabeled or missing its required proof. Fail before publication.
- Independent reviewer observes per-issue behavior through a channel distinct from carrier/closed state. It may reuse actual current observations, never invent them from an aggregate pass.
- Before/after record names removed review/recopy/partition work and all added identity checks and fallback costs. Keep existing paths if proposed consolidation loses capability or is more complex for no gain.

## Boundary and non-goals

This is a proof-surface change; retain distinct review, focused regression/mutation proof and publication/readback. No global review cache, fabricated human approval or unrelated closeout taxonomy rewrite. Parent alone integrates/export-syncs and owns final published closeout. Dependencies mean local proof readiness, not premature tracker closure.

## Implementation contract (2026-09-06)

The parent reproduced both failures through unchanged final consumers; see
`charness-artifacts/debug/2026-09-06-multi-issue-closeout-cardinality.md`.
The delivered causal review `goal805-closeout-causal-quoted` passed before this
repair was designed. It approves the diagnosis, not this design or resolution.

### Review membership and observations

Add optional generic `prepared_targets: list[str]` to the existing packet,
produced by repeatable `--prepared-target` through the semantic runner and
prepare runner. Preserve order and duplicates for the consuming owner to judge;
shared code treats targets as opaque and does not interpret issue identities.
Omission leaves historical packet shape unchanged. `prepared_for` remains a
human display label for structured packets.

Add optional `target_observations` to the result schema: an array of closed
objects with nonempty `target`, `verdict` (`pass`, `block`, `defer`), nonempty
`summary`, and a nonempty array of nonempty `evidence` strings. Keep this field
in the model-authored schema. Existing packet/input/parent/capability/delivery
joins remain mandatory; no new hash or global cache is needed.

Live Codex strict-generation preflight rejected an optional property absent from
`required`. The model-facing projection therefore requires all semantic fields;
`target_observations: null` represents absence for an unstructured legacy packet.
Historical delivered results may still omit the field. Neither null nor omission
satisfies a structured packet, and a present empty array remains structured but
insufficient. The runner does not author or remove semantic observations.

The issue owner requires equality of three exact sets: expected qualified
`owner/repo#N` identities, packet targets, and result observation targets.
Check duplicates and cardinality before equality; normalize repository case,
not free-text substrings. All observations must pass with evidence. One-sided
structured presence, omitted/extra/foreign/duplicate targets, or a non-pass
target refuses. When both structured fields are absent, preserve the existing
singleton prefix path; legacy multi-target carriers refuse. One bundled packet
is cited by one targeted `Critique #N #M:` field, not partitioned into false
subset citations.

Identity checks can refuse swapped or mismatched target keys; they cannot prove
that semantically swapped evidence prose is true, or that a bug is really a
feature. The independent behavioral reviewer owns those judgments. Adding an
uncovered target to the request or result alone must refuse mechanically;
fabricating a fully consistent story is not made trustworthy by the schema.

Expose the already-validated packet and result through a generic shared
evidence-returning helper, retaining the existing report-only wrapper for
compatibility. Return the parsed packet from packet-binding verification so
issue policy consumes the verified bytes without a second read. Remove the
issue-number prefix loop from shared support; keep it in the issue owner only
for legacy singleton migration.

### Per-target classification

One issue-owned parser resolves a total target-to-classification map before
verification. No targeted declarations preserves each caller's existing global
or inferred fallback. Once any targeted declaration exists, every invoked
target must have exactly one known classification: reject missing, extra,
duplicate, conflicting, foreign, or mixed global/targeted authority. Strip
fenced code using the existing body conventions. Do not silently default holes.

Keep the scalar verification API for existing singleton callers. Add grouped
verification that reads the carrier once, resolves the map, and invokes each
existing classification floor for that group's issue numbers. Preserve
per-group classification and numbers in reports. Route bare and staged commit
hooks, pause-brief close paths, pre-push's independent report builder, draft
validation, and the plural verify-closeout CLI through this same owner. Invalid
maps fail before provider reads. Existing global evidence fields and targeted
Behavior/HOTL/Critique grammar keep their current meaning.

Keep invocation, citation, and classification scopes distinct. A targeted
Critique line declares its complete citation target set, which must be a
nonempty subset of the full invocation. Packet/result equality uses that whole
citation set, never its intersection with a classification group. Grouped
verification retains full invocation context, validates each cited delivered
bundle once, and passes that call-local validated result to the groups whose
targets the citation covers. Each required group's own targets still need
coverage and its own floors. Separate singleton citations remain possible;
their exact sets are singleton, and a plural packet cannot impersonate them.
Do not require critique for a classification that currently does not require
it. No caller may inject an unvalidated cached approval.

### Acceptance and tripwires

Focused tests cover producer CLI propagation and packet-file mutual exclusion,
schema compatibility/model-authored observations, two-target delivered success,
every membership negative, stale/wrong joins, old singleton acceptance, and old
plural refusal. The same mixed bug/feature stimulus must produce two reports
through draft, hook, staged-artifact, and final pre-push paths; omitting either
floor fails. Test complete maps, fenced examples, malformed authority, and
existing global/inferred behavior. A success that only tests helpers, invents
semantic truth from an aggregate pass, or misses pre-push is a tripwire.

Verification scope: changed producer/shared/issue consumers and focused tests;
no provider close during implementation. Integrated changed-line proof, fresh
behavioral review, publication, and installed observer remain later boundaries.
Design critique is pending; implementation starts after its disposition.

Review 810-D1 is accepted: use one mixed bug/feature fixture with one delivered
two-target packet and one citation through draft, hook, staged, pre-push,
plural CLI, and pause-to-close dispatch. Both group reports must succeed;
removing either applicable floor must fail. This composed case, not two
separate happy paths, tests the distinction above.

The design repair passed before implementation (see the Goal Run design
disposition). Parent code observations now record the composed fixture and a
reproduced hook projection bypass. Hook callers must pass the complete artifact
to the same classification owner; projecting declarations into a dictionary
first destroys the duplicate/conflicting-authority evidence. Code review,
changed-line proof and final behavioral closeout remain separate obligations.

Code-review counterexamples sharpen invocation ownership: active artifact
targets and bare close keywords form one invocation, regardless of artifact
partition. Artifact classifications remain source-attributed and must agree
with independently validated carrier declarations; a supplied map never
suppresses duplicate, mixed, foreign or conflicting message authority. The
commit message remains the ledger body. Behavior/HOTL singleton shorthand uses
the full invocation cardinality, not each classification group's size. Citation
labels accept bare `#N` tokens separated by whitespace or commas; arbitrary
prose and qualified repository labels refuse before numeric projection.
