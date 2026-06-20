# Spec — Skill-Body Diagnosis + Per-Body Disposition (S0 gating artifact)

Status: **LOCKED** — S0 fresh-eye gating critique PASS-WITH-CONDITIONS folded (this run, 2026-06-20); cure slices (S1–S4) may proceed
Goal: [2026-06-20-skill-body-redesign-and-release.md](../goals/2026-06-20-skill-body-redesign-and-release.md)
Provenance: all 20 public cores measured with `check_skill_surface_preflight._core_nonempty_lines`
(cap 160, buffer 4); each body diagnosed by an independent agent against the locked
§5 instrument set + its `check_skill_contracts` pins, then adversarially verified by
a second agent against the actual body (a distinct evidence channel). Raw verified
records: [2026-06-20-skill-body-diagnosis-results.json](./2026-06-20-skill-body-diagnosis-results.json);
measured input: [2026-06-20-skill-body-measured-input.json](./2026-06-20-skill-body-measured-input.json).
Instrument definitions: [per-unit-disposition concept spec §5](./2026-06-20-per-unit-disposition-concept.md).

This artifact **is the contract that gates every cure slice (S1–S4)**. A cure may
land only for a body with a `cure` disposition here, applying the cure this
diagnosis names, and only after the pre-cut check + a per-body fresh-eye pass at
edit time. Success is concept clarity + headroom-where-warranted, **never** line
count ([goodhart retro](../retro/2026-06-20-goodhart-not-line-count.md)).

## What S0 locks

1. The **pre-cut lossless + contract-safe check** (`scripts/check_skill_cut_safety.py`,
   built and tested this slice) — the declarative instrument that replaces the
   manual lossless+contract-safe ritual.
2. The **per-body disposition table** — for all 20 bodies, a named length-cause +
   a `cure`-or-`defer-with-cause` disposition, each adversarially verified.
3. The **binding constraints** every cure inherits (the corrected cures for the 7
   `revise` verdicts; the cure-is-still-a-hypothesis rule; the convert-to-defer
   rule when a cure cannot be made lossless+contract-safe).

## The pre-cut check (built in S0)

`scripts/check_skill_cut_safety.py` composes the two existing pin surfaces and adds
the missing lossless half, keyed to the lines a cut actually removes:

- **BLOCK** (exit 1, deterministic — a wrong answer escapes): a removed phrase
  broke a CORE pin (`check_skill_contracts.CORE_CONTRACTS`, must stay in `SKILL.md`),
  a PACKAGE pin (may move to a reference but must survive the package), or a
  `tests/` literal (`check_prose_pin` test-literal scan).
- **REVIEW** (exit 0, judgment — surfaced not blocked): a removed prose line
  vanished with no reference home. Confirm it is a justified **no-op deletion**
  (the §5 no-op test, legitimate, needs no home) or re-home its content. Blocking
  "every removed line must reappear" would forbid the prune cure the diagnosis-first
  doctrine depends on — so this stays REVIEW; `--strict` opts into failing on it.

Locked by `tests/quality_gates/test_check_skill_cut_safety.py` (contract-break
BLOCK, test-literal BLOCK, reference-home-gap REVIEW, sprawl-split-is-lossless
clean, package-pin-may-move clean, `--strict`). Documented in
[authoring-preflight.md](../../docs/conventions/authoring-preflight.md) and
drift-guarded.

