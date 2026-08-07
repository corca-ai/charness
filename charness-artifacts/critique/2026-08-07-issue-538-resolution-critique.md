# Issue #538 Resolution Critique
Date: 2026-08-07

## Decision Under Review

Resolving `#538` by repairing `quality/SKILL.md` step 8 to name
`resolve_quality_artifact.py` where it instructs that script's flag and keys, and
pinning the repair with three tests — while explicitly DECLINING to build the
repo-wide doc-to-helper gate the causal review recommended.

## Failure Angles

- **Fixing the sentence, not the reason it was writable.** A doc patch over a
  payload-shape problem leaves the next doc free to drift the same way.
- **The doc-only fix under-serves the reporter** if the step is still ambiguous
  after three scripts are named in it.
- **A new claim in the prose being itself wrong.** Replacing an understatement
  with an overstatement is no better.
- **Presence-only tests.** Assertions that a step CONTAINS the right tokens are
  satisfied by a step that says the opposite.
- **Refusing a gate for a bad reason.** Skipping a floor is defensible; skipping
  it on a measurement that does not test the proposal is not.

## Counterweight Pass

The angle that mattered most was the one about my own reasoning. I prototyped the
causal review's proposed gate, measured 25 fires for ~2 real defects, and was
ready to record noise as the reason for skipping it. The resolution critique
showed that prototype was **weaker than the proposal**: it attributed flags from
`git status --short` and `rg --files` to the nearest `.py` script (the proposal
excluded spans that already carry a command), and it probed only top-level
`--help` (the host gate already ships subparser resolution I did not reuse). So
the number is not evidence about the proposed gate, and I do not record it as if
it were.

The gate is still correctly skipped, for a reason that survives: it probes
`--help`, which says nothing about payload key SEMANTICS. `#538` has a loud half
(a rejected flag, exit 2) and a silent half (a key whose value is a destructive
path). Even the strongest version of that gate catches only the loud half and
misses the entire severity. A new blocking floor that prevents none of the harm
fails this repo's floor-addition restraint, at a measured drift rate of one real
instance in seventeen public skills.

Over-worry, checked and dismissed: three scripts in one step reads as clarifying
rather than confusing — each has one job and is named where its job happens.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/SKILL.md:76 | action: fix | note: "the scaffold does not choose one" was literally false — the scaffold does emit `write_artifact_path` — so a skimmer who checked the payload would have concluded the doc was stale and reproduced the bug; reworded to say what the key IS
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/SKILL.md:83 | action: fix | note: the warning described only the symlink layout; where `latest.md` is a regular file the payload returns `latest.md` itself, so a consumer-repo agent could read the warning as not applying — now names both layouts
- F3 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_skill_docs.py:440 | action: fix | note: both original tests were presence-only, so a compaction that FLIPS the instruction while keeping every token passed them; added a polarity test binding the scaffold clause to a prohibition and the write clause to the resolver, and killed the exact flipped-instruction regression with it
- F4 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/SKILL.md:79 | action: fix | note: `write_artifact_path` appeared with two different referents four lines apart, which is the ambiguity class this issue is about; the resolver's is now "the path it returns as `write_artifact_path`"
- F5 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/scripts/scaffold_quality_artifact.py | action: file-issue | note: the payload-level cause — quality's scaffold and debug's scaffold both publish `write_artifact_path` and only debug's is safe to write to, so the two skills correctly give opposite instructions about identically-named keys; that collision is what made step 8's sentence writable | follow-up: https://github.com/corca-ai/charness/issues/548
- F6 | bin: over-worry | evidence: strong | ref: scripts/check_documented_command_flags.py:80 | action: document | note: feared the fix left the flag half ungated; moving `--intent record` into the same backtick span as `resolve_quality_artifact.py` pulled it under the EXISTING gate for free — a rename or a dropped flag now reds without any new floor
- F7 | bin: over-worry | evidence: moderate | ref: skills/public/setup/SKILL.md:148 | action: document | note: `normalization.findings` looked like a sibling defect; `recommendations[]` beside it has no producer either, and both are the agent's own report vocabulary rather than a helper payload read — filing would be a false positive, recorded as a typography trap instead
- F8 | bin: over-worry | evidence: strong | ref: skills/public/debug/SKILL.md:46 | action: document | note: debug's "Edit the scaffold payload's `write_artifact_path`" looked like the same bug; debug's scaffold resolves a fresh dated record and rejects any candidate equal to the current pointer, so it earns the instruction

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded reviewer (`bounded-reviewer` typed agent), two spawns — causal review before design, resolution critique on the implementation.
- Requested spawn fields: subagent_type `bounded-reviewer`, no host addressing name, read-only toolset (Read/Grep/Glob).
- Host exposure state: host-defaulted
- Application state: host-confirmed: both spawns returned findings inline and each reported the read-only envelope bound, with no Bash, Edit, Write, or Agent tool visible.
- Delivery state: findings-received

Per-host note: Claude Code host, so the repo's Codex-only `gpt-5.6-terra`/`medium`
request does not apply; typed `bounded-reviewer` agents were used instead.

## Fresh-Eye Satisfaction

`parent-delegated`. Two bounded reviewers in distinct contexts, each
boundary-fingerprinted with `reviewer_boundary_fingerprint.py` snapshot/verify —
windows `w-20260807T075344Z-1442529` and `w-20260807T080612Z-1466598`, both
verifying `clean` with empty drift.

The causal review found the severity the ISSUE missed (a silent overwrite, not a
loud argparse error). The resolution critique found the severity MY FIX missed
(presence-only tests that a polarity flip would pass) and corrected my stated
reason for skipping the gate. Both rounds changed the outcome.

## Reviewed Input Identity

<!-- No packet consumed: this critique binds to the issue body, the working tree at review time, and the two reviewer reports, all cited inline above. -->

## Boundary Ownership

- Producer: `scaffold_quality_artifact.py` and `resolve_quality_artifact.py`, which emit the artifact contract and the write target respectively.
- Consumer: the agent executing `quality` step 8, which turns those payloads into a file write.
- Owning surface: `skills/public/quality/SKILL.md` for the instruction; the scaffold payload key name for the underlying collision, which is `#548`'s and is not fixed here.
- Verdict: owned-correctly
