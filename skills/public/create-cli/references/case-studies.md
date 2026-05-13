# Case Studies

Use nearby repos and tools as comparison points, not as cargo-cult templates.

`charness`

- thin lifecycle CLI around managed install state
- explicit `doctor`, `update`, and `reset`
- `update all` keeps the user-facing command product-owned while fanning out
  into tracked external tool updates and bundled support refresh
- lock and generated-support artifacts for agent-readable continuation

`agent-browser`

- upstream CLI includes a built-in `upgrade` command
- this makes scripted update automation safer from a consumer repo

`specdown`

- upstream binary is installable through multiple host-controlled paths
- upstream release installer is the recommended bootstrap path
- additional host-controlled install paths may exist, but consumer repos should
  not hardcode them unless they can prove provenance
- without a built-in self-update surface, consumer repos should avoid guessing
  how the operator originally installed it

`cautilus`

- release-first distribution with one checked-in `install.sh`
- installer is intentionally scoped to the product itself, not OS dependency
  managers
- version provenance and latest-release cache are a product-owned runtime
  contract, not installer-only trivia
- automatic update checks are scoped to interactive standalone-binary usage,
  with a 24 hour TTL and explicit skip conditions for CI and non-interactive
  runs

Design takeaway:

- the difference is not one package manager versus another
- the difference is whether the tool exposes a trustworthy self-managed update
  seam or whether the host package manager remains the source of truth
- when the host package manager stays authoritative, agent-readable provenance
  should survive install and doctor flows so later updates can reuse that route

`cautilus 0.15.4 cleanup`

- public command grammar moved from implementation-shaped (`claim discover`,
  `eval test`, `scenario list`) to intent-first (`discover claims`,
  `evaluate fixture`, `discover scenarios`)
- lifecycle scopes (`adapter init`, `healthcheck`, `commands`) routed under
  `init`/`doctor` instead of leaking as their own top-level commands
- the rename was a public-grammar rewrite, not an internal refactor: callers,
  agents, and docs all moved together so the surface kept one obvious shape
- see `intent-first-grammar.md` for the full rename table and the checklist
  that catches implementation-shaped names before they ship

Design takeaway:

- when a CLI starts to read like its own module list, the next refactor is a
  public-grammar rewrite, not another subcommand bolted on
- name verbs from the user's journey and demote implementation nouns into the
  object slot under those verbs

`cautilus workbench`

- workflow surface split into `cautilus workbench prepare-request-batch` and
  `cautilus workbench run-scenarios` instead of one thick command
- the prep command owns deterministic expansion, selection, and filtering of
  the batch; its output is a product-owned machine-readable artifact
- the execute command stays narrow: it consumes an artifact, runs it, and
  reports results
- agents can inspect, diff, subset, and retry the artifact between the two
  steps without recomputing the prep pass

Design takeaway:

- when the primary caller is another agent, a prep/execute split plus a
  product-owned intermediate artifact is often a more stable contract than a
  single command that tries to own selection, expansion, execution, and
  policy at once
- the split is not a default for all CLIs; see `command-surface.md` prep/
  execute anti-patterns for when it becomes cost, not value
