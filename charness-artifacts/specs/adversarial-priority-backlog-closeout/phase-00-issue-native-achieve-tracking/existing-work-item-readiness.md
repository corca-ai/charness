# Existing Work Item Readiness For Goal Run #724

Status: draft execution contract — no GitHub mutation authorized
Audited: 2026-08-26 through the adapter-resolved `issue read` path
Graph: [Proposed child graph](./children/index.md)

## Purpose

Prevent “existing issue identity” from being mistaken for an executable child
spec. All 26 cohort issues remain in the approved initial graph, but none is
eligible for execution until a fresh agent can act and verify from its current
GitHub body plus named durable references.

## Readiness Rule

An open Work Item body must state one current purpose, fresh premise, owned
surface, bounded change, dependencies, acceptance criteria, exact verification
commands, evidence boundary, and non-claims. A closed Work Item must expose an
issue-owned closeout comment with behavioral evidence and channel limits.

Immediately before approved reconciliation, re-read each exact
repository/number, state, title, body, latest relevant comment, and `updatedAt`.
Compute the observed body/title/URL fingerprint. Drift from this audit never
passes silently:

- `managed-addendum-required`: write the prepared bounded addendum/body, read
  exact bytes back, and bind its digest before the issue becomes executable.
- `preserve-closed-evidence-ready`: do not rewrite the body; re-read and bind
  the exact closeout comment/evidence identity, while making no body-equality
  claim.
- premise refuted or scope materially changed: stop that Work Item and reconcile
  a newly approved spec or verified successor; do not implement the stale body.

## Audited Dispositions

| Issue | Current state | Establishment policy | Required executable addendum or preserved evidence |
| --- | --- | --- | --- |
| #723 | open | managed addendum | Make quality planning discover adapter-declared skill paths and name the package verification owner. Pin the Ceal-shaped adapter fixture, exact planner output, first catalog/quality consumer, and advisory-only boundary; exclude the other umbrella improvements. |
| #722 | open | managed addendum | Define the ownership-map output fields, bounded owners, dry-run fixture, exact command, and refusal when only existence—not structure—is known. |
| #721 | closed | preserve evidence | Bind the latest closeout comment that validates the three named debug artifacts and explicitly limits the claim to local behavior. |
| #717 | open | managed addendum | Re-read current module sizes and extraction state; name one cohesive remaining ownership boundary, changed-line proof, focused tests, and review obligation. |
| #715 | open | managed addendum | Require implementation-skill admission to resolve and report the installed/source implementation identity before worker selection. Prove stale installed refusal and matching installed acceptance; source-only green is not installed adoption. |
| #710 | open | managed addendum | Normalize adapter `scope_paths` before edit-advisory matching. Prove `.` and nested roots against changed files and exact advisory output without changing ratchet policy. |
| #708 | open | managed addendum | Report every over-limit Python file in deterministic order and one failing result. Prove a two-invalid-file fixture and preserve per-file reasons. |
| #706 | open | managed addendum | Preserve “not judged” in dup-ratchet summaries for adapter-invalid, inert, and rebaseline paths; never project withheld counts or verdict fields as reassuring zeroes. |
| #704 | open | managed addendum | Make `link_only_lines_slack` one stable `integer|null` field: integer when computable, null plus an explicit reason when unavailable. Prove the first JSON/YAML consumer rejects strings. |
| #703 | open | managed addendum | Trace each uncovered/scope/unreachable field to the ordinary attention renderer; select only the still-missing path and name exact expected output. |
| #701 | open | managed addendum | Define a fixed-point claims-review bundle: review input excludes the artifacts describing that same review or converges on a bound second identity. Prove deterministic candidate identity and retain the prior timeout as unproven. |
| #700 | open | managed addendum | Choose the exact grant-transition producer and narrative consumer; define pre/post-grant fixture, stale prose refusal, and readback criteria. |
| #699 | open | managed addendum | Define candidate identity and verdict fields, candidate A/B same-version fixture, stale HOLD rejection, and release-planner output. |
| #698 | open | managed addendum | Name the exact superseded lifecycle floor, required dispositions/handoff fields, transition fixtures, and two-round verdict-logic review. |
| #697 | open | managed addendum | Specify distinct producer paths/markers for mutation sampling versus changed-line coverage and prove the changed-line producer remains authoritative. |
| #695 | open | managed addendum | Choose one canonical critique shape owner; require `Execution mode` in produced/stub artifacts and validate the typed-subagent closeout carrier. |
| #694 | closed | preserve evidence | Bind the latest closeout comment and exact cadence reproduction showing the negated flag is non-applicable; retain local-only limits. |
| #693 | open | managed addendum | Re-read whether same-context provenance is now enforced; otherwise specify same/distinct-context fixtures, exact identity fields, and two-round verdict review. |
| #692 | open | managed addendum | Define one shared adapter-idempotence owner and prove all 16 public-skill placements plus representative fresh/existing runs and mirror sync. |
| #669 | open | managed addendum | Add deterministic SIGTERM-at-construction injection, process-group/tree readback, exact command, and explicit exclusion of unrelated kernel-level stalls. |
| #668 | open | managed addendum | Run controlled and contention-recorded standing-pytest profiles, bind sample provenance, then retain or revise the advisory budget from those measurements. A green budget check alone is not performance proof and no unrelated scheduler redesign is in scope. |
| #667 | open | managed addendum | Name specialized-lane discovery input, generic/specialized fixtures, exact `next_action` output, and no-release-mutation boundary. |
| #637 | open | managed addendum | Add exact flattened installed-layout positive/negative scaffold fixtures and preflight output; retain source-checkout and installed claims separately. |
| #634 | open | managed addendum | Close the already-repaired dependency-contract arm and make the remaining exported instruction/data-reader paths self-sufficient from an export-only checkout. Audit cwd-relative commands, shell entrypoints, data readers, and bare imports through the existing export checker; split any independently owned live defect discovered by that census. |
| #628 | closed | preserve evidence | Bind the latest closeout comment and four no-argument producer observations; retain the refuted-premise and no-new-repair boundary. |
| #546 | open | managed addendum | Make runtime-budget scheduling intent adapter-owned and explicit for every budget label: always, conditional with named trigger, or external/not locally enforceable. Validate the declared universe without inferring consumer intent; keep unobserved conditional execution an explicit non-claim. |

