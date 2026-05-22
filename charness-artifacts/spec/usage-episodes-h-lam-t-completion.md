# Spec: Usage Episodes — H-LAM/T Completion (Session + T Signal)

Source: follow-up slice to
[charness-artifacts/spec/issue-171-hlam-usage-episodes.md](./issue-171-hlam-usage-episodes.md).

Sibling decisions: this spec consumes the substrate from #171 and the
slice-closeout emitter from #188, then closes the gap between *H-LAM only*
and *H-LAM/T* by adding session grouping and durable T signal capture.

## Problem

The substrate from #171 defines the H-LAM/T usage episode schema. The emitter
from #188 emits one episode per `run_slice_closeout` success. Two gaps prevent
the maintainer's stated want — "is charness being used usefully, and is value
compounding over time?" — from being measurable today:

1. **No session grouping.** Each closeout episode is independent; the natural
   unit of "one charness use" (a session) is not captured in raw data, so
   utility-per-session and per-session value-add cannot be derived without
   ad-hoc clustering.
2. **`t_status` is hardcoded `"none"`.** The emitter never records *whether
   this slice produced a durable improvement link* (memory, specs, skills,
   evaluation, product workflow). Without T, "value compounding" is
   unmeasurable.

Closing both gaps turns the existing H-LAM stream into a real H-LAM/T stream
that can answer the maintainer's question.

## Current State

- Episode schema: `integrations/usage-episodes/episode.schema.json`.
- Validator: `scripts/validate_usage_episodes.py`. Treats `enabled: true` +
  missing records file as an error.
- Emitter: `scripts/slice_closeout_usage_episode.py`,
  `emit_usage_episode_for_slice_closeout()` called by
  `scripts/run_slice_closeout.py` after a successful closeout. Hardcodes most
  episode fields; `t_status` is always `"none"`.
- Adapter: `.agents/usage-episodes-adapter.yaml`. Currently `enabled: false`.
- No host hooks installed by charness today; `charness init`/`charness update`
  only touch marketplace registration and repo `.githooks/`.

## Fixed Decisions

### Episode and session grain

- One `run_slice_closeout` success = one episode (no change to episode unit).
- A session groups multiple closeout episodes that share a host-emitted
  `SessionStart`. Sessions are *implicit* on the closing side: there is no
  `SessionEnd` event. Session boundary on the reporting side is derived by
  gap-based clustering (no charness activity for N minutes ⇒ prior session
  expired). This avoids relying on Codex `SessionEnd` (absent per
  [charness-artifacts/gather/2026-05-22-codex-hooks-surface.md](../gather/2026-05-22-codex-hooks-surface.md)).
- Episodes are linked to sessions via a new optional `session_id` field on the
  episode schema. When no session pointer is found, the field is omitted (not
  null); reporting treats absent `session_id` as "ungrouped".

### Host hook surface

- charness writes a `SessionStart` hook entry to:
  - `~/.claude/settings.json` (or repo `.claude/settings.json` when present)
  - `~/.codex/config.toml` as the default Codex install target. The Codex docs
    confirm `hooks.json` and `config.toml` are *additive* — both run when both
    exist — but the doc explicitly warns "If a single layer contains both
    `hooks.json` and inline `[hooks]`, Codex merges them and warns at startup.
    Prefer one representation per layer." (See
    [codex hooks surface](../gather/2026-05-22-codex-hooks-surface.md).) To
    honor that guidance and avoid the merge warning, charness installs to
    `~/.codex/config.toml` unless `~/.codex/hooks.json` already exists with at
    least one hook entry, in which case the install target for that layer
    becomes `hooks.json`. Repo-level equivalents take precedence when present,
    matching the Codex docs; the same `hooks.json`-already-present rule
    applies per layer.
- The hook command runs a small charness script (e.g.
  `scripts/usage_episode_session_start.py`) that:
  1. Reads `.agents/usage-episodes-adapter.yaml`. If absent or
     `enabled: false`, exits 0 silently (Layer 3 self-check).
  2. Generates a session id (uuid4).
  3. Writes `.charness/usage-episodes/sessions/<id>/start.json` with the
     hook payload subset (`hook_event_name`, `cwd`, `model`, and a
     charness-generated timestamp) — *not* `transcript_path` or
     `last_assistant_message`.
  4. Atomically refreshes a current-pointer file at
     `.charness/usage-episodes/sessions/current` (symlink-safe writer) to the
     new session id.
