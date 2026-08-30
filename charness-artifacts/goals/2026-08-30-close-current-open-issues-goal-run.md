# Achieve Goal: Close the activation-snapshot open backlog with per-issue proof

Created: 2026-08-30
Planning record: mutable until Goal Binding; the binding freezes these exact bytes and the approval-bundle identities named below.

## Goal

Close every issue that is OPEN in `corca-ai/charness` at Goal Run activation through a dependency-aware generative sequence, while preserving each issue's JTBD, provider identity, independent closeout carrier, behavioral verdict or typed disposition, and provider `CLOSED` readback.

## Non-Goals

- Do not keep expanding the goal to issues opened after activation. Later issues are reported and enter only through an explicit Goal Run graph amendment or a later goal.
- Do not replace fourteen independent issue outcomes with one aggregate green build, one umbrella comment, or one shared behavioral verdict.
- Do not detach #748, #749, or #753 from #744, reopen #747, erase historical issue context, or create duplicate cluster trackers.
- Do not publish a release, create a pull request, push, close an issue, or alter the supported-host matrix without the selected route's explicit authority.
- Do not preserve an implementation merely because an issue body proposes it. Revalidate the premise, measurements, current code, and consumer first.
- Do not make Charness own consumer-repository policy or exhaustive Git topology behavior. Charness provides composable capabilities and typed observations/refusals; the agent operating a consumer repository composes them and owns repository-specific decisions.
- Do not weaken closeout, Goal Run binding, fresh-eye, source/export synchronization, provider readback, or skipped-check semantics to make a large backlog appear complete.
- Do not turn #753 into an unbounded deletion campaign or turn #761's unprobed states into a passing claim.

## Boundaries

- Provider target: `corca-ai/charness`; backend: adapter-selected `gh`. The shaping observation on 2026-08-30 found exactly fourteen OPEN issues with `comments_read: true`: #709, #731, #744, #748, #749, #751, #752, #753, #756, #758, #759, #760, #761, and #762.
- Selected executable topology: reuse #744 as the Goal Run parent. Preserve its exact seven existing children (#743, #745, #746, #747, #748, #749, #753), then add the ten currently unparented open issues (#709, #731, #751, #752, #756, #758, #759, #760, #761, #762) as direct children. The resulting approved child set has exactly seventeen identities; four are historical CLOSED children and thirteen are activation-open Work Items. Parent #744 is the fourteenth activation-open issue and is a separate terminal obligation, not a Work Item cursor.
- This topology broadens #744 from a Rust-core umbrella into the Goal Run parent only through an explicit managed addendum. Its original architecture history, existing child graph, and final reconciliation obligation remain visible. A new parent with #744 nested is rejected by current Goal Run execution semantics because nested #748/#749/#753 would not receive direct approved Work Item cursors.
- Goal activation and issue mutation are not authorized by this draft. Do not update #744, add child relationships, comment, close, or bind until the binding-enforcement repair is published, its one bounded proof-surface fresh-eye passes, and the operator approves the exact briefing and final bundle bytes.
- An existing issue may be reshaped only through a managed addendum that preserves its JTBD, evidence, comments, and identity. A failed premise probe changes the work required inside that same Work Item; it does not silently remove the issue from scope.
- Each of the thirteen activation-open child issues keeps its own classification, carrier, falsifiable predicate, behavior verdict or typed disposition, and `CLOSED` readback. Goal execution has one mutable parent `progress.next` cursor; exactly one child carries the active Goal Work Item identity at a time. #744 has no child cursor; its separately bound terminal obligation requires exact seventeen-child readback, 17/17 issue-owned evidence identities, 17/17 closed state, and parent close/readback proof.
- Bug-class issues use `debug` before fix design when the cause is not already falsifiably established. Verdict-rendering repairs use distinct negative controls and the fresh-eye rounds required by the owning contract.
- Reversible, disjoint investigation and candidate authoring use `./charness task run` Codex lanes aggressively across Work Items. Repo-fixed lane model and read-only subagents use `gpt-5.6-luna`; implementation/proof lanes use `xhigh` effort. A future-item candidate is neither integrated evidence nor Goal progress. The parent alone serializes integration, publication, generated-surface synchronization, provider cursor transitions, comments, closes, and final verification.
- The parent worktree must be clean before each lane. A lane receipt is candidate evidence, not parent-tree proof. Collision preflight compares current base, owned paths, generated owners, and overlapping candidates before integration.
- Canonical source is edited before generated/plugin surfaces. Run `python3 scripts/sync_root_plugin_manifests.py --repo-root .` and catalog refresh only when the owner map requires them. A skipped check stays `skipped`, never `passed`.
- Publication route, behavioral proof, remote CI, provider close, and Goal Run terminal readback are distinct boundaries. The chosen route remains durable for retry.
- The existing local-ahead history is not implicitly authorized for publication. Before any push, bind the exact provider merge-base and candidate ref, enumerate every commit/path/close-keyword effect in that delta, map each to an approved Work Item or named supporting artifact, and refuse unrelated or unproven content.
- Pre-activation provider capability includes the guarded `goal-run-close` ingress, typed partial outcomes, idempotent retry/recovery, final-proof index binding, terminal parent-metadata update, still-`CLOSED` readback, and binding-enforced body/relationship writes. The activation manifest names the exact published provider SHA and CI receipt.