## Targeted Proof Map

Every open Work Item creates or reshapes its named focused test and runs it with
`python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
--pytest-target <path>`. The exact targets are:

| Issues | Focused test target |
| --- | --- |
| #723 | `tests/quality_gates/test_quality_run_planner.py` |
| #722 | `tests/quality_gates/test_setup_inspect_policy.py` |
| #717, #708 | `tests/quality_gates/test_python_length_gates.py` |
| #715 | `tests/quality_gates/test_skill_surface_preflight.py` |
| #710 | `tests/quality_gates/test_dup_ratchet_edit_advisory.py` |
| #706 | `tests/quality_gates/test_dup_ratchet.py` |
| #704 | `tests/test_docs_graph_gate.py` |
| #703 | `tests/quality_gates/test_attention_state_visibility.py` |
| #701 | `tests/quality_gates/test_claims_review_scope.py` |
| #700 | `tests/quality_gates/test_release_narrative_gate.py` |
| #699 | `tests/quality_gates/test_release_claims_review.py` |
| #698 | `tests/quality_gates/test_goal_superseded_status.py` |
| #697 | `tests/quality_gates/test_changed_line_mutation_coverage.py` |
| #695 | `tests/quality_gates/test_describe_goal_closeout_shape.py` |
| #693 | `tests/test_critique_round_findings.py` |
| #692 | `tests/quality_gates/test_adapter_consumer_classification.py` |
| #669 | `tests/test_subprocess_guard.py` |
| #668 | `tests/quality_gates/test_standing_pytest_runner.py` |
| #667 | `tests/quality_gates/test_release_run_planner.py` |
| #637 | `tests/quality_gates/test_check_artifact_surface_preflight.py` |
| #634 | `tests/quality_gates/test_export_self_sufficiency.py` |
| #546 | `tests/quality_gates/test_runtime_budget_universe.py` |

Each child also runs repo-selected changed-line proof before any broad gate and
records skipped broad checks. A focused green proves only the named contract;
provider, installed, release, or hosted behavior requires its separately named
channel.

## Establishment Gate

The approved initial graph contains 31 direct children: five system-capability
children and these 26 identities. Before the Goal Run becomes `bound`:

1. all 23 open cohort issues pass a fresh premise read and managed-body/addendum
   exact readback;
2. the three closed issues pass exact state and closeout-comment evidence
   readback;
3. each manifest entry records state, body policy, observed fingerprint, managed
   digest when applicable, dependencies, execution rank, and evidence policy;
4. no open child missing an executable field is selectable; and
5. no preserved closed issue is represented as managed-body equality.

The parent remains open after establishment. This audit authorizes no body edit,
relationship mutation, implementation, or issue closure.

## Verification At Reconciliation

Use only the implemented adapter-resolved Goal Run command surface. Retain:

- one structured preflight receipt;
- pre-write and post-write readback for every managed issue;
- one explicit preserve-evidence disposition for each closed issue;
- exact graph readback for all 31 children; and
- a clean-process `/goal #724` selection proving that a stale or incomplete Work
  Item is skipped/refused rather than guessed into execution.

## Non-Claims

- This planning audit is not current GitHub body equality at implementation
  time; the mandatory fresh read supplies that evidence.
- Closed state alone is not behavioral proof.
- An addendum plan is not an implemented fix.
- No issue was updated, linked, closed, or reopened while creating this file.