- Concurrent SessionStart events from parallel Claude and Codex processes
  race on the same `current` pointer. Resolution: last-writer-wins is
  accepted. Each session's own `start.json` record under
  `sessions/<id>/start.json` is durable regardless of the race; only the
  *pointer* loses one race. Episodes that fire while a pointer is mid-rotation
  attach to whichever id the pointer resolves to at read time. Reporting-side
  gap clustering handles the resulting near-simultaneous sessions; host-scoped
  pointers are out of scope for this slice.
- The slice closeout emitter reads
  `.charness/usage-episodes/sessions/current` if present and attaches the
  resolved `session_id` to the episode.

### Toggle and install posture

- Three-layer toggle, all controlled by the adapter yaml:
  1. **Runtime gate** — `enabled: true/false` (existing field). Validator and
     emitter already honor this. Hook script also honors this so a single
     adapter line silences capture without uninstalling the hook.
  2. **Hook install gate** — new `host_hooks.claude` and `host_hooks.codex`
     fields, each accepting `enabled` or `disabled`. Default `disabled`.
     `charness init`/`charness update` reads these and reconciles host
     settings accordingly.
  3. **Hook runtime self-check** — every hook script reads the adapter and
     exits 0 silently if `enabled: false`. Means runtime can be muted
     instantly without touching host settings.
- `charness init` default behavior: do **not** install host hooks. Seed the
  adapter yaml (or refresh it) with hook fields commented out and a brief
  inline explanation. The maintainer must explicitly set
  `host_hooks.<host>: enabled` and re-run `charness update` to install.
  Rationale: host hooks are intrusive; charness defaults to zero-intrusion.

### Managed entry tracking

- A state file `.charness/usage-episodes/host-hooks-state.json` is the <!-- reproduction-source -->
  authoritative record of which host settings paths and which entry hashes
  charness installed. Uninstall and reconciliation read state first; foreign
  hooks are identified by absence from state, not by absence of a marker.
- Codex `config.toml` entries additionally carry an inline `# charness:usage-episodes`
  marker for human-visible identification; this is *informational only*, not
  used for reconciliation. Claude `settings.json` is strict JSON with no comment
  support, so the marker pattern is not applied there — state-file matching by
  entry hash is the sole identification path for Claude.
- `charness session-capture status` (new subcommand) reports both
  *intent* (adapter yaml) and *actual* (host settings) and names any drift.
  `charness doctor` shells out to this for surface-coverage parity.

### Validator behavior under enabled + no records

- Validator treats `enabled: true` + missing records file as `no_records`
  warning (exit 0), not error. The current behavior (exit 1) makes flipping
  the switch break the gate before any data exists; this is the wrong
  failure mode for an opt-in capture surface.
- `enabled: true` + records file present + schema errors stays as error
  (unchanged).

### T signal classification

- The emitter classifies T at slice closeout time using diff-rule heuristics
  against `git diff HEAD~1..HEAD` (commit range I). Rationale: charness
  commit discipline yields ≈1 commit per slice; closeout fires after the
  commit lands. Multi-commit slices are deferred to a later expansion.
- When `git rev-parse HEAD~1` fails (first commit on a fresh repo, shallow
  clone with depth=1, detached state where the parent ref is missing), the
  classifier does *not* attempt a fallback diff. It emits the episode with
  `t_status: "none"` and `t_evidence: null`, plus a sibling
  `classification_skipped` field carrying the reason (`"no_parent"`,
  `"shallow_clone"`, etc.). Reporting can filter these out without confusing
  them with genuine no-T slices.
- One strongest rule wins and sets `t_status`. Episode also carries a new
  required `t_evidence` field whenever `t_status != "none"`:

  ```json
  {
    "rule_id": "<stable-id>",
    "confidence": "low" | "medium" | "high",
    "matched_paths": ["..."],
    "commit_refs": ["<sha>"],
    "diff_kind": "added" | "modified" | "removed"
  }
  ```

- Initial rule catalog:

  | rule_id | match | confidence |
  |---|---|---|
  | `retro-lesson-path-added` | new `charness-artifacts/retro/<date>-*-session.md` | high |
  | `debug-rca-path-added` | new `charness-artifacts/debug/<date>-*.md` | high |
  | `gate-script-added` | new `scripts/check_*.py` or `scripts/validate_*.py` | high |
  | `gate-script-modified` | modification of the above | low |
  | `quality-runner-modified` | change to `scripts/run-quality.sh` | medium |
  | `convention-doc-modified` | change under `docs/conventions/` | medium |
  | `skill-or-reference-modified` | change under `skills/public/*/SKILL.md` or `references/` | low |
  | `deferred-decision-added` | new D-section in `docs/deferred-decisions.md` | medium |
  | `issue-closed` | commit message matches `Close #N` / `Fixes #N` / `Closes #N` | high |

