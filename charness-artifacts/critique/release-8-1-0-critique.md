# Release 8.1.0 Critique

Date: 2026-09-04

## Execution

Fresh-Eye Satisfaction: `parent-delegated`.
Target: `release-critique.md`.

Two bounded file-backed reviewers ran in parallel through
`skills/public/critique/scripts/run_review.py` (backend `codex_exec`, boundary
`read-only-worker`), with materially different lenses: an operational
checklist (Gawande) asking what release-time step is missing or wrong before
the tag and whether minor is the honest bump, and an operator-surface lens
(Minto and Raskin) asking whether the cut docs pages and the trimmed retro
skill still answer their questions for a reader who did not follow the thread.
Both delivered typed results (`delivery_state: findings-received`); the
counterweight pass below is parent-owned. A third file-backed reviewer
verified the repairs. No in-process host subagent was used.

## Reviewed Input Identity

- Reviewed-path manifest: `charness-artifacts/critique/2026-09-04-release-8-1-0-reviewed-paths.txt`
  (the non-artifact paths changed since `v8.0.3`; every packet below is a
  `prepared-for` packet over that manifest or over the repaired paths).
- Reviewer 1 packet: `charness-artifacts/critique/release-8-1-0-gawande-1-packet.json`,
  SHA256 `9a1ed604e6e395454d64832612d32cf1b38eaf3ce5c1a717861de1941bc800b8`,
  identity `84eb398279bdf6d0f857546495f391b19880061632e60c502ea70f1cfdc0b2ac`,
  attempt `release-8-1-0-gawande-1`, verdict `block`, one finding.
- Reviewer 2 packet: `charness-artifacts/critique/release-8-1-0-minto-raskin-1-packet.json`,
  SHA256 `5fc2674da91ed392ab7f0e51a6c01cf98ef994f16456f9327a135002b8192132`,
  same identity, attempt `release-8-1-0-minto-raskin-1`, verdict `block`,
  three findings.
- Reviewer 3 packet (repair verification, on the repaired tree `8215ca142`):
  `charness-artifacts/critique/release-8-1-0-repair-verify-1-packet.json`,
  SHA256 `aa7c32f3d53d201370918566c65801e332c50f7d7e4844e28428b978e8096b07`,
  identity `f016d601cbf3738e2f26cec8c5fc704d0158bd6439e4384c2594427350d50835`,
  attempt `release-8-1-0-repair-verify-1`, verdict `block`, five findings
  (four confirmations, one new act-before-ship on a test caller).
- The two first-round reviewers judged the tree at `d90266ea4`; the repairs
  are commit `8215ca142`, judged by reviewer 3. Stated rather than hidden.
- Worker receipts, ledgers, prompts, and results under
  `.charness/reviewer-round-release-8-1-0-*/` (run state, not tracked).

## Reviewer Tier Evidence

- requested tier: `high-leverage` (adapter `reviewer_tiers.high-leverage`:
  `gpt-5.6-terra`, `reasoning_effort: medium`, `service_tier: priority`).
- requested spawn fields: file-backed Codex worker through `run_review.py`
  with the adapter's `reviewer_runner` (`mode: file-backed-worker`,
  `backend: codex_exec`); no host subagent spawn.
- host exposure state: `host-defaulted`; the packet records the request, not
  the model the host chose. Application state: unverified-by-packet.
- backend: `codex_exec`, capability status `ready`, capability envelope
  `28cb0f1d3d601800661d75b180c688ec47fe1f164ccfd593c22bae8fd3d2715f`;
  `receipt` status `succeeded`, `output_fresh` true, for every worker.

## Boundary Ownership

- The docs word budget has one owner, `scripts/gates/check_docs_length.py`,
  wired as a `check-docs.sh` component and listed in `.agents/quality-gates.yaml`
  as `label-only`; its record lives under `charness-artifacts/quality/`.
- The graduated-lesson readback is produced by `check_lesson_ledger.py` from
  the `reviewed_retros` field that `record_lesson_lifecycle.py` writes; the
  shared graduation reference and the retro skill cite it and restate nothing.
- Verdict: owned-correctly.

## Release Scope

Version: `8.1.0`. Tag: `v8.1.0`. Previous: `8.0.3`.

