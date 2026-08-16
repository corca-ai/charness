# S7 6.0.0 Release Execution Critique

Date: 2026-08-16

## Decision Under Review

Publish charness `6.0.0` from `main` and close
[#608](https://github.com/corca-ai/charness/issues/608) and
[#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627)
against executed proof. Scope: the whole release — the notes generated over the
final tree, the eleven issues' premise, the contract's success criteria, and the
publish path's own mechanics. The per-issue premise verdicts are F23-F27 and
F27b-F27d, covering eight of the ten `bug`-classified issues; #622 and #624 have
no fresh reproduction in this slice and their verdicts rest on the earlier cohort
review plus F10 and F13 below, stated here and in the ledger rather than left to
a reader to notice. This artifact is the resolution critique bound by
the closeout ledger for every issue in that set, and the release critique the
`release` skill places before the bump.

Supersedes `charness-artifacts/critique/2026-08-14-v6-0-0-release.md`, which
reviewed `0a1a53405` — a tree from before S1-S6b-2 — and whose F1 asserts "only
12 public skill scripts DECLARE one", the exact claim this release exists to
retire and which the derived block now measures at `0`.

## Failure Angles

- **Claim-versus-tree**: the notes assert something the shipped tree does not do.
  This repo's recorded failure: the prepared notes said "twelve public skill
  scripts still declare `--json`" over a measured zero, one day after a
  hand-repair for four other false claims.
- **Premise**: an issue is closed against a fix that does not reproduce as fixed,
  or whose requested outcome is wider than what shipped.
- **Contract satisfaction**: a success criterion is asserted complete while its
  proof is a passing fixture over dead code, or a `manual` acceptance nobody
  checked in.
- **Publish mechanics**: the irreversible path mis-reports, or reaches a state it
  cannot recover from — the worst case being a pushed tag, a partially closed
  issue set, and no resume lane.
- **Repair recursion**: a fix on a proof surface ships the class it fixes. This
  repo has measured that in every slice of this release.

## Counterweight Pass

- The contract is unusually well discharged: every criterion except SC12 has
  named executable proof that tests what the criterion says, and the two most
  at-risk `manual` criteria (SC9, SC10) each have an honest artifact checked in
  that states what it does NOT establish. The over-claim was concentrated in the
  one step that had not run.
- Three reviewer claims were REFUTED rather than repaired: that the notes carried
  an ungrounded prior version (all four occurrences are inside code spans, and
  `mask_exempt_regions` blanks inline code before the version patterns apply);
  that `#626`'s resurrection slot is still unfillable (a premise reviewer filled
  it by execution — `record_lesson_lifecycle.py ... --action archive` then a
  preview showing `archive: 1`); and that the exported cost gate can turn a
  green consumer red on upgrade (with no registry it returns unarmed and exits
  `0`).
- Not everything red is this release's to fix. `check-python-lengths` and
  `check-boundary-bypass-ratchet` were red AT HEAD before this slice began,
  verified by running both in a detached worktree at `6416e7023`. They are fixed
  here because `run-quality.sh --release` runs inside the publish, not because
  S7 introduced them.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check-markdown.sh | action: fix | note: `check-markdown` exited 1 AT HEAD on `cost-dominance.md:49` (MD040), taking the default quality lane and CI red on markdown HEAD's own commit introduced. Fenced language added in source and mirror.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/check_doc_authoring_preflight.py:148 | action: fix | note: a live unguarded `npm exec --` in a shipped command three planners emit, whose docstring claimed to mirror `check-markdown.sh`. Demonstrated reaching the registry with an npm shim on PATH. #630's own "not verified here" item, real. Now three tiers with `--no`.
- F3 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_markdown_lint_resolution.py:153 | action: fix | note: the guard whose docstring claimed to catch "a third unguarded call site" iterated two hardcoded `.sh` filenames and could not see Python at all. Now discovery over `scripts/**` in both languages, proven red on the pre-fix spelling.
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/argparse_surface_lib.py:205 | action: fix | note: `check-documented-command-flags` was red AT HEAD because `iter_invocation_tails` was quote-blind — a command inside another's `--test-command "..."` value stole the outer command's remaining flags. Same quote-blind-splitter class a round-2 reviewer already found once in the dominance detector, surviving in a second splitter.
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume_state.py:154 | action: fix | note: the resume lane's own artifact commit sat between the claims record and the carrier, so EVERY post-publication claims arm fell through to `release-content` and `--resume` answered "nothing to resume" — after the tag was pushed and an arbitrary prefix of the issue set was closed. Invisible because the end-to-end tests stub that commit to a no-op.
- F6 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/release_issue_closeout_artifact.py:90 | action: fix | note: a failed release-observer capture did not stop the carrier commit whose push auto-closes the issues, and then made recovery structurally impossible. Now refused before any git call.
- F7 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/release_issue_closeout_artifact.py:8 | action: fix | note: found while testing F6 — `str(None)` is the truthy string `"None"`, so the observer-path presence read passed for the exact failure it guarded and would have staged a pathspec named `None`.
- F8 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_cli.py:250 | action: fix | note: `commit_sha` read HEAD while the tag was created at the prepared record, so the durable record, the observer JSON, and the comment posted on every closed issue would have named a commit `v6.0.0` does not point at.
- F9 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_narrative_gate.py:78 | action: fix | note: `_known_versions` read the packaging manifest, which is bumped on the resume lane and not on the execute lane — so a note legal at prepare was refusable at publish, where the only remedy lands a commit on top of the claims record and locks the resume out.
- F10 | bin: act-before-ship | evidence: strong | ref: skills/public/retro/SKILL.md:146 | action: fix | note: #622 named `retro`'s skill text as part of the defect; it still told a reader to act on `triggered: true` with no undetermined branch. `prove` had been repaired and `retro` had not.
- F11 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-08-16-v6.0.0-notes.md | action: fix | note: the notes carried a known-weak entry claiming `sample_mutation_files.py` has no runner override — stale S6b-1 text that S6b-2 refuted and the contract records repairing. A false claim inside the note whose purpose is to stop false claims, surviving because it reads as humility.
- F12 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-08-16-v6.0.0-notes.md | action: fix | note: the notes stated `orphans`/`islands` no longer gate at `> 0`; both keep an effective bar of `0`. A stated relaxation that did not happen, in the Breaking section.
- F13 | bin: act-before-ship | evidence: strong | ref: scripts/render_lesson_lifecycle_review.py:95 | action: fix | note: `rewrite-in-place` told the reader to revise the wording at its source retro, while the displayed wording is rebuilt from `latest_source_path`; the two diverge in this repo today, so the instruction changed nothing a reader sees. The #624 class inside the #626 fix.
- F14 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/command_dominance_lib.py | action: fix | note: `check-python-lengths` was red AT HEAD at 619 code lines against a 360 cap. Split on the concept seam into registry (what a declaration is) and carriers (where a command is written), with the export asserted to IMPORT rather than merely contain the siblings.
- F15 | bin: act-before-ship | evidence: strong | ref: scripts/boundary-bypass-exemptions.txt | action: document | note: `check-boundary-bypass-ratchet` was red AT HEAD; the two crossings are S6b-2's and S6c's. Their recorded reasons DIFFER and the exemptions state each separately: one because a review measured that the exported inventory's scan loop had never executed, the other because an in-process assertion cannot distinguish declaration from availability — only a fresh interpreter with the package blocked can. Converting either in-process would restore the defect its crossing exists to prevent, so both are exempted with their own reason.
- F16 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-08-16-v6.0.0-notes.md | action: fix | note: the lesson-ledger schema was stated as moving from `5` to `6`; `git show v5.2.0:scripts/lesson_ledger_lib.py` measures `4`. A consumer migrating from the shipped version was told the wrong starting point.
- F17 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md | action: fix | note: SC14's criterion text says "a repo-owned document" while the rule reaches artifacts passing through the handoff validator; the contract itself recorded this as "to reword at S7" and it had not been reworded, and the wide wording had reached the operator-facing notes.
- F18 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-08-16-v6.0.0-notes.md | action: fix | note: `quality` was described as refusing rather than routing on a subject mismatch; it routes onto its own dated record and refuses only when that record exists. A wrapper author coding for a nonzero exit would get a successful run at a different path.
- F19 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-08-16-v6.0.0-notes.md | action: fix | note: "a ratchet record whose bars RISE is refused" — it is DISCARDED with no payload key naming the cause, and the run falls to the strict default. Corrected, and the single-row-rewrite bypass added to the known-weak list.
- F20 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-08-16-v6.0.0-notes.md | action: fix | note: the parity gate was described as judging "every copy" of the closeout vocabulary; its own docstring records narrowing that claim after an earlier overclaim. The note reproduced the sentence the source had already corrected.
- F21 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md | action: fix | note: the release CLI applies ONE classification to every `--close-issue` number, and the eleven do not share one. `bug` for #608 fabricates a root cause for a capability request the contract itself says "is not build work". The set is split: ten close as `bug` through the release, #608 closes separately as `feature`.
- F22 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/issue/2026-08-16-6-0-0-closeout-ledger.md | action: fix | note: no classification ledger existed on the tree, and the closeout floor requires one committed before the prepared release record.
- F23 | bin: valid-but-defer | evidence: strong | ref: scripts/validate_debug_artifact.py | action: defer | note: #620's date-coherence detector is quality-family-only, proven by an exit-0 validate of a date-incoherent debug record — this file carries no such rule and no module docstring at all. The measured non-transfer reasoning lives at `scripts/validate_quality_artifact.py:532-538` and is about the CRITIQUE surface, not `debug`; an earlier draft of this line mis-attributed it here. The subject-identity prevention IS family-shared, so the close asserts prevention repo-wide and detection for one family, and the ledger's `Jtbd:` states that per issue.
- F24 | bin: valid-but-defer | evidence: strong | ref: scripts/recent_lessons_lib.py | action: defer | note: #627's title says a failed lesson "is never rewritten"; the SIGNAL half ships and is now live (11 `effect-recorded`), but no mechanism rewrites wording — `rewrite-in-place` is an instruction to a human. The close asserts the signal, not the rewrite.
- F25 | bin: valid-but-defer | evidence: strong | ref: scripts/apply_contract_transition.py | action: defer | note: #626's secondary section (post-graduation compaction) is open — a graduated lesson stays `active` against the cap. The TITLE scope is delivered and demonstrated by execution; the ledger's `Jtbd:` names this remainder explicitly as a NOT-closed clause.
- F26 | bin: valid-but-defer | evidence: strong | ref: scripts/command_carrier_discovery.py:90 | action: defer | note: #619's carrier scan covers three families; shell scripts and workflow `run:` steps are unscanned, so a flag deletion can still break CI with the gate green. Closed on the two repaired instances, not on the class.
- F27 | bin: valid-but-defer | evidence: moderate | ref: skills/public/setup/references/default-surfaces.md:136 | action: defer | note: #618's residual — consumers were pointed at an exported `check-links-internal.sh` that refuses inside a consumer repo. REPAIRED before publish rather than carried: the setup reference now names the runnable half and the CHARNESS_REPO_ROOT retarget, so the notes carry no known-weak entry for it.
- F28 | bin: over-worry | evidence: strong | ref: charness-artifacts/release/2026-08-16-v6.0.0-notes.md:4 | action: document | note: a reviewer flagged the prior version as ungroundable on the resume lane; all four occurrences are inside code spans and `mask_exempt_regions` blanks inline code before version patterns apply. Repaired anyway at F9 because relying on that is one hand-edit from biting.
- F29 | bin: over-worry | evidence: strong | ref: charness-artifacts/release/2026-08-16-v6.0.0-notes.md | action: document | note: the cost-dominance gate was listed among gates that turn a green consumer red on upgrade. It cannot: unarmed without a registry. Removed from that list.
- F27b | bin: over-worry | evidence: strong | ref: scripts/init_lesson_ledger.py | action: document | note: [#621](https://github.com/corca-ai/charness/issues/621) survived a full reproduction from a bare `git init` tree — `init_lesson_ledger.py` then `check_lesson_ledger.py` both exit 0, and the emitted next step resolves the seeder against the READING tree rather than a hardcoded `scripts/...`. No repair owed; recorded so the close rests on an executed reproduction rather than on the earlier comment.
- F27c | bin: over-worry | evidence: strong | ref: skills/public/retro/scripts/scaffold_retro_artifact.py | action: document | note: [#623](https://github.com/corca-ai/charness/issues/623) survived the same treatment: the scaffold's verbatim output validates clean in a ledger-less tree, the missing-line error names the whole key set and a copyable canonical line, and the planner reports the dated rules. All four of the issue's items are met. One residual, disclosed rather than repaired: a consuming repo still reads a literal `<authoring-repo>` placeholder in the North Star section.
- F27d | bin: over-worry | evidence: strong | ref: scripts/seed_lesson_transitions.py | action: document | note: [#625](https://github.com/corca-ai/charness/issues/625) reproduces as fixed end to end in a fresh repo with no hand-edit of the append-only ledger, and the seeder is mirrored byte-identically into the export so it ships. Two residuals, listed in the ledger's `Jtbd:` closing paragraph: nothing re-prompts the seeder after a cold start, and the script's file mode differs from its sibling's.
- F30 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/quality/dup-review.json | action: document | note: four duplicate families classified intentional — the canonical bootstrap shim family (enforced uniform by a different gate), a two-line optional-string normalizer across eight owners, and two intra-module families in the resume classifier whose members answer different questions.

### Round 2 — reading the repairs

Two bounded reviewers read only the round-1 repairs. They found defects IN them,
which is why this round is owed: four repairs changed verdict logic on a proof
surface.

- G1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume_closeout.py:241 | action: fix | note: F8's `commit_sha` repair reached one caller of `finalize_release_payload` and not its sibling — the recovery lane an operator lands on after a failed close, which is exactly where the wrong sha gets posted to every issue.
- G2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_helpers.py:408 | action: fix | note: F7's `observer_path` repair left the OTHER reader on the defective `str(None)` spelling while the new function's own docstring claimed "one reader, so the staging site and the refusal cannot disagree". The claim was false when written. There is one reader now, in the shared helper.
- G3 | bin: act-before-ship | evidence: strong | ref: scripts/argparse_surface_lib.py:205 | action: fix | note: F4's quote awareness was wrong three ways — a single-state scanner missed single-inside-double (this repo's live spelling in `.agents/quality-adapter.yaml`), `match.end() - 1` fell ON a consumed closing quote, and escapes were unhandled. Worse, the first repair of THOSE treated any quoted command as nested, dropping the flags of ~130 carriers written `python3 "$SKILL_DIR/..."` and cutting the gate's probe count from 317 to 263 — a silent coverage loss in a blocking gate, strictly worse than the false red being fixed. The rule is now "nested means another command precedes it from outside the span"; measured blast radius is exactly one carrier repo-wide, the one that was wrong.
- G4 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume_state.py:75 | action: fix | note: F5's boundary walk proved the commits it stepped over by SUBJECT while the commit it protects is proved by content — and the subject is the one thing an operator can read off `git log` and copy. An `--allow-empty` commit carrying that subject would have been walked past, publishing over content the reviewed claims record does not cover. Now proved by change set, with an empty diff refused and an exhausted budget returning a sentinel rather than silently classifying as legacy content.
- G5 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_markdown_lint_resolution.py:138 | action: fix | note: F3's widened guard wrote its flag as `"--no "` and then `.strip()`ed it at the comparison, cancelling the trailing space that was the whole point; `npm exec -- markdownlint-cli2 --no-progress` satisfied a guard about reaching the registry. Now a whole-flag pattern, and the `*` skip that would have hidden a shell `case` arm is gone.
- G6 | bin: act-before-ship | evidence: strong | ref: scripts/doc_authoring_rules.py:229 | action: fix | note: F2's three-tier resolution was inert on the second call site, which did not pass `repo_root` — one command reported markdownlint as forecast and the other as unavailable on the same machine. The no-drift test had the same omission and was silently skipping its markdownlint arm.
- G7 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/issue/2026-08-16-6-0-0-closeout-ledger.md | action: fix | note: the ledger opened "Every issue here was fixed in-repo", which this artifact's own F23-F27 narrow for five of the ten — and that sentence is the second line of a body posted on ten issues. The `Jtbd:` now names each narrowing as a NOT-closed clause.
- G8 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md | action: fix | note: this artifact asserted three times that residuals were "stated in the ledger" when the ledger contained none of them — a compensating claim that made the pair internally consistent and jointly false. Both are repaired, in the direction of the ledger carrying the residuals.
- G9 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/issue/2026-08-16-6-0-0-closeout-ledger.md | action: fix | note: `Siblings:` offered an executable scan as proof of a class scan that measures a DIFFERENT class — the parity gate judges vocabulary agreement and cannot see "a surface rendering a verdict about a thing it cannot observe". Now stated as a reviewer scan with no executable carrier, which is itself the honest finding.
- G10 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/issue/2026-08-16-6-0-0-closeout-ledger.md | action: fix | note: `Debug artifact:` claimed the per-issue reproductions were re-executed for all ten; #622 and #624 have none. Narrowed to eight and re-pointed at the cohort's actual debug record, which it had omitted.
- G11 | bin: bundle-anyway | evidence: strong | ref: .agents/surfaces.json | action: fix | note: the split left `command_dominance_registry.py` and `command_dominance_carriers.py` in no declared surface, so no verifier would be selected for a future edit to them. Both added with their mirrors.
- G12 | bin: over-worry | evidence: strong | ref: skills/public/release/scripts/publish_release_resume_state.py:154 | action: document | note: a reviewer could not verify whether the rewritten phase chain silently weakened an arm. `git show 6416e7023:` settles it — arm ORDER is identical, and the only guard change is the three claims arms moving from direct equality to the boundary walk, which returns its input unchanged whenever that input is not a generated artifact commit. No arm weakened.
- G13 | bin: bundle-anyway | evidence: moderate | ref: scripts/boundary-bypass-exemptions.txt:18 | action: fix | note: an exemption reason described `removed_name_consumers.py` as emitting "a `--json` payload"; that flag is what this release removes, so the comment described a spelling that now exits `2`.
- G14 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md | action: defer | note: the S3 and S4 slice headers still read "BUILT; two-round review in progress" although both reviews closed, which is the same stale-status shape the S3 entry itself records a reviewer catching. Left as-is: editing a slice header at S7 rewrites a record of what was true when written, and the S7 block states the delivered status explicitly.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: charness:bounded-reviewer read-only one-shot, inherited model, no host addressing name
- Host exposure state: requested_fields_sent
- Application state: round 1 ran three bounded reviewers over disjoint angles — release-notes claim-versus-tree, contract criteria coverage, and publish-path integrity — plus three general premise reviewers over the eleven issues, each required to RUN the reproduction rather than read the closeout comment. All findings above are theirs; the implementer found none of F1-F13 independently. Round 2 ran two bounded reviewers over the repairs alone — one on the publish path and the split, one on the artifacts and the ledger. It returned four blockers and eight majors, all in round-1's repairs, including one repair that traded a false red for a silent 17% coverage loss in a blocking gate. Its findings are G1-G14 above. Round-2 repairs ship accepted-unreviewed at the two-round cap.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare packet was consumed. Reviewers were briefed against the live worktree at 6416e7023 plus the uncommitted release notes, and the premise reviewers additionally read each issue body through `gh issue view` and executed its reproduction. -->

## Boundary Ownership

- Producer: the release publish path (`publish_release_*`, `release_issue_closeout_*`), the release notes and their derived claim block, and the four proof surfaces repaired here.
- Consumer: a maintainer running `--execute`/`--resume`, and every consuming repo that upgrades to `6.0.0` and reads the notes as its migration record.
- Owning surface: release for the publish path and the notes; quality for the dominance family and the length/duplication ratchets; retro for the lesson-loop instruction text.
- Verdict: owned-correctly

## Non-Claims

At the time this artifact was written: no push, tag, version bump, publish,
hosted CI, installed-consumer readback, or issue closure had occurred. Round-2
repairs ship accepted-unreviewed at the two-round cap. The premise verdicts are
executed local reproductions, not consumer-machine observations. `#634` stays
OPEN and is not in the closing set. The publish-path repairs at F5-F9 are proven
by unit assertions and by each being shown red on the defect they fix; none has
been exercised by a real publish, because a real publish happens once.