- When multiple rules match, the *strongest confidence* wins; ties broken by
  rule_id alphabetical order (deterministic, audit-friendly). Secondary
  matches are deferred (not stored) in this slice.

### Privacy posture (unchanged, with one new constraint)

- `raw_prompt: false`, `raw_transcript: false`, `user_identity: none` from the
  adapter remain authoritative. Session-start hook script must not write
  `transcript_path` or `last_assistant_message` into any record. Privacy
  fields stay on the existing assertion path.
- New constraint for consumer products: `t_evidence.matched_paths` captures
  *charness-internal repo paths* by design. Consumer products that adopt this
  classifier with rules whose path components can encode user input (for
  example, a `debug/user-asked-about-<phrase>.md` convention) must redact or
  cap `matched_paths` to the rule's glob/pattern, not the literal matched
  path. The shared schema does not enforce this; product-specific adapters
  do.

## Probe Questions

These are checked during implementation; their answers may revise this spec.

- Does `hook_event_name` arrive literally as `"SessionStart"` on both hosts,
  or is the casing/format different? Confirm before depending on it for
  filtering.
- Is `session_id` stable across a Codex `resume`, or does each resume create
  a fresh id? If fresh, gap-based clustering still works; if stable, gap-based
  clustering may over-merge resumed sessions. Validate against real
  resume behavior.
- Does Claude Code merge multiple `SessionStart` arrays from
  user + project settings, or does the more specific one override? Confirm
  before assuming the maintainer's other hooks survive a charness install.

## Deferred Decisions

- Multi-commit slice support (commit range II/III). Today commit discipline
  keeps slices to one commit; if that changes, revisit.
- Secondary T-signal matches in `t_evidence`. First slice keeps single
  strongest match; expand only when reporting demands multi-rule analysis.
- `charness session-capture` as a top-level CLI subcommand vs nested under
  `charness capability`. First slice ships as a top-level command; revisit
  if CLI surface gets crowded.
- Reporting/visualization of accumulated episodes. Out of scope for this
  slice. The data shape this spec produces is what later reporting consumes.
- Cross-host hook script delivery (where the script physically lives in the
  installed plugin, and how update flow refreshes it). First slice ships the
  script under `scripts/usage_episode_session_start.py` in the canonical
  repo and exports it through the existing plugin packaging path; revisit if
  Codex/Claude path resolution differs in practice.

## Success Criteria

Behavioral, measurable claims this slice must satisfy:

1. With `enabled: true` and `host_hooks: disabled`, `charness init` and
   `charness update` make zero changes to any host settings file.
2. With `host_hooks.claude: enabled`, `charness update` adds exactly one
   `SessionStart` hook entry to the resolved Claude settings file and
   records the install in `.charness/usage-episodes/host-hooks-state.json` <!-- reproduction-source -->
   so future uninstall/reconcile can identify it. Same applies to Codex
   independently; the Codex TOML install also writes a
   `# charness:usage-episodes` comment line above the inserted
   `[[hooks.SessionStart]]` block for human-visible identification. Claude
   `settings.json` and Codex `hooks.json` carry no inline marker (strict
   JSON, no comments); state-file matching is the sole identification path
   for those formats.
3. With `host_hooks.claude: disabled` after a prior install,
   `charness update` removes only the charness-installed entry (verified by
   diffing against fresh-state and marker presence) and leaves any other
   maintainer-installed hooks untouched.
4. With `enabled: false` (Layer 1) but hook installed, the hook script
   produces zero file writes under `.charness/usage-episodes/sessions/`.
5. A slice that lands a new file at `charness-artifacts/retro/<date>-foo.md`
   and runs `run_slice_closeout` emits an episode with
   `t_status: "memory_lesson_added"`, `t_evidence.rule_id:
   "retro-lesson-path-added"`, `t_evidence.confidence: "high"`,
   `t_evidence.matched_paths` containing the new path,
   `t_evidence.commit_refs` containing the HEAD sha, and
   `t_evidence.diff_kind: "added"`.
6. The same slice's episode carries a `session_id` field iff
   `.charness/usage-episodes/sessions/current` is present and resolves to a
   non-empty session id.
7. `validate_usage_episodes.py` returns exit 0 with status `no_records` and
   a warning (not error) when `enabled: true` and the records file is missing
   under repo root.
