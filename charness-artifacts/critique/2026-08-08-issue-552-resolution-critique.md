# Issue #552 resolution critique (delegated)

Classification: bug
Reviewer: delegated bounded reviewer (fresh-eye, read-only envelope: Read/Grep/Glob)
Fresh-eye context: `parent-delegated`
Envelope: bound as expected — no Bash, Edit, Write, or Agent tool exposed to this spawn
Verdict: RESOLVED WITH RESIDUAL RISK — one residual blocked the close as first drafted (F1) -> residuals repaired in-slice, ledger restated, one instance filed as `#556`

## Boundary Ownership

- Producer: `scripts/setup_skill_routing_lib.py` — sole computation of the
  `charness_managed` verdict (`skill_routing_declares_charness_management`), with
  `skill_routing_semantically_complete` and `agents_skill_routing_semantically_complete`
  layered on it.
- Consumers, all three exercised: `scripts/setup_agent_docs_lib.py:207`
  (`_detect_charness_subagent_policy`, gates the two findings), `:408`
  (`_detect_skill_routing_normalization`, gates `skill_routing_block_custom_or_drifted`),
  and `skills/public/setup/scripts/render_skill_routing.py:69` (decides `leave_as_is`).
- No consumer holds a competing copy of the routing recognizer. The repair is in the right
  place: it is in the producer, and the reader deliberately did not become a string
  comparison against the renderer, which is correct because it must keep reading
  hand-written `AGENTS.md`. No producer/consumer split to make.
- But the same file holds a SECOND notion of "is this repo charness-managed", and the
  original sweep missed it. `scripts/setup_agent_docs_lib.py:160`:
  `codex_policy_evidenced = repo_root.name == "charness" or "codex multiagent v2" in agents_text.lower()`.
  A repo-wide grep for that phrase returns exactly two hits: this line and its `plugins/`
  mirror. No template, no reference, no renderer, and not this repo's own `AGENTS.md` ever
  writes it. So `critique_adapter_codex_profile_drift` is reachable only for a repo whose
  directory is literally named `charness` — a `review_required` check whose only live
  subject is this repo, gated on a token no writer emits. That is #552's exact shape, ten
  lines above the repaired predicate.
- Owning surface: the producer module itself; the two `setup` references and the renderer
  are WRITERS of the block it reads, and each is now pinned to it by test rather than by
  agreement between authors.
- Verdict: owned-correctly — the defect and its repair both sit in the producer of the
  `charness_managed` verdict, and no consumer holds a competing copy of the routing
  recognizer. One ADJACENT managed-ness predicate in a consumer file was found unswept and
  filed as `#556` rather than folded in, because it is a different contract with a
  different owner.

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (read-only fresh-eye, `.claude/agents/bounded-reviewer.md`)
- Requested spawn fields: agent_type=bounded-reviewer, model=inherited (no per-agent
  override), one-shot spawn with no host addressing/team name
- Host exposure state: requested_fields_sent
- Delivery state: findings-received
- Application state: applied as requested; the reviewer envelope was Read/Grep/Glob only
  and structurally could not write. Worktree+index integrity was fingerprinted around this
  round with `skills/shared/scripts/reviewer_boundary_fingerprint.py`
  (window `issue552-resolution-critique`, verdict `clean`, no drift), as it was around both
  earlier slice rounds (`slice1-552-round1` clean; `slice1-552-round2` parent-attributed
  with no unattributed drift).

## Fresh-Eye Satisfaction

parent-delegated — a separate bounded-reviewer context read the committed tree with no access to the parent's
reasoning or to the two prior slice-review rounds' conversation. The two load-bearing
findings (F1, F2) were reached by reading the writer files against the reader's token set
and by reading the assertion form of the test cited as their proof — not by re-checking the
parent's list. This is not a same-agent pass.

## JTBD

An operator who runs `charness setup` on a repo needs the AGENTS.md policy checks that only
apply to charness-managed repos to actually run against the surface `setup` told them to
write. Before #552 the recognizer answered a different question — "does this block contain
the token `context-only`" — and every writer of the block said the same thing in other
words, so the answer was permanently no and two review-required findings were permanently
green.

## Findings

### F1 (BLOCKER as first drafted) — the third writer was still incomplete, and the sentence claiming otherwise was false

