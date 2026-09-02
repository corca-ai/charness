# Goal Run #765 Final Proof

Date: 2026-09-03
Provider: `corca-ai/charness`
Frozen draft SHA-256: `129f065a28ce2c6a6a7fd7dc5f6ff2b63349b75ddf1ab62411ea4879ff8d2501`
Binding SHA-256: `20fdaf7e9a3e1489a308b11041555a9249b2e826d93d951f294a565b24d161cf`
Draft: `charness-artifacts/goals/2026-09-02-north-star-realignment.md`

## Outcome and boundary

The Goal Run realigned the repository with `docs/design-north-star.md` in nine
Work Items: seven operator-approved at activation (766 docs-as-code, 767
gate-scope-repair, 768 subprocess-retroactive-removal, 769
quality-boundary-and-run-quality, 770 scripts-packaging, 771
rework-instrument, 772 integrated-closeout) and two approved amendments (773
goal-run-binding-simplification, 774 ledger-only-lessons). All nine are
provider `CLOSED`, each through a `Closes #N` commit on `origin/main` whose
body is the closeout carrier, each with `verify-closeout` = `verified`, and
each now carrying an issue-owned closeout comment whose URL is the evidence
identity in `final-close-proof.json`.

No release, tag, publish, or installed-host mutation on operator machines is
claimed. The parent closes through `issue_tool.py goal-run-close` only.

## Child closeouts

| child | key | carrier commit | issue-owned comment |
| --- | --- | --- | --- |
| #771 | rework-instrument | `6673ad6d9` | https://github.com/corca-ai/charness/issues/771#issuecomment-5516530365 |
| #773 | goal-run-binding-simplification | `b8a6c7421` | https://github.com/corca-ai/charness/issues/773#issuecomment-5516530662 |
| #766 | docs-as-code | `d27274cf7` | https://github.com/corca-ai/charness/issues/766#issuecomment-5516528447 |
| #767 | gate-scope-repair | `7f4bcf835` | https://github.com/corca-ai/charness/issues/767#issuecomment-5516528792 |
| #768 | subprocess-retroactive-removal | `bff819a9a` | https://github.com/corca-ai/charness/issues/768#issuecomment-5516529240 |
| #774 | ledger-only-lessons | `2681dba4e` | https://github.com/corca-ai/charness/issues/774#issuecomment-5516530985 |
| #769 | quality-boundary-and-run-quality | `c6477cefb` | https://github.com/corca-ai/charness/issues/769#issuecomment-5516529628 |
| #770 | scripts-packaging | `ff71dc9a9` | https://github.com/corca-ai/charness/issues/770#issuecomment-5516530017 |
| #772 | integrated-closeout | `9b7b0115b` | https://github.com/corca-ai/charness/issues/772#issuecomment-5516558678 |

## Whole-system evidence

- Clean consumer install proof from the exported plugin on a throwaway
  repository: `charness-artifacts/probe/2026-09-03-772-installed-consumer-proof.md`
  (source and installed checkout both `55a1f235e`; every consumer command
  exit 0; no `tools/` shipped or executed; the exported runner refuses by name).
- Release lane on the integrated tree: `./scripts/run-quality.sh --release`
  84 passed, 0 failed at `3fd042d4c`; the release-only tests it re-admitted
  found three regressions hidden since #768, fixed in `1da602d3f`,
  `1a9235c34`, `3fd042d4c`.
- Standing evidence at the last child closeout: full standing pytest 8592
  passed, full read-only lane 80 passed (`ff71dc9a9`).
- Distinct-observer review of the export boundary and gate classification:
  `charness-artifacts/critique/2026-09-02-769-export-boundary.md` (12
  findings, 7 fixed before the #769 closeout, F9 and F10 answered by the
  live install proof).
- Gate-universe parity across the packaging:
  `charness-artifacts/quality/2026-09-02-gate-universes-before-770.yaml`
  against the packaged tree, identical by basename.
- Session narrative and lessons:
  `charness-artifacts/goal-runs/765/2026-09-02-session-record.md`; retros
  `charness-artifacts/retro/2026-09-02-session-retro.md` and
  `charness-artifacts/retro/2026-09-03-session-retro.md`.

## Exact graph

`expected-final-graph.json` lists the nine children above. The live readback
that this proof binds is `observations/goal-765-final-read.yaml`
(`goal-run-read`, `verified-read`), taken after #772 closed: nine linked
children, all `CLOSED`.

## User acceptance from the draft, answered

- docs/index.md routes only to current contracts and every docs page carries
  a `Last verified` line that `check-docs.sh` enforces (#766).
- Spawns live only inside `subprocess_guard.py`; the form gate refuses a new
  one; test files naming an interpreter carry `boundary_contract` (#768).
- The export contains no repo-only gate; `tools/` is not shipped; the exported
  runner refuses by name and the consumer route is the planner (#769, #772).
- `scripts/` has seventeen concept packages and every gate reports the same
  file universe before and after the move, `.sh` included (#767, #770).
- Unreferenced scripts are gone and the standing lane refuses new ones (#767).
- A child's scope can be corrected and a Work Item appended to a live Goal Run
  under operator approval without re-bootstrapping (#773, exercised by #774).
- The rework label path exists and was exercised (#771, #774).
