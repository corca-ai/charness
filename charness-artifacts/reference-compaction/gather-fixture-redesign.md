# gather fixture redesign — per-condition, designed from docs+routing (2026-07-01)

Corrects the coarse Slice-7/#411 conclusion ("gather → substance judge"). Method
(operator-corrected): read the full doc set + the routing that decides *when* each
ref is consulted (`gather_plan.py`, `advise_slack_path.py`,
`advise_google_workspace_path.py`), map each ref to its trigger condition, and design
a scenario **per condition** so every genuinely load-bearing doc is forced under its
trigger. No capture is needed to design this — the conditional structure is readable
in the code. Capture only VERIFIES a designed scenario triggers its read.

## Reference → trigger → floor role (traced, not assumed)

| ref | census | trigger condition | genuine run-time DEPTH? | floor role |
|---|---|---|---|---|
| source-priority.md | INLINE | before widening from a named source | NO — the primary-source ordering is inlined in SKILL.md Workflow step 1 + `## Source Integrity` | retire (not a floor) |
| capability-contract.md | INLINE | interpreting provider access / degradation | NO — its only stranded token is the Access-Modes enum (`grant>binary>env>public>human-only>degraded`); inline it into SKILL.md `Access Mode` Output-Shape, then retire | retire after enum inline |
| asset-refresh.md | INLINE | refresh-in-place | NO — inlined in SKILL.md step 4 (`Refresh in place when the source identity matches` + `write_record.py` atomic rule) | not a floor |
| adapter-contract.md | INLINE | adapter location override | NO — script-resolved by `resolve_adapter.py` | engage-always, not RCF |
| **gather-provider.md** | DEPTH | **CONFIGURING** `.agents/gather-adapter.yaml` provider-mode grammar | NO for an ACQUIRE run — the advisers resolve the mode VALUE (`provider_mode`); the field GRAMMAR is config-time authoring, not acquisition | config-ref / script-resolved, not an acquire-run floor |
| **google-workspace-access.md** | DEPTH | a Google Workspace gather | NO — **absorbed by `advise_google_workspace_path.py`**, which emits the exact load-bearing content ("no repo-owned direct GWorkspace CLI" + host-mediated→export→browser ladder); a run runs the adviser and consumes its output | script-resolved, not RCF |
| document-seams.md | DEPTH | repo has an existing knowledge surface to follow | thin — the default path + adapter-override is inlined in SKILL.md Bootstrap; only "follow the existing surface" nuance remains | on-demand, not a floor |
| **browser-mediated-private-sources.md** | DEPTH | **private SaaS URL / authenticated UI, no official export** | **YES** — the auth/bootstrap-mode vocab (imported auth state, persistent profile, session-name persistence, auth vault, origin-scoped headers, human-only bootstrap) + the decision ladder + remote/headless rule are NOT in SKILL.md and NOT emitted by any script | **RCF floor of a NEW private-SaaS scenario** |

## Key correction

The census called 4 gather refs DEPTH, but tracing the routing shows only ONE
(`browser-mediated-private-sources.md`) is a genuine **run-time** doc-floor. Two
(`gather-provider.md`, `google-workspace-access.md`) are **script-resolved** — the
advisers consume/emit their content, so a run reads the script output, not the doc
(the same lens-3 pattern as `adapter-contract.md`). The census flattened
"DEPTH content" into "DEPTH floor"; a floor must be a doc a *run* must OPEN.

## Corrected scenario set (fan-out)

1. **public-URL** (existing `spec.json`): no skill-local doc a run must open (web-fetch
   tactics live in a support ref). Retire the INLINE RCF `[source-priority,
   capability-contract]`. This scenario's honest floor is the **produced durable
   artifact** (output) — the one place a substance/output instrument legitimately
   fits, and only here. (This is the correct, narrowed reading of #411.)
2. **private-SaaS** (NEW scenario): "gather from a private authenticated SaaS URL with
   no official export/API." Floor = **browser-mediated-private-sources.md** (genuine
   DEPTH). This is the scenario the current single-fixture set was MISSING — the real
   fix, not a substance judge.

## Execution

- Inline the Access-Modes enum into gather SKILL.md `Access Mode` Output-Shape (plain
  edit; then capability-contract retires cleanly).
- spec.json (public-URL): retire RCF → floor on the produced artifact (output_glob
  `charness-artifacts/gather/**/*.md` via outcome-assertions, OR accept coverage-advisory
  + the artifact check). Reclassify source-priority/capability-contract INLINE,
  gather-provider/google-workspace-access script-resolved (engage-always, not RCF),
  browser-mediated/document-seams on-demand.
- Add `private-saas.spec.json`: RCF `[browser-mediated-private-sources.md]`, a
  private-SaaS prompt, register in the claim-fidelity registry (fan_out_fit yes).
- VERIFY each scenario with a fresh capture: the private-SaaS run must OPEN
  browser-mediated-private-sources.md; the public run must produce the artifact.
