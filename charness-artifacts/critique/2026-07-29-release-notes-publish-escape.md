# Closing the release-notes escape at the publish boundary
Date: 2026-07-29

## Decision Under Review

Adding two arms at the release-publish boundary: a BLOCKER when notes drafted for
the target tag are not the notes being published, and a distinct `unauthored`
verdict when the PUBLISHED body carries nothing authored.

The premise came from a multi-lens audit of the last week's 161 commits, and it
was reproduced rather than inferred. Twelve releases shipped in that window;
`gh release view` puts five of them at a one-line body (v2.6.0, v2.7.0, v2.8.0,
v2.11.0, v2.11.1 — 81-83 bytes, a `**Full Changelog**` link). v2.11.0 is the
sharp case: its notes were authored, committed to
`charness-artifacts/release/2026-07-26-v2.11.0-notes.md`, and left there while
publish took the `--generate-notes` default. Those notes carry an
`## Amends the 2.10.0 notes` section telling operators that two things they read
in 2.10.0 — including a migration instruction — are now wrong. That correction
reached nobody.

Mechanism: `run_notes_file_preflight` returned immediately on `notes_file is
None`, so the `--generate-notes` path was audited by nothing before publish; and
`audit_published_release_body` looked only for mutable source-tree pointers, so a
body with no content had none and was recorded `clean`. The repo had a surface
judging notes QUALITY and no surface establishing their EXISTENCE, and it put a
green on the absence.

North-star fit: release publish is in the named irreversible set, and this is P4
(`clean` was a claim read as a conclusion) and P5 (teeth where a wrong answer
escaped — five times). It is not a gate that checks gates: the surface is the
operator-facing product.

## Failure Angles

- **A gate nobody can publish through.** `--generate-notes` is a legitimate
  shape. An arm that refuses it as such trades a silent escape for a blocked
  release, and the fastest route around a blocking gate is deleting it.
- **The fix reproduces the class it fixes.** The subject is "a verdict rendered
  over a scope never established". A new branch that renders `unauthored` — or
  `clean` — over a body it did not actually classify is the same defect one
  surface over.
- **A filename is not a fact.** Deciding which drafted file belongs to this
  release from its NAME is an inference, and a blocker that states it as a fact
  is the same over-claim in the message rather than the code.
- **Cost placement.** A refusal decidable from a directory listing, paid for
  after the bump and the pre-push gates, is a refusal operators route around.
- **Portability.** This surface is adapter-declared (`release_view_body`), so any
  rule pinned to GitHub's own rendering silently exempts every other host.

## Counterweight Pass

- Not over-worry: the escape is measured, not theorized — five published bodies,
  one of them the correction of a wrong migration instruction.
- Real constraint accepted: whether `v1.2.3-rc1-notes.md` belongs to `v1.2.3` is
  undecidable from the filename, because a pre-release suffix and a role word
  (`-notes`, `-public`) are the same shape after the version. The arm does not
  decide it. It names every candidate and requires the publisher to choose —
  a forced question, which is what P5 permits, rather than a declared answer.
- Deliberately NOT built: a rule requiring notes to exist at all. That is a
  contract change for consuming repos, and v2.6.0/2.7.0/2.8.0/2.11.1 (no draft
  on disk) are therefore still publishable. Arm 2 records that case; it does not
  refuse it. Named as a non-claim rather than left implied.
- Backfilling the five escaped bodies was scoped out by the repo owner. The
  wrong v2.10.0 migration instruction stands uncorrected on the public releases;
  this slice closes recurrence only.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/audit_public_release_narrative.py | action: fix | note: arm 1 is the teeth -- `find_drafted_notes` resolves v2.11.0's real draft, so it would have refused that publish; arm 2 runs after the release exists
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_post_create.py | action: fix | note: False for the live bodies of v2.11.0/v2.11.1/v2.6.0 and True for v2.11.3/v2.9.0/v2.4.2; post-hoc by construction, so it corrects the RECORD and never blocks
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_verification_sections.py | action: fix | note: round 2 showed one `unestablished` label collapsed two remedies -- "could not look" is a tooling fix, "looked and found nothing" is `gh release edit`
- F4 | bin: act-before-ship | evidence: moderate | ref: skills/public/release/scripts/publish_release_narrative_gate.py | action: fix | note: round 1 measured the refusal firing only after the bump and the pre-push gates; two call sites over one helper cannot disagree
- F5 | bin: over-worry | evidence: strong | ref: tests/quality_gates/test_release_narrative_audit.py | action: document | note: refusing `--generate-notes` as such was rejected -- the arm returns no candidates for a repo that drafts no notes, pinned by test

