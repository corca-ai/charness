# Gather: browser-harness as an agent-browser replacement candidate

## Source

- URL: <https://github.com/browser-use/browser-harness>
- Owner/repo: `browser-use/browser-harness`
- Accessed: 2026-05-06 UTC
- Access mode: public GitHub repository, README/raw files, GitHub API

## Freshness

- Repository created: 2026-04-17
- Latest observed main commit: `32d8d515ed5e2b6e2aa72c18f3632eea1666d368`
  on 2026-05-06, message `feat(ipc): split BH_RUNTIME_DIR (sock) from BH_TMP_DIR (logs/screenshots)`
- GitHub releases: none published; `/releases/latest` returns 404 and tags list is empty
- `pyproject.toml` reports package version `0.1.0`

## Requested Facts

The question was whether `browser-use/browser-harness` should be used instead
of `agent-browser` in `charness`.

Observed `browser-harness` shape:

- Python package, requires Python `>=3.11`, dependencies include `cdp-use`,
  `fetch-use`, `pillow`, and `websockets`.
- Console command is `browser-harness`.
- It connects directly to Chrome or Chromium through CDP.
- It supports local Chrome via `chrome://inspect/#remote-debugging`, local
  isolated Chrome via `--remote-debugging-port`, and Browser Use cloud via
  `BROWSER_USE_API_KEY`.
- It encourages an editable install from a durable clone, with agent-edited
  task helpers under `agent-workspace/agent_helpers.py` and optional
  domain-specific skills under `agent-workspace/domain-skills/`.
- It has a small core package under `src/browser_harness/` and tests under
  `tests/unit` and `tests/integration`.
- It has no published release artifacts yet, despite docs mentioning
  `browser-harness --update`.

Observed `agent-browser` shape in this repo:

- `charness` currently models `agent-browser` as an external browser runtime
  integration used by `gather`.
- The local manifest points to `vercel-labs/agent-browser`, with `agent-browser
  --version` detection and a repo-owned runtime guard for daemon health.
- Current lock state has `agent-browser 0.26.0`; upstream latest release is
  `v0.26.0`, published 2026-04-16, with platform binary assets.
- The existing `gather` contract says browser-mediated private SaaS fallback
  should go through `agent-browser` only after local artifacts, grants, and
  official API/export paths are checked.

## Assessment

`browser-harness` is interesting as a future browser runtime seam, especially
for local human-in-the-loop browser work where direct CDP against the user's
real browser and editable helper learning are valuable.

It is not yet a clean drop-in replacement for `agent-browser` in `charness`:

- Distribution is less mature for repo-owned install/update: no releases or
  tags are published yet.
- Its intended operating model is editable local harness plus agent-written
  helper code. That is powerful, but it conflicts with `charness`' preference
  for explicit integration manifests, deterministic checks, and portable
  support/runtime boundaries.
- It relies on Chrome remote debugging permissions and, on newer Chrome, a
  per-attach user approval popup for the real-profile path. That is good for
  attended local work, but weaker for unattended or CI-like runtime contracts.
- The cloud-browser path introduces Browser Use account/API-key ownership,
  billing/timeout, profile-sync, and provider policy questions that would need
  a separate integration contract.

## Recommendation

Do not replace `agent-browser` wholesale yet.

Better path:

1. Add `browser-harness` as an experimental alternate external runtime
   manifest only if there is a concrete task where `agent-browser` is weak.
2. Keep `agent-browser` as the default `gather` browser fallback until
   `browser-harness` has a stable release/update story and a repo-local doctor
   check comparable to the current runtime guard.
3. If tested, scope the probe to local attended browser acquisition first:
   open page, screenshot, coordinate click, DOM extraction, daemon restart,
   auth-wall stop behavior, and artifact capture.
4. Treat cloud Browser Use support as a separate decision, not as part of the
   default replacement.

## Scoped Premortem

- Decision: answer the operator's replacement question without locking an
  integration change.
- Likely misread: treating GitHub popularity and direct-CDP ergonomics as
  enough evidence to replace the current runtime.
- Counterweight: a pilot is reasonable because `browser-harness` is small,
  active, and aligned with local attended browser use; the blocker is default
  runtime ownership, not exploration.
- Next move: keep default runtime unchanged, test `browser-harness` behind an
  experimental manifest only when a concrete `agent-browser` weakness appears.

## Open Gaps

- No local trial was run in this gather pass.
- No code audit beyond source layout, install instructions, package metadata,
  admin/runtime surface, and repository metadata.
- No comparison against hard cases from existing `agent-browser` failures.
