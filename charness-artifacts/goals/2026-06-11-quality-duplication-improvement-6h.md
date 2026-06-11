# Achieve Goal: Quality and duplication improvement timebox

Status: draft
Created: 2026-06-11
Activation: `/goal @charness-artifacts/goals/2026-06-11-quality-duplication-improvement-6h.md`
Timebox: 6h maximum
Activation time: pending until `/goal` activation
Closeout reserve: 30m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-11-quality-duplication-improvement-6h.md`.
- Timebox posture: spend at most six hours after activation; reserve the final
  30 minutes for final proof, artifact closeout, retro disposition, and commit.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Use a maximum six-hour autonomous run to improve Charness quality posture,
starting with the `nose` duplicate findings and especially recurring
bootstrap/scaffold/load-helper duplication. The desired outcome is not merely a
lower clone count: it is fewer real maintenance hazards, clearer classification
of intentional portable boilerplate versus extractable debt, and at least one
committed structural simplification when a safe slice exists.

## Non-Goals

- Do not push to `origin`, cut a release, publish, or rely on remote CI unless
  the operator explicitly approves that external side effect during the active
  run.
- Do not use `nose --exclude` or `nose.ignore.json` as proof that excluded
  duplication was resolved. Filters are only for focused review after
  classification.
- Do not refactor all `resolve_adapter.py` files in one broad sweep unless the
  run first proves a portable/shared-helper contract that preserves public skill
  export safety.
- Do not chase every advisory clone family. Leave intentional boilerplate alone
  when extraction would increase coupling or reduce arbitrary-machine
  portability.
- Do not take over #184 product metrics work; file or defer off-goal product
  questions separately.

## Boundaries

- External side-effect scope: no push, release, remote-CI watch, publish, or
  live apply is approved by this draft. Any later approval is phase-scoped and
  does not carry forward.
- Source scope: repo-local quality and public-skill support surfaces under
  `scripts/`, `skills/public/`, `skills/support/`, tests, integration manifests,
  and generated plugin mirrors.
- Quality scope: duplicate/code-shape, testability, validation/quality-gate
  ergonomics, and adjacent source hygiene discovered while classifying the
  duplication.
- Portability boundary: public skills must remain export-safe and runnable on
  arbitrary machines. Host-specific behavior stays in adapters, presets, and
  integration manifests.
- Commit boundary: each meaningful slice that changes repo state should commit
  with its tests, mirrors, and durable artifacts before the next unrelated
  slice.
- Discuss before activation: resolved — the operator requested a maximum
  six-hour quality/duplication improvement goal. The draft assumes local
  implementation only, no push/release, and no live/provider proof.

## User Acceptance

After completion, the user can inspect the final report and verify:

- the goal stayed within the six-hour maximum or recorded an honest early stop;
- `nose` baseline and focused scans were used to classify duplicate families,
  including whether bootstrap duplication was reduced, intentionally retained,
  or deferred with a reason;
- at least one safe quality improvement landed when the run found one within
  the timebox;
- every change has local deterministic proof and a committed artifact trail;
- residual quality issues are named with next-slice candidates rather than
  hidden behind a green gate.

## Agent Verification Plan

### Low-Cost Checks

- `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json --top 0`
  for broad duplicate inventory, plus focused filtered scans such as
  `--exclude '**/resolve_adapter.py'` to reveal non-resolver candidates.
- `python3 scripts/check_changed_surfaces.py --repo-root .` after each
  meaningful mutation to derive sync and verification obligations.
- Focused pytest for touched modules/tests.
- `ruff check` and `python3 -m py_compile` for touched Python surfaces.
- `python3 scripts/validate_skills.py --repo-root .`,
  `python3 scripts/validate_integrations.py --repo-root .`, and plugin mirror
  drift checks when public skill or integration surfaces move.

### High-Confidence Checks

- Fresh-eye critique for each substantial refactor slice before finalizing the
  slice.
- `bash .githooks/pre-commit` before commits.
- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest` as
  a pre-lock rehearsal when a slice spans multiple generated or validator
  surfaces.
- Final broad non-release pytest or `run_slice_closeout.py --verification-lock`
  when the changed surface warrants it and time remains after the closeout
  reserve.

### External Or Live Proof