### Activation observation and drift contract

1. After the three operator decisions are resolved, perform one approval-cut observation `O0`: uncapped OPEN listing, exact read including comments for every observed issue, #744 body/state read, and exact sub-issue read.
2. Materialize `charness-artifacts/goals/2026-08-30-close-current-open-issues-activation-manifest.json`. It records repository, observation timestamp, provider base SHA, each activation-open issue number/title/state/canonical provider-payload digest/parent, exact digest producer commands, the desired seventeen-child set, current graph, and every approval-bundle identity.
3. Materialize `charness-artifacts/goals/2026-08-30-close-current-open-issues-expected-children.json` with exactly `[709, 731, 743, 745, 746, 747, 748, 749, 751, 752, 753, 756, 758, 759, 760, 761, 762]` in canonical numeric order. Validate shape before approval and use it with `list-sub-issues --expect-child-file` after graph establishment and before parent close.
4. Validate `charness-artifacts/goal-runs/744/approved-work-items.json` through Goal Binding V1's canonical manifest validator. Its seventeen rows freeze stable key, exact reuse identity, dependencies, integer rank, body policy/digest, and observed title/body fingerprints. The thirteen open bodies live under `charness-artifacts/goal-runs/744/bodies/`; the four closed rows use `preserve-closed-evidence`.
5. Present only the files consumed by binding or activation: the draft, activation and expected-child manifests, V1 Work Item manifest/bodies, parent terminal obligation, provider plan, and durable provider-preflight receipt. Run docs/secrets once before briefing; the proof-surface fresh-eye belongs to the integrated provider repair, not to later hash/prose refreshes.
6. Immediately before local immutable binding creation, rerun the activation manifest's exact `jq -cS` digest commands and parent/graph reads. Any mismatch stops for re-observation, repaired review, and reapproval. Create Goal Binding only after an exact match.
7. After binding, publish only the audited approval metadata on an isolated integration base if required for durable clean-process recovery, then perform binding-bound parent/body/relationship writes. Each open issue body file is a complete target body whose byte prefix is the exact `O0` provider body and whose suffix is the approved managed addendum. Immediately before its write, `read-body` must match the binding's observed body SHA; the target file must match its manifest SHA; `update-body` must read back the exact combined bytes. This preserves the original issue context in place rather than replacing it with a short fragment. Re-run the activation digest/graph comparison immediately before the first provider mutation. Establish the exact graph, set the single parent cursor to the first executable child, and activate only after strict readback is green.
8. Drift after binding never passes silently; it uses the explicit amendment/reapproval path and a new immutable planning/binding identity.

Approval-cut identities from `O0`:

- Activation manifest SHA-256: `102a2f849b49accb968869200338db92d17810267446d72cabd7c90e70cddf70`.
- Expected-child-file SHA-256: `8c7d8a81f9fcb8d66977cca5ee569a8d8bbdd4632508f06fe980dd92a8f312b8`.
- Approval reviewed-path manifest: 21 paths (20 activation inputs plus this binding-consumed briefing); SHA-256 `f35cd92a9d61541d36da6e4e512dc31411ae9fdeaaf57a018e0fb6ac4807cf0b`.
- Desired canonical child-number digest: `f6503f10c15a89d855bbb0da9cb52fc082e4dd2410f9b9f8ccebfa0383e8a7ab`.
- V1 approved Work Item file SHA-256: `0d4cfbcc39c5fb04ffdd76d0a7aaf1ab85b8777e7021ddd433bf60af5b0e7d48`; canonical items SHA-256: `e6be1f983d6c3851a1f4810ec45b4980c027a7d49fccb5be724d3e261e9da475`; count: 17.
- Parent terminal obligation SHA-256: `05d1037be37f14f2ce15f3b64d88cea1b5673e9c950926a3ed2c1e1f6e26f486`.
- Provider prerequisite: main `ab4b2d8b72d9450dbab32da89e4934acdf6724e8`; Quality Core run `33295371954` succeeded for that exact SHA.
- Provider plan SHA-256: `76b0c45e485e6feb66956004fc53974229c07cd39000cca1aacd5b9f96c6f440`; provider-preflight SHA-256: `dfb76379c819aae241f68c4d87e833a54ed96ccfdfae49e1bcc85ae712af7338`. The durable parent-run preflight observed `ready` against that provider main and invoked no mutation. Readiness is re-proved again immediately before activation.
- Current graph read is an expected pre-activation `graph-mismatch`: exactly the ten approved additions are missing and no unexpected child exists. This is a verified read and no mutation claim; post-binding graph establishment must turn the same strict read green.

