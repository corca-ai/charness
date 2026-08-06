# Issue #518 Awiki / Evidence-Boundary Contract Critique

Date: 2026-08-07

## Decision Under Review

Lock the unified #514/#515/#518 goal and the #518 awiki quality dependency
contract before implementation. The decision keeps the three issue carriers
independent, makes the source freeze require all three protected issues, keeps
target/source authorization semantics-neutral until a shared projection is
proven, and makes the final quality consumer the sole owner of verdicts.

This is a design closeout, not an implementation or issue-close claim.

## Execution

The first bounded architecture/execution/counterweight review found the missing
#518 source capture, missing verdict algebra, shared-schema risk, absent
final-consumer route, unresolved awiki policy, and weak install evidence. Those
repairs were committed as `16a4da15`.

A second bounded architecture/execution/counterweight review read that repaired
surface. All three reviewers returned findings; all three boundary fingerprints
verified `verdict: clean` with no drift. Their findings drove the final contract
repair committed as `457df09f`. Because this was the second and capped review
round for the design surface, those final edits are recorded as
`accepted-unreviewed`; the first implementation slice must receive its own
fresh review of the executable runner and final-renderer surface.

## Findings and Disposition

- F1 | act-before-ship | #518 verdict algebra did not require covered
  coverage, valid receipt binding, or an explicit producer-error/deferral
  state. **Fixed in `457df09f`** by adding typed fields, precedence, and the
  exhaustive clean tuple; final implementation still needs fixtures.
- F2 | act-before-ship | the route could become a second aggregate-verdict
  producer. **Fixed in `457df09f`** by assigning aggregate verdict and
  displayed disposition solely to the final consumer.
- F3 | act-before-ship | read-only mode was promised a tracked receipt even
  though the current runner defines it as non-mutating. **Fixed in `457df09f`**
  by separating full-mode tracked receipts from read-only/pre-push ephemeral
  receipts and requiring render-before-cleanup.
- F4 | act-before-ship | the direct awiki fixture included an aggregate
  verdict although it explicitly proved only direct observation. **Fixed in
  `457df09f`** by removing that verdict from the fixture.
- F5 | act-before-ship | the current runner would render a valid exit-1
  graph finding as ordinary `PASS` if the wrapper returned success. **Specified
  for implementation**: carry a typed `advisory` phase through the runner and
  make the final renderer emit `advisory-non-clean`.
- F6 | act-before-ship | no concrete final-renderer command/readback was
  named, and the docs-only pre-push selection currently omits awiki.
  **Specified for implementation**: add the renderer, receipt-binding refusal
  fixtures, the four mode tests, and the hook label.
- F7 | bundle-anyway | the install command used a tag without enforcing the
  verified commit, and raw stdout/stderr retention was underspecified.
  **Fixed in the contract** with immutable `--rev`, provenance binding, and
  per-run raw artifact/digest requirements.
- F8 | over-worry | deleting an existing linter or generalizing sibling-repo
  gate policy remains unsupported. **Retained as a hard boundary**; the
  overlap matrix is required before any deletion.

## Reviewed Input Identity

- Packet path: `charness-artifacts/critique/2026-08-07-issue-518-awiki-repaired-contract-packet.json`
- Packet SHA256: `b7bcf799d7bdc45763eac8128ada19649646b1626312371c6bc78c58998f3249`
- Identity SHA256: `7a8592d07add3f72b1f3902fb354e8ca866fbb5eefd8f9bdd8ce92dab981a980`
- Round-2 packet consumed by the reviewers:
  `charness-artifacts/critique/2026-08-07-issue-518-awiki-repaired-contract-packet.md`
- Round-2 packet SHA256 at review time:
  `08ee6da22207fcccb4edf22db77baf3d00469547e688b3c7e4cbfbf594dbeb71`
- Round-2 reviewed-input identity at review time:
  `eb11f94ce3dad1fbd0f4a5c13b560eca009688d033f2f3551de95dac5fb14a1e`
- Current rebinding packet after the accepted-unreviewed repairs:
  `charness-artifacts/critique/2026-08-07-issue-518-awiki-repaired-contract-packet.json`
- Current rebinding packet SHA256:
  `b7bcf799d7bdc45763eac8128ada19649646b1626312371c6bc78c58998f3249`
- Current rebinding identity SHA256:
  `7a8592d07add3f72b1f3902fb354e8ca866fbb5eefd8f9bdd8ce92dab981a980`

The current packet is a durable post-repair binding, not a claim that the
reviewers read edits made after their capped round.

## Reviewer Tier Evidence

- Requested tier: `gpt-5.6-terra`, medium reasoning, priority service tier.
- Requested spawn fields: unnamed one-shot reviewers;
  `model=gpt-5.6-terra`; `reasoning_effort=medium`;
  `service_tier=priority`; `fork_context=false`.
- Host exposure state: requested_fields_sent
- Application state: host accepted the three unnamed agents and returned their
  findings; provider-side model application is not independently exposed.
- Delivery state: findings-received.

## Fresh-Eye Satisfaction

parent-delegated — three distinct unnamed reviewers completed the second round;
no same-agent substitute was used. Boundary verification for architecture,
execution, and counterweight windows returned `verdict: clean` and `drift: []`.
The final edits after that round are explicitly accepted-unreviewed because the
two-round cap applies.

## Boundary Ownership

- Producer: `scripts/run_awiki_quality.py` owns invocation facts and typed
  observation receipt only.
- Consumer: `scripts/render_awiki_quality_artifact.py` and the quality artifact
  own the aggregate verdict and displayed disposition.
- Source authorization: the pre-activation crosswalk owns only protected
  target/source identity until a conditional shared projection is proven.
- Existing detectors: `check-doc-links`, `markdownlint`,
  `check-links-internal`, and `nose` retain their own reader boundaries until
  an overlap/replacement proof exists.
- Verdict: owned-correctly — ownership repaired in the contract; executable ownership remains
  unproven until the next implementation slice runs.

## Deliberately Not Doing

- No `integrations/tools/awiki.json` or runner/final-renderer implementation
  was added in this design slice.
- No claim that Charness has run awiki through `run-quality.sh`; only the direct
  read-only awiki observation is durable.
- No linter deletion, sibling-repository write, issue close, release, push,
  Cautilus evaluation, or consumer product/browser behavior claim.

## Next Move

The next session must implement and synchronize the awiki manifest/dependency,
immutable install/readiness receipt, parser, full-mode tracked and
read-only/pre-push ephemeral paths, typed runner advisory state, final renderer,
docs-only hook selection, and all refusal/fold fixtures. It must then run the
actual Charness route in every promised mode, inspect the persisted/ephemeral
readback through a different observer, and only afterward begin the independent
#518, #515, and #514 implementation slices. The overlap matrix remains a
precondition to deleting any detector.

## Verification

- Goal artifact validator — passed; goal remains `draft`.
- Handoff, quality, debug, current-pointer, doc-link, Markdown, secret, and
  diff checks — passed; the repository-wide Markdown command retains its
  pre-existing advisory inline-code warnings only.
- Pre-commit for `457df09f` — passed.

## Non-Claims

The #518 implementation, Charness final-consumer execution, source-freeze
capture, crosswalk validator, issue closeout, and awiki install on a fresh host
remain unproven. The pinned `cmanki` and read-only `craken-agents` materials
remain causal/comparison evidence only.
