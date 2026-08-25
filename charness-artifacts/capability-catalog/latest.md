# Capability Catalog
Date: 2026-08-25
Updated: 2026-08-25T11:47:01Z

## Summary
- public skills: 20
- support skills: 2
- support capabilities: 2
- integrations: 13
- trusted skills: 0

## Public Skills
- `achieve` (public skill): Use when operating a long-running autonomous objective as an auditable goal lifecycle: interview prose intent into a reviewable goal artifact under charness-artifacts/goals/, keep slice progress and verification visible during the run, and prove the goal with honest non-claims at the end. Coordinates ideation/spec/impl/quality/issue/critique/retro around one goal artifact instead of replacing them, and stays a goal operator rather than a task execution engine.
- `announcement` (public skill): Use when drafting or delivering human-facing repo change communication such as release-note style summaries or chat-ready updates. Draft value comes first; delivery, audience, and omission policy stay adapter-driven.
- `create-cli` (public skill): Use when creating or upgrading a repo-owned CLI, bootstrap script, or command runner. Define the command surface, install/update contract, structured output, dry-run and doctor behavior, distribution path, and quality gates before spreading ad hoc shell or Python entrypoints.
- `create-skill` (public skill): Use when creating a new charness skill or improving a migrated one. Defines the canonical portable authoring contract: classify public/support/profile/integration boundaries, simulate failure modes, keep host-specific behavior in adapters and presets, and express external tool dependencies through manifests instead of hidden assumptions.
- `critique` (public skill): Use when a non-trivial design decision, code change, release, rename, deletion, spec, or workflow change needs a before-the-fact critique, or when reported review findings need approval-oriented evidence disposition. Probe distinct failure angles, then run a counterweight pass that separates real blockers from over-worry before the change locks in.
- `debug` (public skill): Use when investigating a bug, error, reported review finding, or unexpected behavior that needs root cause, Five Whys, or recurrence analysis. Follow a disciplined root-cause workflow, adversarially verify the report, preserve a durable debug artifact so future sessions inherit what was learned, and do not jump to fixes before a falsifiable hypothesis exists.
- `gather` (public skill): Use when a public web page, GitHub content, a published or exported document, an arbitrary URL, a local file, or other public source should become a durable local knowledge asset instead of a transient answer. Gather is public-source only: credentialed organizational data (Slack, Notion, private Google Workspace) is out of scope and belongs to the consuming runtime's own capability/connector. Prefer primary sources, refresh existing assets in place when the source identity matches, and keep the result scoped to the user's actual request.
- `handoff` (public skill): Use when the user wants the next session prepared or asks to update a handoff artifact. Keep the handoff short, current, and operationally useful, and treat mention-only pickup as an instruction to continue the workflow named in the handoff trigger.
- `hitl` (public skill): Use when automated review is not enough and deliberate human judgment needs to be inserted into a bounded review loop. Keeps review state resumable, chunked, and adapter-driven without hardcoding one host runtime.
- `hotl` (public skill): Use when applied live behavior needs human-on-the-loop closure: inventory what needs proof, write a proof packet before execution, run or record roundtrip/readback evidence through repo-owned commands, and keep every loop entry verified or explicitly dispositioned so unproven behavior is never closed as working.
- `ideation` (public skill): Use when the user is still shaping a product, system, or workflow concept and needs discovery before `spec` or implementation. Build the concept through conversation because the user may not know the full shape yet: maintain a living world model, separate verified facts from assumptions, test demand/status quo/wedge/moat early, think about feedback and expansion from the start, and treat agents, APIs, CLI, and interface choices as first-class design constraints.
- `impl` (public skill): Use when work should move into code, config, tests, or operator-facing artifacts. Consume the current implementation contract when it exists, bootstrap a small honest contract inline when it does not, implement the smallest meaningful slice, then load `prove` to verify it and emit the slice closeout ledger before stopping.
- `issue` (public skill): Use when filing a GitHub issue from current context or resolving GitHub issues end-to-end through the adapter-resolved backend (`gh` by default, or a host-mediated capability such as `acme github`). Issue creation reports the observed problem before suggesting solutions; issue resolution treats GitHub as the source of truth, classifies the issue, runs a causal review for bug-class issues before designing the fix, and runs a resolution critique so the same class of issue does not recur.
- `narrative` (public skill): Use when a repo's source-of-truth docs and current product or project story need to be aligned together. Tighten the durable narrative first, then derive one audience-neutral brief skeleton when a compressed handoff artifact would help.
- `prove` (public skill): Use when a built implementation or contract slice needs its closeout proven before stopping: run the strongest honest verification, sync truth surfaces, bind the required fresh-eye critique, and emit the slice closeout ledger. `impl` loads this at its stop gate; contract-completing work consumes the same ledger.
- `quality` (public skill): Use when the goal is to understand and improve the repo's current quality bar. Detect existing gates, run the available ones, inspect concept integrity, test confidence, and security posture, then propose concrete quality moves instead of only complaining about what is missing.
- `release` (public skill): Use when a maintainer needs to cut, bump, or verify a repo release surface such as plugin versions, generated install manifests, and operator update instructions.
- `retro` (public skill): Use after a meaningful work unit or when the user asks for a retrospective. Reviews what happened, what created waste, which decisions mattered, which named expert lens or direct counterfactual would have changed the next move, and which workflow/capability/memory improvements should make the next session better. One retro shape; scale the depth to the work unit under review.
- `setup` (public skill): Use when a repo needs its initial operating surface created or normalized. Bootstrap the README, AGENTS.md, CLAUDE.md symlink policy, and documentation index from minimal ideation for greenfield repos, conditionally add roadmap or operator-acceptance docs when evidence warrants them, or realign those surfaces for partially-initialized repos without pretending quality review or deep product ideation already happened.
- `spec` (public skill): Use when a concept needs to become a living implementation contract. Refine ideation artifacts or existing design docs into the current build contract, decide what must be fixed now versus probed during implementation, define testable success criteria, and keep the contract synchronized as `impl` learns new facts.