## User Acceptance

- The approval-bound activation manifest contains every issue OPEN at `O0` exactly once: #744 as the non-cursor parent terminal obligation and the other thirteen as direct open Work Items. The exact provider graph equals the seventeen-child expected file with no additions, omissions, duplicates, or reparenting.
- The operator can see the dependency rank, issue class/JTBD, premise status, Codex lane boundary, falsifiable proof, publication gate, and provider carrier for every activation issue.
- #758 and #759 are premise-probed first. A passing already-fixed/published probe produces a no-code closeout in the same Work Item; a failing probe produces implementation and proof there, without changing rank or identity. Each proved Work Item publishes its comment/close/readback and advances the single cursor before another begins.
- #751, #752, and #709 close the shared “verdict about a question never asked” class without adding a meta-gate, while retaining separate positive and negative controls.
- #756 precedes #731 so backend invocation and normalization have one owner before broader lifecycle/partial-progress work.
- #759, #760, and #762 converge on one coherent declaration/input identity contract: deletions remain bound, enumerators agree, and default-path refusal gives an actionable supported route. #761 closes through an explicit ownership disposition: consumer-specific submodule topology belongs to the consumer repository's agent, not Charness core.
- #748 closes the generic native capability slice already proven on provider main, without claiming the two consumer-artifact-dependent helper migrations. #753 and #749 close as explicit `not planned` dispositions: current evidence does not establish capability equality, a consumer-rework JTBD, or mutation/type-boundary proof that would justify count-driven deletion or migration. #744 closes only after its original architecture is reconciled and all seventeen direct children are CLOSED.
- Every implementation issue has focused deterministic proof and an independent behavioral verdict or typed disposition. Every bug close has required causal/critique evidence. Every child close has an issue-owned comment URL captured in the exact 17-row close-proof inventory plus provider `CLOSED` readback distinct from behavior proof.
- Applicable focused gates run before broad gates. `./scripts/run-quality.sh --full --read-only` runs on each material integrated tree defined below. Changed-line/mutation proof is claimed only if the operator selects a release and `./scripts/run-quality.sh --release` completes; it is not an ordinary implementation requirement.
- The final report lists all fourteen activation issues with carrier, behavior evidence, CI classification, and provider state; then performs a fresh uncapped OPEN query. Later-opened issues are reported out of scope.
- #744 closes only after all thirteen activation Work Items, four historical children, seventeen issue-owned evidence identities, whole-system docs/proof reconciliation, exact graph readback, final provider-main CI requirement, guarded close, terminal metadata update, and a second still-`CLOSED` parent readback succeed.

## Agent Verification Plan

### Low-Cost Checks

- Re-run the lesson preview with seed `close-all-open-issues-20260830`; resolve achieve/issue/critique adapters and record backend/interview ceiling.
- At `O0` and both drift barriers, run the activation manifest's literal canonical commands, exact issue/comment reads, #744 graph read, and expected-child-file comparison. Compare complete hashes, not prose or timestamps.
- At each Work Item pickup, re-read issue state/comments, current branch SHA, approved cursor, earlier carrier, and premise status before design.
- Validate closeout carrier shape before publication. Record close keywords, classification, `AI-provenance`, issue-specific `Behavior #N:`, HOTL disposition when present, and critique binding where required.
- Before freezing approval bytes run `./scripts/check-docs.sh` and `./scripts/check-secrets.sh`. Re-run them whenever a later draft edit changes reviewed bytes.

### Per-issue falsifiable proof and closeout matrix

