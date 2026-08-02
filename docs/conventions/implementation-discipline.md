# Implementation Discipline

This document owns the validation and mutation rules that are too detailed for
the root instruction file but still apply to Charness maintenance work.

## Validation Discipline

- Repo-owned diff obligations live in [.agents/surfaces.json](../../.agents/surfaces.json);
  use `python3 scripts/check_changed_surfaces.py --repo-root .` to inspect them.
- The full `run_slice_closeout.py` runs the cheap structural sweep FIRST
  (`staged_commit_gate_plan` subset: `validate_skill_ergonomics`,
  `validate_attention_state_visibility`, the `SKILL.md` authoring preflight),
  fail-fast, before surface-match / cautilus / broad pytest. A #329-class
  regression therefore blocks at the cheap boundary in <1s instead of deferring
  to the slow gate (#332). A `structural-sweep` failure phase in closeout output
  means a cheap presence/structural gate fired; fix it before rerunning.
- Run `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
  as a pre-lock rehearsal when the slice spans generated surfaces or multiple
  validator families. Before the final broad closeout, record that the mutation
  set is locked and rerun with `--verification-lock`; a broad closeout without
  either flag must refuse before launching broad pytest. The runner prints a
  broad-pytest policy mode and recommendation when broad pytest is selected or
  skipped. Under `--verification-lock`, broad pytest proof is cached by locked
  diff fingerprint under `.charness/closeout/`; the fingerprint includes `HEAD`,
  the changed-path diff, staged diff, and file bytes, so any later file content,
  staging, or base-commit change intentionally invalidates the cached broad
  proof. The same locked diff reuses the cached proof, while a changed
  fingerprint blocks until the operator reruns with
  `--refresh-broad-pytest-proof`. Record focused current-diff proof for pre-lock
  slices rather than treating the skipped broad run as final evidence.
- When a slice changes eligible mutation-pool Python files, add
  `--produce-mutation-coverage` to the final `--verification-lock` closeout. By
  default, it instruments that one broad pytest run with plain coverage (no
  double run) and emits `reports/mutation/test-coverage.json` plus the
  `.fingerprint` freshness marker. Since D40 the pre-push lane
  (`check-changed-line-mutation-coverage`) no longer reuses that artifact: it
  PRODUCES its own incremental coverage from the standing tests the mapper resolves
  for the changed pool files, writes it to `reports/mutation/prepush-focused-coverage.json`
  so subset coverage never sits at the broad producer's path carrying a valid
  freshness marker, and BLOCKS on uncovered changed lines in the mapped files. The
  closeout producer remains the broad proof. When the changed pool has an
  honest focused pytest proof, prefer a focused producer command alongside
  `--produce-mutation-coverage`; for example,
  `--mutation-coverage-command "python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_x.py"`.
  This focused form retains the standing runner's bounded xdist parallelism and
  external temp isolation while replacing its broad target set. Use
  `python3 scripts/suggest_mutation_coverage_command.py --repo-root .`
  to find a focused producer command from changed mutation-pool files and their
  standing-test references before falling back to the broad producer.
  The broad pytest proof stays on the normal closeout/cache path, and only the
  focused command is instrumented for the freshness marker. Without a fresh
  producer run the gate skips non-blocking, so run the producer before a
  pool-touching push to keep the gate active. To check your own uncommitted slice
  when the standing runner is nearly enough but missed one focused node, append
  it with `--mutation-coverage-extra-pytest-target tests/path.py::test_name`
  instead of shell-chaining commands inside `--mutation-coverage-command`.
  [run_standing_pytest.py](../../scripts/run_standing_pytest.py) accepts
  `--pytest-target` to replace the standing set and `--extra-pytest-target` to
  append to it; both feed `--print-expanded-targets` diagnostics.
  To check your own uncommitted slice early, run the producer (it stamps the
  marker over base->worktree) then the
  consumer, or run the consumer over a head that includes the worktree — a manual
  `--head-sha HEAD` dry-run **before commit** is a false green (HEAD is the
  parent, so `base..HEAD` excludes your changes and they are judged only
  post-commit). The consumer now **warns** (non-blocking `warning` field +
  stderr) when the analyzed head resolves to `HEAD` and an eligible mutation-pool
  file has uncommitted worktree changes, so this trap is surfaced instead of
  silently passing (handoff-4). Also run the cheap doc gates the broad pytest
  enforces, such as `python3 scripts/check_spec_evidence_durability.py`, before
  paying for the producer run (see the
  [producer-rerun retro](../../charness-artifacts/retro/2026-06-07-producer-rerun-waste.md)).
- When a slice adds a `run-quality.sh` gate, a new module, or a new argument on
  a shared helper, the focused proof must include the registry/importer test
  files of that surface class —
  [test_quality_runner.py](../../tests/quality_gates/test_quality_runner.py)
  for gates; `grep -rl` the module name under `tests/` for new modules or
  changed helper signatures — not only the slice's own test file. Two escapes
  in one goal (2026-07-08) lived exactly in importer/registry tests the
  producer never ran and surfaced only in later broad runs.
- Run and record the critique required by
  [operating-contract.md](./operating-contract.md) before final closeout for
  task-completing repo work.
- Run the fresh-eye slice critique BEFORE the locked `--produce-mutation-coverage`
  producer run, not after: critique-driven code or test changes invalidate the
  coverage fingerprint and force a full instrumented broad-pytest rerun (two
  reruns in one goal on 2026-06-10 — one per mutating slice). This covers EVERY
  round: a proof-surface slice owes a second review of its repairs
  ([operating-contract.md](./operating-contract.md) Critique Discipline), so the
  order is round 1 -> repairs -> round 2 -> repairs -> producer, and the cap is
  two rounds (round-2 repairs are recorded as accepted-unreviewed rather than
  triggering a third). Satisfying "critique before producer" with round 1 alone
  buys back the exact rerun this rule exists to prevent.
- `python3 scripts/sync_support.py --json` and
  `python3 scripts/update_tools.py --json` are dry-run sanity checks.
- Use `python3 scripts/doctor.py --json` only when intentionally collecting
  real machine-state diagnostics.
- Route evaluator-backed validation through `quality` before `hitl` or
  same-agent manual review.

## Change Discipline

- **A remedy a durable record names is a hypothesis, not a plan.** Before shaping
  a slice around "the better repair is X" — in a deferred decision, a sweep row,
  or an issue — verify X's premise with one command or one file read. The remedy
  was written at the moment of deferral, when its author had the most context and
  the least obligation to check it. Measured on 2026-08-01: two of three entries
  picked up in one goal named remedies that could not be built as described, both
  killed by plan critique after slices had been shaped around them. Both premises
  were answerable by READING, not by running: one from
  `sync_root_plugin_manifests.py`'s `written_paths` (which names the plugin root as
  a directory — and which must not be *run* to check, since running it rewrites the
  generated tree), one from the field list in `inventory-consumer-fields.json`. A
  premise check is a file read as often as a command, and reaching for a command
  first is how a mutating script gets run mid-review. Tracked as
  [#468](https://github.com/corca-ai/charness/issues/468).
- The edit-time half of that discipline — assert a scripted replace landed, grep
  for a superseded number — lives with the rest of claim fidelity in
  [operating-contract.md](./operating-contract.md) *Critique Discipline*.
- Before authoring into a gated surface, skim
  [authoring-preflight.md](./authoring-preflight.md): the attention-state banned
  vocabulary, the length-headroom check, and a string/regex edge checklist —
  the constraints existing gates enforce, gathered so you know them up front
  rather than after a rework cycle (#308).
- Before a large addition to a skill helper or repo script, check headroom with
  `python3 scripts/check_python_lengths.py --headroom --paths <file>`
  (`limit − current`, where current is measured by `tokei` Python code lines);
  if the file is near its limit, start a new module rather than append.
  [run_slice_closeout.py](../../scripts/run_slice_closeout.py) auto-surfaces
  near-limit *changed* files at every slice closeout, so the near-limit trap is
  workflow signal, not memory (#256).
  The advisory never blocks on near-limit status; the existing length gate is
  the hard floor. Function limits remain AST-span based because `tokei` does not
  report function-level counts.
- The sibling trap has the same shape of affordance (#474):
  [dup_ratchet_edit_advisory.py](../../scripts/dup_ratchet_edit_advisory.py),
  carried on the already-installed PostToolUse edit hook, warns once per file
  per HEAD at the first substantial addition to a file inside the dup ratchet's
  declared `scope_paths` — rather than at the closeout aggregate, where a new family is a
  hard block found after the slice is finished and the commit message is
  written. Four consecutive runs wrote "run the ratchet early" into a plan and
  hit the aggregate anyway. It is strictly advisory and never changes an exit
  code; [dup-ratchet.md](../../skills/public/quality/references/dup-ratchet.md)
  *Two Arms* owns the mechanism and the reason it checks scope rather than
  membership.
- The per-surface aggregate preflights below —
  [check_skill_surface_preflight.py](../../scripts/check_skill_surface_preflight.py)
  for skills,
  [check_doc_authoring_preflight.py](../../scripts/check_doc_authoring_preflight.py)
  for docs, and
  [check_artifact_surface_preflight.py](../../scripts/check_artifact_surface_preflight.py)
  for artifacts (the `## Generated And Installed Surfaces` bullet) — are one guard
  class, not three unrelated tips: **before editing ANY gated authoring surface,
  run its matching aggregate preflight.** Each bundles that surface's real
  validators into one pre-edit pass, so the surface passes its commit gates first
  try instead of one serial rejection at a time. Running the preflight for one
  authoring seam but skipping a sibling seam is the same
  guard-propagation-across-seams miss the `quality` Behavior lens names — apply
  the guard at every authoring crossing, not only the one you remember.
- Before adding prose to `skills/public/*/SKILL.md`, `skills/support/*/SKILL.md`,
  or their `references/*.md`, run
  `python3 scripts/check_skill_surface_preflight.py --repo-root . --path <file> --preview-delta <planned-lines>`;
  it reports SKILL.md total/core headroom plus markdown, doc-link, mirror-sync,
  and staged-index couplings before the broad gate.
- Before authoring into a general doc surface (the handoff artifact or any
  `docs/*.md`), run
  `python3 scripts/check_doc_authoring_preflight.py --path <doc>`; it aggregates
  the markdownlint, wrapped-inline-code, `check_doc_links`, and surface
  length-cap constraints in one pass (reusing the real validators), so the doc
  passes `check-markdown.sh` / `check_doc_links.py` first try instead of one
  serial rejection at a time. Affordance only — the doc still commits without it.
- When deleting a public symbol or named concept, run
  `python3 scripts/check_symbol_residue.py --repo-root .` before closeout. It is
  advisory by design (#259): it scans deleted Python symbols and common phrase
  variants across `docs/` and `skills/`, then leaves intentional historical
  mentions to human judgment. For a concept that is not derivable from a deleted
  Python name, pass `--concept "<name>"` or `--symbol <name>` explicitly.
- Never stop a background process with a loose `pkill -f <pattern>` — the pattern
  can match your own replacement/parent command and kill it (observed: a stray
  poll loop's `pkill` killed the in-flight goal flip). Target by PID, or use the
  harness `TaskStop` for background tasks.
- Prefer deleting drift over documenting drift.
- Current-pointer helpers should be no-op when canonical content has not
  changed. If a startup or inventory command rewrites an artifact without a
  canonical change, treat that as invocation drift or a helper bug.
- Treat `mutate -> sync -> verify -> publish` as hard phase barriers.
- After a command rewrites generated surfaces, plugin exports, versioned
  manifests, or git state, finish that phase before starting validators or
  publish steps.
- Use parallel tool calls only for read-only inventory or file inspection;
  never run sync, export, bump, install, update, or git mutation commands in
  parallel with validators, closeout, or publish steps.

## Floor-Addition Restraint

The repo's reflex to an observed waste is "add one more deterministic floor."
That reflex is asymmetric: it over-applies blocking teeth where they create
authoring churn (the validator-post-hoc-churn class, spec
[achieve-efficiency-improvements](../../charness-artifacts/spec/achieve-efficiency-improvements.md)
Problem 1) while real recurrences stay teeth-less. Before adding a **new
deterministic blocking floor** (a gate that refuses closeout/commit), run this
checklist and record the call:

1. **Does it raise closeout-contract weight?** A new required field/section/form
   the author must satisfy up front is Problem-1 cost: it is one more shape an
   author discovers by failing the flip. If yes, the bar to add it is higher, not
   lower.
2. **Is advisory/prose enough?** Default to a **non-blocking advisory** (stderr +
   durable payload, like the over-slice and gate-runtime advisories in
   [slice_closeout_advisories.py](../../scripts/slice_closeout_advisories.py)).
   Promote to a blocking floor only when prose has a **recorded recurrence count**
   (the lesson kept decaying and recurring) — not on first sight. An advisory that
   false-fires trains token-theater; so does a premature floor.
3. **Can an existing describe-first preflight absorb it?** If the concern is "the
   author did not know the required shape," the fix is usually to surface it in the
   describe-first closeout preflight
   ([describe_goal_closeout_shape.py](../../skills/public/achieve/scripts/describe_goal_closeout_shape.py))
   so it is seen up front, **not** a new serial gate. A floor the author meets
   only as a reactive end-gate is the churn pattern; a floor the preflight lists is
   absorbed. Caveat: today's preflight renders a **static catalog**, so it can
   absorb only *static or form-shaped* floors. A *goal-conditional* floor (one that
   needs runtime evaluation of the specific artifact) cannot be absorbed by the
   current preflight — that is A2 (deferred); such a floor stays a `keep` gate, and
   adding one is a `keep`, not an `absorb`.

Prefer advisory or describe-first absorption over a new blocking floor unless the
recurrence is recorded. The standing closeout floors are audited (with an
`absorb`/`merge`/`keep` call each) in
[closeout-floors audit](../../charness-artifacts/audit/closeout-floors.md);
consult it before adding a sibling floor that an existing one could merge.

**Teeth (non-blocking).** This checklist is prose and shares the decay risk it
guards against, so a deterministic **non-blocking** nudge gives it the intended
(advisory) teeth: `advise_floor_addition_restraint` in
[slice_closeout_advisories.py](../../scripts/slice_closeout_advisories.py)
(wired into `run_slice_closeout.py`) runs a conservative before/after detector
over the slice diff and, when it sees a **new** blocking floor — a new
`report["ok"] = False` site or a new `REQUIRED_*` / `_SECTIONS` / `_EVIDENCE_NAMES`
member in `skills/`/`scripts/` source — *without* a recorded restraint call, it
prints an advisory naming this checklist. **Record the call** to silence it (and
to leave the durable provenance): a `Floor-Addition Restraint:` line in the
slice's commit/goal/critique, or a `# floor-addition-restraint: <call>` comment at
the floor site. The detector is deliberately conservative (a probe): exotic floor
shapes may escape it — a missed nudge beats a false one that trains token-theater.
A *blocking* enforcement gate for this rule is deliberately rejected: it would be
the exact reflex the rule names.

## Repair Discipline

- **State the intended delta; prove the complement is unchanged.** A bounded
  reviewer's finding is a POINT. The repair is a change to a FUNCTION, and the
  blast radius is that function's entire prior behaviour. Tests written for the
  original only cover properties someone already thought to name, so a repair can
  silently NARROW a property nothing asserts while every gate stays green. This
  is the mechanism behind the recurring "the fix carries the class it fixes"
  signature, measured six times in this repo.
- **The evidence is a same-session controlled comparison, not a theory.** In one
  slice, three surfaces were repaired by the same agent on the same day:
  `check_doc_links.validate_link` and `markdown_doc_scan.iter_doc_lines` were
  differentially verified against their baseline and the next bounded round found
  ZERO defects in them; `check_plugin_doc_links.iter_unfollowable_links` was not,
  and the same round found THREE narrowings in it.
- **The baseline is what the reviewer READ, not the last commit.** A function
  created earlier in the same slice is simply new at commit granularity, so a
  commit-ranged diff cannot see its repair at all — which is exactly the case the
  three defects landed in. `reviewer_boundary_fingerprint.py snapshot` captures a
  strict subset of what it certifies — the CHANGED and untracked `.py` files, not
  symlinks, under 512 KiB — and
  [parity_harness.py](../../scripts/parity_harness.py) recovers them
  (`--against review-snapshot`). A file that was clean when the reviewer read it
  has no captured baseline and is reported as `uncomparable`, never as a clean
  zero; for that case, and for repairing a function that already shipped, a
  committed ref is the right baseline.
- **`run_slice_closeout.py` surfaces this as an advisory**, naming every function
  (by qualified name, so `A.run` and `B.run` cannot collapse into one verdict)
  whose signature is unchanged but whose body — including its decorators — changed
  since the reviewer read it, plus a count of paths it could not compare.
  It is advisory rather than blocking because the delta is often intended and only
  the author can say so — the gate forces the question, it does not render the
  verdict. The snapshot it reads is bound to `HEAD`, so a stale one from an
  earlier slice cannot make it announce a review that never ran; it cannot
  substitute for a review either way.
- **Deleting a module-level name is allowed; shipping it without its readers is
  not.** A dynamic `module.NAME` access — the shape `import_repo_module` produces
  — is invisible to ruff and to the import graph, and no commit-boundary gate
  runs the broad suite, so the readers surface only later. `run_slice_closeout.py`
  lists them via
  [removed_name_consumers.py](../../scripts/removed_name_consumers.py). Advisory,
  never blocking: the missing thing was information, not permission. Measured
  frequency over the 13 preceding commits: one commit, one name — the `LINK_RE`
  case that shipped a red suite. Each hit is a textual candidate, not a proven
  binding.
- **Non-claim:** identical outcomes over a corpus is evidence about that corpus,
  not a proof of equivalence. The harness narrows where a narrowing can hide; it
  does not prove none is left.

## Generated And Installed Surfaces

- **`parents[N]` in a skill script is correct in both trees only by a
  cancellation, and the invariant is pinned by a test, not a comment.** The
  exporter flattens `skills/<kind>/<skill>/` to `skills/<skill>/` and adds a
  `plugins/<pkg>/` level; those two cancel, which is why the same index resolves
  correctly in the authoring tree and the mirror. No call site says so, so one
  layout change would turn every such site into an unreachable-file instance at
  once. [test_parents_index_layout_invariant.py](../../tests/quality_gates/test_parents_index_layout_invariant.py)
  states the invariant executably and owns its revisit trigger: any change to
  `export_plugin.py`'s skill-tier layout, or a new `parents[N]` site in a skill
  script, arrives with that test updated in the same commit. If it goes red and
  the repair is "bump the number", that is the class recurring and the call sites
  need a shared helper instead. Prefer a marker-based ancestor walk over level
  counting in new code — `repo_root_from_skill_script` is the worked example, and
  the `parents[4]` fallback removed from it was both dead and wrong in the mirror.

- **Portability classification is a closeout checkpoint, not an optional
  nicety.** It fires for two scopes, not one:
  - a *new reusable mechanism* — a repo-root `scripts/*.py`, a new gate, or a
    generalizable pattern/doctrine (an invariant, failure mode, or cost lesson);
  - an *improvement, issue, or policy* whose resolution should be inheritable by
    charness-consuming repos — a new operating rule, a contract, a lint/check, or
    a lesson that other repos would also want.

  For either scope, classify it `host-local` vs `skill-capability` before
  closeout and state the call. In this harness repo do **not** default to
  repo-local: if the mechanism, policy, or doctrine generalizes, route it to the
  owning public skill or reference (at minimum a `references/*.md` doctrine line,
  a `quality`/skill capability, or a packaging/[AGENTS.md](../../AGENTS.md)
  absorption) so adopting repos inherit it, not just charness. A soft "inspect
  whether a skill should absorb the lesson" version of this rule already existed
  and still did not fire during a defect-repair slice — the low-altitude framing
  of defect, improvement, or issue work keeps the call out of view — so make the
  classification explicit rather than remembered. The narrower code-mechanism-only
  reading is exactly why a portable policy nearly shipped repo-local; see the
  [portability-miss retro](../../charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md).
  A deterministic nudge (flagging a new repo-root capability script that belongs in
  a skill) is a tracked follow-up: `follow-up:portability-classification-tripwire`.
- If a public skill needs repeated bootstrap, adapter resolution, artifact
  naming, or recovery behavior, ship a helper script instead of leaving it as
  prose-only guidance.
- When tool install, update, or support-sync work is partly manual or mutates
  the operator surface, emit structured output and persist machine-readable
  state so a later agent can continue without rediscovering the machine.

## Sync Before Validation

- Repo-owned diff obligations and closeout stay downstream of generated-surface
  sync.
- If checked-in plugin export is touched, run
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .` before
  validators.
- A pre-commit gate
  ([check_staged_mirror_drift.py](../../scripts/check_staged_mirror_drift.py),
  wired in `.githooks/pre-commit`) blocks committing when exported source is
  staged but its regenerated `plugins/` mirror is not — it archives the staged
  index (`git write-tree`) and validates that snapshot, catching both "forgot to
  sync" and "synced but forgot to stage the mirror" at commit time instead of
  post-commit at `validate_packaging_committed` (#257). Still stage the
  regenerated mirror (`git add plugins/ .claude-plugin/ .agents/plugins/`)
  alongside the source.
- A commit-message gate
  ([check_issue_closeout_commit_msg.py](../../scripts/check_issue_closeout_commit_msg.py),
  wired in `.githooks/commit-msg`) blocks commits that stage issue closeout
  artifacts with `Close #N` keywords unless the final commit message carries
  those keywords and the required closeout ledger. `pre-commit` cannot enforce
  this because it does not see the final message.
- Machine-local discovery output under `.agents/charness-discovery/` is not a
  checked-in surface; generated local stubs should not be committed as drift.
- **Batch source edits before regenerating a derived surface.** Re-running the
  plugin mirror sync and rebuilding the debug-seam index each cost a regen+verify
  cycle, so make ALL planned edits — **including critique-driven fixes** — before
  the regen, not one regen per edit round. A pure line-shift no longer rotates a
  dup-ratchet family (slice 4 re-keyed the gate onto a path-independent content
  fingerprint, resolving D30), so ordinary edits to scanned clone-member files are
  not a re-baseline trigger; membership growth, a nose-version bump, and an algo
  bump still are. When the ratchet does report a delta, prefer the scoped accepts
  (`--accept-family NEW_ID`, `--accept-rotation OLD=NEW`) over `--write-baseline`,
  which is a full-scan overwrite that silently re-accepts every unreviewed family
  too. [dup-ratchet.md](../../skills/public/quality/references/dup-ratchet.md) owns
  the mechanism; keep it there rather than restating it here.
- **Author strict-validator artifacts to their contract first.** Debug, critique,
  retro, goal, and issue-closeout carriers have machine-enforced required shapes.
  Read the contract before authoring (`describe_closeout_draft_shape.py --stub`,
  the validator's `REQUIRED_SECTIONS`, etc.) and dry-run the owning validator with
  `python3 scripts/check_artifact_surface_preflight.py --path <artifact>` at
  authoring time, instead of discovering the shape via serial commit-time gate
  failures (that preflight is already a commit gate; running it early just avoids
  the retries).
