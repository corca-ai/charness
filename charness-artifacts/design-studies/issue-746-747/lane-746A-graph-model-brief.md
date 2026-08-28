# Lane brief: 746-graph-model (lane A)

Governing contract: read
`charness-artifacts/design-studies/2026-08-28-issue-746-topology-core-plan.md`
(rev 2) FIRST and follow it exactly — especially D1 (node/edge/root model),
D1a (role rules — the ordered table is normative, do not invent rules), D1b
(mirror rule table — transcribe from `scripts/packaging_lib.py`
`export_plugin_tree`, do not summarize), D3 (determinism), D6 (command
conventions: `--exclude-prefix` defaults, exit classes), D8 (fixtures), D9
(no YAML crate; frontmatter-subset reader). Do not spawn descendant agents.
Read `scripts/packaging_lib.py`, `scripts/runtime_bootstrap.py`
(`import_repo_module`, `skill_script`), `pyproject.toml`, and the existing
crate modules before writing code.

## Outcome (this lane only)

In `native/repograph/` (touch nothing outside `native/`):

1. Typed node/edge/root model per plan D1 (serde Serialize; input-facing
   config structs use `deny_unknown_fields`).
2. Graph builder: file nodes with D1a roles; package nodes + `packages`
   edges; skill nodes (frontmatter-subset reader; `malformed-skill` for a
   candidate without valid frontmatter — `skills/public/handoff` is the
   live case; candidacy excludes `generated/` and upstream-consumed
   support ids exactly as `packaging_lib.py` discovery does); adapter
   nodes from the explicit enumerated `.agents/*` table with
   `unmodeled-declaration` fallback; mirror pairs from the D1b rule table
   with `unmodeled-mirror-rule` + `content-transformed` typing; `imports`
   edges (reuse the existing parser: plain imports, `from` imports,
   `import_repo_module(__file__, "pkg.mod")` call form, `sys.path.insert`
   + import, pytest-pythonpath plain imports); `documents` edges (markdown
   links to snapshot files); `tests` as a VIEW over imports/invokes whose
   source role is `test` (roles resolve first).
3. `graph` command: full emit per D6 (pure report, exits 0/2/3;
   `--exclude-prefix` repeatable, default `plugins/` +
   `native/repograph/fixtures/`; `--analyzer-result <file>` repeatable —
   plumbing only: accept, record identity, mark the affected scope
   `unestablished` with a typed `analyzer-not-parsed` condition; lane D
   implements real parsing later).
4. Determinism: builder dedups inventory paths; stable (class, id)
   ordering; double-build byte-equality test pinned via `--file-list`.
5. Fixtures (extend `native/repograph/fixtures/`, snake_case `.py` names,
   markdownlint-clean `.md`, no `key`/`token`/`secret` JSON member names,
   short non-hex-looking digests): cross-package import cycle, mirror
   pairs (collapse rule + one subtractive rule), a Go-shaped tree
   (`x.go` + `x_test.go` + `testdata/`), role-rule cases including a
   conflict → `unestablished` with both rules named, and a skill with
   missing frontmatter.
6. Tests: role table cases (every rule row + tie-break + conflict),
   mirror-pair derivation vs a small fixture manifest, malformed-skill,
   adapter fallback, determinism. `cargo test`, `cargo fmt -- --check`,
   `cargo clippy --offline --all-targets -- -D warnings`,
   `cargo build --release --offline` all green.

Whole-repo sanity to run and report (not to assert in tests): `graph` over
the real repo — report node/edge counts per class, the mirror-destination
count, the number of `unmodeled-mirror-rule` and `unmodeled-declaration`
entries, and the role census (count per role including unestablished).

## Boundaries and non-claims

- Only `native/**`. The four frozen v1 commands' inputs/schemas/exit
  contracts unchanged; the shared usage string and its verbatim copy in
  `ABI.md` are updated together (additive line only).
- No YAML crate; no new dependencies without a one-line justification and
  exact pin (offline cargo cache is provided via CARGO_HOME; network may
  also work).
- No invokes-edge extraction, no classify/changed/components/explain
  commands, no analyzer parsing — later lanes. Design module boundaries so
  those lanes add modules rather than rewriting yours; add dispatch-arm
  stubs ONLY for `graph`.

## Stop condition and result shape

Stop when the battery above is green and the whole-repo `graph` run
completes. One coherent commit, prefix `topo(746):`. Final message: what
was built, exact commands + observed results including the whole-repo
census numbers, any deviation from plan rev 2 with its reason, and the
module map lane B/C1 will build on.