- No external/live proof planned. Remote push, release publication, or live
  provider proof is out of scope unless the operator explicitly approves it
  during the active run.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Rebaseline duplication and classify top families | The new `nose` scope/ranking support makes broad versus filtered scans comparable. | Broad `--top 0` scan, resolver-filtered scan, classification notes in Slice Log. | planned |
| 2 | Choose and implement the safest structural reduction | Start with narrow bootstrap/scaffold/load-helper repetition rather than broad resolver surgery. | Small refactor, focused tests, plugin sync if needed, before/after nose sample. | planned |
| 3 | Apply a second quality improvement if time remains | Done-early policy should continue into the next safe improvement instead of stopping after one cleanup. | Another committed cleanup or `No safe next slice:` with reason. | planned |
| 4 | Closeout proof, residual ledger, retro disposition | Timebox requires protected final proof and explicit non-claims. | Final gates, critique/retro artifacts, completed goal artifact. | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns which skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at
  the gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

## Slice Log

No slices executed yet. This draft is inert until `/goal` activation.

## Context Sources

- User request on 2026-06-11: "앞으로 최대 6시간 동안 이 중복을 비롯한 품질 문제를 개선하는 골".
- Commit `f8921433 Add nose advisory scope filters`: added `nose` advisory
  `--exclude` / `--ignore-file`, `scope`, and `ranking` support.
- Latest observed `nose` broad scan after `f8921433`: `20` shown families out
  of `526` total ranked families; shown duplicated lines `3124`.
- Latest observed resolver-filtered scan: `--exclude '**/resolve_adapter.py'`
  produced `20` shown families out of `496`; shown duplicated lines `2551`.
- `charness-artifacts/critique/2026-06-11-215156-nose-exclude-adapter-code-critique.md`
  for the previous slice's reviewer concern that filtered scans must disclose
  scope and ranking.
- `skills/public/quality/references/inventory-dispatch.md` source-hygiene
  guidance: treat `nose` as advisory and review extractable non-bootstrap
  families first.
- `charness-artifacts/retro/recent-lessons.md` for current repeat traps around
  broad proof, stale assumptions, and closeout discipline.
- `docs/conventions/implementation-discipline.md` and
  `docs/conventions/operating-contract.md` for mutate/sync/verify/publish,
  critique, and commit discipline.

## Interview Decisions

- Mode: artifact-only draft now, implementation-continuation after explicit
  `/goal` activation. Rejected immediate execution because `achieve` separates
  shaping from pursuit and must not consume the host goal slot while drafting.
- Timebox: maximum six hours, closeout reserve 30 minutes, done-early policy
  `continue_next_improvement`. Rejected open-ended "clean up all duplicates"
  because advisory clone families exceed what one safe run can responsibly
  refactor.
- First target family: classify first, then pick the safest structural cleanup
  among bootstrap/scaffold/load-helper repetition. Rejected broad
  `resolve_adapter.py` extraction as the default first move because public skill
  portability/export coupling needs proof before shared resolver surgery.
- Proof level: local deterministic proof and fresh-eye slice critique. Rejected
  live/remote proof by default because this quality goal does not require a push
  or release.
- Axis probe: host/provider/release are variable axes in this repo; this goal
  chooses local-only proof as a single run boundary, not a global policy.

## Plan Critique Findings

- Same-agent shaping critique: the main risk is optimizing the metric rather
  than reducing maintenance hazard. Folded into Goal, Non-Goals, and User
  Acceptance by requiring classification, structural simplification, and
  residual non-claims rather than a raw clone-count win.
- Same-agent shaping critique: broad resolver commonization can break public
  skill portability. Folded into Boundaries and Slice Plan by requiring narrow
  candidates first and proof before resolver surgery.
- Fresh-eye plan critique: planned for the first substantial active slice,
  using a bounded packet with changed files, owning/generated surfaces, proof,
  non-claims, and reviewer questions.

## Off-Goal Findings

None yet.

## Final Verification

Pending until active run closeout.

Retro: pending until active run closeout.
Host log probe: pending until active run closeout.
Disposition review: pending until active run closeout.

## User Verification Instructions

Pending until active run closeout. Expected final instructions should name the
commits, before/after duplicate evidence, local gates run, residual risks, and
any off-goal issues filed.

## Auto-Retro

Retro dispositions: pending until active run closeout.
Structural follow-up: pending until active run closeout if the retro names a
transferable waste item.
