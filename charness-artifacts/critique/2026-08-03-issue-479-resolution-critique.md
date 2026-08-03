# Issue 479 resolution critique
Date: 2026-08-03

## Decision Under Review

Whether [#479](https://github.com/corca-ai/charness/issues/479) — *shipped prose
names files a consumer cannot reach* — is genuinely resolved, or is a fourth
narrow zero. The reporter's job-to-be-done: **"a future enumeration of this class
starts from a real zero rather than a measured-with-the-wrong-ruler zero."**

## Failure Angles

- The four axes were repaired and gated, but the DURABLE RECORD a future
  enumerator reads could still misstate the ruler — which is the failure mode the
  issue is about, not the residue.
- The armed gates cover markdown backtick tokens and relative links. Carriers the
  gates never read (commands, non-markdown assets) could hold the same defect.
- `skills/shared/**` ships but is not a portable package, so the rules may be
  structurally off there.
- A "verified" behaviour verdict rendered by re-reading a gate's own green would
  be the same-proxy re-read the contract forbids.

## Counterweight Pass

**Real blockers, both folded.** The reviewer refused the close on the record, not
on the repairs: the sweep artifact's own arming table said A3 "not gated" and A4
"not gated, 29 live" after both had been armed and their sites repaired. That is
the fourth honest zero, produced inside the artifact built to prevent it, one
axis over from the A2 instance a claims review had already caught. And three
in-class axes had no ruler and no record.

**Not over-worry, and worth naming as such:** the reviewer verified the repairs
independently before refusing. Two `<plugin-dir>/` references were hand-read from
the consumer's position and both resolve; the gate fixtures were confirmed to be
transcribed from real historical instances rather than invented; both new gates
report what they skipped on the pass and refusal paths. The refusal was scoped to
the denominator record, which is exactly where the issue's reusable finding lives.

**Genuine over-worry, not folded:** `PATHY_TOKEN_RE`'s directory blindness
(`charness-artifacts/`, `docs/specs/` are invisible). A bare directory name makes
no single-file reachability claim, and the `./`-prefixed directory form is already
resolved. Recorded in the sweep's bounds rather than treated as residue.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/audit/2026-08-04-unreachable-file-denominator-sweep.md | action: fix | note: the arming table said A3/A4 ungated after both were armed and repaired, so a future enumerator starts from a wrong ruler — the exact failure #479 exists to stop, inside the artifact built to prevent it
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/critique/references/prepare-packet.md:23 | action: file-issue | note: 14 shipped docs name `skills/<kind>/…` in COMMAND carrier, which every armed gate is green on (whitespace kills the backtick candidate; the command resolver checks the authoring tree) — the most action-bearing spelling, since a consumer executes it | follow-up: https://github.com/corca-ai/charness/issues/482
- F3 | bin: act-before-ship | evidence: strong | ref: plugins/charness/skills/achieve/adapter.example.yaml:9 | action: file-issue | note: every gate globs `*.md`, so shipped `.json`/`.yaml` assets were never enumerated; the adapter template is worse than prose because a consumer copies it into their own config and runs it | follow-up: https://github.com/corca-ai/charness/issues/483
- F4 | bin: bundle-anyway | evidence: moderate | ref: scripts/check_doc_links.py | action: file-issue | note: `PORTABLE_SKILL_KINDS = {"public","support"}` leaves `skills/shared/**` — 18 shipped files — with the unmarked-tree, portable-absolute, and portable-escape rules all structurally off; prevention gap first, residue second | follow-up: https://github.com/corca-ai/charness/issues/484
- F5 | bin: over-worry | evidence: moderate | ref: scripts/check_doc_links.py | action: defer | note: `PATHY_TOKEN_RE` requires an extension-bearing tail, so directory tokens are invisible; a bare directory makes no single-file reachability claim, so this is a stated bound rather than residue

## Reviewer Tier Evidence

- Requested tier: n/a — Claude Code host. Per `AGENTS.md` `## Subagent Delegation` the per-host split says to use the host's own controls here (typed `bounded-reviewer`, session-model inheritance) and NOT to request the Codex model/effort pair.
- Requested spawn fields: `subagent_type: bounded-reviewer` (read-only Read/Grep/Glob), no host addressing or team `name` (the #458 spawn-shape rule), `run_in_background: false` so findings return to the parent.
- Host exposure state: applied
- Application state: host-confirmed: the spawn returned a full findings report inline and the envelope bound held — the reviewer reported having only Read/Grep/Glob and listed the `git` evidence it could not fetch instead of asserting it.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — the resolution critique ran in a separate bounded
`bounded-reviewer` context that had not produced the fix.
`reviewer_boundary_fingerprint.py` snapshot/verify around it returned
`ok: true, verdict: clean, drift: []`.

## Boundary Ownership

- Producer: this goal's run — it produced the four axes' repairs, the three gates,
  and the denominator record a future enumeration would start from.
- Consumer: the next session enumerating this class, and any consumer following a
  reference in a shipped skill doc.
- Owning surface: the measurement artifact
  (`charness-artifacts/audit/`) for the denominator, and `check_doc_links.py` /
  `check_plugin_doc_links.py` / `check_plugin_dir_references.py` for the rules.
- Verdict: escalated-to-issue-spec

## Behaviour Verdict

**Repairs: verified, on two channels independent of the gates' green and of the
`CLOSED` state.**

1. **Consumer-position hand read** by the reviewer:
   `plugins/charness/support/README.md:26` now names
   `<plugin-dir>/scripts/sync_support.py`, which resolves to a file that exists
   (it previously named `../../scripts/sync_support.py`, resolving to
   `plugins/scripts/`, which exists in no tree); and
   `plugins/charness/shared/references/agent-assessment-invariant.md:31` now
   names `<plugin-dir>/skills/hitl/scripts/check_chunk_contract.py`, which
   exists (it previously carried the kind-flattening miss).
2. **An independent agent**, given only an installed-layout tree and no access to
   the resolution doc, resolved a repaired `<plugin-dir>/` reference to the
   correct concrete path and, as a negative control, refused the
   `skills/public/…` spelling and diagnosed the stale kind segment
   (`docs/deferred-decisions.md` D50; bounded to one host, one model, two prompts).

**JTBD at the time of review: REFUTED, and that refusal is what this critique is
for.** The reviewer did what a future enumerator would do — read the sweep
artifact and the handoff as its starting point — and both handed it a wrong
picture of the ruler. Running the enumeration off the tree instead of the record
then found 16 live in-class instances the record did not name.

**JTBD after the folded repairs: met.** The arming table now states what shipped,
carries the three unruled axes with their rulers and counts, and records that it
was wrong in the false-zero direction. F2/F3/F4 are filed as #482/#483/#484.

**Honest bound on that last paragraph:** the record repair was made by the parent
AFTER this critique returned, so it is accepted-unreviewed under the two-round
cap. What a third observer has NOT confirmed is that the corrected record is
itself complete.

Behavior: verified — consumer-position hand read of two repaired references in
`plugins/charness/**` by a distinct observer, plus an independent agent resolving
a repaired reference and refusing a broken one on an installed-layout-only tree.
