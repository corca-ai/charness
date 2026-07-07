# Retro-Informed Improvement: Five Design Briefs (2026-07-08)

Read-only investigation briefs produced by five bounded fresh-eye subagents,
condensed for next-session implementation. Operator decisions (recorded in the
goal artifact `2026-07-08-retro-informed-improvement-5pack.md`) are folded in
as **DECIDED** lines. Selection rationale: prioritize friction that prior
sessions paid for at least twice over new backlog items.

## Brief 1 — ratio gate: remove the live hard bound (Slice R)

- The live-repo hard ratio bound exists in EXACTLY ONE place:
  `tests/quality_gates/test_test_production_ratio.py:25-26`
  (`assert source_lines > test_lines`; `assert 0 < ratio < 1`) run against the
  LIVE repo. Live: 96803/96808 = 0.9999 — **5 lines of headroom**; any
  test-adding slice trips the whole pytest suite (forced test-trimming in two
  consecutive sessions — Goodhart behavior).
- `run-quality.sh:504` already runs the script gate `--advisory` (demoted
  2026-06-19, `78a1790b`); the script's own help text names the rationale
  (smell sensor, not irreversible boundary; north-star P1).
- Change: replace lines 25-26 with degenerate-zero sanity checks
  (`source_lines > 0`, `test_lines > 0`, `ratio > 0`); keep scope/engine/
  plugin-exclusion asserts. ADD a synthetic `tmp_path` fixture covering the
  under-threshold rc0 branch (mirror lines 97-111 pattern) so all three main()
  ratio branches have per-branch falsifiable fixtures. Keep in-process /
  no-stderr to avoid flipping this file's `likely_keep_boundary` in the
  boundary-bypass ratchet (file is already at `boundary-bypass-baseline.json:51`;
  removal touches no COUNT_FIELDS).
- Test-debt premise caveat: the 2026-07-03 84-agent audit
  (`charness-artifacts/quality/history/2026-07-03-pytest-suite-test-value-audit.md`)
  found the suite lean (bloat "a rounding error"); ratio was 0.9734 then. The
  headroom collapse is the post-audit +~3,160 test-LOC delta. Reduction runway =
  that delta + inline fixture-script duplication (fake `gh` blocks in
  `test_issue_skill.py`, low-hundreds LOC). Parametrize folds are LOC-neutral
  (audit Batch C) — not a lever. Every deletion needs mutation-coverage proof
  (audit's kill-overlap was argued, not executed) + fresh-eye review.
- **DECIDED: advisory-only.** No soft `no_increase` ratchet; no hard sub-target
  (re-Goodharts). Test-debt reduction = standing rotation item scoped to the
  post-audit delta, value-motivated, never headroom-pressured.
- Sequencing: this slice lands FIRST — every other slice in this goal adds
  tests and would trip the current 5-line headroom.

## Brief 2 — conditional required-reads validator (Slice V)

- Incident (retro 2026-07-02): #412/`c1a66f4d` conditionalized
  `skills/public/handoff/scripts/plan_handoff_run.py` (`continuation-sequence.md`
  forced only for ambiguous pickup, `_pickup_needs_continuation_sequence`
  :166-173); the initial plan deferred the ambiguous-arm fixture — a conditional
  required-read NO scenario forced. Operator caught it by hand.
- Mechanically possible today with ZERO schema change: scenario side already
  declares per-ref `engagement` (`engage-always` = "scenario forces this doc";
  RCF is a subset — `scripts/claim_fidelity_lib.py:156-158`, `validate_spec`
  returns per-scenario `engage_always` :200-222). Planner side: forced tier =
  refs emitted into `required_reads` under some code path (handoff:
  `INTENT_REFERENCE_READS` :14-36 + imperative adapter-contract :232-240).
  On-demand tiers (retro/debug `ON_DEMAND_REFERENCE_READS`, issue pause
  actions) are EXEMPT by construction — counting them is the false-positive
  machine (critique has 9 never-forced pure-DEPTH refs, setup 5, gather 4).
- Design: `scripts/validate_scenario_conditional_reads.py` (thin) over
  `cross_check_conditional_reads()` in `claim_fidelity_lib.py`. Per skill:
  flagged = planner_forceable − engage_always_union − waived. Waivers: classTag
  DUP/INLINE (token-moved refs, e.g. state-selection.md) OR
  `validate_scenario_conditional_reads.allowlist.txt` with reason (idiom:
  `check_skill_ownership_overlap.allowlist.txt`). Planner sourcing: per-planner
  extractor registry, handoff first; skills without extractor = advisory
  "not yet covered", never silent pass; per-planner unit test pins extractor set
  == planner forced tier.
- Live truth table verified: continuation-sequence.md covered by
  pickup-ambiguous (removing that fixture reproduces the incident → FLAG);
  TWO real findings surface: state-selection.md still in `judge_from_user_request`
  forced tier (INLINE-waived, no scenario forces it) and adapter-contract.md
  (adapter-health branch unfixtured).
- **DECIDED: blocking + seeded waiver channel (green day one); v1
  handoff-only; the two real findings get waiver+reason in the same slice, not
  new scenarios.** Wiring: after `run-quality.sh:404`
  (`validate-claim-fidelity-specs`); sync plugin mirror. Floor-Addition
  Restraint call must be recorded (new blocking floor; justification: an
  unforced conditional branch's regression escapes the eval = north-star
  "wrong answer escapes"; waiver channel keeps authoring churn bounded).
- Tests: synthetic pass/flag/waived fixtures (reuse `_scaffold_skill` helpers
  from `tests/quality_gates/test_claim_fidelity_specs.py`) + real-repo green
  assert + temp-copy incident reconstruction. ~120-180 lib + ~30 script +
  ~15 extractor + ~150 test LOC.

## Brief 3 — #371 Tier 1: gather-path signal-safe teardown (Slice B)

- Ownership split: the ceal incident's dominant path (raw host tool-call
  `agent-browser ... open` self-daemonizes to PPID=1; host kills only the exec
  client) is NOT charness-reachable — prior disposition split it to upstream
  `vercel-labs/agent-browser#1334`
  (`charness-artifacts/debug/2026-06-15-issue-371-agent-browser-upstream-lifecycle.md`).
  **`docs/handoff.md` item 3's "self-contained" label is wrong — correct it.**
