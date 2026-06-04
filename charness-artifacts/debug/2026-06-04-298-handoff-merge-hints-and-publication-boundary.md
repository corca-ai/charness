# Debug Review: #298 Handoff Merge Hints And Publication Boundary
Date: 2026-06-04
Issue: #298

## Problem

#298 contains two related Charness workflow bugs from the same Ceal pickup:
deterministic handoff merge hints can present broad-token overlap as normal
merge guidance before adapter policy and agent judgment consume it, and issue
closeout guidance can make a post-carrier docs-only lifecycle artifact commit
look like it requires immediate second publication.

## Correct Behavior

Given handoff entries that only share broad policy tokens, deterministic scripts
should expose the observed token facts without claiming clearance or semantic
fitness. Agents decide coherence, urgency, dependency, and operator value.
Validators may reject high-confidence proposals that ignore strong warning
facts, but `broad_only_overlap: false` is never proof that a merge is good.

Given a direct-to-default issue resolution, the pushed carrier containing the
fix, close keywords, closeout ledger, and required proof is the publication
boundary for issue closure. Later goal/retro/critique bookkeeping commits are
local lifecycle state unless required for the verified carrier, requested by the
operator, or needed for public/remote proof.

## Observed Facts

- GitHub issue #298 is open and labeled `bug`.
- The issue body reports a deterministic 7-source merge hint caused by shared
  broad tokens `label/future-work` and `label/operations`.
- The handoff adapter policy already declares broad boundary tokens and an
  `allowed_broad_boundary_tokens` escape hatch.
- The issue body states the later agentic proposal validator can reject
  broad-label-only merges, but the earlier `merge_hints` packet still exposes
  the noisy bundle.
- A 2026-06-04 issue comment adds carrier-vs-lifecycle publication waste from
  Ceal #246: the functional carrier already had fix, close keywords, closeout
  ledger, critique reference, and verification, then a docs-only goal/retro
  commit was pushed separately because Charness guidance made it look required.
- The user clarified the design principle for #298a: scripts should provide
  honest facts; agents should make judgment calls; script false negatives must
  not become clearance.

## Reproduction

For #298a, handoff entries sharing only broad policy tokens can still become a
normal deterministic merge hint before the policy-aware packet/validator stages
consume the broad-token facts.

For #298b, a direct issue-resolution carrier can close and verify the issue, but
the workflow wording can imply a later docs-only lifecycle artifact commit also
needs immediate remote publication, creating an avoidable second push.

## Candidate Causes

- Pipeline ordering: deterministic merge hints are computed before the
  policy-bearing packet path consumes broad-token policy.
- Semantics overreach: script output can be read as a recommendation rather than
  as observed evidence.
- False-negative risk: absence of a broad-only signal can be mistaken for merge
  clearance.
- Publication-boundary ambiguity: issue guidance says "commit, push" broadly
  instead of naming the resolution carrier as the remote closeout boundary.
- Lifecycle coupling: achieve/retro bookkeeping is treated as part of issue
  closure even after the pushed carrier is verified.

## Hypothesis

If deterministic handoff scripts output token-policy facts without clearance and
agentic validators only block ignored strong warnings, then broad-token noise is
visible without moving judgment into scripts. If issue/achieve/retro guidance
names the issue-resolution carrier as the closeout publication boundary, then
verified closure remains strong while later docs-only lifecycle state can batch
under repo publication policy.

## Verification

Planned focused proof:

- Handoff merger/packet tests for broad-only, unknown-token, mixed-token, and
  non-broad-looking semantically weak cases.
- Tests or fixtures proving no output field means `safe_to_merge` or equivalent
  clearance.
- Agentic proposal validator tests proving a high-confidence proposal that
  ignores broad-only warning facts is rejected, while `broad_only_overlap:
  false` does not auto-accept.
- Skill/reference text checks for `issue`, `issue/references/closeout-
  discipline.md`, `achieve`, and `retro` publication-boundary guidance.

## Root Cause

Charness exposed intermediate workflow artifacts as if they were already
policy-filtered recommendations, and it described issue closeout publication as
a broad lifecycle push instead of the specific carrier that proves closure.
Both failures let downstream agents over-trust workflow scaffolding.

## Invariant Proof

- Invariant: deterministic workflow scripts expose evidence, not semantic
  clearance; issue closure is proven by a pushed carrier verified against
  GitHub state, not by every later lifecycle artifact publication.
- Producer Proof: merge hint generation should include broad/unknown token facts
  and publication guidance should define carrier boundaries.
- Final-Consumer Proof: agentic validators/rankers consume the facts without
  auto-accepting false negatives; issue closeout verification runs after the
  pushed carrier and does not require a second docs-only push.
- Interface-Shape Sibling Scan: inspect handoff merge hints, packet schemas,
  proposal validators, issue closeout wording, achieve closeout wording, and
  retro closeout-waste guidance.
- Non-Claims: this RCA does not encode Ceal-specific labels or bypass repo
  pre-push/CI parity for any push that is actually performed.

## Detection Gap

- handoff merge hints | broad-token policy was not reflected in the first
  operator-visible hint surface | expose broad/unknown token facts at that
  surface.
- agentic proposal validation | can reject bad broad-only proposals late but not
  prevent early hint noise | bind validation to explicit warning facts.
- issue closeout wording | broad "commit, push" phrasing hides the carrier
  boundary | define carrier vs lifecycle artifact publication.
- retro closeout-waste wording | can conflate intended gate cost with avoidable
  push-boundary mistakes | require the distinction when recording the lesson.

## Sibling Search

- Mental model: workflow scaffolding output was treated as a recommendation or
  publication obligation instead of evidence for agent/operator judgment.
- handoff hint axis: same bug, fix now; proof: #298 body names the exact broad
  token case.
- packet/validator axis: same class, fix now if touched by #298a; proof: issue
  body says policy exists later in the pipeline.
- issue closeout wording axis: same bug, fix now for #298b; proof: issue
  comment names suggested issue wording and closeout-discipline changes.
- achieve/retro wording axis: same bug, fix now for #298b; proof: issue comment
  names both surfaces.
- helper/preflight axis: valid follow-up outside the slice only if manual
  publication-boundary classification stays ambiguous; proof: user accepted
  conditional scope.

## Seam Risk

- Interrupt ID: issue-298-handoff-merge-hints-and-publication-boundary
- Risk Class: workflow-boundary
- Seam: deterministic script output to agentic ranking, and issue carrier proof
  to lifecycle artifact publication.
- Disproving Observation: broad-label-only merge guidance and docs-only second
  push both reached the operator workflow as if they were required/high-value.
- What Local Reasoning Cannot Prove: every consumer host's ranking prompt or
  publication policy; final proof is repo-local unless later live host proof is
  routed through `quality`.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl after issue causal review confirms the substrate.
- Handoff Artifact: charness-artifacts/goals/2026-06-04-issue-294-298.md

## Prevention

Keep deterministic Charness scripts factual and non-clearing, and make
publication boundaries name the carrier whose remote state proves the claim.