`skills/public/setup/references/default-surfaces.md` is the reference an agent reads when
"scaffolding or rewriting the basic docs" (`skills/public/setup/SKILL.md:78`). Mapped
against the six `all(...)` signals, its described routing paragraph named signal 2 and part
of 1 and 3, and did NOT name signal 4 (`gather` appeared **zero times in the whole file**)
or signal 5 (`quality`/validation in a routing sense). So a repo whose `## Skill Routing`
was hand-written exactly as this reference described still read as not charness-managed, and
the two findings still never fired — on a live, non-overlapping load path. Correcting signal
6 alone did not make "a repo hand-written from the shipped reference" acceptable, which is
what the draft ledger claimed it now did. The draft's premise sentence ("it enumerated five
signals") was wrong by reading.

The cited proof did not close the gap either, because the test SUPPLIED the missing tokens
itself: its reference-voice body wrote `gather` and `quality` clauses that appeared nowhere
in either reference. That is the fixture-lies-about-the-writer mechanism the closeout says
was eliminated — narrowed, not removed.

REPAIRED in-slice: the `default-surfaces.md` routing bullet now names every route the reader
requires, and the test extracts that bullet and feeds it to both readers AS WRITTEN, so the
guidance must itself be recognizable. Verified by mutating the reference three ways (drop the
`gather` clause, drop the `quality` clause, delete the standing spellings) — each fails.

### F2 (overclaim, same family) — "the same test covers both files" was an `any()`, so neither file was individually bound

The assertion was `assert any(standing in text for text in collapsed.values())` — a union
over the two files, not a per-file requirement. Since both files carried both spellings,
either file could have had its entire standing sentence deleted with the test still green.
Concrete scenario: a future slice trims `bootstrap-seams.md` as redundant, the build stays
green, and a repo bootstrapped along that load path silently reads as unmanaged again. The
identical overclaim was checked into `docs/public-skill-dogfood.json`.

REPAIRED in-slice: bound per file; deleting the standing from either file now fails, verified
by mutation. The dogfood registry line was corrected to match.

### F3 (misstatement in root_cause) — the gate in front of the ladder test's assertion was OPEN, not shut

The draft said the fixture meant "the gate in front of that test's assertion was shut and the
assertion could not fail." Inverted. If the preamble hand-wrote `context-only`, then
`charness_managed` was `True` inside that test, the gate was open, and the assertion ran and
passed — about a surface that does not exist. The committed code comment says exactly that. A
root_cause paragraph that misdescribes its own mechanism is the wrong thing to check in as
the durable diagnosis.

CORRECTED in the ledger.

### F4 (overclaim) — the parity differential was stated as a universal, contradicting the slice log's own lesson

The draft said "0 divergence against the committed baseline, so the complement of the
intended deltas is unchanged." The goal record already says why that inference does not hold:
every real routing text in this repo joins the claim with a semicolon, so the differential
was silent about the bulleted and multi-sentence shapes round 2 found broken. Corpus
agreement is evidence about the corpus.

CORRECTED in the ledger, which now carries the corpus limitation.

### Q2 — is the `Behavior #552:` channel genuinely distinct? Real, but weak; say so

Genuinely different: process boundary, `argparse` CLI invocation, YAML rendering, a real
filesystem repo, and — the increment that matters — the block was seeded from the printed
stdout of the shipped CLI rather than from an in-process return. Since #552 was precisely a
divergence between what a writer emits and what a reader requires, exercising the
emitted-bytes path is a non-trivial addition.

NOT different: both CLIs import the predicate under repair. There is no independent oracle,
so if the recognizer were semantically wrong within a segment both channels would agree
wrongly. Compared with #553's verdict, which added an execution-root difference, the draft
did not say which tree the CLIs ran from.

ADDRESSED: the verdict was re-run from a detached worktree at the closing commit, and the
ledger now states both the execution root and the absence of an independent oracle.

### Q3 — the unbound set

Bound, and bound well: the renderer against both readers from its real output; all three
call sites, each mutated independently; the composed `inspect_repo` refusal; the
`HOOK_NOUN_RE` guard (verified by reading that its test really kills the mutant); both
inflection fixes, which are writer-derived rather than fixture-derived.

Unbound, reported:

