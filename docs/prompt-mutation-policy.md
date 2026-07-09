# Prompt Mutation Policy

Owner surface for the prompt-surface mutation pipeline: what its verdicts
mean, what they may and may not authorize, and the gates between a survival
observation and any change to shipped prompt prose. The pilot that grounded
this policy is
[2026-07-09-prompt-mutation-pilot.md](../charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md).

## What The Pipeline Is

A **ranking and scenario-coverage detector, never a deletion prover**. It
splits a skill's installed-plugin prompt surface
(`plugins/charness/skills/<skill>/**` — the tree captures actually resolve)
into section-level mutation units, and asks two questions:

1. Statically (zero capture cost): which units have a **deterministic
   witness** — an eval floor or behavior-trace marker that would fire
   differently if the unit were removed, with a written causal-path
   rationale? Everything else is `UNTESTED`, and the `UNTESTED` list is the
   pipeline's primary product: scenario-coverage debt, i.e. skill-contract
   clauses no capture scenario currently observes.
2. Live (bounded capture cost): for witnessed units only, does a real
   captured run at a unit-removed mutant ref still fire every witness?

Tooling:
[generate_prompt_mutants.py](../scripts/generate_prompt_mutants.py) (units +
mutant refs), [witness_coverage.py](../scripts/witness_coverage.py) (static
verdicts), [run_skill_efficiency_ab.py](../scripts/run_skill_efficiency_ab.py)
(ref-armed captures), and
[score_prompt_mutation_survival.py](../scripts/score_prompt_mutation_survival.py)
(survival verdicts).

## Verdict Semantics

- `UNTESTED` — no deterministic causally-rationalized witness exists. This is
  a **missing-scenario signal first** and a compaction candidate never:
  removing an untested unit is unmeasured risk, not proven deadness. The
  correct response is a witness (new assertion, trace marker, or scenario),
  or an explicit `excluded` disposition with reason.
- `DETECTED` — a witness failed to fire in at least one mutant run. The unit
  is load-bearing for the observed scenario; keep it.
- `NO-OBSERVED-EFFECT` — every witness fired in every mutant run
  (survival rate reported per run, never a binary deadness claim). This
  ranks the unit as a **demotion candidate**; it proves nothing about
  scenarios, hosts, or judge-observed behavior outside the battery.
- `INVALID-FOR-VERDICT` — the arm finished with fewer than 2 valid runs; no
  rate is reported.
- `EXPERIMENT-INVALID` — a mutant unit's witness did not fire in every
  baseline run. A baseline whose witness never fires cannot detect anything,
  so no mutant verdicts are emitted at all.

## What Survival May Authorize: Demote, Never Delete

`NO-OBSERVED-EFFECT` authorizes at most a **demotion proposal**: moving the
unit from the always-loaded core (`SKILL.md`) to a progressive-disclosure
reference file. A demoted unit still exists and is loadable, so a wrong
survival verdict costs one re-promotion commit, not a silent capability
loss. Physical deletion is a separate, later decision gated by all of:

1. the unit was demoted (not deleted) in an accepted batch;
2. a real-usage observation window passed with **tripwire silence** — no
   retro repeat-trap, eval regression, or operator correction traceable to
   the demoted content;
3. a fresh-eye review confirms the deletion with a different evidence
   channel than the original survival run (north star: at irreversible
   boundaries, confirm with a different observer and a different channel).

## Ship-Configuration Integrated Rerun

Per-unit mutant runs rank candidates; they do not test interactions
(units A and B individually survivable can be jointly load-bearing). Before
any demotion batch ships, the **final post-demotion state — all batch edits
applied together — runs the same capture battery once** and must keep every
baseline witness firing. The combinatorial space is irrelevant: the only
configuration that must be proven is the one that ships.

## Batch Ratchet

- At most **k demotions per cycle** (default k=2) per skill.
- A real-usage window between batches; tripwires from that window gate the
  next batch.
- Any re-promotion resets the ratchet for that skill.

## Experiment-Integrity Floors

Learned in the pilot and binding on every future run:

- **Mutate the resolved tree.** Captures resolve the installed-plugin
  mirror; a mutant touching only `skills/public/**` silently tests the
  unmutated skill (pilot plan-critique F1).
- **Blind the run.** Neutral uniform mutant commit messages, digest-only ref
  leaves, baseline committer date, and a baseline ref whose tree does not
  contain the experiment's own blueprint (witness map, goal artifact,
  pipeline commit messages) — a faithful run reads recent history and would
  recover the expected tokens from them (#423-class leaks).
- **Red-team the observer once, up front.** Before a new capture-experiment
  design ships, enumerate in one pass every channel the captured agent can
  observe — cwd and env paths, `git log`/`diff`/`show`, refs and reflog,
  sibling and parent files, commit metadata — and neutralize or disclose
  each. The pilot patched blinding three times because channels were
  discovered iteratively; the diff-against-parent channel that 4/6 mutant
  runs used was derivable up front from "handoff runs do git ops".
- **Causality, not channel existence.** A witness counts only with a written
  causal path from the unit to the signal; run-level sanity assertions that
  fire on any packet have zero detection power (pilot plan-critique F2).
- **Same-scenario baseline.** A mutant arm is interpretable only against a
  baseline of the same scenario, valid in **all** baseline runs.
- **Budget honesty.** Capture budgets are declared up front; failures consume
  the budget; N=1 arms report `INVALID-FOR-VERDICT`; small-N survival rates
  carry explicit caveats.
- **No gate.** The pipeline is advisory tooling (floor-addition-restraint);
  it never blocks commits or CI.

## Known Channel Caveats

- RCF (required-command-fragment) floors prove file-*open* only; they never
  witness sections inside a reference body, and they are survival-biased
  when the fragment string appears in multiple prose surfaces — pair them
  with a sharper trace marker where possible.
- `trace-digest.jsonl` truncates command args at 160 chars; keep
  `stream.jsonl` available at scoring time (`--keep-runs`, copy into the
  bundles) as the untruncated fallback for trace markers. Before dropping
  streams from committed evidence, re-score without them: if any fire
  pattern differs, either commit the stream that carried the difference or
  withdraw the stream-only fire (a stream match can be a mention, not an
  execution — the pilot hit exactly this).
- Commit-diff unblinding: a captured run can `git show` the mutant snapshot
  commit and read the removed section verbatim (observed in 4 of 6 pilot
  mutant runs). Neutral messages are necessary but not sufficient; prefer
  symmetric parentless snapshot commits for **all** arms, baseline included,
  so no arm has a diffable history.
- Judge-kind witnesses are modeled in the witness-map schema but spend
  evaluator budget; they follow the repo cautilus ask-before-run contract
  and never contribute to deterministic survival verdicts.