| Issue | Class / JTBD predicate | Positive and negative control | Evidence / disposition carrier | CI and provider close |
| ---: | --- | --- | --- | --- |
| #709 | deferred-work: `new_doc_family_count` and sample represent a real non-zero new-family set | non-zero family drives count+sample; zero-family input stays zero/empty; deliberately stale projection fails | focused projection tests + issue resolution brief | local behavior; closeout carrier then `CLOSED` readback |
| #731 | feature: bounded review preserves useful partial progress while lifecycle cleanup remains correct | partial worker output survives timeout; exit-code-only/identity-mismatched output is ineligible | lifecycle/cleanup tests, task receipt, resolution critique | local behavior; final main CI gates parent |
| #744 | feature umbrella/Goal parent terminal obligation: original Rust-core reversal and all approved children reconcile honestly | exact 17-child file passes only at 17/17 CLOSED with 17 issue-owned evidence identities; missing/extra/open/evidence-less child refuses | bound parent terminal obligation, architecture reconciliation, graph and terminal receipts | no Work Item cursor; guarded parent close, metadata update, still-`CLOSED` readback |
| #748 | completed capability slice: typed native inventory/classification/component/reverse-reader commands are published | exact-SHA native inventory JSON is established; deferred helper/plugin/consumer claims stay absent | provider commits plus exact-SHA `repograph.inventory.v1` readback | close `completed` for the bounded capability, then provider readback |
| #749 | not-planned disposition: no current consumer-rework JTBD or approved retained-Python capability delta | source audit shows no checker/boundary/selective export; absence is not rendered as implementation success | provider-source boundary audit + explicit non-claims | close `not planned`, then provider readback |
| #751 | bug: reviewer is not launched when reviewed semantic content is empty | semantic packet launches; empty/deletion-only subject refuses or skips; wrong path-count proxy fails | focused packet/worker tests + resolution critique | local behavior; closeout readback |
| #752 | bug: prepare/doctor reports ready only for responsibilities it actually proved | prepared state passes; omitted responsibility remains unready; false-ready fixture fails | doctor/prepare coverage + resolution critique | local behavior; closeout readback |
| #753 | not-planned disposition: additional pruning requires capability equality, not a ratio target | 358/371 quality-gate files remain load-bearing and mutation non-regression is absent; historical `wc` is rejected in favor of current official `tokei` | bounded JTBD audit + current `tokei` readback + explicit residuals | close `not planned`, then provider readback |
| #756 | deferred-work: backend invocation/normalization has one owner | all supported backends normalize; backend-specific failure/timeout stays typed; duplicate path fixture fails | backend matrix tests and source-owner diff | local behavior; closeout readback |
| #758 | bug/premise probe: provider-main mutation workflow is green for the relevant published SHA | original failing run contrasted with current same-scope success; unrelated green run rejected | live workflow URLs/SHAs or new debug+fix artifact | remote CI is behavioral and must precede close |
| #759 | bug/premise probe: deletion ranges remain reviewable and bound in the published implementation | added/modified/deleted ranges pass; deliberate deletion omission or stale digest fails | range tests, carrier audit, resolution critique | local behavior; provider-main CI observational for issue, gating for parent |
| #760 | deferred-work: every changed-path enumerator agrees on one canonical subject | merge/rename/delete/non-ASCII/staged/worktree fixtures agree; deliberately divergent enumerator fails | agreement matrix and owner-map evidence | local behavior; closeout readback |
| #761 | decision disposition: Charness exposes composable reviewed-input capabilities but does not own consumer-specific submodule topology policy | core makes no new nested/conflicted/non-HEAD claim; the closeout must not describe missing consumer proof as verified behavior | architecture ownership record and `not planned / superseded` closeout | no implementation or live consumer proof; provider readback only |
| #762 | decision-needed: default refusal identifies differing paths and exact supported remedy | committed-packet mismatch lists paths+`--reviewed-paths-file`; silent auto-inclusion/self-review mismatch fails | default-path UX tests and decision record | local behavior; closeout readback |

Premise and decision writebacks are mandatory: #758 and #759 record `already resolved` or `implementation required`; #748 records the exact completed capability boundary; #753 and #749 record `not planned` with the evidence that prevents count-driven work from reading as a tie; #762 records the operator-approved actionable-remedy policy; #761 records the consumer-agent ownership boundary and makes no new submodule correctness claim. Each writeback lives in its issue-specific resolution artifact and the provider closeout carrier.

### High-Confidence Checks

