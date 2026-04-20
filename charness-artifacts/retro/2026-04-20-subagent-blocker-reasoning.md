# Session Retro

Mode: session

Context: Quality review on 2026-04-20 misreported the reason a canonical fresh-eye subagent premortem path was not used.

Evidence Summary: user correction in-thread, `skills/public/quality/references/fresh-eye-premortem.md`, `skills/public/premortem/references/subagent-capability-check.md`, current `docs/handoff.md`, current `charness-artifacts/quality/latest.md`, bounded subagent probe in this turn.

Waste:
- I let a host-side spawning rule collapse into a repo-contract explanation and reported "not explicitly allowed" instead of separating `probe required`, `blocked`, and `degraded fallback`.
- Current-pointer artifacts allowed that wording to persist because validators only checked structure, not this specific misleading blocker explanation.

Critical Decisions:
- Fix the public-health link gate structurally by excluding reserved/private placeholder hosts from external URL checks instead of treating the failing example as ambient noise.
- Add narrow validators that reject `explicit subagent allowance` wording in quality and handoff current-pointer artifacts.
- Refresh `docs/handoff.md` and `charness-artifacts/quality/latest.md` to current numbers and clearer blocker wording in the same slice.

Expert Counterfactuals:
- Gary Klein: run the capability probe before naming the blocker; uncertainty about host permission is not evidence.
- John Ousterhout: keep the repo contract and host runtime policy in separate seams so a temporary operator rule does not become durable product truth.

Next Improvements:
- workflow: whenever a skill requires a canonical subagent path, either perform one bounded probe or state the exact host/tool error that prevented it.
- capability: keep validators for misleading blocker wording narrow and explicit instead of trying to infer all good premortem prose.
- memory: keep `docs/handoff.md` pointer-heavy and avoid stale quantitative/status restatements when a rolling artifact or tool proof already owns them.

Persisted: yes `charness-artifacts/retro/2026-04-20-subagent-blocker-reasoning.md`
