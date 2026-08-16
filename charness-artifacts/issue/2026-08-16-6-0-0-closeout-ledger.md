Classification: bug

Jtbd: a maintainer or consuming repo can run the gates, bootstrap the lesson
lifecycle, and read a repo-owned instruction that does what it says — without
first discovering that the fix exists only in an unreleased tree. For every issue
here the repair landed in-repo and was stranded behind the publish. For four of
the ten the repair is NARROWER than the issue's title or its stated expected
behavior, and each of those closes on what shipped rather than on the class.
#618 was a fifth until its residual was repaired between preparation and publish;
it is kept in the list below because this ledger's own claim about it CHANGED, and
a reader of a close comment deserves to see which way:

- **#618** — the rooting defect is fixed and the gate stopped measuring a narrower
  tree. The residual this ledger first recorded as unfixed — a reference pointing
  consuming repos at an exported `check-links-internal.sh` that refuses inside a
  consumer repo — is now repaired too: the reference names the runnable half and
  the environment variable that retargets the other, and the refusal text names
  the reader's own repo root rather than the charness checkout. This entry is the
  one narrowing in the cohort that CLOSED between preparation and publish.
- **#619** — both reported instances are repaired and `charness init` runs clean.
  NOT closed as a class: the carrier scan covers markdown, `.agents/` configs and
  Python argv, while shell scripts and workflow `run:` steps are unscanned, so a
  flag deletion can still break the broad gate and CI with
  `check-documented-command-flags` green.
- **#620** — the overwrite is PREVENTED across families by subject identity and
  DETECTED only in the quality family; a date-incoherent `debug` record still
  validates clean. The issue asked for the check over every dated artifact. That
  is not what shipped, and widening a validator inside a release slice was
  declined rather than forgotten.
- **#626** — the title scope is delivered and shown by execution: the lifecycle
  review emits runnable commands, `record_lesson_lifecycle.py --action archive`
  writes `state: archived`, and the preview's archive bucket then fills. NOT
  closed: the issue's own post-graduation-compaction section —
  `apply_contract_transition.py` writes no lifecycle event, so a graduated lesson
  stays `active` against the budget.
- **#627** — the SIGNAL half is delivered and live rather than theoretical. NOT
  delivered: nothing rewrites a lesson's wording; `rewrite-in-place` is a
  disposition addressed to a human, so the title's second clause remains literally
  true.

Three further residuals, disclosed rather than repaired: #625's seeder is not
re-prompted after a cold start and its file mode differs from its sibling's, and
#623 leaves a consuming repo reading a literal `<authoring-repo>` placeholder in
the scaffold's North Star section.