- The charness-owned gap: `skills/support/web-fetch/scripts/acquire_public_url.py`
  `main()` (:293) installs no signal handler; host SIGTERM (turn cancel/timeout)
  skips the `try/finally` → `_close_cleanup_error` → `close_session` chain in
  `browser_fallback_stages.py:82-121` → daemon + profile dir leak. SIGKILL is
  out of scope (runtime-guard reaper is the backstop).
- Fix: SIGTERM+SIGINT handlers + `atexit` in `main()`, best-effort teardown of
  a module-level live-session registry (populate at open, clear at close) via
  the EXISTING `_close_cleanup_error` — no second reaper. Handler must be
  idempotent, never raise, no-op when no session, must not alter normal-exit
  disposition; route through the existing guard (no regression of #302
  fail-visible or #365 cwd-scoping).
- Proof: fake `agent-browser` sh script on PATH logging calls (idiom:
  `tests/test_web_fetch_cleanup.py`); red = SIGTERM mid-render leaves log
  without trailing `close` (proves today's leak); green = log ends with
  `close`.
- **DECIDED: Tier 1 only; #371 stays OPEN** (partial-resolution comment +
  upstream #1334 reference; no `Close #371`). Tier 1b (profile-dir lease) gated
  on a pinned-CLI capability probe (installed v0.9.2 vs latest v0.28.0) —
  deferred, not in this goal. Tier 3 (host-adapter PDEATHSIG watchdog) out of
  scope.

## Brief 4 — dup-ratchet: S4-Defer-1 + S4-Defer-3 combined migration (Slice D)

- Mechanics: v1 fingerprint = rstrip-only normalization
  (`skills/public/quality/scripts/nose_fingerprint_lib.py:45-51`), family
  fingerprint folds sorted duplicate-preserving member hashes (:80-101);
  baseline `dup-ratchet-baseline.json` stores OPAQUE fingerprints only; newness
  = pure set-diff (`dup_ratchet_lib.py:298`) → a rotation is indistinguishable
  from a new family. Live: 546 families, gate CLEAN, `fixable_ceiling=0` (both
  residuals affect only re-baseline churn, not blocking).
- Rotation anatomy: dominant observed driver = MEMBERSHIP SHRINK from template
  extractions (S4-Defer-3), per overlay notes; comment/whitespace edits
  (S4-Defer-1) have zero attributed observations (PQ2 "measure materiality"
  stands). Pure-offset rotations died with D30.
- S4-Defer-1 design (proven by prototype): Python members → `tokenize`, drop
  COMMENT/NL/NEWLINE/INDENT/DEDENT, join kept token strings, hash; per-member
  graceful fallback to v1 on tokenize-fail (4.2% with dedent) or non-Python
  (39 `.mjs` members — accept-and-document). Anti-over-merge proven: real code
  edit still rotates. `FINGERPRINT_ALGO_VERSION` 1→2; migration = member-
  preserving REMAP (S4-D8 machinery, spec :600-611) preserving overlay
  class/note/reviewed_at; add one-shot `distinct(v2 fp)==distinct(nose id)`
  collision assertion (546==546 today).
- S4-Defer-3 design (proven by prototype): baseline schema v3 stores per-family
  sorted member-hash list; pre-pass before hard-block classifies a candidate-new
  family whose member multiset is a PROPER subset of a vanished baseline
  family as REDUCTION → advisory + one-command scoped accept (not silent —
  S4-Defer-2 shrink-then-recur adversary fixture required). Keep `evaluate`'s
  pure set-diff signature (S4-D9); layer as pre-pass to preserve ~15 policy
  tests.
- **DECIDED: A+B combined in ONE slice with ONE migration** (algo bump + schema
  bump together — avoids two back-to-back full re-baselines of the three
  lockstep artifacts: dup-ratchet-baseline, nose-baseline, dup-review overlay).
  Corpus-reduction lever REJECTED (fixable_ceiling already 0; largest families
  are confirmed portable-by-design boilerplate). History probe for S4-Defer-1
  materiality: optional documentation only, since A ships regardless.
- Fixtures: comment-edit stable; whitespace stable; real-edit rotates;
  fallback==v1; migration remap preserves all live intentional ids; reduction /
  genuine-new / grow / shrink-then-recur; schema-v3 migration. ~2 days.
  Implementation must batch ALL scanned-scope edits before the single
  `--write-baseline` (implementation-discipline batching rule).

## Brief 5 — #408 residual item 4: forbidden-string prose guidance (Slice G)

- Original ask (#408 bullet 4): discourage permanent forbidden-string/prose
  assertions except as temporary migration sentinels; disclosed NOT delivered
  in the close.
- Corpus: ~178 `assert "<lit>" not in <blob>` candidates; harmful subset is
  ~10-25 and SEMANTICALLY defined (permanent wording locks over human-authored
  rendered prose — pass vacuously when wording drifts; e.g.
  `tests/test_gather_google_workspace.py:120-121` `"Slack thread" not in
  description`, `tests/test_quality_scaffold.py:108`,
  `tests/test_critique_scaffold.py:51`). Legitimate permanent negatives that a
  syntactic detector would fight: secret/PII leak invariants, quiet-mode output
  contracts, structural dict key-absence, crash-free smokes, migration
  sentinels.
- **DECIDED: prose-only.** One principle + worked example in
  `skills/public/quality/references/unit-test-quality.md`, cross-linked from
  `brittle-source-guards.md` (its negative mirror; pick ONE home to stay
  dup-ratchet clean). Must explicitly bless the legitimate classes and name the
  deferred advisory ratchet as the recurrence-triggered escalation path (per
  that doc's own "policy without enforcement stays visible as follow-up" rule).
  Validator REJECTED under north-star P1: harmful/legit split is not
  syntactically separable. No tracking issue — this goal + handoff carry it.
- Worked example: `assert "Slack thread" not in description` still passes after
  someone re-adds "Slack channel export"; assert the positive scope
  (`"public-source only" in ...`) instead. Size S (~15-30 lines + cross-link +
  catalog/index entries + skill-surface preflight).
