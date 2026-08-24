# Consumer Friction Retirement And File-Backed External Work

Date: 2026-08-24

## Concept

Charness should give an external host worker one complete, subject-bound work
packet and judge a typed terminal receipt. The consuming repository declares
its own commands and capability topology; the machine supplies ignored local
policy; Codex and Claude adapters supply only host mechanics.

This is the portable form of the workflow that proved useful in Ceal. The
valuable idea is not the literal `codex exec` command. It is the combination of
a file-backed brief, an isolated checkout for writers, a finite host-observed
lifecycle, a complete result payload, and parent-owned integration.

The concept has two independently closable deliverables. Neither is a gate for
the other unless an issue row records and proves a causal dependency:

1. retire every currently open issue with actual consumer-repository friction
   by repair, current-behavior closeout, a narrower residual, or an evidence-backed
   defer; and
2. make the file-backed external-worker method a reusable Charness capability so
   future consumers do not rebuild Ceal's orchestration locally.

## Capability Or Capability Failure

The actor is an agent or maintainer working in a repository that consumes an
installed Charness plugin.

The failed capability is: "run a bounded investigation, implementation, or
fresh-eye review against the exact current subject, on the current host, and
receive a trustworthy terminal result without inventing repo-local orchestration."

Today the actor chooses among incomplete paths:

- built-in subagents have good parent delivery and steering, but scarce slots and
  host-specific lost/interrupted-result states;
- the Charness file-backed worker has the strongest receipt/delivery contract,
  but is review-specific and difficult for a consumer to invoke end to end;
- Ceal's `codex exec` lanes handle broad and write-capable work well, but their
  lifecycle is partly prose/log parsing and their worktree preparation is
  Node/Ceal-specific;
- individual skills sometimes discard the current subject, installed package
  root, lifecycle state, or repo-declared command topology and then emit a global
  or generic verdict.

The threshold for success is not "a process ran" or "all issues closed." It is:

- every current open issue appears in an auditable inclusion/exclusion matrix,
  and every included consumer-friction issue has a current, consumer-shaped
  disposition;
- every external run binds its subject, inputs, authority, and terminal result;
- an installed consumer can use the path without referencing the Charness source
  checkout or copying Ceal-specific machinery.

## Product Posture

This is a portable developer-tool capability and an upstream cleanup program,
not a new product mode. The public surface should be a strong default behind a
small Charness CLI entrypoint plus repo adapter, rather than a menu of host and
workflow taxonomies.

Do not introduce a second durable `lane` owner. Charness already owns durable
repo-local work through `charness task` and `.charness/tasks/*.json`. Extend that
task envelope with immutable execution-attempt and terminal-result references;
keep `worker` as an execution component and `lane` as informal operator language
at most. `review`, `implementation`, and `investigation` remain result contracts,
while `codex_exec` and `claude_p` remain host execution methods.

## Verified Facts

- GitHub had 46 open Charness issues at the 2026-08-24 inventory. Reading all 46
  bodies and comments identified 13 with direct consumer-repository observations
  plus one required lifecycle dependency. The remaining 32 lack a current
  consumer episode or carry a Charness-internal residual. The complete inclusion,
  exclusion, and dependency evidence is frozen in the
  [open-issue matrix](./2026-08-24-open-issue-consumer-friction-matrix.md); the
  selected cohort below is not the audit surface by itself.
