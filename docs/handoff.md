# Charness Handoff

## Workflow Trigger

- **Next pickup:** shape or activate the [one-rule-one-owner goal](../charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md). It is `draft` and pursue-ready; `/goal @charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md` activates it. Its slice 1 is `#552` — a checker requiring a token its renderer never emits, so two AGENTS.md policy checks can never fire. The [arm-the-verdict goal](../charness-artifacts/goals/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md) is CLOSED early at 2 of 7 by operator instruction; its remaining claims are re-homed in the successor.
- **Ask for the push before anything else.** Local commits sit unpushed (`git log --oneline origin/main..HEAD`), one of which carries the `#553` closeout. `git push` is not a standing approval and must be requested every time.
- **The WARN tier is now ARMED for `unknown` only, on the operator's recorded decision.** `python3 scripts/validate_adapters.py --repo-root .` warns by name on a declared key nothing reads, exits 0, and states the count AND the file scope so a clean run is a claim rather than silence. `reader-elsewhere` and `text-asserted` stay reported-but-unarmed: 3 of `reader-elsewhere`'s 23 instances are association residue where the reader really does read the file through dynamic dispatch, and one of those ships inside the [handoff adapter example](../skills/public/handoff/adapter.example.yaml). `survey()` still reports and refuses nothing. Recount with `python3 scripts/adapter_key_registry.py --repo-root .`, which prints the adapter/key totals, the per-state counts, and every gap with its reason. The goal artifact's Slice Log holds the as-of measurement.
- **Widening a scope needs a measured UPPER bound in the same commit.** This is the generalized lesson and it is now an executable test. Every seed in the key registry was justified by a measurement of under-reporting and none by a measurement of over-reporting — and that asymmetry is exactly how the defect recurred, as association by module-BASENAME collision: every skill ships a `resolve_adapter.py`, so a bare-basename match tied every one of them to every adapter (`ls skills/public/*/scripts/resolve_adapter.py | wc -l`).
- **The premise-check phase is now 5 for 5 across this goal family, including where the premise HELD.** Slice 1's premise held and the check still found `version: true` accepted at all 17 sites; slice 2's premise held and the check sharpened the refutation. Keep opening every slice with it.
- **Two review rounds, not one, when verdict logic changes — and round 2 reads the REPAIRS.** Measured again this session: round 1 fixed the AGENTS.md reader and left the setup TEMPLATE writing a baked model id, so charness would have shipped a template its own inspector flags. Round 2 caught it. A fix carrying the class it fixes is this repo's most reliable failure mode.
- **A gate firing is evidence about the tree, not about your diff.** The dup ratchet reported 19 new families; reading two members showed the slice REVEALED pre-existing duplication rather than adding it (the deleted 6-line block had been splitting identical resolver bodies into sub-threshold runs). Read the members before dispositioning — it took a minute and inverted the answer. Filed as #550.
- Recount the backlog with `gh issue list --repo corca-ai/charness --state open`; this session filed #550, #551, #552, #553.

## Continuation Capability

- Keep semantic coverage, proof execution, evidence identity, execution root, final consumer, and external observation as separate claims.
- Do not let #518 consume #515's taxonomy, #515 consume #514's taxonomy, or any issue wait on another. Share fields only when one canonical projection producer per field and at least two real readers with identical semantics are proven; source facts may have separate producers.
- At irreversible boundaries, a green gate, `CLOSED` state, or local artifact is provisional; require a different observer and evidence channel.
- Any reviewed input change invalidates packet identity and the verification lock.
- Refresh kept, because each changes the next action: the unified #514/#515/#518 repair goal, the conditional shared-seam decision, independent issue slices, read-only sibling-repo comparison, and the current CI non-claim.
- Refresh non-claims: #516/#517 implementation detail, consumer browser/provider behavior, and any current-head green verdict not proven by an independent run.

## Current State

