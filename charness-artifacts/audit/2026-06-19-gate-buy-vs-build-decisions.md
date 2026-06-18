# Gate buy-vs-build — deep analysis + decided plan (2026-06-19)

Companion to the first-pass triage
([2026-06-19-gate-buy-vs-build-triage.md](./2026-06-19-gate-buy-vs-build-triage.md)).
This record holds the **steelman-vs-critique** of each BUY candidate's bespoke
intent (4 independent read-only subagents), the **operator's refinements**, the
**verified facts**, and the **decided plan** — so the next session executes
without re-deciding. North-star lens: P1 (reversible-work gate bears the burden),
P5 (teeth only at irreversible boundaries), "count is not a metric."

## Verified facts (re-checked this session, different channel)

- **markdownlint CANNOT catch a broken relative link.** `markdownlint-cli2 0.21`
  on `[x](./does-not-exist.md)` → 0 errors for that link. So "BUY doc-links →
  markdownlint" is false; there is no off-the-shelf broken-relative-link checker
  installed except **lychee**.
- **lychee IS on the machine** (`~/.cargo/bin/lychee`) but is **not a charness
  managed integration** (no `integrations/tools/lychee.json`) → gates can't use it.
- **tokei is file-level only** (no per-function counts; stated in
  `check_python_lengths.py` comments) → the file-length cap already uses tokei;
  the function cap cannot.
- **ruff PLR0915 (too-many-statements) is available** (pylint port, default
  max-statements 50, `lint.pylint.max-statements`). mccabe complexity 15 already
  enabled (`pyproject.toml`).
- **nose v0.13.0 markdown dup = char-n-gram MinHash** (order-invariant, robust to
  scattered single-word diffs; PR-AUC 0.995/0.944) → resolves the prior
  "block-clone ≠ whole-file similarity" objection that kept difflib. CLI:
  `nose query <path> --format json` (markdown family array), `--baseline`/
  `--write-baseline`/`since=`/`--fail-on new`. Gather asset:
  [2026-06-19-nose-v0-13-markdown-duplication.md](../gather/2026-06-19-nose-v0-13-markdown-duplication.md).
  Local nose checkout is at v0.13.0.

## Per-item steelman/critique verdicts + DECIDED plan

### ① `validate_critique_packet` (179 lines) → DELETE (decided, IN PROGRESS)

- Steelman: the cross-field invariants (`section_count==len`, `ok==all-ok`,
  id-uniqueness) are genuinely unbuyable by jsonschema.
- Critique (wins): those invariants **re-check the producer's own arithmetic**
  (`critique_packet_lib.build_packet` computes `len()`/`all()`; the validator
  re-derives the same from the same code path) = circular. Wired into **no gate**;
  the only live reader of the JSON aggregates is the producer's in-memory dict;
  reviewers consume the `.md`. Producer correctness is already covered by
  `test_build_packet_envelope_shape` / `..._one_failed_section...`.
- **Decision: DELETE outright** (NOT jsonschema — that adds surface for zero
  protection). Confidence HIGH.

### ② `check_doc_links` (396 lines) → lychee BUY + split (decided)