Root cause: the shared cause across the cohort is a proof surface that reports a
verdict about something it cannot actually see, plus the export boundary that
kept each repair from reaching a consumer. Concretely: a shell gate rooted at
the exported plugin copy instead of the git root (#618); a caller migrated to a
flag its producer no longer accepts (#619); a scaffold resolving a write path
onto a record belonging to a different subject (#620); a lifecycle whose ledger
had no creation command and whose transitions had no seeding command, so the
whole loop was unreachable from a clean repo (#621, #625); probes returning
`triggered: false` for runs that never happened, so every failure mode failed
toward silence (#622); a scaffold emitting an artifact its own validator rejects
(#623); a drift message instructing edits to surfaces #596 had superseded (#624);
a lifecycle-review surface with no production caller, so `state: archived` could
never be written (#626); and a lesson-evaluation loop that recorded no signal
when a lesson was read and failed to transfer (#627).

Debug artifact: the reproductions for eight of the ten were re-executed against
this tree before closing rather than read off the earlier closeout comments, which
is what caught that several of those comments are now stale in the CONSERVATIVE
direction — #626's says the archive disposition is absent, and running
`record_lesson_lifecycle.py --action archive` followed by
`render_lesson_selection_preview.py` shows the bucket filling. Stated exactly,
because a first draft of this paragraph claimed all ten: #622 and #624 have no
fresh reproduction in this slice, and their verdicts rest on the earlier cohort
review plus the repairs this slice made to their surfaces. The durable records are
`charness-artifacts/debug/2026-08-14-issue-cohort-618-624-causal-analysis.md` (the
cohort's causal analysis, whose `## Observed Facts` is the direct evidence for the
#619 and #622 root-cause clauses above),
`charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md` (this
release's execution critique, carrying the per-issue premise verdicts as F23-F27
and F27b-F27d), and
`charness-artifacts/critique/2026-08-14-issue-618-628-closeout.md` (the earlier
cohort closeout review, whose F10 and F11 first recorded two of the narrowings
carried forward here, and whose F13 recorded the #618 residual this slice
REPAIRED rather than carried; #627's rewrite half was first recorded in that
review's cohort-B failure angle, and #626's post-graduation compaction section
was NOT — that angle records #626's resurrection slot, which this slice
delivered, and the compaction remainder was first recorded as F25 of this
release's own execution critique).

Siblings: decision — the transferable class is "a repo-owned surface renders a
verdict about a thing it cannot observe", and it was scanned across the gate,
probe, scaffold, and lesson-loop families rather than only at the reported
sites. Proof — the scan was a REVIEWER scan with no executable carrier, and that
is stated plainly because no gate detects this class and claiming one would be an
instance of the class. Its output is the four siblings below, each reproduced and
repaired in this slice. The one adjacent scan that IS executable and checked in
measures a different, narrower thing and is recorded as a separate fact rather
than as proof of the class scan: `scripts/check_closeout_classification_parity.py`
judges vocabulary AGREEMENT across population: 6; removed: 0 sites, with no copy
deleted to reach agreement. Four siblings, found by this release's own reviewers
and repaired here rather than filed:
`scripts/check_doc_authoring_preflight.py` (a docstring claiming to mirror
`check-markdown.sh` while skipping its guard), `scripts/argparse_surface_lib.py`
(a splitter blind to quoting, the second instance of a class already repaired in
the dominance detector), `tests/quality_gates/test_markdown_lint_resolution.py`
(a guard whose docstring claimed a reach its implementation did not have), and
`scripts/render_lesson_lifecycle_review.py` (an instruction naming a file whose
edit changes nothing a reader sees).

Prevention: the class now has executable carriers rather than prose. The
npm-registry guard is a discovery scan over `scripts/**` in both languages
instead of a hardcoded filename pair, and it was shown red on the pre-fix
spelling before being accepted. The documented-flag gate reads quoting, so a
command carried inside another command's flag value no longer steals its flags.
The retro trigger text and its reference now name the undetermined state, which
is the half of #622 that shipped repaired in `prove` and unrepaired in `retro`.
The lesson-lifecycle disposition names the path whose edit is observable. What
is NOT prevented, stated rather than implied away: the registry behind the cost
gate is authored memory, not measurement, and every gate above is a denylist or
an enumeration whose false negatives are real.

AI-provenance: authored by Claude (Opus 5) operating the charness `release` and
`issue` skills, under a maintainer's explicit session grant to publish and close.
Every verdict cited here was produced by executing the named command in this
worktree; the premise verdicts for eight of the ten were produced by read-only
premise reviewer agents that ran each issue's own reproduction, and #622 and
#624 rest on the earlier cohort review as stated above.

Critique #618 #619 #620 #621 #622 #623 #624 #625 #626 #627: charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md

Closeout targets: #618 #619 #620 #621 #622 #623 #624 #625 #626 #627

Carrier derivation, stated because this file is deliberately NOT a close carrier
as committed. The close keywords are appended when the release CLI is handed this
body, never earlier: a `Closes #N` line inside a staged
`charness-artifacts/issue/*.md` makes the committing change a closeout carrier,
and this commit is the release PREPARATION, whose branch push must not auto-close
anything. `scripts/check_issue_closeout_commit_msg.py` refuses that shape and its
first-listed remedy is exactly this rewrite. Derive the carrier immediately before
`--execute`, and re-validate it before use:

```bash
{ cat charness-artifacts/issue/2026-08-16-6-0-0-closeout-ledger.md
  for n in 618 619 620 621 622 623 624 625 626 627; do echo "Closes #$n"; done
} > /tmp/6-0-0-closeout-carrier.md
```
