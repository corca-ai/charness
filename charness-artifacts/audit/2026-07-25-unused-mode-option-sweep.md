# Unused Modes and Options Sweep

Date: 2026-07-25
Goal: [2026-07-25-ranked-chunks-1-3](../goals/2026-07-25-ranked-chunks-1-3.md) slice 6
Operator decision at sweep time: report-first, zero deletions. **Sign-off has since
been given — see `## Operator Disposition` below for what was acted on.** The
inventory itself is unchanged from the sweep; the disposition is appended rather
than edited in, so the evidence and the decision stay separable.

Method: a 17-agent fan-out — four parallel scouts (one per surface family), then an
adversarial refutation pass per candidate whose default was that the candidate is
wrong, then synthesis. 27 candidates scouted, 13 sent to refutation, 12 adjudicated,
9 confirmed, 3 refuted.

**Provenance caveat on this run:** the scout agents were not constrained to read-only
and one of them edited `.agents/cautilus-adapter.yaml` (`run_mode: ask` -> `auto`) to
A/B the planner branch, without restoring it. The parent caught this via `git status`
and restored the file. Nothing else in the worktree was touched. Treat any
"observed dirty" note inside the report below as an artifact of that contamination,
not a pre-existing repo condition. A future sweep should spawn read-only reviewers.

---

# Unused-Modes-and-Options Sweep — charness

Report-first inventory. Zero deletions were made and none are recommended here; every entry is presented so the operator can decide individually.

## What was swept

Four surface families were swept for options that were *built with intent but never used*: adapter enums (`.agents/*.yaml` + their resolvers), planner branches (`plan_*.py` arms), CLI flags (`scripts/`, `skills/*/scripts/`), and preset/profile variants (`presets/`, `profiles/`).

The shape being hunted is specific: a deliberately designed option whose arms produce (near-)identical output, with no caller that selects the non-default arm. Options with a real, distinct delta — even rarely-passed ones — are *not* findings, and several were rejected on exactly that ground.

Method was static: grep/AST reading, `git log -S` for birth-and-never-touched history, `charness-artifacts/` scans as a usage proxy, plus a handful of in-process differential runs (planner arms A/B'd with a monkeypatched adapter; `setup_agent_docs_lib` run against a mutated adapter copy; `scan_scenario` A/B'd across all 54 real JSON specs). Each candidate was then re-verified by a second pass that actively tried to refute it — three candidates did not survive that pass and are listed below.

---

## Confirmed unused (9)

### Adapter enums

**1. `hitl-adapter` `default_scope: all`** — `.agents/hitl-adapter.yaml:7`
- *Delta:* none. Three-arm enum (`all`/`code`/`docs`), loaded, defaulted and range-validated at `skills/public/hitl/scripts/resolve_adapter.py:34/46/91-92`, then read by nothing. The only scope consumer, `bootstrap_review.py`, takes scope from argparse (`--scope`, default `"all"`, line 186) and never asks the adapter. Even the CLI value is inert — it reaches only the scratchpad template and `state.yaml` (lines 65, 90, 117); no chunker, gate, or report branches on it.
- *Evidence:* `bootstrap_review.py` loads the adapter (line 98) and reads only `require_explicit_apply`. `grep -rni scope skills/public/hitl/SKILL.md` → zero hits. Two commits ever, both the original collaboration-layer import. `charness-artifacts/hitl/` holds one dated session (2026-04-25).
- *If deleted:* removing the line from `.agents/hitl-adapter.yaml` alone breaks nothing (`resolve_adapter` backfills `"all"`). End-to-end removal also changes no runtime behavior but requires re-syncing the `plugins/charness/skills/hitl/` mirror in the same change, and downstream repos that already wrote `default_scope:` would get an unknown-key *warning* (not an error). What is lost is the option to implement scope-aware review later without re-litigating the contract.

