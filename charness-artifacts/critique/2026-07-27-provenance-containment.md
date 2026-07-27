# Critique Review

Date: 2026-07-27

## Decision Under Review

Remove the containment exemption from the helper provenance guard, so the
checked-in `plugins/charness` mirror is compared instead of passed as
`same-tree` (bug-hunt A1, plus A2 and half of A9); recorded as `## Decision 2`
in [the foreign-copy spec](../spec/2026-07-27-foreign-copy-write-enforcement.md).

## Failure Angles

- **Jackson (problem framing).** The guard module a mirror invocation loads is
  the mirror's own, so the structural constraint the spec claimed did not apply
  to the contained copy still applies to the guard file itself; the spec's
  closure claim was wider than the code. The population newly refused is in-repo
  dogfooding, and the incident class (an installed copy predating the guard)
  is untouched by design — a cheap win, not the closure the first draft implied.
  Success criterion 1 is unmet and only option 1 can meet it.
- **Weinberg (diagnostic).** `compared_pairs` was computed and consumed by
  nothing, so a PASS over zero compared bytes was still a PASS — and a control
  test pinned that state as intended. The export-layout fact is hard-coded in
  three places in one module; this slice repairs copies 1 and 2 of the same
  omission a prior slice repaired in copy 3. `counterpart_path` is
  one-directional, kept inert only by the accident that an export root carries
  no `packaging/charness.json`.
- **Gawande (operational).** `issue_tool.py` declares `--repo-root` on each
  subparser, so the refusal's remediation hoisted the flag ahead of the
  subcommand and printed a command argparse rejects. The refusal never named the
  one cure the newly-refused population wants (`sync_root_plugin_manifests.py`),
  and the no-counterpart branch's "do not resync" advice is wrong for a
  contained mirror. `capability_catalog_resolver` ranks the plugin export above
  the repo's own skills, so the documented recovery procedure hands back a path
  the guard now refuses. Two unreadable files digested to `None` and compared
  equal — a fail-open inside a fail-closed guard.

## Counterweight Pass

- Real blockers, all fixed in-slice: the empty-comparison pass, the unrunnable
  subcommand remediation, the missing mirror cure, the fail-open digest, and
  every overstated claim in the spec, the audit ledger, and the operator-facing
  reference.
- Over-worry: the `scan="tree"` cost. It runs at two entrypoints only, and a
  repo-local invocation returns before any hashing. No hook, no loop.