## Executed Proof

- Both arms reproduced against real state, not fixtures: `find_drafted_notes`
  resolves `2026-07-26-v2.11.0-notes.md` for `v2.11.0` (so arm 1 would have
  blocked that publish), and `_body_says_anything` is False for the live
  published bodies of v2.11.0/v2.11.1/v2.6.0 and True for v2.11.3/v2.9.0/v2.4.2.
- `bash scripts/run-quality.sh`: 83 passed, 0 failed, 182.9s.
- Focused suites: 72 passing across `test_release_narrative_audit.py`,
  `test_release_narrative_gate.py`, `test_release_distinct_channel.py`; 568
  passing across the release/narrative/mirror/packaging selection.
- `check_export_safe_imports.py`: 610 files validated, after the shared-helper
  move below.
- Plugin mirror re-synced after every mutation round; `sync_root_plugin_manifests`
  reports the five release scripts as the only changed export paths.
- The changed-line mutation verdict was NOT established pre-commit: the gate
  warned that five mutation-pool files had uncommitted worktree changes excluded
  from `base..HEAD`, so a clean verdict there would have been a false green. Run
  after commit, where the verdict is real, it BLOCKED on three uncovered changed
  lines — and both were guards that had never executed:
  `except OSError` around `notes_dir.glob` (`Path.glob` swallows the scandir
  error rather than raising, so an unreadable directory never reached it) and
  `_drafted_notes_for`'s invalid-adapter return (`not: a valid adapter`
  VALIDATES, because every field is optional over inferred repo defaults). Each
  had a test that passed for a reason other than the one it named. The dead guard
  was removed and the real behavior stated as a non-claim; the adapter test now
  asserts `valid is False` before exercising the branch. Re-run after that repair:
  `check-changed-line-mutation-coverage` PASSES.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: agent type `bounded-reviewer` (read-only Read/Grep/Glob),
  no host addressing name, session model inherited per the Claude Code host
  branch of the per-host subagent contract.
- Host exposure state: host-defaulted
- Application state: host resolved the typed read-only agent and inherited the
  session model; no per-subagent model/effort control was requested on this host.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — two bounded rounds, as this slice owes: both arms change what
a proof surface DECIDES at an irreversible boundary.

Round 1 ran two reviewers, one per arm, and both found real defects:

- Arm 2, blocker class: the content check ran BEFORE the pointer rule, so
  `Full changelog: <blob/main link>` — an authored one-line body — was recorded
  `unauthored` with `advisories: []`, DROPPING the mutable-pointer finding the
  audit exists to surface, under a `reason` that was affirmatively false for that
  body. Repaired by computing the advisories first and carrying them onto
  whichever record wins.
- Arm 1, false-PASS class: the version token was dotted-only and silently missed
  `2026-07-14-v1-0-7-public-notes.md`, a dash-separated shape this repo used
  three times — the v2.11.0 defect exactly, while the audit reported `passed`.
- Arm 1: the per-file remedy told an operator to `--notes-file
  v1.2.3-rc1-notes.md` for a `v1.2.3` publish — a verdict surface handing out an
  instruction it cannot support. Now one blocker naming candidates.
- Arm 1: an absolute `output_dir` (an unvalidated adapter string) made
  `relative_to` raise after the bump and the gates, stranding a publish.
- Arm 1: passing ANY `--notes-file` discharged the whole arm, so handing over
  `latest.md` satisfied the arm's own premise undetected.
- Test defects that let the above through: a test asserting exhaustiveness over
  `charness-artifacts/release/` that never read the directory (this is why the
  dash shape shipped), and a guard test that never reached its guard.