**2. `achieve-adapter` `closeout_publication.default_mode: handoff-only`** — `.agents/achieve-adapter.yaml:6`
- *Delta:* six-value enum (`audit-only`, `handoff-only`, `direct-commit`, `pull-request`, `release`, `manual`) with one executable branch (`achieve_adapter_policy.py:257`) that lumps `audit-only` and `handoff-only` together and emits a warning differing only by the interpolated mode name. Measured: 6 values → 2 distinct outputs; the two conservative arms differ by one word. The value is otherwise passed straight into `closeout_policy_report()["publication_default"]` (line 328) as an informational field; `goal_artifact_closeout_evidence.py:276-281` gates on adapter *validity*, never on the mode.
- *Evidence:* `grep -rn 'publication_default' charness-artifacts/` → no output across 3.5 months of goal/retro artifacts. `skills/public/achieve/SKILL.md` never mentions publication. One commit (518bdc23), never revisited.
- *If deleted:* (a) removing just the repo's line — nothing breaks; the fallback is `audit-only`, on the same warning branch, so only the advisory string and the reported value change. (b) Removing the field/enum from the skill — breaks `tests/quality_gates/test_achieve_adapter_policy.py:41,56,78,204,242`, requires edits to four reference docs plus `adapter.example.yaml` and `init_adapter.py`, and removes a documented knob from a *portable public skill* other repos may adopt with different publication postures.

**3. `cautilus-adapter` `profile_default: evaluator-required`** — `.agents/cautilus-adapter.yaml:79`
- *Delta:* the parsed value is never read. Four sites total: the required-text snippet (`scripts/cautilus_scenarios_lib.py:277`), the allow-list (`cautilus_adapter_lib.py:17`), the inferred default (`:116`), and the yaml line. The profile every eval actually uses comes from `parser.add_argument("--profile", default="evaluator-required")` at `scripts/eval_cautilus_scenarios.py:112`. The adapter's own `held_out`/`full_gate` command templates are also never rendered by any code, so `{profile}` is filled by whoever types the command.
- *Evidence:* all three `load_cautilus_adapter` consumers (`plan_cautilus_proof.py`, `control_plane_lifecycle_lib.py`, `validate_adapters.py`) read only pattern lists, `run_mode`, `disabled_reason`, and validity. `evals/cautilus/scenarios.json` has exactly one profile key, so the knob's domain is size one. Sibling adapters `.agents/cautilus-adapters/*.yaml` never set it. No test references it. Added once (236ca594), never touched.
- *If deleted:* deleting the yaml line **alone** hard-fails `scripts/validate_cautilus_scenarios.py` (the literal string is a required snippet) — a red CI. A complete 4-line removal plus plugin re-sync changes no eval, plan, or control-plane behavior. The field's only remaining function is documentary: it records intent, and is the natural hook if a second registry profile ever exists.

### Planner branches

**4. `run_mode: auto` branch** — `scripts/plan_cautilus_proof.py:181`
- *Delta:* one `notes` string. In-process A/B against the real planner (adapter monkeypatched) shows `auto` vs `adaptive` differ in exactly two keys: the echoed `run_mode` and one advisory sentence. `must_ask_before_running`, `status`, `proof_kinds`, `required`, `next_action`, `recommended_commands`, `recommended_followups`, `scenario_registry_review_required`, `intent_tags` are all identical. By contrast `ask` really flips `must_ask_before_running` and `disabled` really flips `status`.
- *Evidence:* live adapter is `run_mode: ask`; the two per-eval adapters set no `run_mode`; `infer_cautilus_defaults` only ever defaults to `ask` or `adaptive`; tests cover ask/adaptive/disabled and never `auto`; every downstream consumer tests only `== "disabled"`. `grep 'run_mode: auto\|Repo policy is auto' charness-artifacts/` → no matches. One commit (669eaaee, 2026-04-21).
- *Note:* `auto` appears in three non-generated places, not two — the third is the no-adapter operator hint at `cautilus_adapter_lib.py:210`, which advertises `auto` to downstream repos while no doc explains what it does.
- *If deleted:* removing only the branch and leaving `auto` in `VALID_RUN_MODES` is the worst option — a downstream repo set to `auto` would still validate but get an empty policy note. Removing the branch *and* the enum value is a public contract narrowing: any downstream `.agents/cautilus-adapter.yaml` with `run_mode: auto` flips from valid to a hard exit-1. A one-line alias (`if run_mode in ("adaptive", "auto")`) removes the dead arm without that.