8. `charness session-capture status` reports intent vs actual and explicitly
   names any drift, with exit 0 when in sync and exit 1 when drifted.
9. Existing read-only quality gate (`./scripts/run-quality.sh --read-only`)
   passes throughout the slice and after the slice is complete.

## Implementation Plan

Two slices to keep each commit reviewable.

**Slice A — host-agnostic substrate**

1. Extend `integrations/usage-episodes/episode.schema.json` with:
   - optional `session_id` (string, uuid-like)
   - optional `t_evidence` object (rule_id, confidence, matched_paths,
     commit_refs, diff_kind)
   - optional `classification_skipped` (string, enum)
   - an `allOf`/`if-then` clause that makes `t_evidence` *required* when
     `t_status != "none"` and `classification_skipped` *required* when
     `t_status == "none"` and the classifier was actually invoked. Pattern
     follows the existing `t_link` conditional already in the schema.
   - All existing test fixtures (`tests/test_usage_episodes_schema.py`,
     any sibling fixture files) must be updated in the *same commit* so the
     change is bisectable.
2. Extract a `classify_t_signal(repo_root, head_sha)` helper into a new
   module under `scripts/` that runs `git diff --name-status HEAD~1..HEAD`
   and applies the rule catalog. Returns `(rule_id, confidence,
   matched_paths, commit_refs, diff_kind)` for the strongest match, or
   `(None, skip_reason)` when `git rev-parse HEAD~1` fails (no parent,
   shallow clone).
3. Update `scripts/slice_closeout_usage_episode.py` to:
   - call the classifier and populate `t_status` + `t_evidence` (or
     `classification_skipped` on classifier-skip)
   - read `.charness/usage-episodes/sessions/current` and attach `session_id`
     when present
4. Relax `scripts/validate_usage_episodes.py`: `enabled: true` + missing
   records → `no_records` warning (exit 0).
5. Add unit tests for the classifier (per-rule fixtures, plus skip-on-no-parent
   and skip-on-shallow fixtures) and for the relaxed validator path.
6. Run `./scripts/run-quality.sh --read-only`. Commit (schema + fixtures +
   emitter + validator all in one commit).

**Slice B — host hook surface and CLI**

0. **Done.** Codex precedence resolved against the refreshed
   [gather/2026-05-22-codex-hooks-surface.md](../gather/2026-05-22-codex-hooks-surface.md):
   `hooks.json` and `config.toml` are additive, but Codex warns when a layer
   defines both. Default install target promoted to `~/.codex/config.toml`,
   with a fallback to `~/.codex/hooks.json` when the JSON file already carries
   hook entries on that layer. See the Host hook surface Fixed Decision above.
1. Add `scripts/usage_episode_session_start.py` (the SessionStart hook
   payload script). Self-check the adapter; write
   `sessions/<id>/start.json`; refresh `sessions/current` via the symlink-safe
   writer.
2. Add `scripts/host_hook_install_lib.py` with `install_claude_hook`,
   `install_codex_hook`, `uninstall_*` companions, marker handling, and
   state-file management.
3. Wire `charness init` / `charness update` to read
   `host_hooks.{claude,codex}` from the adapter and call the install/uninstall
   helpers.
4. Add the `charness session-capture status` subcommand (and minimal
   `install` / `uninstall` wrappers if the install/uninstall flow needs to be
   triggered without a full `charness update`).
5. Update the adapter example to include the new fields with commented
   guidance.
6. Add tests for: install/uninstall round-trip, no-touch when
   `host_hooks` is disabled, drift detection by status command,
   foreign-hook preservation.
7. Run `./scripts/run-quality.sh --read-only`. Commit.

Both slices land behind the existing `enabled: false` default; flipping to
`enabled: true` becomes a separate, intentional act after both slices ship.

## Sources

- [issue-171-hlam-usage-episodes.md](./issue-171-hlam-usage-episodes.md):
  H-LAM/T substrate (#171).
- Commit `6721487` (#188): slice closeout emitter introduction.
- [gather/2026-05-22-codex-hooks-surface.md](../gather/2026-05-22-codex-hooks-surface.md):
  Codex hook lifecycle surface.
- [scripts/slice_closeout_usage_episode.py](../../scripts/slice_closeout_usage_episode.py).
- [scripts/validate_usage_episodes.py](../../scripts/validate_usage_episodes.py).
- [integrations/usage-episodes/episode.schema.json](../../integrations/usage-episodes/episode.schema.json).
- [.agents/usage-episodes-adapter.yaml](../../.agents/usage-episodes-adapter.yaml).