1. Signals 1, 3, 4, 5 at both reference writers — F1, live at review time. REPAIRED.
2. Each reference file individually — F2. REPAIRED.
3. `scripts/eval_setup.py:226-232` asserts five renderer snippets and NOT the hook-standing
   sentence, and never asserts `skill_routing_semantically_complete` or `charness_managed`.
   Delete the standing sentence from the renderer and this evaluator scenario stays green.
   pytest catches it, so this is single-channel coverage rather than a hole — but the
   evaluator is the surface that speaks to consumers. NOT repaired; recorded here.
4. `plugins/` mirrors are read by no test here; assumed covered by the export-sync gate,
   not verified by this reviewer.
5. Adjacent, out of class: `scripts/session_start_routing.py` `DIRECTIVE` is a fifth
   statement of the routing contract and nothing compares it to the renderer's block. No
   reader refuses it, so it is not #552 — but the owning spec says a renderer that disagrees
   with AGENTS.md is a drift bug by definition, and this pair is untested.
6. Named coupling, not a defect: the owning spec's current slice plans to INVERT this
   sentence ("this block is canonical; the hook points here"). The polarity tokens match only
   `context-only|fallback`, so the planned phrasing would be refused — but the renderer pin
   and the reference pin would both fail loudly if that inversion shipped without the reader,
   which is prevention working.

### Q5 — is the siblings ledger honest?

Three of the four claimed instances held as stated. Mis-assigned: the third writer was
claimed repaired and was only partly repaired (F1); the fourth writer's proof was the wrong
assertion (F2); and one in-class instance was missed by the sweep entirely — the
`repo_root.name == "charness"` predicate above, which belongs on the ledger or in a new
issue. All three were addressed: the first two repaired and restated, the third filed as
`#556` with its decision and proof recorded in the ledger.

### Q6 — is the debug artifact pointer adequate?

Yes, adequate. The Slice 1 premise-check entry is a real diagnosis record, not a summary: it
names the detector, the renderer, the exact executed method, the verdict sharper than the
issue's ("exactly ONE of six signals fails", with the other five enumerated), the second
gated half, and the writer-of-record. A future session can reconstruct and re-execute the
diagnosis from that text alone. A `charness-artifacts/debug/` file would add nothing; the
premise check IS the debug artifact and it is checked in ahead of the build, which is the
stronger property.

Gaps, both fixed: the record did not name the round-2 SHA, and two checked-in claims about
the same command disagreed (85 vs 86 for `run-quality.sh --read-only`) because the first run
was made against a dirty worktree, where the changed-line mutation check correctly refuses
to certify a tree it cannot analyze.

## Q7 — Verdict

RESOLVED WITH RESIDUAL RISK. The residual blocked the close as first drafted, and does not
block it after the bounded edits recorded above.

The issue's own claim is genuinely fixed and the fix is well proven for what it covers. The
repair is in the producer, all three consumers are exercised and independently mutated, the
surviving mutant was answered with a test, the composed verdict is pinned rather than only
the computing module, and both previously unreachable findings are observed firing. The
two-rejected-shapes record is the strongest thing in the closeout: the class reappearing
inside its own repair, caught and named twice.

What blocked the close was the `siblings`/`prevention` ledger, which the floor requires to
carry a decision AND proof: as drafted it claimed a repair at the third writer that the code
did not carry, and cited for the fourth writer an assertion that bound neither file. Under
this repo's rule that the floor is the authorization rather than a checklist, a sibling
asserted repaired-with-proof but not repaired is the authorization failing, not a wording
defect.

The fix-then-close path was taken: the reference now names every signal, the binding is
per-file, both are mutation-verified, the inverted root_cause sentence and the parity
overclaim are corrected, the behavioural verdict states its execution root and its lack of an
independent oracle, the 85-vs-86 discrepancy is reconciled and explained, and the missed
instance is filed as `#556`. Once the ledger says only what the tree carries, `#552` is
finished.

## Non-claims

No command was executed by this reviewer: the mutation results, the parity differential,
`run-quality.sh` exit 0, and the `pytest` count are taken as reported and are unproven by
this review, not disputed. Prior file versions were not read (`git show` unavailable in this
envelope), so claims about what the pre-fix fixtures spelled rest on committed code comments
that agree with each other. No consumer repo was read. The `plugins/` mirror's fidelity to
source is assumed covered by the export-sync gate. The eleven deferred issue numbers were not
opened. F1 and F2 are wrong-by-reading and needed no execution to confirm; F3 is a
contradiction between two checked-in texts; F4 is a contradiction between the closeout and the
goal record.