**5. Hardcoded `required = False` and its dead consumer arms** — `scripts/plan_cautilus_proof.py:149`
- *Delta:* `required` is a bare literal, never reassigned, never adapter-derived. Three consumer true-arms are therefore unreachable: `run_slice_closeout.py:125-129` (`missing_required_proof` always False → the cautilus-blocking closeout path at 140-145 is dead), `slice_closeout_reporting.py:31` (contributes nothing to `_cautilus_plan_has_visible_work`), and the CLI's own `if plan["required"]:` at line 251 — verified live: default output prints only `status: ready-for-validation`.
- *Evidence:* `git show 66c7a729` is the smoking gun — the commit literally changed `required = bool(prompt_paths)` → `required = False` and in the same commit deleted the dynamic assignments for `recommended_commands` and `next_action`, leaving all consumer scaffolding standing. Worst-case invocation (prompt-affecting + artifact-changed + scenario review) still yields `required: false`. `"cautilus proof is required for this slice"` appears nowhere but its own definition. The two tests that touch it assert `is False` — they pin the constant.
- *If deleted:* the `required` field and its three arms are safe to remove; the only breakage is two constant-asserting test lines (`test_run_slice_closeout_review_obligations.py:54,103`) plus the plugin mirror re-sync. **Do not** remove the sibling `next_action` without follow-up: it has three readers that would `KeyError` (including `run_cautilus_eval.py:155`) and it is the *documented* agent refusal gate at `skills/public/quality/references/cautilus-on-demand.md:17`, cited as evidence in 8+ artifacts. What is genuinely lost is the ability to ever say "this slice needs a live Cautilus run" — deletion makes that permanent by construction rather than merely pinned.
- *Incidental, unrelated:* `.agents/cautilus-adapter.yaml` was observed dirty in the worktree (`run_mode: auto` locally vs `ask` as documented). Someone should look at that uncommitted edit.

### CLI flags

**6. `--granularity` on `generate_prompt_mutants.py split`** — `scripts/generate_prompt_mutants.py:137` (`GRANULARITY_CHOICES` at :35)
- *Delta:* none. The choices list has exactly one legal value, which is also the default; the only "other arm" is an argparse rejection. `prompt_mutant_lib.py:200` then re-checks the same thing — a guard unreachable from the CLI.
- *Evidence:* two hits repo-wide outside `plugins/`: the `add_argument`, and a test asserting `--granularity paragraph` exits nonzero. `build_split_manifest` has exactly one production caller. The echoed `{"granularity": ...}` field's only reader is a test assertion; no split manifest is ever persisted (`grep -rl granularity charness-artifacts/prompt-mutation/` → none). One commit (213f8986, 2026-07-09).
- *If deleted:* two tests must be deleted (not adapted) and one assertion dropped; the `split` subcommand's stdout JSON loses a key no in-repo consumer reads; the plugin mirror must be re-synced. What is lost is a recorded design seam — `charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md:346-350` explicitly names granularity as a future axis (sentence/paragraph/whole-file).

**7. `--replace-file` on `refresh_current_pointer.py`** — `scripts/refresh_current_pointer.py:32` (guard at :122)
- *Delta:* unreachable as useful. Its only effect is relaxing a guard inside `_symlink_pointer` that requires `strategy == "symlink"` on a non-symlink pointer. But `main()` resolves `auto → symlink` only when the pointer *is already* a symlink, else `auto → copy`. The guard's precondition can never hold on the default path (including the broken-symlink edge).
- *Evidence:* every reference lives inside the defining script. Zero tests, docs, SKILL.md, or adapters. The companion `--strategy` has exactly one caller repo-wide (`test_artifact_naming.py:550`), and that test returns blocked earlier for an unrelated reason, so even it never reaches the guard. Of 11 `latest.md` pointers, 2 are symlinks and 9 regular files — all handled by the auto path. One commit (d0b918d1, 2026-05-06).
- *If deleted:* nothing in the repo breaks, but this flag is the *escape hatch on a safety guard*, so removal forces a choice. Dropping flag **and** guard makes `--strategy symlink` silently unlink a checked-in `latest.md` — losing the "won't clobber a file you didn't create" property that `skills/public/gather/references/asset-refresh.md:46,52` cites as the shared writer-surface contract. Dropping the flag and keeping the guard as a hard block is safe but makes copy→symlink migration impossible through the helper (an operation never yet performed).

