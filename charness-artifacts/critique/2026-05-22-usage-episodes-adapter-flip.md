# Critique — Usage-Episodes Adapter Flip

- Date: 2026-05-22
- Target reference: `code-critique` (install/update touching host settings)
- Execution: bounded fresh-eye subagents (three angles + one counterweight)
- Fresh-Eye Satisfaction: parent-delegated
- Packet Consumed: [charness-artifacts/critique/2026-05-22-230117-packet.md](2026-05-22-230117-packet.md)

## Change

Slice B closeout flip of [.agents/usage-episodes-adapter.yaml](../../.agents/usage-episodes-adapter.yaml):

- `enabled: false` → `enabled: true`
- `host_hooks` block uncommented; `claude: enabled`, `codex: enabled`.
- `python3 charness session-capture install --repo-root .` then ran, installing
  the SessionStart hook into `~/.claude/settings.json` (claude-json) and
  `~/.codex/config.toml` (codex-toml).
- Slice closeout emission is now active; the first
  `.charness/usage-episodes/usage_episode.jsonl` record landed for this slice's
  own closeout.

Success for this slice: at least one closeout/SessionStart episode lands with
`session_id` and `t_evidence` populated so SC5/SC6 are satisfied against real
charness commits.

Out of scope: pre-emptive hardening of the install/uninstall path; the test
isolation leak that pollutes `.charness/usage-episodes/host-hooks-state.json`
from `tests/test_usage_episodes_host_hooks.py`.

## Angles

Three bounded fresh-eye subagents, one lens each, plus one separate
counterweight subagent.

- Privacy & Data Minimization — adapter privacy flags vs. what the SessionStart
  script and emitter actually persist.
- Reversibility & Host-Settings Collision — repo path embedding, state-file
  divergence, Codex representation flip, sibling-repo writes.
- Failure Modes & User-Visible Noise — JSONL append concurrency, hook
  discovery cost, hardcoded interpreter, closeout failure posture.

## Findings

### Privacy & Data Minimization

- P1: Privacy block (`raw_prompt`, `raw_transcript`, `user_identity`) is
  advisory; neither the SessionStart script nor the closeout emitter consults
  it. (medium)
- P2: SessionStart `start.json` persists raw `cwd` from host payload
  (`scripts/usage_episode_session_start.py:122`). (medium)
- P3: `host-hooks-state.json` embeds absolute home-rooted paths and full hook
  command strings. (low, gitignored)
- P4: Closeout episode embeds commit SHAs and `matched_paths`. (low, intended)
- P5: Latent — `classify_t_signal` reads commit messages; future fields could
  capture text. (low latent)
- P6: `model` field persisted unredacted. (low)

### Reversibility & Host-Settings Collision

- R1: Hook command embeds absolute repo path
  (`scripts/host_hook_install_lib.py:95-97`); a moved checkout leaves an
  orphan in `~/.claude/settings.json` and `uninstall` cannot reach it because
  the recorded `command` no longer matches. Overlaps with D21. (high)
- R2: Test-isolation leak — `tests/test_usage_episodes_host_hooks.py:326,346`
  pass `REPO_ROOT` as `--repo-root` with a tmp `--home-root`, so each test run
  rewrites the real repo's `host-hooks-state.json` to point `settings_path` at
  a pytest worker tmp dir that gets deleted seconds later. Next real
  `uninstall` reads stale state, no-ops on `not is_file()`, then clears the
  state entry anyway, leaving the actual on-disk hook untracked. The
  round-trip test cannot catch it because both halves use the same poisoned
  `--repo-root`. (high; filed as GH issue)
- R3: `resolve_codex_target` picks `codex-toml` vs `codex-json` at install
  time only; later creation of `~/.codex/hooks.json` re-installs there without
  removing the original TOML block. (medium → D23)
- R4: `_discover_repo_root` walks all the way up; a sibling repo with its own
  adapter receives writes silently. Overlaps with D22. (medium)
- R5: Codex TOML block matcher requires marker line to be immediately
  followed (modulo blank lines) by `[[hooks.SessionStart]]`; hand edits
  silently break uninstall. (medium → D23)
- R6: Uninstall clears state on `absent`/`not_installed` without confirming
  the file was actually touched. (medium)

### Failure Modes & User-Visible Noise

- N1: JSONL append has no file lock; parallel emits can interleave.
  (`scripts/slice_closeout_usage_episode.py:204`) (medium)
- N2: Rotation is non-atomic; `stat()`-then-rename races on concurrent
  writers. (medium)
- N3: SessionStart writes into a stranger repo's `.charness/` (same root cause
  as R4). (medium)
- N4: PyYAML import on every host session adds startup latency. (low)
- N5: Hook command is bare `python3 …`; `python3` not on PATH surfaces a
  host-side error. (medium → D26)
- N6: `run_slice_closeout.py` sets `payload["status"] = "failed"` on emitter
  error, turning a verified slice into a non-zero exit. (high → D24)
- N7: `cmd_session_capture_install` returns 0 even when one host reports a
  `HostHookError`; partial drift is hidden in JSON. (medium → D25)
- N8: `_record_start` can leak `.tmp` files on kill between write and
  `os.replace`. (low)
- N9: Malformed host JSON payload silently no-ops without a debug record when
  `CHARNESS_SESSION_START_DEBUG` is off. (low)

## Counterweight Triage

### Act Before Ship

- (none) — no finding rises above "speculative for a solo single-machine
  dogfooder enabling a gitignored, local-only capture." SC5/SC6 needs the
  adapter on, not pre-emptive hardening.

### Bundle Anyway

- (none) — this is a two-line YAML flip; bundling unrelated hardening
  muddies the Slice B closeout signal and every candidate is either already
  deferred or belongs in a follow-up the maintainer is already planning.

### Over-Worry

- P1–P6: gitignored output, no upload pipeline, no third-party transmission.
  The maintainer's own `cwd` and `model` on the maintainer's own box are not
  PII leaks.
- N1/N2: solo single-machine maintainer at episode-boundary emission rates;
  parallelism + locking would be premature.
- N4/N8/N9: noise-level, not worth blocking the flip.
- R6: paranoia-shaped — clearing stale state is the right default.

### Valid but Defer

- R1 / N3 / R4 → already covered by D21 (orphan after checkout move) and D22
  (depth cap on hook script repo-root walk). Reopen on first real hit.
- R2 → GH issue (test isolation leak in `tests/test_usage_episodes_host_hooks.py`).
- R3 + R5 → D23 (Codex TOML hooks block dedup + boundary fragility).
- N5 → D26 (hook command python interpreter resolution).
- N6 → D24 (slice closeout emitter best-effort posture).
- N7 → D25 (per-host install exit code).

## Deliberately Not Doing

- Pre-emptive hardening of the install/uninstall path. Reopen-trigger
  philosophy plus D21/D22 plus the new D23–D26 own the latent risks.
- Redacting closeout `commit_refs` / `matched_paths`. Those are the SC5/SC6
  evidence; redacting defeats the slice's success criteria.
- File locking on JSONL append. Single-machine episode-boundary writes do not
  need it; reopen when a duplicate-rate or interleaved-line report fires.

## Next Move

- Ship the flip as a single intentional commit with this critique artifact,
  the four new deferred decisions (D23–D26), and the handoff refresh.
- File a GitHub issue for the test isolation leak (R2). Do not fix in this
  slice.
- Monitor `.charness/usage-episodes/usage_episode.jsonl` after the next
  Claude or Codex session for a record carrying both `session_id` and
  `t_evidence`. That closeout satisfies SC5/SC6 against real charness commits.
