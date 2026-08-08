# Issue #556 Resolution Critique
Date: 2026-08-08

## Decision Under Review

Resolving `#556` by replacing the `repo_root.name == "charness"` applicability
gate with a declaration a consumer can actually carry — the critique adapter
naming the profile's model on any tier, or an AGENTS.md that declares it in prose
— and measuring drift over every tier the adapter declares.

Two delegated bounded rounds ran before the close call. Both are recorded here.

## Failure Angles

- **Deleting the check instead of fixing its reach**, which the issue offers as
  one of three options.
- **Widening reach while silently narrowing coverage.** A permanent green turning
  into a narrower green is not progress.
- **Turning a green into a wolf-cry.** The issue's own class warns against gates
  that fire at repos that never opted in.
- **Circularity.** The field evidencing adoption also being the field reported as
  drifted.
- **Another dead token.** Swapping one never-emitted prose phrase for another.
- **A test that passes for an unrelated reason** — an adapter that failed to load
  produces the same green as a correctly quiet check.

## Counterweight Pass

The angle that paid was the one about my own repair, three times.

The premise held exactly as filed and needed no correction: both disjuncts do
fail for a consumer, and the prose token really was emitted by nothing. What
needed correcting was every version of the replacement.

Round 1 found that keying adoption on the model deleted coverage — a repo whose
tiers all left the profile used to fire inside this directory and no longer could
— and that my docstring had claimed other findings covered that, which is false.
It also found that measuring against the literal `high-leverage`/`medium` pair,
each defaulting to `{}`, told a consumer declaring one correct tier that it
drifted on a tier it does not have. That wolf-cry was not pre-existing: removing
the directory-name gate is what made it reachable for consumers at all.

Round 2 then found my fix for that had gone too far in the other direction — a
repo with a RENAMED tier evidences adoption and measured nothing, a permanent
green for exactly the repo shape my own docstring said was supported. The same
line, moved in opposite directions across two rounds, wrong both times. The
invariant neither version held is worth stating as the finding: the set a check
MEASURES must match the set its applicability predicate ITERATES, and when those
two live in different places they drift invisibly from either site.

Round 2 also refuted the comment I had written specifically to be HONEST about
the prose disjunct's weakness. I described the writer landscape from memory;
`skills/public/setup/references/default-surfaces.md` instructs an agent to write
exactly that profile into a repo's contract. Being about honesty is not being
checked.