**8. `--scan-comments` on `prompt_mutation_clean_proof_preflight.py`** — `scripts/prompt_mutation_clean_proof_preflight.py:133`
- *Delta:* measured as zero on all real inputs. A/B run of `scan_scenario(..., scan_comments=False/True)` over all 54 real JSONs under `evals/cautilus/**` and `charness-artifacts/**/*config*.json` produced 0 findings on every file in both arms. 47 files carry `_`-prefixed keys; only 4 of those values even contain the word "git", and none matches the detection pattern.
- *Evidence:* zero hits outside the defining script — no docs, no CI, no workflows. The one documented invocation (`docs/prompt-mutation-policy.md:128`) omits the flag. The test that looks like a caller (`test_scenario_scan_ignores_comments_by_default`) pins the *default* arm and would pass verbatim if the flag were removed. Added 2026-07-09 (0115654f), never invoked.
- *Worth flagging:* the on-arm arguably contradicts the script's own docstring ("scans the parts of an eval scenario that are actually shown to the captured run") — `_comment` keys are author-only and not shown to the run, so the widened scan would report on text the agent cannot see.
- *If deleted:* no test, caller, or output changes; only the `plugins/` mirror needs re-syncing. Lost: a latent paranoia switch, restorable in ~3 lines.

### Preset/profile variants

**9. `profiles/` instance files are documentation, not runtime configuration** — `profiles/{constitutional,collaboration,engineering-quality,meta-builder}.json`
- *Delta:* none at runtime. `bundles.public_skills`, `bundles.preset_ids`, `activation`, and `validation.smoke_scenarios` are read only by `scripts/validate_profiles.py`, and only to assert referenced artifacts exist. `smoke_scenarios` is never executed (`run_evals.py` runs the registry). Swapping one profile for another changes zero observable behavior for any skill, adapter, CLI, hook, or gate.
- *Evidence:* the three similarly-named surfaces are different concepts and were each checked and cleared — machine runtime profiles (`record_quality_runtime.py`), the cautilus scenario registry (`--profile evaluator-required`), and the CLI's capability-resolution `profiles`/`bindings`. Strongest signal: six shipped public skills (`achieve`, `create-cli`, `critique`, `issue`, `prove`, `setup`) appear in *no* profile and nothing complains. The only content edit since creation (412f4f29) was mechanically deleting a removed skill id — profiles react to the repo, never drive it.
- *If deleted:* zero runtime change; `validate_profiles.py` takes its "No profile instances found." path and exits 0. Lost: a passive referential-integrity tripwire that only guards references the profiles themselves created (and demonstrably does not catch skill *additions*), plus declarative bundle documentation shipped to installed hosts. **Do not delete** `profiles/profile.schema.json` (routed by `skills/public/create-skill/SKILL.md:34`) or the `profiles/` directory itself (`packaging/charness.json` `presets_dir`/`profiles_dir` is required by `validate_packaging_install_surface.py:103`).

---

## Refuted on verification (3)

These looked like the target shape and are not. Recording them so the next sweep does not re-file them.

**`critique-adapter` `reviewer_tiers.medium`** — `.agents/critique-adapter.yaml:19`. The candidate correctly found that `scripts/critique_packet_lib.py` hardcodes `DEFAULT_REVIEWER_TIER = "high-leverage"` and never resolves the `medium` arm, and that the two arms differ only by `service_tier: priority`. But it missed two real consumers. (1) `scripts/setup_agent_docs_lib.py:144-176` reads `reviewer_tiers["medium"]` and cross-checks it against the default Codex profile; running the function against a copy of the adapter with the arm removed goes from `[]` findings to a `review_required` `critique_adapter_codex_profile_drift` finding. That is the exact enforcement the arm's birth commit advertised, and it exists so *non*-high-leverage subagents are also pinned to Terra/medium rather than inheriting parent effort. (2) `skills/shared/references/fresh-eye-subagent-review.md:18-28` explicitly instructs agents to request `medium` for routine reviews — the tier is agent-selected, so the absence of a `--tier` flag is not evidence of no caller; 7 artifacts record `Requested tier: medium`, several citing that reference, some after the arm landed. Two quality gates pin the arm's exact contents and it ships in the portable scaffold.
**What survives:** a genuine inconsistency worth filing separately — because the packet path hardcodes `high-leverage`, an artifact recording "Requested tier: medium" while citing a generated packet is self-contradictory. That is a packet tier-propagation bug, not a case for removing the arm.