## Support Skills
- `markdown-preview` (support skill): Internal support capability for rendering checked-in Markdown into durable preview artifacts so doc-facing workflows can review real terminal output instead of raw source alone.
- `web-fetch` (support skill): Internal support capability for routing public-web fetch requests through the strongest honest access path and classifying blocked or partial fetch responses without turning those tactics into a public workflow concept.

## Support Capabilities
- `markdown-preview` (support capability): charness-owned markdown preview support that renders checked-in Markdown into width-specific text artifacts for doc-facing workflows.
- `web-fetch` (support capability): charness-owned public-web fetch routing and response classification support used by gather when plain direct fetch is weak, blocked, or ambiguous.

## Integrations
- `agent-browser` (external integration): Browser automation CLI for JS-rendered pages, DOM inspection, interactive browser debugging, and browser-mediated `gather` fallback when private SaaS acquisition cannot stay on an official API/export path.
- `awiki` (external integration): Flat-file Markdown wiki graph linter. Use when `quality` needs to ask whether the docs form a CONNECTED graph — orphan pages, disconnected islands, largest-component ratio — a question `check_doc_links.py` does not ask, because it validates whether each link RESOLVES, not whether a page is reachable at all.
- `cautilus` (external integration): Standalone evaluation engine and bundled skill for bounded behavior review beyond repo-local deterministic gates.
- `defuddle` (external integration): Article and documentation page cleaner used by gather/web-fetch to turn cluttered public HTML into readable markdown before falling back to browser-mediated acquisition.
- `github-worker` (external integration): Authenticated GitHub CLI provider for repository, pull request, issue, and discussion gather flows.
- `gitleaks` (external integration): Fast Go-based secret scanner. Preferred over the secretlint fallback by `scripts/check-secrets.sh`; sub-second on the charness tree vs ~5s for the npm secretlint path.
- `glow` (external integration): Terminal markdown renderer used by doc-facing seams such as `narrative` and `quality` for width-specific rendered review artifacts.
- `lychee` (external integration): Fast Markdown link checker used by the canonical docs lint to validate internal and external links.
- `nose` (external integration): Required (>=0.17.0) clone scanner used by `quality`: advisory code clone families plus the Markdown near-duplicate engine that replaced the bespoke document near-copy gate. The code path runs `nose query` (`nose scan` was removed in 0.13.3). The committed dup-ratchet/clone baselines are seeded on 0.17.0 (schema v7) and keyed by gate-computed offset/path-independent content fingerprints (slice 4), not nose family ids; the family SET nose groups is still scanner-version-scoped.
- `ruff` (external integration): Fast Python linter used by `scripts/run-quality.sh` as the standing Python lint gate, including mccabe complexity checks.
- `specdown` (external integration): Executable specification runner that turns Markdown specs into runnable tests and reports.
- `tokei` (external integration): Fast multi-language source-lines-of-code counter. Use when `quality` needs an honest SLOC inventory that separates code, comments, and blanks instead of treating raw `splitlines()` totals as code size.
- `vulture` (external integration): Python dead-code and dead-file advisory scanner. Use after the Ruff baseline when whole-repo reachability or stale modules are the quality question.

## Trusted Skills
- none
