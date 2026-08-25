# Craken-like Flat-Wiki Profile

This is the default setup proposal for a repository that wants a Craken-like
operating surface. It copies the shape, not a product's Cloudflare or
TypeScript assumptions.

## Profile outputs

The proposed core is:

- a minimal `README.md` that points to `AGENTS.md` and the consumer-owned
  documentation index at `<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path -->
- a minimal `AGENTS.md` containing the repository contract, documentation rule,
  quality command, and bounded subagent-delegation policy
- `CLAUDE.md -> AGENTS.md` when Claude compatibility is wanted
- the consumer-owned documentation index at `<repo-root>/docs/index.md` as the one entry point <!-- not vendored: consumer-repo path -->
- a flat `docs/*.md` wiki for new repositories; existing nested docs are
  preserved until an explicit migration plan is approved

Every page is listed once from the consumer repository's documentation index
(`<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path -->), owns one topic, and links to
neighbors. `awiki lint -root docs -recursive` is the graph probe. A missing or
unhealthy `awiki` binary is `unproven`, never a clean docs verdict.

## Quality proposal

Setup does not invent a second quality contract. It runs the quality skill's
read-only bootstrap and plan, then presents the result for approval:

```bash
python3 "$SKILL_DIR/../quality/scripts/bootstrap_adapter.py" --repo-root . --dry-run
python3 "$SKILL_DIR/../quality/scripts/plan_quality_run.py" --repo-root . --detail
```

After approval, quality owns the adapter write, exact gate commands, and
ratchets. Setup only carries the approved plan into the repository surface:

```bash
python3 "$SKILL_DIR/../quality/scripts/bootstrap_adapter.py" --repo-root . --migrate
```

The plan must state language evidence, package manager, formatter/linter,
type-checker/test command, duplication/coverage/mutation ratchets, and every
deferred capability. `configured` means the quality adapter resolves; it does
not mean the gates passed.

## Fast and correctly scoped hooks

The default hook policy is:

1. run staged-file checks for changed files;
2. run related-file or package-owner checks where the tool requires them;
3. reserve whole-repository gates for pre-push/CI or an explicitly approved
   repository policy;
4. record the measured command and budget in the quality adapter.

`lint-staged` is a compatibility option, not a goal. Prefer a native tool mode
when it preserves the same scope and diagnostics; use `lint-staged` only when
the native command cannot express the staged/related-file boundary. A fast hook
that lints the wrong files is not a quality improvement, and a precise hook that
rescans the whole repository on every commit is not an acceptable default.

The machine-readable hook recommendation is `prefer-lefthook-when-no-hook-manager`.
Lefthook is recommended when no hook manager exists because its declarative
stages, parallel commands, per-command file filters, worktree installation, and
failure-message/log routing make this contract easier to operate. Existing
Git-native hooks, Husky, simple-git-hooks, or another manager are respected and
integrated rather than replaced. Any replacement requires a separate explicit
approval with a migration and rollback plan.

## Approval boundary

The inspector emits a plan-only payload. Before setup writes docs, installs a
tool, registers a hook, moves a document, or changes a ratchet, show the user:

- current files and detected tools
- current docs inventory, nested-doc conflicts, and the no-implicit-move policy
- proposed files, commands, scopes, and dependencies
- existing-hook action (`preserve-and-integrate` or `propose-lefthook`)
- quality adapter status and deferred fields
- conflicts, destructive moves, and non-claims

The inspector emits an `approval_plan.identity` digest. Proceed only after an
explicit user approval naming that digest, then immediately re-run the
read-only inspection with `--expect-plan-identity <digest>` before any apply.
A changed plan requires a new approval. Never treat a green command, existing
binary, or inferred language as approval.

## Conditional surfaces

`<repo-root>/docs/roadmap.md` is a consumer-owned operator surface created only when the repository has active ordered work or
the user requests planning. `<repo-root>/docs/operator-acceptance.md` is a consumer-owned operator surface created only when
there is a real install, deployment, or operator takeover path. Both remain
available as explicit adapter surfaces; neither is required by this profile.

Retro memory, worktree adapters, and other Charness seams remain opt-in or
evidence-triggered. They are not silently added while bootstrapping the
documentation and quality surface.
