# Pre-design critique — #546 (a declared label universe instead of a sample-history discriminator)
Date: 2026-08-10

## Decision Under Review

Whether to build, for [#546](https://github.com/corca-ai/charness/issues/546), a check
that fails when a budgeted runtime label is in NO declared universe of labels the runner
can queue — replacing the sample-history discriminator that was built, measured
defective and reverted on 2026-08-10 (see
[the revert critique](./2026-08-10-issue-546-unenforceable-budget-critique.md)).

Sketched design: derive the universe from (1) `queue_selected` / `queue_timed` sites in
`scripts/run-quality.sh`, (2) the aggregate label built at `run-quality.sh:602-604`, and
(3) adapter `startup_probes:` entries; fail only on a budgeted label in none of them;
hard-error the extractor on a `queue_*` label it cannot statically resolve. Parent
measurement before review: those three sources account for all 28 budgeted labels on
`local-linux-x86_64-36cpu` with zero residual.

**Outcome: PROCEED-WITH-CHANGES.** The discriminator swap is sound and genuinely immune
to the two defects that killed the previous attempt (F2 fresh-machine hard-fail, F3
conditional labels), because it never reads sample history and conditional labels still
appear literally in the runner. But it must not be the basis for closing #546 as the
issue is written.

## Failure Angles

- **A universe derived from one bash file is a universe that an ordinary refactor
  deletes.** Splitting the queue into a second runner script, or sourcing a helper,
  silently shrinks it and turns correct bars into blocking false reds.
- **The gate is EXPORTED.** `check_runtime_budget.py` ships to consumers who have no
  `run-quality.sh` at all, so a repo-specific universe is being wired into a
  deliberately repo-agnostic surface — the same "fit the rule to this repo" class the
  revert critique named, one file over.
- **Being spelled in the runner is not the same as being runnable.** The predicate
  proves presence, not reachability.
- **This repo already has a bash-label extractor.** A second one drifts silently.

## Counterweight Pass

- The F2/F3 immunity is real, not asserted: the predicate reads no sample history, so a
  fresh machine's first run answers identically to its thousandth, and a release-path or
  opt-in label is in the file whether or not it ran.
- The "zero residual today" measurement is true but was over-read by the parent: it was
  taken against the SELECTED profile's budget block, and it missed a third queue wrapper
  whose two labels simply are not budgeted yet.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh | action: fix | note: source 1 is incomplete. `queue_agent_browser_runtime_gate` (`:453-465`, called at `:641` and `:957`) is a THIRD wrapper forwarding to `queue_timed "$label"`. Its two labels are not budgeted today, which is why the zero-residual measurement looked clean; budget either one and the new gate hard-fails a correctly queued label. Specify source 1 as any `queue_*` wrapper.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh | action: fix | note: the stated hard-error rule is DOA on first run. `:450` and `:464` are `queue_timed "$label" "$@"` inside dispatcher bodies — non-literal by construction. Worse, a naive regex ACCEPTS them and admits the literal string `$label` to the universe. The rule must be "unresolvable at a call site outside a `queue_*` function definition"; `run-quality.sh:663-665` records the literal-label invariant that makes this safe.
- F3 | bin: act-before-ship | evidence: strong | ref: .agents/quality-adapter.yaml | action: fix | note: budgets are profile-relative — `profile_commands`/`profile_budgets` return exactly ONE block per run — so checking only the selected block never reaches the aarch64 block, which the adapter itself says has zero recorded samples and where a typo would outlive the repo. Membership is machine-independent, so validate against the UNION of all four budget blocks at no cost in false reds.
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/check_runtime_budget.py | action: fix | note: the gate is exported and mirrored under `plugins/`. A consumer repo has no `queue_selected` anywhere — it drives gates from `gate_commands`, npm scripts, a Makefile, or an adapter `command_timing_log` whose labels are in no bash file. So the check must arm only on a non-empty derivable universe and NAME the universe it used; failing on an empty one is F3 reborn one layer out, and no-opping silently re-creates #546 for every consumer.
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/check_timing_layer_completeness.py | action: fix | note: this repo already has the extractor (`QUEUE_SELECTED_RE`, `run_quality_labels`, `:36-45`) and already enforces a declared inventory against it. It also already under-counts — `queue_timed` sites are invisible to it, so `dead-code-advisory` is missing from its universe. Lift and widen it rather than writing a second regex over the same file. Its degrade shape (`:94-95,136-138`: exit 0 and print why when the runner is absent) is the precedent F4 needs.
- F6 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/measure_startup_probes.py | action: fix | note: source 3 must be narrowed to `startup_probes` entries with `class: standing`, because `_selected_probes` (`:61-64`) filters on class and run-quality invokes it with `--class standing` (`run-quality.sh:923`). A probe declared with any other class is admitted to the universe but never measured — a dead bar the design would pass.
- F7 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/scripts/runtime_budget_lib.py | action: file-issue | follow-up: deferred docs/handoff.md `## Discuss` -- to be filed with the #546 slice, since both siblings live on the surface that slice repairs | note: two siblings of #546's shape on the same surface. `runtime_visibility_findings` are all emitted at `severity: "weak"` and no exit path consults them. `latest_spikes` is computed (`:258-266`) and rendered as `LATEST-SPIKE` (`:368`) and is likewise structurally unable to fail — a label whose latest run blew its bar while the median held scrolls past in an ~85-gate run and exits 0.
- F8 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/scripts/check_runtime_budget.py | action: fix | note: `summarize()` (`:36`) emits `"commands_observed": report.get("commands_observed")`, but `evaluate` returns `commands_source` and never `commands_observed`. Every `--summary` run has emitted `commands_observed: null` — a declared summary field with no producer, on the surface being repaired.
- F9 | bin: over-worry | evidence: strong | ref: .agents/quality-adapter.yaml | action: document | note: the fear that a 4-core-only bar would fail on a 36-core box does not materialize. Every label budgeted only in the 4cpu or aarch64 blocks resolves to a literal `queue_selected` site, and the predicate is membership rather than measurement, so it is machine-independent by construction.

## Disposition

PROCEED-WITH-CHANGES, and with one scoping requirement that is not a code change.

**The design fixes the RENAME rot mode only.** #546's body names three: renamed,
conditionally queued and then never queued, and moved behind an opt-in. A label in the
runner but unreachable is spelled in the file, so the universe predicate passes it —
and `dead-code-advisory` is a live in-repo instance: budgeted at 12500, queued only under
`CHARNESS_QUALITY_DEAD_CODE=1` or explicit selection (`run-quality.sh:684-688`), never
sampled in a normal run, and the proposed gate reports it green. Shipping this and
closing #546 would report clean against the clearest live instance of the defect being
closed.

So either the slice also ships the adapter-declared `conditional:` marker the earlier
review recommended — which covers the other two modes AND supplies the F3 exemption the
reverted attempt lacked — or #546 is re-scoped in writing to the rename mode with the
remainder left open. That choice belongs to the operator and should be made before
implementation, not discovered at close.

## Reviewer Tier Evidence

- Requested tier: bounded read-only fresh-eye reviewer (`bounded-reviewer`), unnamed and synchronous.
- Requested spawn fields: subagent_type=bounded-reviewer, run_in_background=false, no host addressing name.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer returned findings in-band. This is the pre-design causal review the `bug` classification owes, run before any implementation existed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. The review changed the design before it was built: it found a third
queue wrapper the parent's measurement had missed, showed the stated hard-error rule
would fire on the runner's own dispatchers, found the existing extractor the parent was
about to duplicate, and identified the export boundary that would have turned the fix
into a consumer-wide false red. Its most valuable finding is negative — that the design
does not close the issue it is being built for.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed: the reviewed input was a design sketch in the spawn prompt plus the current worktree. No implementation existed. -->

## Boundary Ownership

- Producer: `check_runtime_budget` / `runtime_budget_lib`, which render the budget verdict.
- Consumer: the pre-push quality run in this repo AND in every consumer repo that installs the quality skill.
- Owning surface: `skills/public/quality/**`.
- Verdict: single-surface