- The consumer-friction cohort is:
  [#713](https://github.com/corca-ai/charness/issues/713),
  [#687](https://github.com/corca-ai/charness/issues/687),
  [#680](https://github.com/corca-ai/charness/issues/680),
  [#637](https://github.com/corca-ai/charness/issues/637),
  [#634](https://github.com/corca-ai/charness/issues/634),
  [#692](https://github.com/corca-ai/charness/issues/692),
  [#671](https://github.com/corca-ai/charness/issues/671),
  [#667](https://github.com/corca-ai/charness/issues/667),
  [#689](https://github.com/corca-ai/charness/issues/689),
  [#601](https://github.com/corca-ai/charness/issues/601),
  [#691](https://github.com/corca-ai/charness/issues/691),
  [#690](https://github.com/corca-ai/charness/issues/690), and
  [#688](https://github.com/corca-ai/charness/issues/688). Goal-terminal integrity
  also depends on [#698](https://github.com/corca-ai/charness/issues/698).
- This is not fourteen unbuilt repairs. Current Ceal replay nevertheless keeps
  #689, #690, and #691 open: TAP replay still has three failures, a historical
  hollow goal passes `--pursue-ready`, and the same pursue-ready path accepts
  `superseded`. #637 was classified `already-satisfied`; #680's original
  explicit-path premise was refuted; #671 is partial; and #634 has shipped repairs
  with enumerated residual families. Sources:
  [tracker requalification](../issues/2026-08-22-tracker-requalification.md) and
  [repairs goal](../goals/2026-08-20-repairs-that-carry-their-class.md).
- #688 is no longer input-blocked. The malformed generated output and the three
  source bullets are present in `../ceal`, so an exact positive fixture can now be
  frozen.
- Ceal's tracked root contract points to ignored `AGENTS.local.md`, and its worktree
  helper safely wires `AGENTS.local.md` plus `CLAUDE.local.md` into isolated lanes.
  The local file supplies machine policy but explicitly does not replace a bounded
  task brief. Sources:
  [`../ceal/AGENTS.md`](../../../ceal/AGENTS.md),
  [`../ceal/.agents/codex-host.md`](../../../ceal/.agents/codex-host.md),
  [`../ceal/.agents/claude-host.md`](../../../ceal/.agents/claude-host.md), and
  [`../ceal/scripts/lane-worktree.ts`](../../../ceal/scripts/lane-worktree.ts).
- Ceal separates broad/long external `codex exec` work from built-in subagent work,
  uses file stdin and a pinned cwd, isolates writers in detached worktrees, appends
  a host-authored exit marker, and makes the primary checkout integrate by commit
  SHA. Its general external lanes do not yet have a finite typed timeout receipt.
- Charness already has the stronger reusable primitives:
  [`charness worktree create --prepare`](../../scripts/worktree_create.py),
  the backend-neutral [reviewer worker runtime](../../skills/shared/scripts/reviewer_worker_runtime.py),
  [delivery ledger](../../skills/shared/scripts/reviewer_delivery.py),
  [combined worker report](../../skills/shared/scripts/reviewer_worker_report.py),
  and a [Codex runtime](../../scripts/agent-runtime/codex-eval-runtime.mjs) with
  isolated `CODEX_HOME` and auth handling.
- The existing reviewer path has gaps that must be resolved before it becomes the
  general substrate: `host-defaulted` still needs a caller-selected backend,
  reviewer tiers are not applied to file-backed workers, there is no simple
  prepare-and-run consumer command, `AGENTS.local.md` composition is absent, and
  the runner appears to resolve some relative artifact paths once against the repo
  root and later again against the launch cwd. The last item is a code-reading
  hypothesis, not a reproduced defect; reproduction is the decision gate and a
  refuted hypothesis creates no repair work.
- `charness task` already persists claim, submit, abort, status, summaries, and
  artifact references. A new durable lane store would duplicate this owner.
- Host execution normalization currently has two owners: the Python reviewer
  runtime and the JavaScript Codex eval runtime. The first implementation contract
  must select one executable process/configuration owner rather than add a third.

## Assumptions

- A file-backed worker is the default portable external channel; typed subagents
  remain an optional host adapter for short, steering-heavy work.
- Consumer repositories will accept one small tracked execution adapter and one
  ignored machine-local policy surface. This must be tested rather than assumed.
- The public capability may support write-capable work eventually, but its first
  executable slice can be read-only without making the public taxonomy read-only.
- Ceal is the first real consumer proof target, but no Ceal vocabulary, paths,
  model ids, Node dependency links, or machine grants belong in portable Charness.
- "Resolve all friction issues" permits evidence-backed closure or narrowing when
  current behavior already satisfies the issue. Reimplementation is not progress.

## Decision Candidates

### A. Copy Ceal's lane scripts and host notes into Charness

This is the shortest visual path, but it copies Node dependency links, process-table
parsing, host-specific flags, model ids, and a no-finite-timeout lifecycle into every
consumer. It also duplicates Charness's existing receipt and worktree mechanisms.

### B. Extend `charness task` and generalize the existing worker/worktree primitives

Keep review verdict semantics intact, extract a host-neutral process/receipt layer
under them, attach immutable attempts to the existing durable task envelope, and let
task-specific result contracts sit above it. Consumers provide repo commands and
machine-local capability bindings through existing adapter/config families. This is
the recommended direction.

### C. Fix the fourteen issue rows independently and leave orchestration local

This has the smallest initial platform diff, but it preserves the exact reason Ceal
grew `codex-host.md`, `lane-worktree`, and `lane-status`. The next consumer pays the
same integration cost and subject/root/delivery failures remain unrelated patches.

## Recommended Current Decision

Choose B, with three boundaries:

1. issue retirement and external-worker capability remain independently closable;
2. `.charness/tasks` remains the one durable lifecycle owner; and
3. generalize host execution and receipt mechanics, not review verdict semantics.

An implementation attempt's successful receipt means "a candidate result was delivered
and its declared artifacts are internally consistent." It must never inherit the
reviewer's `approval_eligible` vocabulary. Review approval stays owned by the bounded
review result schema and combined worker report; implementation completion stays owned
by `impl -> prove`, fresh-eye review, and parent integration.

## Proposed Architecture

### 0. Two independently closable programs

The issue matrix owns issue-retirement truth. The worker contract owns external-run
truth. An issue row may consume the worker only after recording a tested causal edge;
write-capable external work cannot gate unrelated issue repair, current-behavior
closeout, narrowing, or defer.

### 1. Existing task envelope as lifecycle owner

Extend `charness task` rather than create a lane store. A task keeps its objective,
claim, and task-specific result. Each external execution adds an immutable attempt
reference with a durable attempt id, invocation identity, lifecycle state, receipt,
logs, and result carrier.

The minimum operator journey is:

```text
claim/create -> launch -> status/inspect -> collect
                         -> cancel -> terminal receipt
                         -> retry as a new attempt identity
```

Parent loss does not erase an attempt. Repeated status or collect is idempotent and
cannot overwrite or reinterpret a terminal result. Timeout/interruption preserves
logs and partial artifacts; cleanup refuses to discard uncollected output silently.
The specification may refine verb spelling, but not omit these lifecycle operations.

### 2. Subject-bound invocation envelope

A frozen invocation record should carry:

- logical repository identity and explicit current checkout root;
- task objective and canonical contract/artifact;
- exact subject paths, reviewed-input manifest digest, and writable-path allowlist;
- base ref and expected worktree identity for write-capable work;
- backend selection, finite timeout, portable tier, and an orthogonal capability
  envelope for filesystem reads/writes, external reads, and external effects;
- prompt, result schema, required proof, stop-and-return-partial rule, and
  non-claims;
- tracked instruction identity plus optional local-instruction identity.

Global discovery may populate the packet, but no global verdict may stop a bounded
slice until applicability is rebound to the packet paths. That is the shared repair
shape behind #713 and the path/identity side of #680 and #671.

### 3. One host-neutral process/configuration owner and terminal receipt

Make one Python executable boundary behind the Charness CLI the canonical owner of
host process construction. `run_reviewer_worker.py` delegates to it. The JavaScript
Codex eval runtime delegates argv/env/auth execution to the same boundary while
retaining eval-only case and telemetry semantics. Acceptance fails while two
independent normalizers still own the same host fields.

That boundary owns:

- `codex_exec` and `claude_p` argv/env/auth/output normalization;
- stdin-from-file and explicit cwd;
- stale-output refusal and repo-root-relative path confinement;
- process-group creation, finite timeout, interruption cleanup, and one typed
  terminal state;
- prompt/schema/instruction/output hashes and host-authored start/finish/exit data.

Configuration ownership is field-level and deterministic:

| Field | Owner |
| --- | --- |
| portable backend/tier/timeout default | tracked workflow adapter |
| logical provider binding and authenticated-binary readiness | existing ignored `.charness/local/capability.json` family |
| one-run high-risk authority | explicit host/runtime grant, never prose |
| objective, subject, writable paths, requested authority | frozen invocation |
| requested and effective backend/authority | host-authored receipt |

“Read-only” is not one authority. The invocation and receipt must distinguish
checkout mutation, remote observation, and remote mutation. A required external
read is preflighted before launch; a transport failure cannot be interpreted as
credential invalidity. The named contract is
`charness-artifacts/spec/2026-08-24-external-worker-capability-envelope.md`.

Preflight shows the selected backend, selection source, auth readiness, requested
and effective authority, and capability-config identity. There is no silent backend
fallback, authority escalation, or parsing of `AGENTS.local.md` as a grant.

The status vocabulary must distinguish at least succeeded delivery, input-invalid,
backend-unavailable, backend-failed, timed-out, interrupted, result-missing,
result-invalid, and input-drift. A process exit or commit SHA alone never becomes a
semantic success.

Input drift is executable, not model-reported: the process boundary receives a
canonical readable input manifest and hashes subjects, instructions, local policy,
and expected checkout identity immediately before launch and after collection.
Changed inputs yield `input-drift` and never a delivered semantic result.

### 4. Worktree and local policy composition (later write-capable slice)

Write-capable work uses the existing Charness worktree create/doctor/prepare path.
Do not copy Ceal's `node_modules` or `dist` symlinks; consumer preparation stays in
the worktree adapter's `prepare.commands`.

When the primary checkout has ignored `AGENTS.local.md`, Charness may create managed
links in the isolated worktree:

```text
<task-worktree>/AGENTS.local.md -> <primary>/AGENTS.local.md
<task-worktree>/CLAUDE.local.md -> AGENTS.local.md
```

Missing source is a no-op; a foreign file or unexpected symlink refuses. The run
records the local-policy hash at launch and collection; a mid-run change becomes
typed input drift. This keeps Ceal's useful read-last behavior without pretending a
live symlink is a frozen input.

`AGENTS.local.md` remains human/agent policy. The CLI must not parse prose as an
unsandboxed grant. Machine-executable provider bindings stay in the existing ignored
`.charness/local/capability.json` family; one-run authority comes from an explicit
host/runtime grant; tracked adapters carry portable defaults only.

Portable `AGENTS.local.md` composition is not promised by the first read-only slice.
Before the later write slice, the tracked consumer contract must explicitly load the
optional local file, define precedence and collision recovery, and prove that local
bytes neither enter tracked artifacts nor the candidate diff.

### 5. Task-specific result carriers

- Review: keep the current bounded-review schema, delivery ledger, and combined
  `approval_eligible` report.
- Investigation: require a complete findings/evidence/non-claims report and a typed
  delivery receipt, but no approval field.
- Implementation: require changed paths, candidate commit or diff identity, executed
  checks, unresolved findings, and non-claims. The parent re-checks load-bearing
  evidence and serially integrates; a candidate commit is output, not authority.

### 6. Consumer-declared capability routing

Generic heuristics should report routing outcomes, not negative repository facts.
The consuming repo owns declarations for specialized release commands, test reporter
accounting, and opt-in quality telemetry. Charness owns the portable schema and the
fallback wording.

This directly shapes #667, #689, and #601 without forcing them into one mega-adapter:
they may share a capability vocabulary and resolution library while retaining
task-specific fields and validators.

## Issue Workstreams

| Workstream | Issues | Current design action |
| --- | --- | --- |
| Requalification | all 46 matrix rows | Refresh the complete inventory; replay the 13 included rows and #698 on current source and installed 6.4.0; classify repair, partial, already-satisfied, premise-refuted, or evidence-blocked before editing |
| Invocation and delivery | #713, #680, #687 | Bind exact subject/input identity; close or narrow #680 if the current explicit-path refutation holds; make file-backed terminal delivery the portable default |
| Installed roots and bootstrap | #634, #637, #692, #671 | Preserve #637's already-satisfied behavior, finish #634/#671 residual families, centralize adapter-init idempotence |
| Capability routing | #667, #689, #601 | Repair #689 against the failing Ceal direct/npm TAP replay and prove a real upstream mutation/restore success; declare specialized release routing; require opt-in telemetry before inventing #601 thresholds |
| Goal lifecycle | #690, #691, #698 | Make `--pursue-ready` reject hollow section bodies and terminal `superseded` goals in the Ceal fixtures; design #698 so `superseded` preserves Auto-Retro/remainder disposition without pretending completion |
| Generated memory | #688 | Freeze the exact Ceal source bullets and malformed output as fixtures; repair index and digest normalization together |

## Independent Program Order

### Issue retirement track

1. Refresh the full 46-row matrix before slices and again before closeout.
2. In parallel, preserve #637's already-satisfied proof; repair and consumer-replay
   #689, #690, and #691; reproduce and repair the independent #688 normalization
   case; requalify #680 before changing it.
3. Execute the remaining issue-specific workstreams by causal dependency, using the
   current manual Ceal-style external process where helpful but never making the new
   worker capability their blanket prerequisite.
4. Serialize generated plugin sync, broad verification, commits, and GitHub closeout
   in the primary checkout. Map every requested issue outcome to executed proof.

### External-worker capability track

1. Reproduce the relative-path hypothesis from repo-root and unrelated cwd. Repair
   only if reproduced.
2. Specify the `charness task` attempt lifecycle, the one Python host process owner,
   and field-level adapter/capability/grant precedence.
3. Implement one read-only installed-consumer slice with durable launch/status/
   collect/retry, finite timeout, executable input-drift checks, and no silent
   fallback or escalation.
4. Accept proof-surface changes through a pre-existing independent reviewer channel.
   Candidate-command dogfood is supplementary evidence, never its own approval. If
   verdict logic is repaired, run the required second independent bounded round.
5. Only then add managed local-instruction composition and write-capable isolated
   tasks. This later slice must not gate the issue-retirement track.
6. Prove the real installed artifact with the Charness source checkout inaccessible,
   then run a bounded Ceal read-only adoption/readback. Write into Ceal only after an
   explicit phase-scoped grant.

This preserves the option to stop after a useful read-only worker and lets already
satisfied issue rows close without waiting for platform work.

## World Model

### Entities

- Consumer repository: owns product topology, commands, proof expectations, and
  tracked portable adapter.
- Machine-local policy: ignored host topology, resource policy, backend/auth settings,
  and explicit high-risk grants.
- Task envelope: the one durable owner of objective, claim, attempts, and typed
  task-specific result references.
- Invocation envelope: frozen identity of one external attempt and evidence contract.
- Host adapter: Codex/Claude command and result normalization only.
- Worktree: isolated checkout/index for one write-capable invocation.
- Terminal receipt: host-observed process and artifact state.
- Task result: review, investigation, or implementation semantics.
- Parent integration: distinct re-check, serial merge, verification, and closeout.

### Stages

```text
discover -> claim task -> bind attempt -> prepare isolated inputs -> launch
         -> running/status -> typed terminal receipt -> idempotent collect
         -> semantic result validation
         -> parent re-check -> serial integration -> consumer readback -> issue closeout
```

No arrow after `running` may be inferred from silence, timeout, a status notification,
or a commit's existence.

## Truth Tests

- A current 46-row matrix accounts for every open issue with a refresh timestamp,
  evidence-backed inclusion/exclusion/dependency reason, and non-close disposition.
- Parent loss, timeout, and retry preserve an immutable task attempt; repeated
  status/collect cannot overwrite its receipt or reinterpret its result.
- An unrelated global forced interrupt plus disjoint packet paths proceeds as
  not-applicable; overlapping paths remain binding (#713).
- Root-cwd and unrelated-cwd controls decide whether relative-path repair is needed;
  if reproduced, the repaired arguments resolve identically and stay confined.
- A timeout kills the full process group and emits one terminal receipt; a stale or
  empty output never becomes delivered, while logs remain discoverable.
- Preflight and receipt expose selected backend, selection source, auth readiness,
  requested/effective authority, and config identity. Missing or conflicting backend,
  prose-only permission, and denied structured grant fail without fallback/escalation.
- Subject, instruction, local-policy, or checkout drift between pre-launch and
  collection yields `input-drift` from executable re-observation, never delivery.
- Reviewer and eval execution both delegate argv/env/auth normalization to the one
  canonical process boundary; no second owner remains for the same field.
- A review packet's identity changes when any reviewed path/content changes and cannot
  claim a freeze over absent inputs (#680).
- Installed plugin layout resolves scaffold, validator, schema, and dependency data
  without a Charness source checkout (#634/#637).
- All shipped `init_adapter.py` paths are idempotent on a valid existing adapter and
  still refuse invalid/conflicting content (#692).
- A Linux-authored cross-repo goal activates on macOS through logical roots or a
  declared mapping, never a silently substituted absolute path (#671).
- A specialized release declaration returns a routing plan, not `not releasable`
  (#667).
- pytest and Node TAP fixtures exercise the same mutation/restore contract (#689).
- `superseded` is terminal without reading as complete, and cannot discard required
  Auto-Retro/remainder disposition (#691/#698).
- Exact Ceal malformed lesson inputs render balanced, readable index and digest output
  (#688).
- A clean-room test installs the real distributable, makes the authoring checkout
  inaccessible, discovers the command through installed help, resolves every runtime
  helper/schema/template from the package, and runs/collects one read-only attempt.
- A pre-existing independent channel judges any new approval/verdict surface;
  candidate-worker dogfood alone cannot close its own acceptance.

## Edge And Expansion

The hard part worth doing is provenance-preserving host execution, not spawning a
process. Charness already has unusual strength in typed receipts, delivery identity,
worktree proof, and irreversible-boundary review. Generalizing those primitives gives
it an edge over repo-local shell orchestration while reducing the need for more prose
rules.

The narrow wedge is one read-only external attempt attached to `charness task` and
used by `critique`. Expansion then follows measured demand: investigation, isolated
implementation, cross-repo work, and other hosts. A consumer's custom command remains
data in its adapter rather than a new Charness feature.

Feedback arrives through two real dogfood loops: Charness authoring and Ceal as an
installed consumer. The second loop is essential because package-root, local-policy,
and repo-capability errors are invisible in the authoring checkout.

## Agent And Human Fit

- Agents receive one bounded brief and structured terminal state rather than needing
  to infer scope, ownership, or whether a child actually returned.
- Humans receive a durable task/attempt id, inspectable status, idempotent collect,
  a final receipt, and full logs on failure; they do not have to tail interleaved
  output or remember which proxy is authoritative.
- `AGENTS.md` stays compact and portable. Host mechanics live in adapters/docs. A
  later, tracked opt-in may load ignored local policy last only after tests prove the
  effective identity and prevent those bytes from entering tracked artifacts.
- High-risk permission remains visible and machine-local. Installing Charness must not
  silently grant unsandboxed execution.

## Open Questions

- Confirm the recommended ownership decision: extend `charness task` with external
  attempts and keep `lane` non-canonical, rather than create a second durable store.
- Should write-capable v1 require the worker to commit in its isolated worktree, or
  accept either a commit or a frozen diff carrier? The parent-integration invariant
  holds either way, but recovery and hook evidence differ.
- Local instruction wiring is a later tracked-adapter opt-in, not a new default of
  `charness worktree prepare`. Its precedence and conflict-recovery details belong to
  that write-capable specification.
- Is Ceal authorized as a write target for the later adoption slice, or should its
  first proof remain read-only while a disposable consumer fixture owns all writes?

## Structured Questions

- Q1 | urgency: must-resolve | depends-on: null | action: spec | note: obtain user confirmation of `charness task` as the one durable owner and `lane` as non-canonical vocabulary before writing the contract
- Q2 | urgency: must-resolve | depends-on: Q1 | action: spec | note: decide whether write-capable v1 requires a candidate commit or permits a frozen diff result
- Q3 | urgency: defer | depends-on: Q1 | action: hold | note: define precedence and conflict recovery for the decided tracked opt-in AGENTS.local.md composition in a later spec
- Q4 | urgency: probe-in-impl | depends-on: Q1 | action: impl | note: reproduce the reviewer runner relative-path mismatch and nested isolated CODEX_HOME requirement before extracting the common executor
- Q5 | urgency: must-resolve | depends-on: null | action: spec | note: bind the refreshed 46-row matrix and replay plan for the thirteen included rows plus #698 before implementation slices
- Q6 | urgency: defer | depends-on: Q1 | action: hold | note: obtain explicit scope before writing an adoption config or tracked artifact into ../ceal

## Next Step

Stay in `ideation` for operator confirmation of Q1. Then create two contracts: an
issue-retirement ledger driven by the 46-row matrix, and an external-worker spec that
extends `charness task`, assigns one host process/configuration owner, and defines the
read-only lifecycle acceptance journey. The first implementation slice is read-only;
local-instruction composition and write-capable attempts follow only after clean-room
installed-consumer proof and independent review of any verdict-logic change.
