# Default Surfaces

`init-repo` uses these as the default operating surfaces.

Existing repos may already keep equivalent surfaces under local names. Declare
those names in [`.agents/init-repo-adapter.yaml`](../../../../.agents/init-repo-adapter.yaml) instead of renaming mature repo
docs only to satisfy the inspector:

```yaml
surfaces:
  roadmap: docs/master-plan.md
```

The inspector matches default paths case-insensitively. A `null` surface value
means the repo deliberately does not carry that surface and should not be
reported as missing.

## README

The repo root [README.md](../../../../README.md) should answer:

- what the repo is
- who it is for
- what the current scope is
- where the next planning and operator docs live
- when the repo ships an installable surface, where the canonical install and
  probe-surface guidance lives

## AGENTS

The repo root [AGENTS.md](../../../../AGENTS.md) should answer:

- how an agent should operate in this repo
- language or collaboration expectations
- core repo memory surfaces
- when retro memory is enabled, include [`charness-artifacts/retro/recent-lessons.md`](../../../../charness-artifacts/retro/recent-lessons.md)
  in those memory surfaces
- validation and commit discipline when the repo has them
- when the repo uses Charness workflows that write durable artifacts under
  `charness-artifacts/`, say those meaningful artifact changes are repo state
  and commit targets, while current-pointer helpers should no-op when
  canonical content has not changed
- when the repo uses bounded fresh-eye or premortem-style subagent review as a
  stop gate, one short rule that says `explicit delegation request` for the
  bounded scope, the review is already delegated by the repo contract, agents
  should not wait for a second user message asking for delegation, and host
  spawn restrictions should be reported explicitly instead of replaced with a
  same-agent pass
- for Charness-managed repos, the same rule should explicitly cover
  task-completing `init-repo` and `quality` review runs instead of implying
  that only premortem may spawn reviewers
- a short `Skill Routing` block that tells task-oriented sessions to call the
  shared/public charness skill `find-skills` once at startup before broader
  exploration
- after that bootstrap pass, tell the agent to choose the durable work skill
  from the installed charness surface instead of copying a long checked-in
  catalog into [`AGENTS.md`](../../../../AGENTS.md)
- when the repo keeps repo-owned skills, keep one short policy that semantic
  skill changes should freeze the current intent before broad edits by deciding
  whether reviewed dogfood, maintained evaluator scenarios, or checked-in
  scenario review proof will carry the change
- prose wrap policy when the repo uses fixed-string source guards; default to
  semantic line breaks, and require whitespace-normalized matching before
  accepting column-wrapped prose. In [`.agents/init-repo-adapter.yaml`](../../../../.agents/init-repo-adapter.yaml), a repo
  that deliberately keeps column wrapping must set
  `source_guard_matcher.normalize_whitespace: true` or
  `allow_column_wrap_fixed_guards: true`; otherwise the inspector reports a
  `requires_override` warning. Source-guard discovery is intentionally bounded
  to [`AGENTS.md`](../../../../AGENTS.md), [`README.md`](../../../../README.md),
  `docs/`, and `specs/` by default; set `source_guard_scan_roots` in the
  adapter only when fixed guards deliberately live elsewhere.
- selection rules in the core file, with deeper rationale pushed into linked
  docs instead of turning [`AGENTS.md`](../../../../AGENTS.md) into a second handbook
- avoid blanket external-link ignore defaults; when the repo relies on
  checked-in cross-file markdown links (the common case for any docs-heavy
  repo), treat `lychee`-backed internal link integrity and an explicit
  file-reference convention as baseline gates rather than optional
  escalations. The convention has two halves that work together:
  (1) **every relative markdown link target starts with `./` or `../`** so a
  bare `foo.md` in a link is a lint failure, not a style preference;
  (2) **backticks are reserved for concept tokens, runnable commands, and
  explicit file links** — a backticked token that looks like a file (has an
  extension, or matches a tracked path) must live inside a markdown link
  instead of sitting alone as inline code. Concepts stay natural: a bare
  `SKILL.md` whose basename resolves to many tracked files is still allowed,
  because the linter treats multi-match basenames as conceptual references.
  See [`./scripts/check_doc_links.py`](../../../../scripts/check_doc_links.py),
  [`./scripts/check-links-internal.sh`](../../../../scripts/check-links-internal.sh), and
  [`./scripts/migrate_backtick_file_refs.py`](../../../../scripts/migrate_backtick_file_refs.py)
  for the shipped reference implementation and one-shot migrator

Use `scripts/render_skill_routing.py` to render the block. Keep it short and
bootstrap-heavy. On a mature repo whose [`AGENTS.md`](../../../../AGENTS.md) lacks it, propose
adding the block instead of rewriting the whole instruction file.

## Roadmap

The repo roadmap document, usually `docs/roadmap.md`, should answer:

- current priorities
- ordering of the next work items
- near-term exit criteria
- what is intentionally deferred

Prefer short-horizon execution direction over a grand long-range thesis.

## Operator Acceptance

The operator takeover document, usually
[docs/operator-acceptance.md](../../../../docs/operator-acceptance.md), should answer:

- what a human operator should read first
- what commands to run first
- what takeover or acceptance tasks remain
- what counts as done for each item

When the repo already has real functional checks, synthesize operator
acceptance from them instead of inventing a disconnected checklist:

- split machine-runnable checks from human judgment or external-system checks
- separate cheap local commands from expensive or account-dependent runs
- name environment prerequisites explicitly when a command needs credentials,
  services, seeded data, or another repo state
- prefer one honest "run this first" sequence over a long unordered dump

## Optional Bootstrap Docs

Do not scaffold separate bootstrap or uninstall docs by default.

If a repo intentionally keeps an extra bootstrap doc because the README would
become too heavy otherwise, treat that as a repo-local contract, not a default
surface every repo should inherit.

Even then, keep the first successful bootstrap honest in the README:

- prerequisites
- pasteable bootstrap commands
- the next repo-owned probe or next-action command
- any local discoverability or materialization step when agents or plugins
  depend on it

## Optional Retro Memory Seam

Only scaffold retro memory when the repo actually wants durable retrospective
pickup between sessions.

When enabled, keep the seam small and explicit:

- [`.agents/retro-adapter.yaml`](../../../../.agents/retro-adapter.yaml)
- [`charness-artifacts/retro/recent-lessons.md`](../../../../charness-artifacts/retro/recent-lessons.md)
- one stable `summary_path` instead of many ad hoc notes

## Early Quality Baseline

When `init-repo` touches a greenfield or under-initialized code repo, leave one
explicit next-step lint baseline instead of a vague "add quality later" note.
Keep the baseline small and language-specific:

- Python: `ruff check` with `E`, `F`, `I`, and `C90` enabled plus one honest
  type-checking path (`mypy` or `pyright`)
- JavaScript/TypeScript: `eslint`, a standing `complexity` rule, and
  `tsc --noEmit` when TypeScript exists

`init-repo` does not need to install every gate itself. The point is to name an
honest default family early, then let `quality` own the exact gate wiring and
ratcheting.

## GitHub Actions Defaults

When the repo scaffolds GitHub-hosted workflows, pin maintained GitHub Actions
to current Node 24-ready majors by default. Keep the maintained baseline in
[`github-actions-defaults.md`](./github-actions-defaults.md) and prefer direct
major upgrades over compatibility env vars.
