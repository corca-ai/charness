# Verdict-timing sweep: where else can a verdict be rendered earlier?
Date: 2026-07-29

A dynamic-workflow sweep (4 lenses, every candidate put through an adversarial
verifier, 24 agents) for one pattern: **a rule is enforced somewhere, but the
author only learns it AFTER the action it would have changed.** The fix is never
a new gate — it is invoking the SAME validator earlier, or surfacing an EXISTING
verdict where it can still change the next keystroke.

## Headline

**The repo is near-saturated on this pattern.** 19 candidates, **10 refuted**, and
the most common refutation was *"already solved elsewhere"* — which is the finding,
not a disappointment. Of the 9 survivors, **0 required commit-path budget**.

Three shipped the same day (`94bd0378`, `09b004ac`, `1a1cc3b0`). Four remain and are
listed below. **This queue is finished, not an open axis — do not re-run the sweep.**

## The frame it ran against

[validator-timing-layers.md](../../docs/conventions/validator-timing-layers.md)
already owns this: five timings (author-time preflight → edit-time hook →
commit-time → bundle boundary → CI), plus four qualification criteria (cheap,
changed-scoped, deterministic, not validate-all). The sweep's job was not to
invent the pattern but to ask where the repo had drifted from its own frame.

Hard constraint the sweep was briefed on: **the commit path is already over its
own budget** — the contract states a ~1s line and records ~2.0s of full-tree AST
scans, naming its own three revisit-first items. So a recommendation to pull
something earlier had to be free or say what it displaces. Every survivor was free.

## Shipped

1. **The artifact preflight printed a PASS about a different file.** `quality` and
   `handoff` both validate-all, but `handoff`'s prefix is an exact file while
   `quality`'s is a directory — so validate-all happened to equal the target for
   handoff and hid the gap, and for quality it judged whatever the pointer aimed at
   while the author held a dated draft. Reproduced against a real artifact missing
   six required sections: it reported PASS.
2. **The closeout-draft shape omitted three floors its own validator blocks on.** A
   body filled straight from the stub failed `evaluate_behavioral_verdict` and
   `evaluate_ai_provenance` for every classification that reaches them.
3. **The timing meta-gate classified labels at birth.** `label not in region` was
   substring containment over the whole table, so `check-links`, `check-doc`,
   `validate-cautilus` and `validate-skill` all read as present from another row's
   prose. A `\b` boundary does not fix it — `-` is non-word, so it matches inside
   `check-links-internal`. First-cell tokens do. No live violation was hiding behind
   it. Folded in the same commit: `DOCS_ONLY_LABELS` must be a SUBSET of the real
   labels, because `label_is_selected` compares exact names and a renamed label
   leaves the docs-only push reporting a clean pass having run one fewer gate.

## Remaining four, in value order

1. **`check_skill_surface_preflight.py:430-444` says "split a concept or delete one"
   without naming which lines are FROZEN.** Echo the target's CORE/PACKAGE pins from
   `check_skill_contracts.py:53-63` — an in-process dict lookup, no new process. Do
   NOT add `check_skill_contracts` / `check_skill_bootstrap_vars` to `--run-checks`:
   they are repo-wide validate-all and would flip the preflight to blocked on an
   unrelated skill's state. `check_skill_cut_safety` is an after-state checker, not
   a forecast.
2. **`publish_release_resume.py:246`: resume reaches the notes preflight only after
   the ~4min gate run** and the fresh-checkout probes. Resume's most common trigger
   is a flaky gate, so a mistyped `--notes-file` costs the whole run twice. The
   non-resume path already preflights at `publish_release_execute.py:30`; this is a
   pure ordering move reusing the same helper, so the two sites cannot disagree.
3. **`check_public_doc_coupling.py` has no `--path` mode.** Add one on the
   **warnings** channel, never `blocked` — its own docstring calls the pins a
   judgment call, and blocking a judgment call teaches bypass. The residual gap is
   narrow: issue anchors under `skills/public|support/**` are already covered at
   layers 1–2, so what is actually uncovered is `skills/shared/**` anchors plus the
   self-version-pin class (`SELF_VERSION_PIN_RE`), which no preflight, hook, or
   commit gate carries. `docs/generated/**` is out of scope (fix the generator).
   Required with it, not after: `slice_closeout_advisories.py:101-131` matches
   `skills/shared/**` on neither side, and a `--path` mode nobody is told to run is
   not a briefing.
4. **The forbidden-subagent-blocker phrase is forked three ways** —
   `validate_handoff_artifact.py:118-121` (2 phrases),
   `validate_critique_artifacts.py:66-73` (6), `validate_quality_artifact.py:85-91`
   (5); only 2 are common. This violates the timing contract's own "never a forked
   rule copy per timing". **But unifying is a rule-BREADTH change, not a timing
   move**: it creates new refusals on surfaces that did not have them. Separate
   slice. No checked-in artifact hits the union today, so nothing is breaking now.

## Refuted, and worth remembering

- **The prompt-mutation blinding scan flags 12 of 12 checked-in bundles.** An
  always-true qualifier has zero detection power — a failure
  [prompt-mutation-policy.md](../../docs/prompt-mutation-policy.md) forbids in its
  own words — and its verdict contradicts the recorded human judgment. Moving a
  scanner that measures channel *presence* into a causal-judgment seat is the
  refutation, not the timing.
- **Two "the dirty pool pre-empts the verdict" findings both misread the order.**
  `check_changed_line_mutation_coverage.py` evaluates `blocking` BEFORE the
  false-green downgrade, so a blocked result still surfaces. The lesson: *"the
  sibling refuses, so this site should too"* inverts when the two sites' git state
  means different things.
- **Five findings died to "already solved."** The recurring miss was not reading
  `plan_*.py` gate_defs, and not knowing that `.agents/surfaces.json`
  `verify_commands` are executed by `run_slice_closeout.py:416` rather than being
  dead declarations.

## The structural question, answered

**Should the meta-gate's unit change from GATE to RULE?** No. Its unit is the
`run-quality.sh` label, and the 2026-07-29 miss slipped through because a *rule
inside* a correctly-classified validator was un-briefed. Widening the unit is the
"gate that checks gates" the north star names, and it would trade one hand-kept
list for two: a rule registry plus its exclusion list.

The repo already has the better answer, and it is structure, not a gate: **derive
the forecast from the same source as the refusal.** `collect_regenerable_facts`
reuses `REGENERABLE_PATTERNS`; `describe_closeout_draft_shape` renders from the
verifier's live constants and matches its HOTL vocabulary back against the real
pattern; `check_artifact_surface_preflight.describe()` runs the owning validator
rather than restating it. When forecast and refusal share a source, a missing rule
is structurally impossible — there is nothing left to police.

What the current unit *does* owe is a correct predicate, which is why the
substring fix shipped instead.