**`release-adapter` `requested_review_policy: advisory-only`** — `.agents/release-adapter.yaml:73`. The code reading was accurate but the conclusion was wrong: the arms do not produce the same output, and the delta is consumed on every charness release. Under `advisory-only` the gate reports `configuration_status: advisory_only` with no warnings; under `warn-if-unconfigured` it reports `not_configured` plus a warning — and `publish_release_artifact_sections.py:44-56` renders both the label and the warnings into the published release artifact, while `plan_release_run.py:213/248` puts the payload into the evidence envelope agents read. The repo's own `charness-artifacts/release/latest.md:108` currently carries the effect. The arm exists to implement the repo's 2026-05-17 empty-policy lesson (distinguish deliberate-empty from unwired), the same convention implemented in `retro/scripts/check_auto_trigger.py:56-69`, and a test explicitly pins that advisory-only still *blocks* on a failed configured command so it cannot become a bypass. Correct part of the candidate: no code branches on the label — the delta is evidence-semantic, not control-flow.

**`presets/*.md` bodies** — `presets/`. The mechanical half is accurate (bodies have zero runtime effect; behavior is keyed to the preset *id string*). The conclusion is refuted four ways. A June 2026 repo audit deleted `skills/public/quality/references/sample-presets.md` explicitly *because* "vulture is already in `presets/python-quality.md`" — content was deliberately consolidated into the bodies and now lives nowhere else. `docs/deferred-decisions.md` D9 and D13 record the markdown-first preset contract as an intentional decision with reopen triggers. The bodies are advertised by name in `presets/README.md` (which *is* agent-routed) and shipped downstream via `packaging/charness.json`. And they receive continuous substantive maintenance — commit `3b0750a6` (dated today) wrote a hard-won `specdown run -out` gate lesson into `presets/specdown-quality.md:33-37`. Structurally there is no two-armed branch here at all; it is documentation correctly kept out of the runtime path per the repo's own stated rule.
**What survives:** `presets/specdown-quality.md:24-28` duplicates `DEFAULT_SPECDOWN_SMOKE_PATTERNS` (`scripts/quality_policy_defaults.py:6-11`) verbatim with no drift gate and no test pinning it. That is a documentation-drift nit.

---

## Not covered by this sweep

