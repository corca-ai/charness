# Default Surfaces

`setup` uses these as the default operating surfaces. The `flat-wiki` profile
considers README, AGENTS/CLAUDE, and the consumer-owned documentation index at
`<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path --> the core; roadmap and
operator-acceptance are conditional surfaces.

Existing repos may already keep equivalent surfaces under local names. Declare
those names in `<repo-root>/.agents/setup-adapter.yaml` instead of renaming mature repo
docs only to satisfy the inspector:

```yaml
surfaces:
  roadmap: docs/master-plan.md
```

The inspector matches default paths case-insensitively. A `null` surface value
means the repo deliberately does not carry that surface and should not be
reported as missing.

## README

The repo root `<repo-root>/README.md` should answer:

- what the repo is
- who it is for
- what the current scope is
- where the next planning and operator docs live
- when the repo ships an installable surface, where the canonical install and
  probe-surface guidance lives
- that the consumer-owned documentation entry point is `<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path -->

## Documentation Index

The consumer-owned documentation index at `<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path --> is the one entry point for a flat Markdown
wiki. It should list each current page exactly once, group pages by concern, and
link to neighboring pages. New greenfield pages stay directly under `docs/`.
Existing nested trees are preserved until a separately approved migration plan
proves every link and ownership move.

Treat `docs/` as evergreen notes, not a chronological journal. Every page should
state whether it is `current`, `conditional`, or `generated`, own one question,
name its source of truth, and describe current behavior. Dated proposals,
superseded decisions, raw evidence, and retros belong under
`charness-artifacts/`; a stale or duplicate page is classified and linked before
it is moved or removed. Docs are code: use relative links, run link and graph
checks, and regenerate producer-owned pages instead of editing their output.

## AGENTS

The repo root `<repo-root>/AGENTS.md` should answer:

- how an agent should operate in this repo
- language or collaboration expectations
- core repo memory surfaces
- when retro memory is enabled, include `<repo-root>/charness-artifacts/retro/recent-lessons.md`
  in those memory surfaces
- validation and commit discipline when the repo has them
- the quality owner, exact quality-plan command, and whether the quality adapter
  is configured (setup must not call that a green gate)
- the hook policy: prefer Lefthook when no manager exists, but preserve and
  integrate existing Git-native hooks, Husky, simple-git-hooks, or Lefthook
- hook checks must be staged/related-file scoped and fast; whole-repo checks
  belong to pre-push/CI unless explicitly approved
- when the repo routes work through Charness goal/skill routing (a
  `## Skill Routing` block that names installed skill metadata/catalog facts, or explicit Charness
  goal/achieve routing), keep a compact `## Commit Discipline` rule so a long
  autonomous run does not leave the whole implementation uncommitted: commit
  meaningful implementation/workflow slices as they finish, keep commits scoped,
  and do not report a task-completing goal as done while meaningful work remains
  uncommitted unless deferral is explicit. This is distinct from, and listed
  alongside, the durable-artifact commit-target rule below
- when the repo uses Charness workflows that write durable artifacts under
  `charness-artifacts/`, say those meaningful artifact changes are repo state
  and commit targets, while current-pointer helpers should no-op when
  canonical content has not changed
- when the repo uses Charness announcement or release-note workflows, say that
  meaningful behavior commits should include a concise body with issue linkage,
  human-visible value, verification, and operator/apply notes when relevant;
  merge commits that close issues should include close keywords and a summary
  body when the implementation branch commits are terse
