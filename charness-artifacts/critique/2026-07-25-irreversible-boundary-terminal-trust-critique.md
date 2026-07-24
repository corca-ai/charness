# Critique Review
Date: 2026-07-25

## Decision Under Review

Close three terminal-trust defects found by a north-star drift audit, plus the
budget-staleness class the operator raised mid-session:

1. **Mutation CI recovery path.** The scheduled `Close recovered mutation issue`
   step closed GitHub issues with `state_reason: 'completed'` on its own job's
   green, selecting victims by `label:<label> in:title "<title>"` search without
   ever reading the marker its own open step writes. Replaced with
   `Comment mutation recovery candidate`: marker-scoped selection via
   `issues.listForRepo` (not search), an evidence comment carrying run URL, sha,
   mode and the green run's sample manifest, a `mutation-recovered-candidate`
   label, and **no issue-state change at all**.
2. **HOTL disposition floor.** `evaluate_hotl_dispositions` used an unanchored
   `re.search`, so `not verified` / `could not be verified` / `a known issue with
   the provider` all satisfied the floor gating issue closeout. Anchored to the
   value's leading token, mirroring `scripts/disposition_form.py`.
3. **Floor composition gap.** `issue_close_comment_floor.py` — the carrier that
   mutates GitHub directly — never composed the HOTL floor. Wired in.
4. **Runtime budget staleness.** Budgets only ever ratcheted up; nothing reported
   when a raise stopped being needed. Added an advisory naming budgets whose worst
   recent run is far under the bar, and retuned the one profile with measurements.

## Failure Angles

- Michael Jackson (problem framing): is the mutation auto-close genuinely an
  irreversible boundary, or a self-owned status mirror where the north star's
  irreversibility test does not bite?
- Atul Gawande (checklist/operational): does removing auto-close strand issues
  with no observer, and does the new code introduce a path that turns a green
  mutation run red?
- Barbara Minto (structure/communication): do the changed reference docs and
  dogfood entries claim more than the code supports?
- Jef Raskin (humane interface): does the anchored recognizer refuse a form the
  contract's own prose teaches authors to write?

## Counterweight Pass

- **Act Before Ship:** the backtick regression — the contract renders every HOTL
  status as code (`` `verified` ``), and the first anchored implementation refused
  exactly that form. Fixed before commit. Also the single try/catch spanning
  comment+label, which on partial failure would have re-posted the candidate
  comment every 12h forever.
- **Bundle Anyway:** marker-scoping the *open* step's dedupe search too (it did not
  read the marker either, so the doc's cross-repo-collision rationale was false in
  both directions); rejecting a comma in `auto_issue.label`, which `listForRepo`
  reads as an AND-filter and which the old quoted search tolerated; extracting the
  three near-identical `format_human` section blocks and the three
  `_validate_mutation_*` skeletons that the dup-ratchet flagged.
- **Over-Worry:** "dropping auto-close is a P5 violation — deleting a safeguard and
  replacing it with nothing." Rejected on the reviewer's decisive reading: the
  deleted thing was never a gate *guarding* the boundary, it was a machine
  *performing* the irreversible action, and P5's stop condition (a populated
  evidence record) is exactly what the comment now supplies. Also rejected: "the
  sample-coverage check would be a better close condition" — it is a different
  channel but the same observer, so it is still self-certification.