Change: minor, and the operator named this version on 2026-09-04. What changes
for a consumer: the shipped `check-docs.sh` gains a docs word-budget component
with a shrink-only record; a lifecycle event records the retros that tagged a
class and the ledger check names a graduated lesson tagged again; the export
self-sufficiency scan prunes build output and survives a vanishing path; the
retro skill and the generated CLI reference preamble are shorter with the
same rules. No public skill, CLI subcommand, shell gate, or install surface
gained or lost a member (the derived claim block is byte-identical to the
v8.0.3 notes' block); the new gate and the readback are additive maintained
behaviour adopted without migration, which is the minor shape in
`version-policy.md`.

## Surface-Lock Inventory

- Packaging and manifests: `packaging/charness.json`, the plugin manifests,
  and the root marketplace files (unchanged since `v8.0.3` until the bump the
  publish helper writes).
- Root CLI `charness` (unchanged in this range) and the install/update path.
- The docs pages this range touched (the `docs/` set cut under the budget),
  `docs/development.md`'s mechanisms table, `docs/implementation-discipline.md`.
- Exported shared guidance: `skills/shared/references/lesson-graduation.md`;
  public `skills/public/retro/SKILL.md`; the quality skill's
  `consumer-validator-catalog.yaml`.
- Adapters: `.agents/quality-gates.yaml`.
- New or changed mechanisms: `scripts/gates/check_docs_length.py`,
  `scripts/check-docs.sh`, `scripts/lessons/*`,
  `scripts/gates_support/render_cli_reference.py`,
  `tools/export_self_sufficiency_lib.py`.

## Findings

### Act Before Ship — fixed in `8215ca142` before the bump

- Reviewer 1, G1 (critical). `check_docs_length.py --write-baseline` guarded
  every increase with `and previous`, so an existing record whose pages map
  had emptied was re-founded from whatever was over budget, converting a
  refusal into a permitted exception. Confirmed at the named lines. Now an
  absent record reads as `None` and is founded from the tree; an existing
  record, empty or not, refuses any page not in it or above its count; the
  judge receives `previous or {}`. Seeded by two new tests (existing empty
  record refuses; absent record is founded) and the changed-line gate is
  `clean` on the repair commit.
- Reviewer 2, MINT-RASK-001 (act-before-ship). The mechanisms row said a
  lesson leaves the working set only by an event pointing at a `docs/` page;
  `lesson_ledger_lib.py` restricts `docs/` to `graduate` and an archive cites
  any canonical Markdown decision. Row rewritten to say exactly that, under
  the page budget.
- Reviewer 2, MINT-RASK-002 (act-before-ship). Step 4 of the implementation
  sequence commits the slice before the changed-line proof; step 6 said
  "commit after verification". Step 6 now says what is pushed is the verified
  commit and a repair forced by verification lands as a further commit on the
  same unpushed branch.
- Reviewer 2, MINT-RASK-003 (act-before-ship). The shared graduation
  reference addressed the lifecycle helper as `<repo-root>/scripts/...`, which
  in a consuming repo names the consumer tree; it now uses
  `<plugin-dir>/scripts/lessons/record_lesson_lifecycle.py`, the checkable
  placeholder from `bootstrap-resolution.md`, and the helper is shipped under
  `plugins/charness/scripts/lessons/`.

### Over-Worry — rejected with evidence

- Reviewer 1 triage, consumer breakage from the new validator: the catalog
  classifies `check_docs_length.py` as not consumer-facing; a consumer that
  runs the shipped `check-docs.sh` on its own `docs/` founds its own record on
  the first `--write-baseline` and is refused only for a page over budget and
  not in it, which is the gate's stated contract. Not a blocker; named in the
  notes.
- Reviewer 2 triage, the trimmed retro skill lost a step: cleared by the
  reviewer (bootstrap, ordered workflow, persistence helper, chat-only
  fallback, and the `Persisted` requirement are all present).

### Valid but Defer

- Reviewer 2 triage, the graduated-recurrence detector is advisory rather
  than blocking: intentional, the reference and the implementation agree, and
  what to do about a re-tag is settled with the person, as the graduation was.

## Repair Verification (reviewer 3)

- G1, MINT-RASK-001, MINT-RASK-002, MINT-RASK-003: confirmed repaired, file
  and line named in the worker result.
- NEW-LOAD-BASELINE-OPTIONAL-CALLER (act-before-ship, fixed): one existing test
  passed `load_baseline`'s now-optional return straight to `judge`; it passes
  only because the live record exists. Normalized with `or {}` in the commit
  that carries this artifact; the gate file itself was not changed by it, so
  reviewer 3's confirmations of G1 stand on the same bytes.

## Operator Action Required

- None outstanding at the tag. G1 and the three docs findings are in the tree
  the bump is cut from.

## Upgrade Path

- `charness update` fast-forwards the managed checkout; restart Claude Code
  or start a new Codex session afterwards. No migration. A consuming repo that
  runs the shipped `check-docs.sh` sees the new `check-docs-length` component;
  its record is founded by `--write-baseline` once. Rollback is
  `git checkout v8.0.3` in the managed checkout followed by `charness update
  --no-pull`.

## Deliberately Not Doing

- Making the graduated-recurrence advisory blocking.
- Sizing the hosted mutation job's exec budget to its job timeout (#764's
  next work, outside this release).

## Verification

- Focused: `tests/test_docs_length_gate.py` and the skill-docs contracts (43
  passed); `./scripts/check-docs.sh` PASS with the docs-length record
  unchanged (none new); changed-line gate `clean` against `d90266ea4`.
- Standing runner on the repaired tree: 8865 passed in 87.50s.
- Install/update rehearsal on the pre-bump tree:
  `charness-artifacts/release/2026-09-04-v8.1.0-install-update-rehearsal.md`
  (37 passed).
- The publish helper runs the release lane, the fresh-checkout probes, and the
  derived-notes check on the exact candidate before the tag; that record is
  the byte-bound proof for packaging, not this artifact.