- Verified: no buyable broken-relative-link checker except lychee (above).
- Steelman (KEEP ~90 lines, P5): `validate_link` broken-relative-link resolution
  + repo-boundary escape (#43) + **portable-skill `<repo-root>/` placeholder**
  convention (used in 24 exported SKILL.md — ships to operators). Empirically
  not covered by any installed tool.
- Critique (DELETE/soften ~170 lines, P1): the backtick-as-link + bare-mention
  **house-style** enforcement.
- **Operator refinement:** "linkable-things-should-be-links 원칙은 맞다. 그냥
  백틱 규칙이 FP/FN이 너무 많았다." → keep the PRINCIPLE, do **not** delete it;
  **demote the noisy backtick/bare-mention enforcement to advisory**.
- **Decision:** (a) add `integrations/tools/lychee.json`, make lychee a managed
  binary; move broken-relative-link resolution → lychee. (b) KEEP bespoke residue
  (`<repo-root>/` placeholder + repo-boundary + canonical-surface — lychee can't
  express). (c) Demote backtick/bare-mention enforcement to **advisory** (keep
  the principle/signal, drop the FP-heavy block).

### ③ `check_python_lengths` FUNCTION-length cap → ruff PLR0915 (decided)

- Steelman: line-count is a distinct signal from mccabe (catches long-but-simple);
  #332 retro shows the hard cap caught real over-accumulation.
- Critique + **operator refinement (decisive):** "길이는 복잡도의 프록시 → 그냥
  statement 수 + 복잡도를 직접 보면 된다." PLR0915 (statements) catches the
  long-but-simple case mccabe misses, is a **better proxy** than AST-span
  line-count (which counts blanks/comments), and is a configured tool rule (the
  craken pattern). tokei can't do per-function.
- **Decision:** enable ruff **PLR0915** (tune `max-statements` so current repo
  has ~0 violations, like the file-cap approach) + keep **mccabe 15**; **delete
  the bespoke AST function-length arm** (`validate_function_lengths` + its hard
  raise + caps + warn bands). **File-length cap stays bespoke+tokei (unchanged).**

### ④ `check_doc_near_duplicates` (123 lines) → nose advisory (decided)

- Algorithm objection resolved (char-n-gram, above).
- **Operator decisions:** "nose advisory 좋음. nose는 필수설치." → replace
  difflib with `nose query --format json` markdown families, **ADVISORY (not
  blocking)** posture (matches all other nose integrations), and make **nose a
  REQUIRED install** (`integrations/tools/nose.json`: bump constraint to
  `>=0.13.0`, drop `degraded` access mode / advisory doctor → required). Mirror
  the `nose-baseline.json` drift pattern with a separate doc baseline (or
  `since=`/`--fail-on new`). Delete difflib gate + tests + mirrors + the
  `run-quality.sh:481` / `.githooks/pre-push:60` wiring + adapter budget keys;
  rewrite `docs/duplicate-detection-strategy.md` §1 (it currently promises the
  bespoke gate survives nose absence — no longer true once nose is required).

## Still-queued DEMOTION items (from the prior turn, decided, not started)

- **`validate_critique_artifacts`** (375): keep `validate_reviewer_tier_evidence`
  (tier-honesty) BLOCKING; demote `validate_structured_findings` (form) +
  `_check_forbidden_blocker_phrases` (brittle phrase blocklist) to advisory
  (raise→WARN, the run-quality.sh:294 surfacing pattern from B1).
- **`validate_skill_ergonomics`** (324, run-quality:382): keep the export-leak
  arm (`portable_package_issue_anchor`, `portable_package_dated_incident`)
  BLOCKING; demote the 7 authoring-taste rules to advisory. DELICATE — needs the
  adapter `skill_ergonomics_gate_rules` split into blocking/advisory lists
  (adapter-contract change, same class the operator withdrew for length-config);
  confirm appetite before doing.

## Withdrawn / settled

- **length-floor config-ification: WITHDRAWN.** SKILL.md 200-line cap +
  core-headroom ratchet (160/4) + Python file-line caps stay **hard + hardcoded**
  (no off-the-shelf rule exists; the operator declined the adapter-constant
  compromise).

## The demotion mechanism (B1 pattern, reuse for all advisory demotions)

A gate that exits 0 but prints a line starting `WARN:`/`ADVISORY:` is surfaced
**non-blocking** by `run-quality.sh:294` (`print_phase_output`). So "demote to
advisory" = change the violation path from `raise`/`exit 1` to print a `WARN:`
line + `return 0`, and (if it has a blocking wiring flag like `--strict`) drop
that flag in run-quality.sh + staged_commit_gate_plan.py. Keep a focused test;
beware `inventory_boundary_bypass` no-increase ratchet — test CLI advisory
behavior **in-process** (main() + capsys), not via a new subprocess assertion
(that flips the test file to keep-boundary; cost us a fix in B1).
