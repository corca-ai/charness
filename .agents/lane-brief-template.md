# Lane brief template

Copy this template for every `charness task run` lane brief. It encodes
the scope and format rules this repo has already paid to learn (see
`claude-host.md` lane-orchestration lessons). A brief that omits a
section must say why in that section's place, not delete it.

```markdown
# Lane brief: <lane-name>

Governing contract: <link to the design study / issue that owns this
work, naming the specific decisions (D-numbers or sections) that are
normative for this lane>. <If sibling lanes run concurrently on shared
files, name them and state the additive-change rule.> Do not spawn
descendant agents.

## Outcome

<Numbered, checkable deliverables. Each item states observable behavior
or an artifact, not activity. Include the verification the lane itself
must run before reporting done.>

## Boundaries

<The exact path scope. This list MUST match the `--scope` flags of the
task run — a brief instructing a path outside `--scope` invalidates the
lane. Name what is out of scope, frozen contracts that must not change,
and generated surfaces the lane must not hand-edit.>

## Verification

<The canonical runners, by name — never ad hoc pytest/py invocations:
- focused tests: `python3 scripts/gates_support/run_standing_pytest.py <paths>`;
- gate labels: `./scripts/run-quality.sh <label>` with the exact label;
- Rust work: `cargo test` / `cargo fmt --check` /
  `cargo clippy -- -D warnings` / `cargo build --release` in
  `native/repograph`.
State which of these the lane runs and which the parent runs after
integration. Lane self-reports are not integration proof.>

## Stop condition and result shape

<One coherent commit with the agreed prefix. Final message: what was
built, commands run with observed results, and every deviation from
this brief with its reason. Stop at the stated outcome; do not widen
into a repo audit.>
```

Format rules that have burned lanes before:

- State scan/skip/match sets by CITING the owning source (file and
  symbol or line), never by paraphrase. A brief that describes a rule in
  its own words invites a lane to implement a second, subtly different
  rule: "scans outside fences and inline code, matching `iter_doc_lines`"
  read as two contradictory clauses and sent a real-repo subject set to
  zero. Write "the scan set is exactly what `<file>:<symbol>` yields"
  and let the lane read it.
- Seam fakes must reject malformed argv, not only emit the right
  payload. Pin the argv SHAPE — a fake that tolerates `--path a b c`
  lets a real usage-error (exit 2) regression ship past every lane test.
- `.agents/*-adapter.yaml` checklist entries are single-line quoted
  strings; adapter readers refuse multi-line continuations.
- Markdown artifacts must pass the repo markdownlint gate.
- Fixture `.py` files count toward `check_test_production_ratio.py`'s
  production denominator; note the drift when adding many.
- No `key`/`token`/`secret` member names for digest-bearing values
  (gitleaks generic rules).