- Not this slice: the resolver ranking and the three-copy layout fact. Both are
  real, both need their own blast-radius review, and folding either into a
  defect-repair slice is the "while we're here" creep the counterweight exists
  to stop.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/helper_provenance_lib.py:299 | action: fix | note: a verdict with zero resolved counterparts passed as `consuming-repo`; now refuses as `scope-unestablished`
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/helper_provenance_lib.py:312 | action: fix | note: remediation hoisted `--repo-root` ahead of a subcommand, so the printed `issue_tool.py` command exits 2; now rewritten in place
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-07-27-foreign-copy-write-enforcement.md:95 | action: document | note: the guard loads from the invoked tree, so the structural constraint still applies to the guard file; claim narrowed to a shorter horizon
- F4 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md:318 | action: document | note: the non-claims section still read `every id above is OPEN` and listed A9 as an unreproduced lead after A9 was half-fixed
- F5 | bin: act-before-ship | evidence: moderate | ref: skills/shared/references/bootstrap-resolution.md:94 | action: document | note: the operator contract named `build_retro_lesson_selection_index.py` as guarded before doing any work; it is guarded indirectly and late
- F6 | bin: bundle-anyway | evidence: strong | ref: scripts/helper_provenance_lib.py:274 | action: fix | note: two unreadable files both digest to `None` and compared equal; an unreadable file is now drift
- F7 | bin: bundle-anyway | evidence: moderate | ref: scripts/helper_provenance_lib.py:399 | action: fix | note: a contained-mirror refusal now names the resync command, which the generic branch cannot
- F8 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_helper_provenance_guard.py:596 | action: fix | note: the one-directional counterpart map is inert only because an export root is not a source tree; pinned by test
- F9 | bin: valid-but-defer | evidence: strong | ref: scripts/capability_catalog_resolver.py:29 | action: file-issue | note: the resolver ranks `repo-plugin-export` above `repo-public-skill` inside the source repo, so the documented recovery hands back a path the guard refuses | follow-up: deferred docs/handoff.md `## Next Session`
- F10 | bin: valid-but-defer | evidence: strong | ref: scripts/helper_provenance_lib.py:100 | action: file-issue | note: the export-layout fact is maintained in three places in one module; it should be read from the exporter, not re-encoded per comparator | follow-up: deferred docs/handoff.md `## Next Session`
- F12 | bin: act-before-ship | evidence: strong | ref: scripts/helper_provenance_lib.py:325 | action: fix | note: verification pass — `--repo` is a distinct required option on `issue_tool.py` subparsers, so prefix-matching rewrote the issue's target repo to `.` at an irreversible boundary; retargeting now needs the exact spelling or a value equal to the checked root
- F13 | bin: act-before-ship | evidence: strong | ref: scripts/helper_provenance_lib.py:309 | action: fix | note: verification pass — the empty-scope refusal was gated behind the entry-counterpart test, leaving a `tree`-scan path that still passed `in-sync` over zero compared pairs; it is unconditional now
- F14 | bin: act-before-ship | evidence: strong | ref: scripts/helper_provenance_lib.py:430 | action: fix | note: verification pass — a contained mirror with no counterpart landed in the branch that warns against resyncing, which is backwards for the one copy a resync repairs
- F15 | bin: act-before-ship | evidence: strong | ref: scripts/helper_provenance_lib.py:191 | action: fix | note: verification pass — the resync cure was gated on containment alone, so a git worktree inside the repo would be told to run the plugin resync; it is gated on the `plugins/` export root now
- F16 | bin: bundle-anyway | evidence: strong | ref: scripts/helper_provenance_lib.py:286 | action: fix | note: verification pass — the fail-closed digest named only the target counterpart, pointing the operator at a file that is fine; the unreadable own-side path is now reported
- F17 | bin: bundle-anyway | evidence: strong | ref: scripts/helper_provenance_lib.py:443 | action: fix | note: verification pass — an f-string with no placeholder would have failed `ruff` F541 at the gate
- F18 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_helper_provenance_guard.py:566 | action: fix | note: verification pass — the `chmod(0o000)` test errors under root; skipped there rather than left as a CI flake
- F19 | bin: bundle-anyway | evidence: strong | ref: skills/shared/references/bootstrap-resolution.md:94 | action: document | note: verification pass — `publish_release.py` was still listed among the write-site callers when it is guarded at the entrypoint, and the spec's "no test pins the containment behavior" had become false
- F11 | bin: over-worry | evidence: strong | ref: scripts/skill_runtime_bootstrap.py:95 | action: defer | note: the 605-file tree scan is paid once per publish or issue close on a foreign invocation only; no hook or loop reaches it

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: none — this is a Claude Code host, where the repo contract uses typed `bounded-reviewer` agents with session-model inheritance instead of the Codex `gpt-5.6-terra` request
- Host exposure state: host-defaulted
- Application state: host-defaulted — typed `bounded-reviewer` spawns accepted; the adapter's Codex model/effort fields were not sent
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated` — five bounded read-only reviewers ran in this session: one
scoped fresh-eye pass over the first draft (8 defects, all repaired), three angle
reviewers (Jackson, Weinberg, Gawande) over an earlier packet
(`charness-artifacts/critique/2026-07-27-104618-packet.json`, sha256
`5666ea96abe9e0e96d82d31cbcb2b9d7dac752e5ff1919a32a17e7058060bd9d`), and one
verification pass over the repairs those angles drove, which found nine more
(F12-F19 plus the unsynced mirror it correctly refused to accept as identical).
Boundary fingerprint snapshot/verify bracketed each window: the first two
returned `clean`, the third `parent-attributed` with zero unattributed drift.

Non-claim: the final state was reviewed by the verification pass at the packet
below, but the F12-F19 repairs themselves were not re-reviewed by a further
fresh eye. They are covered by regression tests that fail against the pre-repair
module, not by a sixth reviewer.

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-27-provenance-containment-packet.json
- Packet SHA256: eba3b0a0e52e2a8a4adec313c234595c5ff04dba5a563cb8283571f704f11e5c
- Identity SHA256: 5a2b83b8e56777ba17b1d6e4596d15f8753a81ecba9c0cf86ad59071d0c8f622

## Boundary Ownership

- Producer: `scripts/helper_provenance_lib.py` produces the provenance verdict; the exporter and packaging manifest produce the layout fact it keys on.
- Consumer: five write-site guards, `refuse_foreign_entrypoint` at two irreversible entrypoints, and the operator reading `format_refusal`.
- Owning surface: `repo-python` owns the comparator; `checked-in-plugin-export` owns the layout map.
- Verdict: escalated-to-issue-spec

## Deliberately Not Doing

- Not re-ranking `capability_catalog_resolver` candidates so the repo's own
  skills win inside a charness source tree (F9). It is the operational other
  half of this decision, but changing host skill resolution needs its own
  review; folding it into a defect repair would ship an unreviewed change to how
  every skill invocation resolves.
- Not extracting the export-layout map to a single exporter-owned source (F10).
  Three sessions have now patched one fact in three places, so the debt is real
  and recorded — but the refactor touches every comparator path at once and is
  not what this slice was asked to prove.
- Not adding a live test that runs the real mirror against the real repo root.
  It would fail during every legitimate `mutate -> sync` window and duplicates
  `check_staged_mirror_drift`.
- Not closing the `mutate -> sync` window itself (sync-on-edit). That is the
  cause behind the symptom, and it is a workflow change, not a guard change.
