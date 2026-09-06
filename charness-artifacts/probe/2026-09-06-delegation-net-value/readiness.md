# Comparison protocol local readiness

Date: 2026-09-06

The protocol is locally ready to supply #808's implementation scenarios. No
actual comparison cell has run. Candidate export/revision freeze and discovery
preflight remain required before a candidate cell; #809 is not provider-closed.

The initial fairness and observer reviews blocked; their exact findings and
parent dispositions are retained under `reviews/`. The single bounded repair
review passed with no findings. Typed report:
`charness-artifacts/critique/workers/goal805-protocol-repair/worker-report.yaml`.
Packet `e844f56aef584fcabbbc3e246689acdd29ae1df88a1873c1acec482ae48c9ea6`;
reviewed input `9060153dc7a4fcbcf29782a23ba0ce7974472adf29116eb74b89f8cdbc63ae35`.
The parent consumed the delivered result, receipt and ledger and verified the
review binding before freezing inputs. This is protocol approval only.

Retained `control-observations.json` accepts two correct implementations and
rejects eight faulty variants; `launcher-control-observations.json` covers seven
launch/continuation controls. `preflight/high-transport.jsonl` and
`preflight/low-transport.jsonl` retain actual fresh model shell/read/write
preflights. These are infrastructure checks, not task outcomes or backend model
attestation. The 17 entries in `frozen-inputs.json` were independently rehashed
with no mismatch on 2026-09-06. Frozen comparison inputs remain unchanged.

The added protocol/observer/launch and review overhead is visible in this probe.
No product improvement, general crash recovery, significance, or no-plugin
superiority claim is established. Next: implement the candidate without viewing
pilot outputs, export and freeze it, verify candidate visibility, then run the
precommitted four cells and retain both phases and failures.
