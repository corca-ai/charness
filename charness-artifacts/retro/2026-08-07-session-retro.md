# Session Retro
Date: 2026-08-07

## Context

This retro reviews the #517 semantic-quality repair and the #516 mutation-regression diagnosis, portability repair, and closeout. The important question is not whether those two issues were fixed; it is why both required late evidence reconciliation before a trustworthy close was possible.

Strong evidence is the committed #517/#516 artifacts, the original GitHub run logs, the successful post-repair run, the current open-issue readback, and the read-only expert reviews. The latest run `31118030353` is a strong external observation of GitHub Actions service unavailability, not a code verdict. The telemetry mining result is strong for what this local stream contains, but weak for current runtime ownership because the recurring samples are historical.

Structural pattern: a shallow proof proxy was allowed to stand in for the semantic contract it was meant to observe, while the evidence identity needed to interpret that proxy was distributed across goal, handoff, manifest, packet, checkout root, workflow run, and issue.

Pattern of patterns: invariants were bound at the terminal closeout boundary instead of at evidence production. The harness is fail-closed enough to catch the drift, but it still makes closeout reconstruct ownership, scope, and identity after expensive work. Quality routing (#515) and deterministic evidence assembly (#514) are two views of this same seam.

## Window

From the #517 closeout through the #516 issue review, repair, remote readback, final bookkeeping push, and this next-session design on 2026-08-06–07.

## Evidence Summary

- #517 is `CLOSED/COMPLETED`; its repair added the surface-contract packet and synchronized root/plugin quality surfaces.
- #516 is `CLOSED/COMPLETED`; the historical `79ea3447…` source-claim mismatch was separated from the later `5df4fb61…` absolute-packet-path failure, and the repaired carrier received distinct remote proof in run `31117396157`.
- The current open-issue readback leaves #515 (quality routing/browser-provider boundary) and #514 (deterministic closeout evidence assembly) open; #516 and #517 must not be reopened from this retro.
- Final-head run `31118030353` failed before gates because GitHub Actions returned `Service Unavailable` while resolving action download metadata; its mutation job was cancelled. This is an external infrastructure non-claim, not a repository regression.
- `mine_closeout_telemetry.py --detail` found recurring historical over-budget verification and over-slice records, but does not establish that the current owner or current runtime still has the same defect.
- Packet Consumed: `charness-artifacts/retro/2026-08-06-192538-packet.md`.

## Waste

- Evidence identity was frozen after a reviewed ledger change, causing packet regeneration and an extra bookkeeping cycle (recurrence-class: release-proof-identity-churn). The repair preserved safety, but the dependency should have invalidated the packet immediately.
- Historical and current observations were initially close enough to be conflated: a later local green could have been mistaken for proof that the old SHA was healthy. The #516 debug/critique records corrected this by separating historical fact, present failure, and distinct current proof.
- Consumer-root portability was discovered only in remote verification: a locally valid absolute packet path was invalid under the runner checkout. The validator correctly refused; the producer-side artifact should have prevented the value earlier.
- Broad closeout work discovered authoring and readback problems later than the cheapest dry-run boundary. This is the unresolved operator-memory problem described by #514, not a reason to weaken the closeout floor.
- The latest remote failure consumed a full setup wait without producing code evidence. It is not actionable as a code fix until the service failure repeats or a repository-owned retry/readback contract is shown to be missing.

## Critical Decisions

- Keep #517's semantic surface-contract fix separate from #515's product/browser/provider routing boundary; a disclosure floor cannot claim a browser or provider behavior judgment.
- Keep #516's historical baseline failure separate from the current portability failure; repair the critique artifact's path field and retain fail-closed validator containment.
- Require a distinct observer and channel before issue closeout. The successful #516 remote run, GitHub state readback, and closeout verifier are separate evidence roles.
- Do not close #515 from its comment alone: its reported consumer checks are useful evidence, but the comment explicitly leaves fresh-eye review blocked. Do not activate #514 as a broad orchestration project without a second consumer or a smaller accepted planner scope.

## Trends vs Last Retro

The previous closeout retro named packet-identity churn and diagnostic visibility. This session confirms the identity-churn recurrence and reveals the higher-order form: semantic routing and evidence identity are separate modules whose seam is only exercised at closeout. The workflow improved at the irreversible boundary—#516 did not close on local green—but still paid the cost of discovering producer/consumer context late.

## North Star Alignment

P4/P5 held at the issue boundary: local green was provisional, the validator was not weakened, a distinct remote channel was required, and the GitHub closeout state was read back. The mis-application was earlier in the pipeline: evidence producers were allowed to emit values whose meaning depended on a later checkout root, later ledger state, or later semantic interpretation. That inverted the North Star's “brief a capable judge” rule by making the judge reconstruct the missing context at the most expensive boundary. The failure signature was terminal trust in a single convenient proxy—proof-ran, local-green, or once-bound packet—rather than a populated evidence record with identity and scope.

## Expert Counterfactuals

- **Ousterhout / deep-module design:** the missing abstraction is a small evidence-boundary module that owns canonical owner, SHA/time scope, repo-relative locator policy, allowed projections, and final consumer. It should hide cross-artifact coordination instead of exposing packet rebinding and closeout repair as operator choreography.
- **Klein/Kahneman / decision quality:** force the question “what is historical fact, what is current behavior to prove, and which independent observer can decide it?” before broad verification. The avoided substitution is treating a convenient local pass or provisional ledger as an answer to the harder current/remote question.

## Sibling Search

- same layer: quality artifact, critique packet, and issue closeout | decision: valid follow-up outside the slice | proof: #516's packet-path failure and #514's acceptance criteria identify the same producer-to-consumer identity gap | follow-up: https://github.com/corca-ai/charness/issues/514
- abstraction up: quality → issue → closeout routing | decision: valid follow-up outside the slice | proof: #515 asks for visible semantic coverage while #514 asks for deterministic evidence assembly; their composition is not owned by one current planner | follow-up: https://github.com/corca-ai/charness/issues/515
- specialization down: packet containment and artifact-shape validators | decision: intentional boundary | proof: local validators and the remote changed-line mirror remained fail-closed; the repair stayed in the malformed artifact field rather than weakening the consumer
- mental-model siblings: historical alert versus current behavior disposition | decision: same waste, fix now | proof: #516 debug and critique now preserve reported SHA, present failure, distinct repair proof, and non-claims

## Portable Candidate

- Abstract pattern: before a proof is consumed at an irreversible boundary, bind its semantic scope, canonical owner, execution root, identity, and final consumer; expose “proof ran” separately from “contract observed.”
- Triggering evidence: #517's semantic-surface gap, #516's source-claim mismatch and absolute-path failure, and #514/#515's open sibling boundaries.
- Intended consumer/repo shape: any repo with multiple quality surfaces, generated evidence, remote runners, or issue/release closeout.
- Destination: not portable as a new broad skill; extend the existing quality/closeout contracts so a second consumer justifies the abstraction before orchestration grows.
- First-prompt acceptance claim: “Name the semantic surface, owner, execution root, identity, final consumer, and unexamined axes before running the broad gate.”

## Next Improvements

- workflow: begin the next session with a read-only identity/state scan, then write a two-column triage lock (`historical fact` / `current behavior to prove`) before any broad gate or issue action.
- workflow: freeze goal/spec/critique packet inputs before broad verification; any later mutation invalidates packet identity and review scope rather than producing a bookkeeping-only repair.
- capability: make a cheap dry-run evidence-boundary preflight report aggregate authoring-path, containment, target-vs-ambient, and producer-coverage gaps before sync or remote execution; keep the existing gates and floors.
- memory: update handoff around the first next action and explicit non-claims, with #515 as the next bug boundary and #514 as deferred unless a concrete second consumer appears.
- memory: treat `31118030353` as external `Service Unavailable` until a later independent run proves otherwise; never use it as current-head quality proof.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-07-session-retro.md