- **Scope discipline, deliberately:** options with a real distinct delta were excluded even when never passed. Named for the record so they are not re-swept: `--include-ready` on `list_tool_recommendations.py` (5 lines vs 212), `--skip-codex-marketplace` on `install_machine_local.py`, `--engine tokei` on `check_test_production_ratio.py`, `--sort` on `inventory_nose_clones.py`, `--keep-basetemp` on `run_standing_pytest.py` (arguably a debug affordance), `cautilus run_mode: ask` vs `adaptive` (the field's `disabled` arm has real teeth and the value has been flipped three times), the `go-quality`/`typescript-quality` preset ids (distinct advisory-string arms, test-exercised).
- **Scouted but never put through the refutation pass** — unadjudicated, not cleared: `presets/monorepo-quality.md` + `quality_bootstrap_detect.py:58` (scout rated this *strong* — a lineage id with no consumer arm, in an order-sensitive if/elif chain where it can never be the deciding element); `quality-adapter runtime_profile_default: default` (the literal value is defined to be indistinguishable from omission, and two prior quality reviews already flagged it as latent); `achieve` `blocked` goal-status arm (0 of 130 goal artifacts have ever reached that status); `plan_quality_run.py` `on_demand_trigger_map` / `required_primer_refs` (self-described compat projections); `plan_release_run_packets.py` critique_reason sub-branch; `--class release` on `measure_startup_probes.py`; `product-slice`/`organization` install_scope validator branches with zero real instances; `profile.schema.json` slots (`extends`, `support_skills`, `integration_ids`, `required_integrations`) no profile sets; `preset_id`/`customized_from` provenance in 7 non-quality adapters.
- **Static analysis only.** This is grep, AST reading, `git log -S`, and a handful of in-process differential runs against the *current* worktree. It cannot see runtime invocation on any other machine, in any installed host, in any downstream repo consuming the exported plugin, or in shell history. Charness ships as a plugin: several confirmed items (`run_mode: auto`, `achieve default_mode`, `hitl default_scope`, the cautilus enum) are *published portable contracts*, and this repo structurally cannot observe whether a downstream adapter sets them.
- **Artifact counts are a proxy, not proof.** "No `charness-artifacts/` record was ever produced by this arm" means the arm left no trace in committed artifacts — not that it never ran. Artifacts are written selectively and pruned.
- **Agent-selected options are invisible to caller-greps.** The `reviewer_tiers.medium` refutation is the cautionary case: the absence of a `--tier` CLI flag looked like proof of no caller, but the selector is prose in a shared reference that agents read. Any option whose "caller" is an instruction in a SKILL.md or reference doc can be missed by a flag grep alone. `plugins/` and `mutants/` were excluded from greps as generated/derived trees; if a generated surface diverges from its source, this sweep would not see it.
- **Not swept at all:** hooks, `integrations/` manifests, `.github/workflows` inputs, environment-variable switches, `charness` CLI subcommand options, adapter fields in the non-quality skills beyond the enums listed, and dead code that is not option-shaped (unreachable functions, unused imports, orphaned references).
- **The sweep is a point-in-time read** against a worktree that had at least one uncommitted local edit (`.agents/cautilus-adapter.yaml`), noted above.

---

## Operator Disposition (2026-07-25)

Signed off after the report was read. Acted on in the same session; the deletions
landed together in one slice.

**Deleted (4):**

- #8 `--scan-comments` — removed with its threaded `scan_comments` parameter. The
  `_`-prefixed-key skip is now unconditional, and its test was rewritten to nest the
  comment inside a visible key so it actually exercises the skip (the old fixture
  used a top-level `_comment`, which the visible-key filter drops regardless).
- #5 `required = False` and its three dead consumer arms — including the
  `missing_required_proof` block in `run_slice_closeout.py`, which could not execute.
  `next_action` was deliberately left alone, as the sweep warned.
- #7 `--replace-file` — flag only. The guard it relaxed became a hard refusal, keeping
  the "a helper does not clobber a file it did not create" property.
- #9 `profiles/*.json` instances — the four instance files. `profile.schema.json`,
  `README.md`, and the directory stay (packaging requires `profiles_dir`), and the
  README now states plainly that no instances are checked in and why.

**Kept (5), with reasons:**

- #1 hitl `default_scope`, #2 achieve `closeout_publication.default_mode`, #3 cautilus
  `profile_default`, #4 cautilus `run_mode: auto` — all published portable contracts.
  Deleting them narrows a contract downstream repos may already set and this repo
  structurally cannot observe. Cost to keep is near zero.
- #6 `--granularity` — kept and **scheduled for extension rather than removal**. It is
  not accidental: the pilot goal artifact records granularity as a real design axis
  (sentence / paragraph / section / whole-file) with only `section` implemented, and
  the library-level guard is reachable via `build_split_manifest`. Going finer than
  `section` is what would distinguish load-bearing prose from decoration inside a
  section.

**Newly surfaced during the deletion, not yet dispositioned:**

- `recommended_commands` in `plan_cautilus_proof.py` is the same shape as #5 — a dead
  literal from the same commit (`66c7a729`), emitted as a payload key and pinned only
  by a constant-asserting test. It was left in place because it was not part of the
  sign-off, not because it was judged different. It needs the same decision.

**Side effects worth knowing:** the deletions shrank code until three previously
distinct spans matched, hard-blocking the dup ratchet. One was genuine intra-file
duplication in `refresh_current_pointer.py` and was extracted into a shared helper;
the other two (a three-term boolean predicate, the argparse `main()` preamble across
five CLIs) were classified `intentional` with reasons in `dup-review.json`. Removing
the `required` branch also took `run_slice_closeout.py`'s only `disabled` string with
it, so that file's attention-state declaration entry — which had been asserting a
visibility that lived inside unreachable code — was retired.
