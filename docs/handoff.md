# Charness Handoff

## Workflow Trigger

- **Next pickup: activate the drafted goal.** Run `/goal @charness-artifacts/goals/2026-08-09-make-proof-surfaces-report-what-they-observed.md`. It is `draft`, `--pursue-ready` passes, and it is shaped with four ordered slices. `/goal` is pursue-only — it shapes nothing, so re-shape with `/achieve @...` if the acceptance boundary has changed.
- **The slice ORDER is the design, not a preference.** Slice 1 (rules-before-authoring) comes first because it changes how every later slice is written. Every gate must be green BEFORE it is promoted — promoting red creates pressure to weaken the floor, which is the condition that forfeits the push.
- **Do not re-run the `## Next Session` list from the previous handoff.** Items 2 and 3 shipped (`0c82364e`, `7caa9b5b`); item 1 was DROPPED on its premise check exactly as that item instructed — the `-packet.md` is the reviewer-facing surface and the `.json` is sha-bound, so neither is the redundant copy.

## Continuation Capability

- **Verify a remedy's premise before shaping a slice around it.** The awiki orphan set was investigated at Before-phase and it reframed the work: three of seven orphans are linked from repo-root `AGENTS.md`/`CLAUDE.md` and are scan-scope artifacts, and the real gap is that the docs tree has no index hub page at all.
- **Settle by measuring, not by debating, when a command can answer.** Widening awiki's scan root was rejected on numbers: `-root .` gives 3564 documents / 2884 orphans / `largest_component_ratio=0.1496`.
- **A gate never observed FAILING is not known to work.** The goal's verification plan carries a deliberate negative test and a binary-absent run, because a clean docs verdict with no binary is the false green this surface exists to prevent.
- A slice changing verdict logic on a proof surface owes a second bounded-review round; both rounds found real blockers this session. Verify the reviewer boundary fingerprint BEFORE applying repairs, or the drift is unattributable.
- At irreversible boundaries a green gate or local artifact is provisional; require a different observer and evidence channel.
- Refresh kept: the push condition, the goal pointer, the operator decisions, the measured awiki facts, and the publish-state claim block below.
- Refresh non-claims: the finished cleanup batch's internals and the awiki manifest's review history, both spilled to their commits and to `#566`; no consumer product behavior; no remote CI verdict.

## Current State

- [make-proof-surfaces-report-what-they-observed](../charness-artifacts/goals/2026-08-09-make-proof-surfaces-report-what-they-observed.md) is `draft`: eight slices. It supersedes the awiki-only draft, WIDENED by operator decision to the four proof surfaces that report a verdict they never observed — the routing floor's keyword guess, a describe module that hardcodes what it says it renders, and an attention-state gate that cannot tell English prose from a status value.
- `#566` step 1 is DONE (`c772f147`): [integrations/tools/awiki.json](../integrations/tools/awiki.json) validates and `charness tool doctor awiki` is `ok`. The lock is generated and gitignored. Step 2 is the goal above. `#518`'s quality-dependency clause is still unmet and is called out on `#566` rather than left looking satisfied.
- **A large unpushed range is outstanding** — recount with `git log --oneline origin/main..HEAD | wc -l`. Push is approved ONLY with the release at the goal's final bundle, and only if the gates are green by their own strength: `--no-verify`, a disarmed check, or a lowered floor revokes it. Remote CI is an explicit non-claim for every commit in this range.
- `awiki lint -root docs -recursive` exits 1 today: `documents=40 orphans=7 islands=0 link_only_lines=229`. Re-measure rather than trusting this line.
- The publish-state claim below is a captured, offline-reconciled snapshot for `published_sha` `e7c3e1b3…`, not a current version or tag claim. It is a machine-read source locator declared by [the publish-state ledger](../charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json): rewriting this handoff without carrying it forward refuses `publish_state_ledger.py` and reddens its whole test group. Recount with `python3 -m pytest -q tests/quality_gates/test_publish_state_ledger.py tests/quality_gates/test_retro_memory.py`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **Activate the goal and run its slices in order.** Slice 1 builds the docs index hub; do not start at slice 3.
2. **Close `#560` — the cheapest close in the tracker.** It is built and PROVEN; only its closeout floor was never run. Outside the goal, so it can go first or last.
3. **Then `#523`**, the opinion file's top consumer-facing pick — but read [that file](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md) as opinion, not instruction; it says so itself and four of its positions were corrected by the operator within one session. `## Subagent Delegation` in `AGENTS.md` is LOAD-BEARING and must be held out of any cut.
4. Recount the backlog before shaping scope: `gh issue list --repo corca-ai/charness --state open`.

## Discuss

- Open, and blocking nothing: whether `awiki` joins [the declared tool dependencies](../integrations/tools/dependencies.json) (the goal defers this to slice 3, because the honest answer depends on how the gate behaves when the binary is ABSENT), `#561`'s equality-versus-invariant pin, `#547`'s re-scope, and the renderer-versus-reference spelling split in `setup`.
- Decided this session, so do not reopen: the awiki gate is charness-INTERNAL only, the orphan repair is a new docs index hub page rather than a baseline exception, and the release is a MAJOR bump (`3.5.0` -> `4.0.0`).
- `check-changed-line-mutation-coverage` fails on six files inherited from the unpushed range; none belong to this session's slices.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read this before changing repo operating contracts, prompt or skill surfaces, exports, or artifacts. It is a machine-read obligation of this file, not a courtesy link.
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
- [Issue #566 corrected scope](https://github.com/corca-ai/charness/issues/566)