- a short `Skill Routing` fallback paragraph. It must name every route, because
  the reader that decides whether a repo is charness-managed requires all of
  them and answers no if any is missing: an active Goal Run starts from the
  exact `/goal #<parent>` objective and its parent cursor; ordinary routing starts the matching
  workflow directly from installed skill metadata and model judgment; unclear
  hidden support/integration availability runs the read-only
  `charness catalog list --repo-root <repo>` inventory, and a nonzero result
  reports a command failure; an external URL or source link goes through
  `gather` before deciding from it; validation closeout and operator reading
  tests go through `quality` validation. Use `AGENTS.md` -> `<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path --> ->
  the owning page for progressive disclosure. The provider parent/cursor is the
  live resume state.
- when the repo keeps repo-owned skills, keep one short policy that semantic
  skill changes should freeze the current intent before broad edits by deciding
  whether reviewed dogfood, maintained evaluator scenarios, or checked-in
  scenario review proof will carry the change
- prose wrap policy when the repo uses fixed-string source guards; default to
  semantic line breaks, and require whitespace-normalized matching before
  accepting column-wrapped prose. In `<repo-root>/.agents/setup-adapter.yaml`, a repo
  that deliberately keeps column wrapping must set
  `source_guard_matcher.normalize_whitespace: true` or
  `allow_column_wrap_fixed_guards: true`; otherwise the inspector reports a
  `requires_override` warning. Source-guard discovery is intentionally bounded
  to `<repo-root>/AGENTS.md`, `<repo-root>/README.md`,
  `docs/`, and `specs/` by default; set `source_guard_scan_roots` in the
  adapter only when fixed guards deliberately live elsewhere.
- selection rules in the core file, with deeper rationale pushed into linked
  docs instead of turning `<repo-root>/AGENTS.md` into a second handbook
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
  `<plugin-dir>/scripts/check_doc_links.py --repo-root <repo-root>` is the
  shipped implementation of the convention and runs against the reader's own
  repo. The lychee wrapper `<plugin-dir>/scripts/check-links-internal.sh` does
  NOT: it derives its root from its own location, so from an installed copy it
  either refuses outright or lints the plugin's markdown instead of the
  consuming repo's. Point it at the reader's repo with
  `CHARNESS_REPO_ROOT=<repo-root>`, or read it as a reference and give the repo
  its own lychee gate.

Use `$SKILL_DIR/scripts/render_skill_routing.py` to render the block. Keep it short and
bootstrap-heavy. On a mature repo whose `<repo-root>/AGENTS.md` lacks it, propose
adding the block instead of rewriting the whole instruction file.

## Roadmap (Conditional)

When active ordered work is evidenced or the user requests planning, the repo
roadmap document, usually `<repo-root>/docs/roadmap.md`, should answer:

- current priorities
- ordering of the next work items
- near-term exit criteria
- what is intentionally deferred

Prefer short-horizon execution direction over a grand long-range thesis.

## Operator Acceptance (Conditional)

When the repo has a real install, deployment, or takeover path, the operator
takeover document, usually
`<repo-root>/docs/operator-acceptance.md`, should answer:

- what a human operator should read first
- what commands to run first
- what takeover or acceptance tasks remain
- what counts as done for each item
- a `Progressive Operator Path` section with day-1 / 8-week / 6-month
  operator capability when the repo is mature enough to ground each
  horizon in observed evidence; leave a horizon empty or remove it rather
  than assert an unverified capability

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

- `<repo-root>/.agents/retro-adapter.yaml`
- `<repo-root>/charness-artifacts/retro/recent-lessons.md`
- one stable `summary_path` instead of many ad hoc notes

## Early Quality Baseline

When `setup` touches a greenfield or under-initialized code repo, leave one
explicit next-step lint baseline instead of a vague "add quality later" note.
Keep the baseline small and language-specific:

- Python: `ruff check` with `E`, `F`, `I`, and `C90` enabled plus one honest
  type-checking path (`mypy` or `pyright`)
- JavaScript/TypeScript: `eslint`, a standing `complexity` rule, and
  `tsc --noEmit` when TypeScript exists

`setup` does not need to install every gate itself. The point is to name an
honest default family early, then let `quality` own the exact gate wiring and
ratcheting.

Before proposing a write, run the quality skill's read-only bootstrap and plan.
Do not invent a parallel linter or ratchet configuration in setup. Prefer
native staged/related-file commands; use `lint-staged` only when the native tool
cannot express the same scope. Report tool installation, hook registration,
adapter migration, and gate execution as separate approval and proof items.

## GitHub Actions Defaults

When the repo scaffolds GitHub-hosted workflows, pin maintained GitHub Actions
to current Node 24-ready majors by default. Keep the maintained baseline in
[`github-actions-defaults.md`](./github-actions-defaults.md) and prefer direct
major upgrades over compatibility env vars.

## Regenerable Facts In Forward-Looking Prose

The surfaces above (README, AGENTS, docs/index, roadmap, operator-acceptance) are read as
CURRENT. So a number written into them is read as today's answer, and it starts
going stale the moment it is written.

Write the COMMAND that regenerates the fact, not one run's output:

- instead of `the suite has 42 tests`, write the command that counts them
- instead of `12 open issues`, write the issue-list command
- instead of a pinned version, write what reports it

When the command is EXPENSIVE — a multi-minute suite, a fan-out census, a
full-corpus sweep — carry the command AND a link to the checked-in artifact
holding its output. Telling every future reader to re-run a long gate moves the
cost onto all of them forever.

Dated, append-only records are the deliberate exception: retros, critiques,
audits, and slice logs SHOULD carry the number, because each describes one
moment and that is the whole reason it exists.

`quality` ships a gate for this (`regenerable-facts` in its catalog) that needs
no adapter configuration to start — it arms on default surfaces. Like every
other gate, your repo still has to RUN it: `setup` names the stance, `quality`
owns wiring it into your standing quality command.

What to check when you wire it:

- It reads the **quality** adapter (`<repo-root>/.agents/quality-adapter.yaml`),
  not the setup adapter. Declare `regenerable_facts.surfaces` there when your
  forward-looking prose lives outside the defaults, and
  `regenerable_facts.exemptions` (`path -> reason`, and the reason is required)
  when a specific file must opt out.
- `surfaces` REPLACES the defaults rather than adding to them. Declaring one
  glob for an extra prose directory drops README, the agent prompt files, and
  skill prose out of scope, and the gate then goes green over what is left.
  Re-list what you still want covered. This is why "narrow `surfaces` until the
  noise stops" is the wrong reflex: it de-arms the part of the gate that still
  renders a verdict for you.
- **Your `docs/` tree is not a default surface, and the gate says so out loud.**
  It cannot know whether your `docs/` holds forward-looking manuals or dated
  records, so it refuses the verdict instead of guessing: an unconfigured docs
  tree is reported `NOT CONFIGURED FOR DOCS` at exit 0, which is a typed
  no-verdict, never a clean claim. Keeping retros or audits under `docs/` does
  not fail your build.
- To bring docs under the verdict, declare your current forward-looking docs in
  `regenerable_facts.surfaces` and give each dated record a reasoned
  `exemptions` entry. Until you do, that tree is unjudged rather than clean.

`quality` owns the field contract and the current default globs; read it there
rather than trusting a list copied into this file.