Round 2 read the REPAIRED surfaces and found that round 1's own repair had
reintroduced the escape: tightening the boilerplate URL to GitHub's
`compare`/`commits` shape sent any other host's generated body to `clean` — "no
mutable pointers found" asserted over an empty body, which is the exact verdict
the five escaped releases got. Repaired by requiring a URL without constraining
its host. Round 2 also found the new preflight arm had no test at all, that
running it before the supplied-file audit hid `notes file missing` behind "which
is none of them", and that the blocker's premise still asserted what its own
remedy called undecidable.

One further defect was found by a test rather than a reviewer, after round 2: the
fixture round 2 asked for exposed that the bounded-substring search matched
`v3-2-1-notes.md` for target `2.1`. Boundary-anchored searching kept producing a
new false match each time it was widened, so the discriminator was replaced with
token EQUALITY over the version-shaped runs in the stem — which also removes the
pre-existing single-component case (`v14` matching every `...-07-14-...` name).

Per the two-round cap, the round-2 repairs and that replacement are recorded as
accepted-unreviewed rather than opening a third round. So is the dead-guard
removal in `Executed Proof` above: it was driven by the blocking changed-line
gate rather than by a reviewer, and it is the third defect in this slice found by
running something rather than by reading it.

Reviewer boundary: round 2 snapshotted before the spawn and verified at return —
exit 0, `verdict: clean`, drift `[]`. Round 1's verification is NOT claimed: the
snapshot was taken before the spawns, but verify was run only after the parent's
repairs had already landed, so the check could not distinguish reviewer mutation
from parent mutation. All twelve drifted paths were the parent's own repair set
and no index drift was present, and the `bounded-reviewer` type exposes no write,
exec, or spawn tool — that is a structural guarantee, not the intended
observation, and it is recorded as the weaker claim it is.

Fresh-eye pass: `skills/public/release/scripts/audit_public_release_narrative.py`
— both rounds read the refusal arm against its own class; round 1 found the
false-PASS naming miss and the harmful remedy, round 2 found the premise
over-claim and the untested second call site.

Fresh-eye pass: `skills/public/release/scripts/publish_release_post_create.py` —
round 1 found the advisory-dropping ordering, round 2 found the repair's
host-pinned discriminator restoring the original `clean` escape.

## Public Skill Validation Decision

The `release` skill's routing contract, prompt surface, and adapter-facing
behavior are unchanged: no SKILL.md, reference, or adapter schema changed, and
the new refusal is silent for any repo that drafts no notes for the tag. The
change is in helper behavior consumed by the existing publish flow, and
`--notes-file` was already the documented way to supply notes. `release` carries
no dogfood scenario obligation for a helper-behavior change of this shape, so
this is recorded as an explicit decision rather than an evaluator scenario run.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-07-29-release-notes-escape-packet.json
- Packet path: charness-artifacts/critique/2026-07-29-release-notes-escape-packet.json
- Packet SHA256: 856f8dffe70e04036044661263bd9fc6d2604f575ce4d912f0c8f34594b85562
- Identity SHA256: 77d4933f7e9ea94b1fd4eaa44537bb0606c91a2c420c339fe0b7df0e1a938fe5

The binding above was rendered after all repairs landed, so it is current against
the tree. It is NOT the input either round read: both rounds were spawned with
inline prompts naming their scope rather than with a packet file, so no packet
SHA exists for round 1 or round 2. That is a gap in this slice's process, recorded
rather than papered over — the identity above establishes what the tree is now,
not what the reviewers saw.

## Boundary Ownership

- Producer: `find_drafted_notes`, which decides WHICH files are candidates for a
  tag, and `_body_says_anything`, which decides whether a published body is empty.
- Consumer: `drafted_notes_blockers` and `build_payload`, which turn candidacy
  into a publish refusal, and `published_notes_audit_lines`, which turns the body
  verdict into the durable operator-facing record.
- Owning surface: `audit_public_release_narrative.py` owns the join for arm 1 —
  it is the one place that knows both what was drafted and what was supplied, and
  the preflight defers to its helpers rather than re-deriving them.
  `publish_release_post_create.py` owns arm 2's join, because it is the only site
  that holds both the readback and the pointer rule.
- Verdict: owned-correctly