- **Valid but Defer:** wiring `evaluate_ai_provenance` and the ledger-field /
  close-keyword checks into `close_comment_floor` (same argument as the HOTL gap,
  but a behavior change beyond this slice — recorded as a known residual in the
  dogfood entry); the pre-existing run-log-tail divergence between the live
  workflow and the shipped template (confirmed pre-existing at `835181c3`).

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_verify_closeout_body.py:328,341 | action: fix | note: anchored recognizer refused `` `verified` ``, the exact form ledger-and-dispositions.md renders; backticks added to the lead-strip class and pinned by test
- F2 | bin: act-before-ship | evidence: strong | ref: .github/workflows/mutation-tests.yml:392-407 | action: fix | note: one try/catch over comment+label meant a failed label write silently defeated the dedupe key and re-posted the comment on every later green; catches split, both escalated to core.error
- F3 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_mutation_testing.py:362-380 | action: fix | note: both P4/P5 invariants were pinned on the shipped template only, leaving the live issue-writing workflow unpinned; now asserted across all three checked-in copies with whole-statement pins
- F4 | bin: bundle-anyway | evidence: strong | ref: scripts/quality_policy_defaults.py | action: fix | note: `listForRepo(labels:)` reads its value as a comma-separated AND-filter, so a comma in `auto_issue.label` makes the label unmatchable and silently files a duplicate per failing run; refused at validation
- F5 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/references/mutation-testing.md:104-130 | action: fix | note: marker-scoping orphans issues filed under a rotated `marker_token`; disclosed rather than left as a surprise
- F6 | bin: act-before-ship | evidence: strong | ref: .github/workflows/mutation-tests.yml:374-377 | action: fix | note: the candidate comment asserted the green "did not observe the surviving mutant", which the step never checks — softened to what the workflow can support, in a slice whose thesis is that machines must not assert what they did not observe
- F7 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/scripts/runtime_budget_lib.py | action: fix | note: budgets only ever moved up because a violation forces a raise and nothing reports a raise that stopped being needed; `check-coverage` sat at 55000ms against a 7835ms max and `pytest` had drifted above the slower aarch64 profile
- F8 | bin: valid-but-defer | evidence: strong | ref: skills/public/issue/scripts/issue_close_comment_floor.py | action: document | note: the composition still omits `evaluate_ai_provenance` and the ledger-field/close-keyword checks `verify-closeout` applies — same class as the HOTL gap, recorded as a known residual rather than silently widened
- F9 | bin: valid-but-defer | evidence: moderate | ref: .agents/quality-adapter.yaml | action: defer | note: only the `local-linux-x86_64-36cpu` profile was retuned; the aarch64 profile and the unprofiled defaults have no measurements from this machine and were deliberately left alone
- F10 | bin: over-worry | evidence: contested | ref: docs/design-north-star.md:88-90 | action: defer | note: "removing auto-close is the P5 failure signature" — the removed thing performed the irreversible action rather than guarding it, and the evidence record that replaces it is P5's own stop condition
- F11 | bin: valid-but-defer | evidence: strong | ref: .charness/specdown/report.json | action: defer | note: every quality run rewrites this tracked derived report because `specdown.json`'s reporters hardcode `outFile`, so `-out <tmpdir>` does not redirect it; restored by hand each run this session, unchanged from the prior session's posture

## Reviewer Tier Evidence

- Requested tier: high-leverage (slice review), high-leverage (remediation delta review).
- Requested spawn fields: session-model inheritance (Claude Code host; the repo's
  Codex-only model/effort override does not apply on this host).
- Host exposure state: host-defaulted
- Application state: host-confirmed — two `bounded-reviewer` subagents spawned via
  the Agent tool with a Read/Grep/Glob-only envelope. Both reported their envelope
  bound and named the evidence they could not fetch (`git show` of the base ref);
  the parent ran those `git show` commands and answered them (N1 confirmed
  pre-existing). Parent-side worktree+index integrity was fingerprinted around each
  review with `reviewer_boundary_fingerprint.py`; both verifies returned
  `{"ok": true, "drift": []}`.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

n/a (no adapter `packet_sections` declared; reviewers were pointed at the live
working tree and the base ref `835181c3`).

## Boundary Ownership

- Producer: `quality` owns the mutation workflow, its shipped template, the
  mutation-testing reference, and the runtime-budget gate; `issue` owns the HOTL
  recognizer and the close-comment floor.
- Consumer: any repo installing the mutation-testing workflow (the template and
  its reference ship outward); this repo for the `issue` floors.
- Verdict: owned-correctly

## Non-Claims

- **No local gate executes `actions/github-script`.** The mutation workflow change
  is deterministically verified only as text (three-copy invariant tests and
  `check_github_actions.py`); its runtime behavior is unproven until the next
  scheduled cycle. No claim is made that the recovery step has run.
- Consumer repos holding an installed copy of the template are not re-rendered by
  this change; only `propose_mutation_testing.py --execute` rewrites `workflow_path`.
- No live GitHub issue was closed, commented, or labeled during this slice. The
  `issue` floor changes are proven by seeded carriers and a fake `gh` backend.
- The retuned budgets are honest for `local-linux-x86_64-36cpu` only, from that
  profile's recent 20-sample window on this machine.