- #516 and #517 are closed; use them only as typed regression fixtures, not new work.
- #515 is open and contains consumer-repo browser/sync/support-skill evidence whose fresh-eye proof is not yet closeout-grade.
- #514 is open and asks for deterministic closeout evidence assembly without weakening gates or building a monolithic orchestrator.
- #518 is open and requires a full Charness repair of adapter/preset/surface reconciliation and false-green final verdicts; its pinned consumer reproduction and sibling comparison are recorded in the [debug artifact](../charness-artifacts/debug/2026-08-07-issue-518-quality-declaration-reconciliation-debug.md).
- The current awiki run is non-clean evidence for #518: `awiki 0.5.0` was detected at `/home/hwidong/.cargo/bin/awiki`, and `awiki lint -root docs -recursive` returned exit 1 with 40 documents, 7 orphans, 0 islands, and 230 link-only lines. It must become an explicit quality integration dependency and final-artifact disposition; it is not a clean result.
- Existing Charness `check-doc-links`, `markdownlint`, `check-links-internal`, and `nose` document-duplicate review have distinct observed semantics from awiki's graph check. No deletion is authorized until a command-level overlap matrix proves a full replacement.
- The goal draft now binds all three issues in one lifecycle while preserving consumer ownership, independent carriers, and separate readbacks.
- Quality Core run `31118030353` for head `0e469e917c6fa1b07f0351da639ac4431f519acc` failed at GitHub action metadata with `Service Unavailable`; mutation was cancelled. Treat it as an external CI non-claim.
- The publish-state claim below remains a captured, offline-reconciled snapshot for `published_sha` `e7c3e1b3…`; it is not a current version or tag claim. The release record separately binds `v3.4.0` to tag SHA `7bf3893b`, and the post-publish bookkeeping is committed at `c34b3dc0`. This block is a machine-read source locator declared by [the publish-state ledger](../charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json), not prose: rewriting this handoff without carrying it forward refuses `publish_state_ledger.py` and reddens its whole test group, which is exactly what `0659d5a0` did. Recount with `python3 -m pytest -q tests/quality_gates/test_publish_state_ledger.py tests/quality_gates/test_retro_memory.py`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. Activate the successor goal above. Its slice 1 (`#552`) is the sharpest
   instance in the tracker: a gate that can never fire is a permanent green.
2. **Open every slice with a premise check.** The record is 5 for 5 that the
   named remedy is wrong — including where the premise held. Slice 2's check
   refuted the plan's own wording and rerouted the work to a different skill.
3. **`#534` is NOT claimed and should not be re-shaped from its issue title.** A
   prior goal built it green, refuted it, reverted it in full, and posted the
   refutation to the issue, concluding it may not be worth building at all.
4. Two operator decisions are open and block nothing: whether the GATE discharges
   `#530` (the resolver still emits the string in its title), and whether `#535`
   is worth claiming at all. Both are in the successor's Operator Decision Queue.
5. Recount before shaping anything: `gh issue list --repo corca-ai/charness
   --state open` (29 at last count). `achieve` now REFUSES a draft goal that does
   not record what it claims and does not.

## Discuss

- No standalone CI retry, Cautilus run, browser/provider roundtrip, release, push, or consumer product claim is implied by the failed setup run or this goal activation. A remote carrier, if required at issue closeout, is a separate gated publish boundary after local proof.
- Do not create a generic evidence framework before Slice 0 proves a common representation, owner, and final reader.

## References

- [Unified goal](../charness-artifacts/goals/2026-08-07-repair-evidence-boundary-close-514-515.md)
- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Session retro](../charness-artifacts/retro/2026-08-07-session-retro.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read this before changing repo operating contracts, prompt or skill surfaces, exports, or artifacts. It is a machine-read obligation of this file, not a courtesy link.
- [#516 debug record](../charness-artifacts/debug/2026-08-07-issue-516-mutation-regression-debug.md)
- [#514](https://github.com/corca-ai/charness/issues/514)
- [#515](https://github.com/corca-ai/charness/issues/515)
- [#518](https://github.com/corca-ai/charness/issues/518)