Over-worry, checked and dismissed: whether the check should simply be deleted.
Its subject is real — a reviewer profile that silently drifts is what the finding
is for — and the defect was in the gate, not in the check.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/setup_critique_adapter_inspection.py:41 | action: fix | note: round 1 — keying adoption on the model made "the repo left the profile entirely" unreachable, where it fired inside this directory before. A coverage DELETION alongside the reach widening, and the docstring claimed the missing-adapter and per-host findings covered it — false, since that finding requires the adapter to be ABSENT. The non-coverage is now stated plainly, and a prose declaration makes the wholly-off-profile case reportable
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/setup_critique_adapter_inspection.py:134 | action: fix | note: round 1 — drift was measured against the literal `high-leverage`/`medium` pair, each defaulting to `{}` when absent, so a consumer declaring ONE correct tier drifted against an empty dict whose every field is `None != expected` and got a `review_required` finding naming a tier it does not have. Newly reachable for consumers precisely because the directory-name gate was removed
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/setup_critique_adapter_inspection.py:134 | action: fix | note: round 2 — the F2 repair narrowed measurement to that same literal pair's truthiness, so a repo with a RENAMED tier evidenced adoption and measured NOTHING: a permanent green for a repo shape the adoption docstring explicitly claims to support, which is this check's original defect reproduced inside its own repair. `critique_adapter_lib` only WARNS on an unknown tier name and still loads it. Measurement now reads the adapter's tiers, like adoption does
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/setup_critique_adapter_inspection.py:31 | action: fix | note: round 2 — the comment written to be honest about the prose token claimed no production writer emits it. `skills/public/setup/references/default-surfaces.md` INSTRUCTS an agent to write exactly that profile into `## Subagent Delegation`, so it is a real writer-emitted declaration. Corrected, and the live tension it exposes is recorded rather than smoothed over
- F5 | bin: act-before-ship | evidence: moderate | ref: scripts/setup_critique_adapter_inspection.py:146 | action: fix | note: round 2 advisory taken as a fix — the finding computed the offending FIELDS and then reported only tier names, so "medium left the profile" and "medium has `fork_turns: all`" read identically to an operator, and the first became newly reportable in this same slice. The message names the fields and their actual values now
- F6 | bin: act-before-ship | evidence: moderate | ref: tests/quality_gates/test_setup_inspect_critique_adapter.py:487 | action: fix | note: round 2 advisory taken as a fix — two of the greens added in round 1 asserted absence without asserting the adapter had LOADED, so an unparseable adapter would produce the same pass. Round 1 had raised this for the earlier tests and I applied it only there
- F7 | bin: act-before-ship | evidence: moderate | ref: scripts/setup_critique_adapter_inspection.py:141 | action: fix | note: found mid-round while repairing F1 — excluding `model` from the measured fields on a circularity worry silently dropped the MIXED case (one tier on the profile, another off it), which is the shape a repo reaches by upgrading one tier and forgetting the other. A tier naming the model is by definition not drifted on it, so including the field costs that tier nothing
- F8 | bin: valid-but-defer | evidence: strong | ref: skills/public/setup/references/default-surfaces.md:83 | action: document | note: a live two-spellings tension this slice surfaced rather than created — the setup RENDERER is gated against baking a model id into the contract while this reference instructs an agent to write exactly that profile, so an agent following the reference produces an AGENTS.md the same inspector can flag. Recorded in the module where the predicate reads it; resolving it is a setup-contract decision with its own owner
- F9 | bin: over-worry | evidence: strong | ref: scripts/setup_agent_docs_lib.py | action: document | note: feared the module split would scatter the subject. The boundary is a real concept split — what the adapter declares and whether it matches, versus what the AGENTS.md prose surfaces say — and it was forced by a length cap that has now named two modules wanting splitting in one session
- F10 | bin: over-worry | evidence: strong | ref: scripts/setup_critique_adapter_inspection.py:103 | action: document | note: feared deleting the check was the right call, as the issue's third option suggests. The subject is real and the defect was in the gate; the two-ended construction proof (fires for a consumer, silent for a repo on another model) is what makes keeping it defensible

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded reviewer (`bounded-reviewer` typed agent), two spawns — a review of the implementation, then a second round reading that review's repairs.
- Requested spawn fields: subagent_type `bounded-reviewer`, no host addressing name, read-only toolset (Read/Grep/Glob).
- Host exposure state: host-defaulted
- Application state: host-confirmed: both spawns returned findings inline and each reported the read-only envelope bound, with no Bash, Edit, Write, or Agent tool visible.
- Delivery state: findings-received

Per-host note: Claude Code host, so the repo's Codex-only `gpt-5.6-terra`/`medium`
request does not apply; typed `bounded-reviewer` agents were used instead.

## Fresh-Eye Satisfaction

`parent-delegated`. Two bounded reviewers in distinct contexts, each
boundary-fingerprinted with `reviewer_boundary_fingerprint.py` snapshot/verify —
windows `w-20260808T065638Z-3952955` and `w-20260808T070208Z-3963158`, both
verifying `clean` with empty drift, and both verified the moment the reviewer
returned, before any repair.

Four blockers, all in repairs, and the pair F2/F3 is the sharpest result this
slice produced: the same line moved in opposite directions across two rounds and
was wrong both times, which is stronger evidence for the two-round rule than any
single finding. Eight mutants were killed across the build and both repair sets;
none of the four blockers was among what they could reach.

The cap is two rounds, so round 2's repairs (F3-F6 and the pins over them) are
recorded as accepted-unreviewed.

## Reviewed Input Identity

<!-- No packet consumed: this critique binds to the issue body, the working tree at review time, the two reviewer reports cited inline, and the constructed repo shapes executed before and after each repair. -->

## Boundary Ownership

- Producer: a repo's `.agents/critique-adapter.yaml` and its `AGENTS.md` — the two surfaces on which a repo declares the reviewer profile it runs.
- Consumer: `setup`'s repo inspection, which turns those declarations into `review_required` findings an operator acts on.
- Owning surface: `scripts/setup_critique_adapter_inspection.py` for the applicability predicate and the drift measurement. The renderer-versus-reference spelling split is `setup`'s contract question and is not decided here.
- Verdict: owned-correctly