- #751/#752/#709 run the matrix's empty, positive, and wrong-answer controls; no aggregate shared verdict substitutes for the three issue predicates.
- #756/#731 cover supported backend commands, normalization, timeout/interruption process-tree cleanup, partial-progress preservation, terminal delivery, identity binding, and approval-ineligibility of partial/exit-code-only evidence.
- #759/#760/#762 vary deletions, committed critique packets, merge commits, staged/worktree removals, non-ASCII default quoting, renames, and pointers. #761 adds no Git-topology test matrix.
- #748 captures exact-SHA native inventory through a command output channel distinct from its implementation commits. #753 uses the existing JTBD audit plus current official `tokei` measurement; historical `wc` counts are context only, comments are never shaved to move a bar, and no mutation claim is made. #749 records the current absence of a checker/boundary/selective-export capability and does not substitute line reduction for consumer value.
- One bounded Luna fresh-eye inspects the integrated proof/provider repair before activation. The next fresh-eye occurs only when the final #744 close packet is ready for its irreversible provider write; approval prose/hash refreshes do not trigger another round.
- Material broad-gate clusters are the integrated #751/#752/#709 tree, #756/#731 tree, #759/#760/#762 tree, and final fully integrated tree. #748/#753/#749/#761 are bounded proof or disposition closeouts, not invented test clusters. Run focused owner gates first, then `./scripts/run-quality.sh --full --read-only` only on a material integrated tree. A previously green broad receipt may be reused only for the identical tree digest and declared command identity.

### External or Live Proof

- The prebinding publication audit rejects the known eleven-commit local prefix as an indivisible publication base. Work Item execution starts an isolated integration lane from current provider main `ab4b2d8b7`; no current local commit is pushed wholesale. Before each publication, recompute the exact `provider-base..candidate-ref` delta and refuse any unmatched commit, path, generated surface, keyword, or carrier.
- Under the selected direct-main route, each active Work Item uses two stages: publish its implementation commits without close keywords; observe required remote CI/live proof; then publish its issue-owned comment and issue-specific closeout carrier, verify `CLOSED`, and synchronize the parent cursor. #758 always requires its remote behavioral proof before close. For other issues, remote CI is observational at child close but a green current provider-main run is mandatory before #744 closes.
- Under a PR route, the same delta audit and proof order apply at the merge candidate. Under a release route, release-final checks and live installed-surface proof are additive and changed-line/mutation coverage comes only from the release owner.
- After each predicate/disposition, publish and read back an issue-owned closeout comment URL; only then invoke its close carrier and run `issue_tool.py verify-closeout --expect-state CLOSED`. Update the exact close-proof inventory. Commit auto-close or tracker state alone cannot satisfy parent proof.
- For #761, publish only the approved ownership disposition: Charness supplies composable capabilities; the consumer repository's agent owns submodule-specific composition and proof. Do not add a live probe, implementation claim, or new product restriction.
- Before #744 close, execute `charness-artifacts/goal-runs/744/terminal-close-recipe.md`: bind final provider-main CI, integrated gates, docs/secrets and skip dispositions, exact 17-row evidence map, graph proof, guarded close comment, terminal observation, parent metadata update, second still-`CLOSED` readback, and final uncapped OPEN query.

## Slice Plan

| Slice | Objective | Why Now | Dependencies |
| --- | --- | --- | --- |
| prerequisite. Provider boundary | Publish the guarded close ingress plus binding-enforced expected graph, managed child bytes/live pre-write digest, parent body preservation, and relationship identities. | Provider capability must exist before activation; prose cannot repair an irreversible boundary. | exact provider SHA and CI are frozen in the activation manifest |
| 0. Observe, approve, bind, establish | Freeze `O0`, V1 Work Items, bodies, parent obligation, close inventory, terminal recipe, publication audit, and provider evidence; run checks/reviews; approve exact bytes; reverify O0; create immutable binding; only then write bodies/add ten relationships, prove exact graph, set the single cursor, and activate. | Makes every provider write binding-bound while giving thirteen non-parent open issues serial executable identities. | prerequisite complete |
| 1. Premise probes and ownership disposition | Execute #758, then #759, then #761 serially. Each item proves/dispositions, publishes its issue-owned comment and carrier, verifies `CLOSED`, updates the evidence inventory, and advances `progress.next` before the next item. | Separates stale trackers and consumer-owned policy from real Charness implementation before later ranks. | Slice 0 |
| 2. Empty-subject class | Resolve/close #751 first, then execute/close #752 and #709 one at a time with separate proof records and cursor transitions. | Establishes the discriminating property before projections and readiness claims. | Slice 1 |
| 3. Worker boundary | Execute/close #756, advance the cursor, then implement/close only #731's revalidated residual. | Gives backend/failure vocabulary one owner before lifecycle/partial-progress changes. | Slice 2 |
| 4. Declaration integrity | Execute/close #760, advance the cursor, then execute/close #762. | Prevents later evidence from binding a different subject than reviewers read. | Slice 1 |
| 5. Native/test disposition | Close #748 from exact-SHA native capability readback, close #753 `not planned` from JTBD audit plus official `tokei`, then close #749 `not planned` from the provider-source boundary audit, one cursor transition at a time. | Applies the North Star's consumer-rework purpose and taste precondition instead of manufacturing code/test-count work. | Slice 0; #749 after #748 and #753 |
| 6. Parent terminal closeout | Reconcile #744, sync owned generated surfaces, audit final publication delta, bind final proof, verify every child/evidence row and graph, execute the prerequisite-hardened close ingress, update/read back terminal metadata, and report later opens. | Keeps behavior, CI, provider, graph, and terminal claims distinct. | Slices 1–5 |