**Known blind spot (defense in depth, precisely scoped):** the gap applies **only
to a phrase pinned *exclusively* as a `tests/` literal** — that half inherits
`check_prose_pin`'s `MIN_PROSE_LENGTH = 24` threshold, so a test-only literal
shorter than 24 chars (e.g. find-skills' `routing miss this`, 17 chars) escapes the
deterministic scan. The contract half (`contract_pin_breaks`) has **no length
filter**: a short CORE/PACKAGE pin (down to setup's 9-char `normalize`) is caught
deterministically. So the only uncaught case is a short, test-only-pinned literal.
The **per-body fresh-eye review at each cure slice is the backstop** for it — the
rung-1 (deterministic presence) + rung-2 (fresh-eye honesty) split from the
per-unit-disposition concept. The check is a helper, not a new commit gate; the
contract gate, prose-pin, and core-headroom ratchet stay the enforcement.

## Cross-cutting findings

- **One dominant length-cause: duplication via negative-restatement.** 15 of 20
  bodies diagnose as `duplication`, 3 `mixed`, 1 `sprawl`, 1 `justified-density`.
  The repeated signature is a `## Guardrails` cluster of "Do not …" bullets that
  mirror, in negative form, rules already stated positively in the numbered
  Workflow / Bootstrap or owned by a reference. The cure is overwhelmingly **§5.5
  named-heuristic collapse + §5.2 single-source cite** — a clarity win independent
  of line count (the reader stops cross-checking a negative mirror against the
  positive procedure). This makes the cures lower-risk than a content rewrite: they
  collapse restatements, they do not cut load-bearing concept.
- **19 cure + 1 defer-with-cause (hotl).** `hotl` (left 46) is deferred with cause:
  its body carries the recorded-decision vocabulary (7 ledger statuses, 7 staleness
  adjudications, 6 proof-class rules) a judge needs to close an **irreversible** live
  loop inline; pulling it to a pointer is a clarity regression, and its guardrails
  sit exactly at the "do not close as verified while proof is missing" boundary the
  north star wants teeth at. This proves count was not the metric — a roomy,
  curable-looking body was left alone with cause. Roomy bodies with a **localized**
  defect (quality's anchor catalog, handoff's 14-bullet wall) correctly cure only
  the defect and defer the rest.
- **The binding risk is the pin hazard, and diagnosis is a hypothesis.** The
  adversarial verify caught that **4 of 20 proposed cures (issue, impl, find-skills,
  retro)** would break a pin the diagnosing agent missed — because it reasoned only
  from `check_skill_contracts` pins and missed **dedicated test files** that assert
  `SKILL.md` literals (`test_issue_closeout_discipline.py`,
  `test_docs_and_misc.py`, `test_find_skills_routing_drive.py`) and a **package-pin
  paraphrase** in a reference (retro). This is precisely why the pre-cut check + the
  per-body fresh-eye are **mandatory before each cure**, and why every cure below is
  still a hypothesis until both pass against the actual edit.

## Per-body disposition table

`core`/`left` from the measured input (cap 160). Verify = the adversarial
fresh-eye verdict. A `revise` is a bounded correction folded as a binding cure
constraint, **not** a rejection of the disposition.

| Body | core/left | Cause | Disp | Cure (primary instrument) | Verify | Binding constraint / pin hazard |
| --- | --- | --- | --- | --- | --- | --- |
| issue | 159/1 | duplication | cure | §5.5 collapse + §5.2 cite (17-bullet Guardrails mirror the numbered flow) | revise | **PIN HAZARD:** keep verbatim the test-pinned literals `Do not silently retarget on retry`, ``Render `issue new` closeout only from the verified``, and L146 manual-close fallback (re-home the literal, do **not** prune it). Disposition all 17 bullets (keep L150 public-fetch nuance, L163 multi-issue-coupling). |
| impl | 158/2 | duplication | cure | §5.2 cite + §5.5 collapse (Step-4 thicket paraphrases 2 refs; Cautilus cluster restates cautilus-on-demand.md) | revise | **PIN HAZARD:** Cure A must preserve verbatim the `test_docs_and_misc.py` literals (`cautilus evaluate fixture …`, `cautilus evaluate observation …`, `review or closeout wording must not silently launch Cautilus`); single-source only the surrounding prose. C/D/E + critique-cluster collapse are pin-safe. |
| debug | 157/3 | duplication | cure | §5.5 collapse + §5.2 cite (discipline stated 3×; anti-pattern roster → cite) | sound | Clean. |
| achieve | 156/4 | duplication | cure | §5.5 collapse (14-bullet Guardrails negate the Workflow) | revise | **COMPLETENESS:** KEEP L162 (`not every prompt is a goal` — distinct, no positive twin); add L175-176 to the prune set (positive twin at L114). Empty pin set. |
| create-skill | 156/4 | duplication | cure | §5.2 cite + §5.5 collapse (principle appears in Workflow + Rules×2 + ref) | revise | **PRECISION:** Cure A off-by-one — PRESERVE L124-125 (concept-singularity invariant, not an anchor bullet); anchor bullet is L126-128. Keep L150 secrets-safety as optional, do not fold. B/C/D safe. |
| create-cli | 155/5 | duplication | cure | §5.2 cite + §5.6 catalog split + §5.5 collapse (gate + command rosters duplicated) | sound | Empty pin set; clean. |
| hitl | 155/5 | duplication | cure | §5.5 collapse + §5.1 no-op (16-line negative checklist mirrors 12-step Workflow) | sound | Empty pin set; clean. |
| release | 155/5 | duplication | cure | §5.5 collapse + §5.2 cite (publish-boundary/critique-gate stated 2×) | sound | Keep the 6 CORE pins + 4 `Critique:` package tokens + FORBIDDEN `local critique` absent. |
| announcement | 152/8 | duplication | cure | §5.5 collapse + §5.1 no-op (Guardrails restate Workflow steps) | sound | Empty pin set; clean. |
| find-skills | 152/8 | duplication | cure | §5.2 single-source (routing-miss rule stated 3× in-body) | revise | **PIN HAZARD (short-pin blind spot):** tighten the Guardrail bullet but keep verbatim `Do not stop after emitting the inventory` and `routing miss this` (`test_find_skills_routing_drive.py`); remove only the re-derived `charness:handoff` mechanic. Already partially cured in `f496812b`; diagnose residual only. |
| critique | 150/10 | duplication | cure | §5.2 cite + §5.5 collapse (canonical-subagent rule stated 6×) | sound | Keep 6 CORE pins + FORBIDDEN `short bounded local pass` absent. |
| gather | 149/11 | duplication | cure | §5.2 cite + §5.5 collapse (symlink hazard + source-priority stated 2×) | sound | Keep 6 CORE + 3 PACKAGE pins (PACKAGE may move to a ref). |
| spec | 148/12 | mixed | cure | §5.2 cite + §5.5 collapse (Guardrails echo Workflow/Contract-Shaping) | sound | Keep 11 CORE pins (incl. the `Fixed Decisions`/`Probe Questions`/… roster) + 5 PACKAGE. |
| ideation | 147/13 | duplication | cure | §5.5 collapse + §5.2 cite + §5.6 split (demand/wedge/moat met 4×) | sound | Empty pin set; clean. |
| retro | 146/14 | sprawl | cure | §5.2 disclose-split (16-line flag-plumbing → phase-aware-efficiency.md) + §5.2 single-source | revise | **PIN HAZARD (check defends this):** the `Trends vs Last Retro` package-pin literal at L81 is **not** verbatim in section-guide.md (only a paraphrase), so the pre-cut check **BLOCKs** its removal (PACKAGE pin not surviving the package). Either leave L81 untouched (collapse Output Shape only) or move the full pin literal into a reference first. Other pins safe. |
| narrative | 144/16 | mixed | cure | §5.5 collapse + §5.2 cite (announcement/ideation routing + source-trust stated 3×) | sound | Keep 6 CORE pins. |
| setup | 137/23 | mixed | cure | §5.5 collapse (3 scope negatives) + §5.2 single-source + §5.1 no-op | revise | **PRECISION:** collapse ONLY L149/L151/L153 into the "stay narrow" heuristic; L145 (`check concept before scaffolding`) is a distinct rule — single-source it to L105, do not fold. 8 CORE pins all survive. |
| handoff | 125/35 | duplication | cure | §5.5 collapse (14-bullet wall) + §5.2 cite (only ~2 bullets add info) | sound | Keep 4 CORE + 2 PACKAGE pins; KEEP mention-only-pickup + `unverified state as fact` bullets. |
| hotl | 114/46 | justified-density | **defer-with-cause** | — | sound | **No edit.** Irreversible-boundary vocabulary (7 statuses / 7 adjudications / 6 proof rules) must stay visible inline; cutting is a clarity regression chasing a count already 46 under ceiling. |
| quality | 103/57 | duplication | cure | §5.6 anchor-split + §5.2 single-source (Load-Bearing-Anchors catalog duplicates inventory-dispatch.md) | sound | Localized to the anchor catalog only (defer the roomy clear body). Keep 4 CORE pins on L110-112; the 2 PACKAGE pins on the moved L116 survive in inventory-dispatch.md + public-spec-layering.md. |

## Binding constraints carried into S1–S4

1. **Every cure runs the pre-cut check before it lands**
   (`python3 scripts/check_skill_cut_safety.py --path skills/public/<id>/SKILL.md`),
   and resolves every BLOCK and reviews every REVIEW, before commit.
2. **Every cure is a governing skill-surface edit → a per-body bounded fresh-eye
   critique before commit** (the short-pin backstop; reviewers run read-only in the
   shared parent worktree per
   [fresh-eye-subagent-review](../../skills/shared/references/fresh-eye-subagent-review.md)).
3. **A cure is still a hypothesis** until the pre-cut check + fresh-eye pass against
   the actual edit. If a body's cure **cannot** be made lossless+contract-safe
   without a contract/test change, it **converts to defer-with-cause** rather than
   forcing the cut (or routes to the operator ODQ — below).
4. **No contract change is required by any cure** if the pinned literal is preserved
   verbatim or re-homed verbatim. The issue/impl/find-skills/retro pin hazards each
   have a verbatim-preserve path; **prefer it** over updating a pinned test (which
   would be a contract change → operator ODQ #2). Only escalate to the operator if a
   verbatim-preserve path genuinely does not exist.
5. **Sync barrier:** re-run `scripts/sync_root_plugin_manifests.py` before validators
   after each SKILL.md edit (`staged-plugin-mirror-drift`).
6. **Public-skill validation** per cured body at slice boundaries (Cautilus
   eval-only/ask-before-run — currently `next_action: none`, so disabled this run;
   recorded fresh-eye; dogfood refresh).

## Re-batched slice plan (confirmed)

S0's diagnosis confirms the up-front tier batching with one change: **hotl is
defer-only (no edit)**, so S4 cures 8 bodies, not 9.

- **S1** issue · impl · debug — sub-buffer must-fix (issue/impl carry pin hazards →
  pre-cut check + fresh-eye are load-bearing here).
- **S2** create-skill · achieve · hitl · release.
- **S3** create-cli · find-skills · announcement · critique (find-skills carries the
  short-pin hazard).
- **S4** gather · spec · ideation · retro · narrative · setup · handoff · quality;
  **hotl deferred-with-cause (record, no edit).** (retro carries a pin hazard;
  quality is the anchor-split flagship.)
- **S5** release cut (terminal live slice). **S6** closeout.

## Operator Decision Queue (from this diagnosis)

- **No cure requires a contract change** under constraint 4 (every pin hazard has a
  verbatim-preserve path). The goal's ODQ #2 (a CORE-contract/test pin that must
  *move*) is therefore **not triggered** by the diagnosis — unless a cure slice
  discovers that a verbatim-preserve path does not exist, at which point that one
  body escalates to the operator or defers with cause.
- The live-release approval (goal ODQ #1) remains the only operator gate, revisited
  at S5.

## S0 gating critique — PASS-WITH-CONDITIONS (folded, 2026-06-20)

A bounded fresh-eye reviewer (distinct `general-purpose` context, read-only) verified
this artifact against the **actual** code and bodies — a distinct evidence channel,
not a re-read of the spec. Provenance: independently re-measured 6 core counts
(issue 159, impl 158, hotl 114, quality 103, find-skills 152, handoff 125 — all
matched the table); grepped 4 test files directly (`test_issue_closeout_discipline.py`,
`test_docs_and_misc.py`, `test_find_skills_routing_drive.py`, retro's PACKAGE
contract) to confirm each pin hazard and its actual home; read and ran
`check_skill_cut_safety.py` (7 passed) and dissected `check_prose_pin._prose_candidate`
for the blind-spot mechanism.

Verdict: **PASS-WITH-CONDITIONS.** Confirmed: the pre-cut check is real and correct;
all 4 pin hazards are genuine with available verbatim-preserve paths; the 19/20 cure
rate is clarity-driven (achieve's negative-restatement is a real clarity tax; the
REVISE that KEEPs achieve L162 is adversarial discipline, not count-chasing; quality
cures only the localized anchor catalog and defers the roomy body); hotl's
defer-with-cause is genuinely justified (irreversible-boundary vocabulary needed
inline); the gating contract actually gates (the hypothesis / convert-to-defer rules
are binding, no row commits to a line target).

Two precision conditions **folded above**: (1) the blind-spot disclosure now scopes
the 24-char gap to *test-only* pins (short CORE/PACKAGE pins are caught — no length
filter); (2) the retro row now notes the check **BLOCKs** removing its paraphrased
PACKAGE pin. Over-worries explicitly dismissed: the REVIEW-not-BLOCK design (doctrine-
justified, fresh-eye backstop), the scoped blind spot, and the cure-bias risk (guarded
by the hypothesis/convert-to-defer rules + per-body fresh-eye).