### Execution waves, ownership, and integration barriers

| Wave | Codex lane / carrier | Scope owner and collision rule | Export and gate barrier |
| --- | --- | --- | --- |
| A | read-only parent probes for #758/#759; while #758 live proof runs, disjoint future-item candidates may be authored locally | Parent owns provider/commit history; candidate lanes name exact source/tests and current base | no future candidate is integrated or published until its cursor turn; issue-specific focused proof precedes publish |
| B1 | provider order remains #751, then #752, then #709 | Disjoint candidate authoring may occur earlier; parent owns shared docs, manifests, and generated surfaces | each Work Item integrates, proves, closes, reads back, and advances before the next provider transition |
| B2 | active #756, then active #731 after #756 closes and cursor advances | #756 owns backend extraction; #731 begins only from the published/closed #756 base | focused backend matrix and transition after #756; lifecycle matrix + cluster broad gate after #731 |
| C | provider order remains #760, then #762 after #760 closes and cursor advances | #760 owns the canonical enumerator; #762 authoring waits for that interface, though read-only premise work may run earlier | declaration cluster broad gate after both serial transitions |
| D | provider order remains #748, then #753, then #749 | Read-only proof capture may run in parallel; these are bounded capability/disposition closeouts with no count-driven implementation lane | per-item comment/close/readback/cursor transition; no invented native test cluster |
| E | parent-only terminal closeout | Parent owns #744 reconciliation, final provider graph, final proof index, direct-main final audit, guarded close, terminal metadata, and readback; child comments/closes already occurred at their transitions | execute the prerequisite-hardened terminal recipe; no release gate because Decision 1A selected no release |

Every lane brief records base SHA, allowed paths, forbidden shared surfaces, focused command, expected artifact, and stop condition. Disjointness must be established before parallel authoring. A changed base or overlapping candidate forces rebase/re-review before integration; no two lanes write parent-only surfaces, and provider progress remains single-cursor serial.

### Exact proposed Work Item graph

| Issue | Activation role | Dependency rank |
| ---: | --- | --- |
| #709 | direct open child | after #751 |
| #731 | direct open child | after #756 |
| #743 | preserved historical CLOSED child | evidence only |
| #745 | preserved historical CLOSED child | evidence only |
| #746 | preserved historical CLOSED child | evidence only |
| #747 | preserved historical CLOSED child | superseding reconciliation, no reopen |
| #748 | preserved direct open child | first native ownership slice |
| #749 | preserved direct open child | after #748 and #753 findings |
| #751 | direct open child | after premise probes |
| #752 | direct open child | after #751 |
| #753 | preserved direct open child | bounded/disjoint with #748 |
| #756 | direct open child | after empty-subject cluster |
| #758 | direct open child | first premise probe |
| #759 | direct open child | first premise probe |
| #760 | direct open child | after #759 probe/proof |
| #761 | direct open child, no-code ownership disposition | Slice 1 after binding |
| #762 | direct open child | after #760 and Decision 1 carrier semantics |

## Discuss Before Activation

- Decision 1 — publication route.
  - Alternative A (recommended): direct-to-main, two-stage publication. Push audited implementation commits without close keywords, wait for required remote proof, then push issue-specific closeout carriers; no release.
  - Alternative B: PR-based carriers and merge readback. Adds a human merge boundary while preserving the same delta/proof order.
  - Alternative C: include a release. Highest external cost; adds release-final changed-line/mutation and installed-surface proof.
  - Operator answer: **A — direct-to-main, two-stage publication.**
- Decision 2 — #761 proof target.
  - Alternative A: make Charness core prove consumer-specific submodule states in a named real repository.
  - Alternative B: make Charness core simulate those consumer states in disposable repositories.
  - Alternative C (selected): close #761 as `not planned / superseded` with no new implementation or restriction. Charness supplies composable capabilities; the agent in each consumer repository owns topology-specific composition and proof.
  - Operator answer: **C — consumer repository agents own this concern.**
- Decision 3 — Goal Run parent topology.
  - Alternative A (recommended): reuse #744 as the Goal Run parent, preserve its seven children, and add the ten unparented issues directly. This is executable with the current direct Work Item cursor and preserves all identities, but explicitly broadens #744 through an addendum.
  - Alternative B: create a new parent and reparent #748/#749/#753 to it so all activation-open issues are direct. This adds provider churn and weakens #744's history.
  - Alternative C: wait for nested Work Item cursor support. No provider mutation occurs, but this goal cannot activate now.
  - Operator answer: **A — reuse #744 as the Goal Run parent.**

## Context Sources

- `AGENTS.md`; `docs/index.md`; `docs/design-north-star.md`; `docs/goal-lifecycle.md`; `docs/operating-contract.md`; `docs/parallel-execution.md`; `docs/agent-task-runs.md`; `docs/implementation-discipline.md`; `docs/validator-timing-layers.md`; `.agents/codex-host.md`.
- `.agents/achieve-adapter.yaml`; `.agents/issue-adapter.yaml`; `.agents/critique-adapter.yaml`.
- Provider shaping reads on 2026-08-30 for all fourteen issues including comments, exact #744 sub-issue list (7 total, 4 CLOSED, 3 OPEN), and parent reads for #748/#749/#753.
- Prior goals: `2026-08-05-close-all-open-issues-generative-sequence.md`, `2026-08-06-current-open-issues-generative-sequence.md`, `2026-08-07-close-every-open-issue-declaration-to-verdict.md`.
- Design/retro evidence: `2026-08-30-next-session-plan.md`, `2026-09-01-next-session-plan.md`, `2026-08-28-umbrella-744-rust-core-session-retro.md`, `2026-08-30-session-retro.md`.
- Codex lane memo: `charness-artifacts/design-studies/2026-08-30-current-open-issue-goal-architecture.md`, integrated as local commit `d309412d6`.
- Approval bundle: `charness-artifacts/goal-runs/744/approval-reviewed-paths.txt`; the Goal Draft and activation/expected-child manifests; `approved-work-items.json`; thirteen `bodies/*.md`; `parent-terminal-obligation.md`; `provider-plan.json`; and `provider-preflight.md`.
- Lesson seed `close-all-open-issues-20260830`: `skipped-is-not-passed`, `goal-closeout-evidence-binding`, `stale-current-pointer-at-closeout`, and release-final changed-line ownership.
- Shaping repository identity began at provider `main` `dc77742f2`; the separately authorized provider prerequisite advanced main through `8f5d18ea2`, `213e28b72`, and `ab4b2d8b7`. Current local `main` still includes eleven excluded commits through `d309412d6`; this is evidence context, not publication authority.

## Interview Decisions

- Scope meaning — resolved: freeze the complete live OPEN set at approval-cut observation `O0`; later issues require amendment or a later goal. Rejected: an unbounded queue with an unstable terminal condition.
- Work Item strategy — resolved: reuse existing issue identities instead of creating cluster duplicates. Rejected: managed duplicates that grow the backlog and weaken direct readback.
- #747 historical correction — resolved recommendation: a verified superseding addendum/comment linked from #744, not reopening #747. Historical completion and later architectural retirement can both remain true.
- #762 owner call — resolved recommendation: retain safe exclusion/exactness while making default refusal enumerate differing paths and name `--reviewed-paths-file`. Rejected: silent auto-inclusion before self-review semantics are proven.
- Capability ownership — resolved by operator: Charness owns composable capabilities and typed results, not consumer-repository Git topology policy. #761 therefore receives a no-code `not planned / superseded` disposition with no new restriction; consumer agents own any repository-specific proof.
- Reviewer/lane policy — resolved by operator: use `charness task run` Codex lanes aggressively for disjoint work and Luna for lanes/subagents. Parent owns integration, external writes, and final proof.
- Publication route — resolved by operator as direct-to-main with two-stage publication: audited implementation commits first without close keywords, required remote proof second, issue-specific closeout carriers last; no release.
- Parent topology — resolved by operator: reuse #744 as the Goal Run parent, preserve its seven existing children, add the ten unparented open issues directly, and record the scope broadening in a managed addendum.

## Plan Critique Findings

Initial two-angle review used packet identity `6015111c...` and reviewed-input identity `550f17e3...`; both file-backed workers returned `block`, correctly treated as design findings rather than runner failure.

- Act Before Ship — activation identity: accepted. Added `O0`, exact issue/comment digests, manifest and graph digests, approval binding, and drift/reapproval rules.
- Act Before Ship — nested cursor: accepted. Replaced the non-executable new-parent proposal with Decision 3 and recommended #744-as-parent direct Work Item topology.
- Bundle Anyway — graph count/set: accepted. Corrected the set to ten added children, seven preserved children, seventeen total direct children, thirteen activation-open children, plus open parent #744.
- Act Before Ship — probe/defer ambiguity: accepted. #758/#759, #749, #761, and #762 now have mandatory typed writebacks and stable issue identities.
- Bundle Anyway — graph proof: accepted. Added the exact expected-child file and strict `list-sub-issues` checks.
- Act Before Ship — unbounded publication delta: accepted. Added provider-base-to-candidate commit/path/keyword mapping and a refusal gate for unrelated content.
- Act Before Ship — lane operability: accepted. Added execution waves, owners, collision preflight, parent-only surfaces, serial integration, and cluster barriers.
- Act Before Ship — issue proof predicates: accepted. Added fourteen falsifiable issue rows with controls, artifacts, CI semantics, carriers, and readbacks.
- Act Before Ship — changed-line owner mismatch: accepted. Removed the ordinary claim; release-final proof exists only under a selected release route.
- Bundle Anyway — pre-freeze checks/reuse: accepted. Added docs/secrets checks, material broad clusters, and digest-bound receipt reuse.
- Act Before Ship — close-before-CI race: accepted. Recommended two-stage direct-main publication and made #758 remote CI behavioral; other issue closes retain local behavior proof while final provider-main green gates #744.
- Counterweight: rejected successor issues for #731/#758 because both existing issues remain usable direct identities. Retained the Codex lane memo's dependency clusters and exact graph evidence, but superseded its new-successor suggestion and its initial #744-parent reasoning where the current cursor contract required correction.
- Follow-up review over packet `c24ac451...` / input identity `366067c6...` also returned two valid `block` verdicts. Graph findings identity: `2ee7ee21...`; operability findings identity: `9be2d81a...`.
- Act Before Ship — exact V1 manifest: accepted. Added a validator-clean, key-sorted seventeen-item manifest with exact issue identities, dependencies, ranks, body policies/digests, observed fingerprints, thirteen managed bodies, and four preserved closed-evidence rows.
- Act Before Ship — binding/mutation order and #744 cursor: accepted. Binding now precedes every provider write; only thirteen non-parent open issues get direct cursors, while #744 has a separately hashed parent terminal obligation.
- Act Before Ship — reproducible O0: accepted. The activation manifest now owns literal `gh`/`jq -cS` producers, serialization/hash rules, and two comparison barriers.
- Act Before Ship — unpublished prefix feasibility: accepted. The prebinding audit rejects the eleven-commit prefix as a wholesale push and selects an isolated provider-base integration lane with incremental mapping/refusal.
- Act Before Ship — child evidence identities: accepted. Added an exact seventeen-row inventory; the four historical comment URLs are bound now and every open child must produce/read back its own comment URL before close.
- Act Before Ship — terminal recipe: accepted and resolved. The separately authorized prerequisite now enforces the bound final-proof index and terminal parent-metadata/readback lifecycle on provider main; the recipe retains no manual execution-time fallback.
- Act Before Ship — single cursor and child closure: accepted for provider state. One child proves, comments, closes, reads back, updates evidence, and advances `progress.next` before the next provider transition. The later North Star review corrected the overreach that had serialized reversible local authoring: disjoint future-item candidates may run in parallel, but integration, publication, shared/generated surfaces, cursor updates, and closes remain serial.
- Third review over packet `1f567e205326ce0881711e3ebc8a851a5af68545c0a6f4c6f9e70917e0168218` / input identity `d03849df9025188769ea99154c46bf6365d115eb78cc722d82577e04bd18daeb` returned two valid `block` verdicts. Graph findings identity: `1a61bed...`; operability findings identity: `df897a...`.
- Act Before Ship — relationship producers: accepted. The activation manifest now owns literal parent and sub-issue producer commands, canonical serialization, digests, and both pre-binding/pre-mutation comparisons.
- Act Before Ship — body preservation: accepted. Every managed target body now starts with the exact observed provider body and appends the Goal Work Item contract; pre-write drift and full-byte readback are mandatory.
- Counterweight — reviewer authentication: the review worker's sandbox could not prove provider auth, but the parent-run durable preflight independently returned `ready` with auth exit 0 and `mutation_invoked: false`. Treat the sandbox result as environment-limited, while still re-running readiness at activation.
- Remaining activation gate: the one bounded proof-surface fresh-eye must pass, the minimal bundle hashes must be frozen mechanically once, and the operator must approve the exact bytes.
