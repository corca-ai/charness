# Critique Round Findings

- Round: 1
- Recorded date: 2026-08-21
- Boundary window id: `r2-semantic-candidate-round-1`
- Boundary snapshot: `charness-artifacts/critique/2026-08-21-r2-semantic-boundary.json`
- Boundary snapshot SHA-256: `9caff0ad130a2cf817b900f23c73a36600fdd0902ade853b828e335784b24048`
- Findings SHA-256: `7dd89088c8225cf75d99eb9ef680f7119bbdb9f3b14e9b5235791e8dcb817053`

## Findings Returned

[
  {
    "kind": "charness.bounded_review.v1",
    "lens": "semantic contract and authorization/proof separation",
    "packet_sha256": "2800c9d0e33aa6303de5106234dc4547014dd8dc9b3098e2dccd85a45592f3dc",
    "reviewed_input_identity_sha256": "e94e1f7602d065b2a23ea56d94d48623850c7066e8be30aa3d00cef322aba9d4",
    "verdict": "block",
    "findings": [
      {
        "id": "SEM-DELIVERY-001",
        "severity": "blocker",
        "summary": "worker-delivered can pass artifact validation without proof of a matching findings ledger or worker report.",
        "evidence": [
          "scripts/validate_critique_artifacts.py:99-100 accepts worker-delivered as a fresh-eye value.",
          "scripts/critique_reviewer_evidence.py:83-85 only treats parent-delegated and nested-delegated as completed delegation claims; :176-195 does not enforce delivery proof for worker-delivered.",
          "scripts/critique_reviewer_evidence.py:224-250 validates only that a delivery-state value has an allowed prefix, including pending-parent-spawn and spawn-accepted-no-delivery.",
          "skills/public/critique/SKILL.md:167-171 requires worker-delivered to follow an approval-eligible worker report.",
          "The packet reviewed-input identity omits the validator and reviewer-evidence consumer, so it cannot support a whole-candidate approval claim."
        ],
        "action": "Make worker-delivered require an approval-eligible reviewer_worker_report plus findings-received delivery state and matching identities, or reject it as unproven. Add negative fixtures and include every final consumer in the packet identity."
      },
      {
        "id": "SEM-PROVENANCE-002",
        "severity": "major",
        "summary": "The final report does not mechanically bind the successful worker receipt to the current delivery attempt, packet, or scope, and ledger readback does not prove the recorded state came from a valid event history.",
        "evidence": [
          "skills/shared/scripts/reviewer_worker.py:289-312 writes receipts without packet identity, scope, delivery-attempt identity, or findings identity.",
          "skills/shared/scripts/reviewer_worker_report.py:57-76 validates output freshness and hashes but not receipt-to-attempt binding or exit_code == 0; :88-136 compares requested provenance only with ledger fields.",
          "skills/shared/scripts/reviewer_delivery_state.py:141-195 accepts serialized state without replaying history, requiring a start/findings event, or enforcing unique event IDs; :217-220 derives approval from state and findings_identity alone.",
          "tests/quality_gates/test_reviewer_worker_report.py:85-123 cover matching fields and failed receipts, but not foreign receipts, forged histories, or cross-run pairing."
        ],
        "action": "Bind receipt, attempt, packet, scope, and findings identities; validate the receipt's exit status; replay and validate the append-only ledger history; add foreign-receipt and forged-ledger tests."
      },
      {
        "id": "SEM-APPROVAL-003",
        "severity": "major",
        "summary": "The delivery CLI exposes approval_eligible=true from ledger state alone, creating an approval signal weaker than the worker report contract.",
        "evidence": [
          "skills/shared/scripts/reviewer_delivery.py:234-245 emits approval_eligible from record_findings without checking a worker receipt.",
          "skills/shared/scripts/reviewer_delivery.py:257-262 emits the same field from ledger state in show output.",
          "skills/shared/scripts/reviewer_worker_report.py:88-136 correctly requires both a valid receipt and matching findings-received ledger.",
          "skills/shared/references/fresh-eye-subagent-review.md:339-346 makes the combined worker report the authority."
        ],
        "action": "Remove or rename the delivery-only field to avoid approval semantics; reserve final approval_eligible for the combined report and test that delivery commands cannot claim approval without receipt evidence."
      },
      {
        "id": "SEM-MODE-004",
        "severity": "major",
        "summary": "Typed subagent mode is declared optional, but the critique workflow lacks an explicit mode-specific execution and authorization branch.",
        "evidence": [
          "scripts/critique_adapter_lib.py:23-33 and :187-214 accept both file-backed-worker and typed-subagent modes, with file-backed-worker as the default.",
          "skills/public/critique/SKILL.md:104-106 directs every lens to run in its own file-backed worker while only mentioning typed subagents as a tier-selection condition; :118-120 and :167-171 do not define the typed execution path.",
          "skills/shared/references/fresh-eye-subagent-review.md:92-171 separates authorization from skill configuration and requires the delegation ladder; :348-406 defines distinct typed delivery evidence.",
          "skills/public/critique/references/adapter-contract.md:62-73 describes worker receipt requirements without a clear typed-mode alternative."
        ],
        "action": "Specify an explicit file-backed versus typed-subagent branch. For typed mode, resolve authorization through the delegation ladder, require actual spawn and parent-context findings delivery, and forbid same-context fallback; retain file-backed-worker as the default."
      },
      {
        "id": "SEM-SAME-CONTEXT-005",
        "severity": "minor",
        "summary": "Standalone fresh-eye review is disallowed in the same context, but the short local-risk cadence can be misread as satisfying that review obligation.",
        "evidence": [
          "skills/public/critique/references/cadence.md:12-20 permits a same-agent scoped critique for small local-risk slices.",
          "skills/public/prove/SKILL.md:75-80 distinguishes short critique artifacts from fresh bounded worker or typed-subagent critique, but the distinction is easy to miss at the caller boundary.",
          "skills/shared/references/fresh-eye-subagent-review.md:496-502 forbids same-context substitution for a blocked fresh-eye review."
        ],
        "action": "Clarify that a same-agent short artifact is never fresh-eye evidence and cannot satisfy worker-delivered or other standalone review claims."
      },
      {
        "id": "SEM-PARITY-006",
        "severity": "observation",
        "summary": "No source/plugin mirror drift was found on the inspected critique, prove, shared-reference, adapter, worker, report, and delivery surfaces.",
        "evidence": [
          "The inspected source/plugin pairs have identical content hashes, including skills/shared/references/fresh-eye-subagent-review.md, skills/public/{critique,prove}/SKILL.md, and skills/shared/scripts/{reviewer_worker,reviewer_worker_report,reviewer_delivery,reviewer_delivery_state}.py."
        ],
        "action": "No action for this lens; parity does not establish runtime or installed-surface correctness."
      }
    ],
    "counterweight_triage": [
      {
        "concern": "worker-delivered is accepted without correlated final proof",
        "bin": "Act Before Ship",
        "disposition": "Blocking semantic gap on the artifact validation boundary."
      },
      {
        "concern": "receipt and ledger can be paired without same-run binding",
        "bin": "Act Before Ship",
        "disposition": "Repair provenance binding and negative tests before relying on approval."
      },
      {
        "concern": "delivery CLI emits approval_eligible independently",
        "bin": "Act Before Ship",
        "disposition": "Consolidate approval authority in the combined worker report."
      },
      {
        "concern": "typed-subagent mode lacks a clear execution/auth branch",
        "bin": "Act Before Ship",
        "disposition": "Clarify and enforce optional typed-host behavior while preserving the file-backed default."
      },
      {
        "concern": "same-agent short critique wording may be confused with fresh-eye review",
        "bin": "Valid but Defer",
        "disposition": "The small-local-risk policy appears intentional; clarify its non-substitutability if retained."
      },
      {
        "concern": "source/plugin parity drift",
        "bin": "Over-Worry",
        "disposition": "Not observed on inspected surfaces."
      }
    ],
    "next_move": "Repair the proof and mode-separation findings, expand the packet identity to cover every final consumer, add the listed negative tests, then run the required second bounded review of the repaired verdict surfaces.",
    "non_claims": [
      "The packet does not prove that a worker ran, that findings were delivered, that a typed subagent was spawned, or that the requested host tier was applied; its host application state is explicitly unverified-by-packet.",
      "This read-only review did not run the worker, spawn a host subagent, run the test suite, run Cautilus, or verify installed/runtime/hosted behavior.",
      "Source/plugin parity on inspected files does not prove parity of omitted consumers or installed surfaces.",
      "This verdict is limited to semantic contract and authorization/proof separation; it is not release, publication, issue-closure, or overall quality approval."
    ]
  },
  {
    "kind": "charness.bounded_review.v1",
    "lens": "delivery, portability, and boundary failure modes",
    "packet_sha256": "2800c9d0e33aa6303de5106234dc4547014dd8dc9b3098e2dccd85a45592f3dc",
    "reviewed_input_identity_sha256": "e94e1f7602d065b2a23ea56d94d48623850c7066e8be30aa3d00cef322aba9d4",
    "verdict": "block",
    "findings": [
      {
        "id": "DEL-001",
        "severity": "blocker",
        "summary": "The changed-line receipt is stale relative to the reviewed candidate.",
        "evidence": [
          "The packet binds the reviewed target to 1ce3de74e08e65dd20c2d6d261b6e58867facecf at charness-artifacts/critique/2026-08-21-r2-semantic-candidate-v2-packet.json:57-67.",
          "The receipt records Resolved HEAD SHA c0738b0f33bb6e69d22abeb2672bc8eaa96e67d at charness-artifacts/quality/2026-08-21-r2-changed-line-proof.md:7-15.",
          "Therefore its clean result does not prove the packet's 825b2a4198..1ce3de74 candidate."
        ],
        "action": "Rerun the exact changed-line producer after the candidate is locked and require the receipt target SHA and packet identity to match before approval."
      },
      {
        "id": "DEL-002",
        "severity": "major",
        "summary": "The approval report does not bind the worker receipt or findings content to the delivery attempt.",
        "evidence": [
          "reviewer_worker_report.py:57-76 checks status, terminal, freshness, output hash, and size, but does not check exit_code, run_id, attempt identity, packet identity, or scope.",
          "reviewer_worker_report.py:96-112 compares only caller-supplied provenance strings with the ledger attempt; no receipt-to-attempt join exists.",
          "reviewer_delivery_state.py:252-297 accepts any non-empty findings_identity, and reviewer_delivery.py:188-194,234-245 supplies that label without reading or hashing findings content.",
          "The worker/report tests construct result, receipt, and findings labels independently in tests/quality_gates/test_reviewer_worker_report.py:19-57."
        ],
        "action": "Add an explicit receipt/result/attempt join and validate receipt invariants and findings content identity; add negative tests for foreign receipts, nonzero exit codes, stale results, and silent channels."
      },
      {
        "id": "DEL-003",
        "severity": "major",
        "summary": "Process cleanup only covers timeout on POSIX and is not safe for interruption or non-POSIX hosts.",
        "evidence": [
          "reviewer_worker.py:252-270 calls terminate_process_group only from the TimeoutExpired branch.",
          "reviewer_process.py:12-21 uses killpg on POSIX but only process.kill() elsewhere, with no descendant-tree mechanism.",
          "reviewer_worker.py:352-368 catches Exception rather than signal/KeyboardInterrupt paths, so an interrupted worker can leave the backend running and emit no durable receipt.",
          "The only cleanup test is POSIX-specific in tests/quality_gates/test_reviewer_worker.py:173-197."
        ],
        "action": "Install cleanup for every worker exit, emit a typed interrupted receipt, and use a Windows job/process-tree mechanism or explicitly declare the unsupported platform boundary."
      },
      {
        "id": "DEL-004",
        "severity": "major",
        "summary": "The declared file-backed default is not wired to a canonical repo-owned invocation or result schema.",
        "evidence": [
          ".agents/critique-adapter.yaml:23-29 declares the file-backed worker, backend, and timeout.",
          "skills/public/critique/SKILL.md:103-120 and skills/shared/references/fresh-eye-subagent-review.md:430-454 describe ledger/report consumption but omit the worker invocation and schema provisioning.",
          "reviewer_worker.py:315-326 requires prompt-file, schema-file, output-file, and receipt-file, yet no checked-in reviewer result schema or non-test caller was found in the bounded scripts/skills/tests search.",
          "Artifact validation only checks typed presence values in scripts/critique_reviewer_evidence.py:18-21 and scripts/validate_critique_artifacts.py:93-100; it does not bind worker-delivered to a report artifact."
        ],
        "action": "Add a repo-owned runner/adapter resolver, canonical schema/evidence carrier, and end-to-end source/export fixture, or explicitly document this as a manual primitive rather than a wired default."
      },
      {
        "id": "DEL-005",
        "severity": "major",
        "summary": "Artifact-path aliasing can produce a successful run with no typed receipt.",
        "evidence": [
          "reviewer_worker.py:141-159 checks whether output, receipt, stdout, and stderr already exist but never requires those resolved paths to be distinct.",
          "If output_file and receipt_file are the same initially absent path, reviewer_worker.py:274-276 creates the result there, then main skips receipt creation at :365-368 because receipt_path now exists, while returning success.",
          "The shared contract requires unique run artifacts at skills/shared/references/fresh-eye-subagent-review.md:450-454, but the CLI does not enforce that precondition."
        ],
        "action": "Reject colliding resolved artifact paths before launch and add collision, alias, and concurrent-run tests."
      },
      {
        "id": "DEL-006",
        "severity": "observation",
        "summary": "Ledger writes are atomic but not serialized, so concurrent updates can lose delivery attempts or events.",
        "evidence": [
          "reviewer_delivery.py:133-158 performs an unlocked read-modify-replace.",
          "Each CLI operation reads the full ledger and writes it back at reviewer_delivery.py:215-245.",
          "The workflow requires multiple independent worker runs at skills/public/critique/SKILL.md:95-105; the current goal's parent-serializes-ledger policy is the only mitigation."
        ],
        "action": "Keep parent serialization as an executable precondition, or add locking/CAS or an append-only event log before sharing one ledger across concurrent workers."
      }
    ],
    "counterweight_triage": [
      {
        "concern": "Changed-line proof target differs from the packet target.",
        "bin": "Act Before Ship",
        "disposition": "The receipt cannot be used for candidate approval until rerun and rebound to 1ce3de74e08e65dd20c2d6d261b6e58867facecf."
      },
      {
        "concern": "Receipt and findings provenance can be cross-run or caller-attested without a content join.",
        "bin": "Act Before Ship",
        "disposition": "This directly defeats the requested distinction between delivered findings and media/process success."
      },
      {
        "concern": "Interruption and non-POSIX process cleanup are incomplete.",
        "bin": "Act Before Ship",
        "disposition": "The failure can orphan a backend and remove the typed terminal receipt."
      },
      {
        "concern": "No canonical worker invocation/schema is wired into the default skill path.",
        "bin": "Act Before Ship",
        "disposition": "Either make the path executable and evidence-bound or narrow the advertised contract."
      },
      {
        "concern": "Artifact-path collision handling.",
        "bin": "Bundle Anyway",
        "disposition": "A small preflight guard and negative test should ship with the worker repair."
      },
      {
        "concern": "Concurrent ledger update loss.",
        "bin": "Valid but Defer",
        "disposition": "The active parent-serialization rule can contain this for now; preserve it explicitly until concurrent ledger writers are supported."
      },
      {
        "concern": "Checked-in source/plugin parity drift.",
        "bin": "Over-Worry",
        "disposition": "The inspected mapped source/plugin pairs are byte-identical locally; no parity defect was found in this review."
      }
    ],
    "next_move": "Block approval. Rebind and rerun changed-line proof on the exact candidate, then repair the receipt/findings join, interruption cleanup, runner/schema wiring, and artifact collision boundary before another fresh-eye round.",
    "non_claims": [
      "This local review does not prove Codex or Claude host-channel routing, live interruption delivery, Windows process-tree behavior, or hosted behavior.",
      "It does not prove installed or machine-local plugin execution, CI/publication, release publication, or issue closure.",
      "Checked-in source/plugin parity was verified locally only; it does not prove generated install/cache parity.",
      "No runtime worker or host roundtrip was executed in this read-only review."
    ]
  },
  {
    "kind": "charness.bounded_review.v1",
    "lens": "skeptical counterweight over the semantic candidate",
    "packet_sha256": "2800c9d0e33aa6303de5106234dc4547014dd8dc9b3098e2dccd85a45592f3dc",
    "reviewed_input_identity_sha256": "e94e1f7602d065b2a23ea56d94d48623850c7066e8be30aa3d00cef322aba9d4",
    "verdict": "block",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "summary": "The packet identity is not closed over the approval-decision surface or its plugin mirrors.",
        "evidence": [
          "The packet's owning-surface inventory includes skills/shared/scripts/reviewer_delivery_state.py and derived plugin reviewer scripts, but reviewed_input_identity.reviewed_paths contains neither source nor plugin reviewer_delivery_state.py and omits the plugin worker/report mirrors.",
          "reviewer_delivery.py imports the omitted state module, while reviewer_worker_report.py uses its approval_eligible predicate; the omitted module owns the findings-received transition and approval decision.",
          "The supplied packet and all 14 named content hashes are internally consistent at target 1ce3de74, and the checked source/plugin bytes currently match. That mirror observation is outside the packet's identity binding."
        ],
        "action": "Regenerate the packet with the full verdict-owning source/derived set, at minimum the delivery-state module and both source/plugin worker, report, output, and process mirrors; then review the re-bound identity."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "summary": "The changed-line receipt is stale and narrower than the semantic candidate.",
        "evidence": [
          "The packet binds the semantic target to 1ce3de74, while charness-artifacts/quality/2026-08-21-r2-changed-line-proof.md records Resolved HEAD SHA c0738b0f.",
          "That receipt analyzes only six eligible mutation-pool files and none of skills/shared/scripts/reviewer_worker.py, reviewer_delivery.py, reviewer_delivery_state.py, reviewer_worker_report.py, reviewer_output.py, or reviewer_process.py, which are the core new worker/approval surfaces.",
          "The goal itself says the receipt does not bind the semantic candidate; its focused-test counts are prose claims without an exact target-bound command receipt."
        ],
        "action": "Rerun the repository's changed-line producer and focused worker, delivery-state, and report suites at the exact semantic target, and record the target identity. Either measure the shared worker surface separately or explicitly leave it unproven; do not use the six-file clean result as candidate-wide proof."
      },
      {
        "id": "F3",
        "severity": "major",
        "summary": "Packet identity is caller-supplied and is not bound end-to-end to the worker prompt or receipt.",
        "evidence": [
          "reviewer_worker.py accepts no packet or reviewed-input identity and its receipt records prompt/schema paths but no prompt hash, packet identity, or reviewed-input identity.",
          "reviewer_worker_report.py compares --packet-identity only with the same caller-supplied ledger value; it does not compare that value with the worker receipt or prompt contents.",
          "A stale prompt can therefore be paired with the current packet hash and a successful receipt, producing the same approval-eligible report."
        ],
        "action": "Carry packet identity, reviewed-input identity, and prompt/schema hashes through the worker receipt, then require the report to compare them with the delivery ledger; add a stale-prompt counterexample."
      },
      {
        "id": "F4",
        "severity": "observation",
        "summary": "findings-received is parent-attested delivery eligibility, not executable proof that findings were read or correspond to the result.",
        "evidence": [
          "DeliveryAttempt.record_findings checks scope, packet identity, parent receipt identity, and a non-empty findings_identity, but does not bind findings_identity to the worker output hash or contents.",
          "reviewer_worker_report.py validates receipt output hash/size and ledger state but never reads or revalidates the result while establishing findings delivery.",
          "The contract's parent-context observation is inherently judgment-bound, so approval_eligible should not be read as semantic approval or correctness proof."
        ],
        "action": "Qualify approval_eligible as parent-attested delivery eligibility and keep that limitation explicit; bind findings_identity to a canonical result hash in a later bounded hardening slice if stronger evidence is required."
      },
      {
        "id": "F5",
        "severity": "major",
        "summary": "The adapter's default-versus-typed runner boundary is declarative but not bound to the consumed report.",
        "evidence": [
          "critique_adapter_lib.py validates reviewer_runner and critique_packet_lib.py renders it, but repository search finds no dispatcher that selects reviewer_worker.py from that field.",
          "reviewer_worker_report.py unconditionally emits execution_mode=file-backed-worker and accepts no expected adapter mode or backend.",
          "A typed-subagent adapter can therefore be configured while a file-backed report is consumed, or a worker can be run without proving it was the configured execution path."
        ],
        "action": "Add a small mode/backend readback check tying the adapter-selected runner to the receipt/report, or narrow the contract to an operator protocol and require the actual selected mode in closeout evidence."
      }
    ],
    "counterweight_triage": [
      {
        "concern": "The omitted delivery-state and mirror paths make the packet identity incomplete.",
        "bin": "Act Before Ship",
        "disposition": "This is a real identity-closure gap on the surface that decides approval; current byte equality does not repair the missing binding."
      },
      {
        "concern": "The c073 six-file changed-line receipt can serve as proof for the 1ce semantic candidate.",
        "bin": "Act Before Ship",
        "disposition": "It cannot; the receipt is explicitly scoped to c073 and excludes the shared worker surface."
      },
      {
        "concern": "A stale worker prompt can pass under a current packet identity.",
        "bin": "Act Before Ship",
        "disposition": "This is a concrete semantic counterexample to the proposed provenance boundary."
      },
      {
        "concern": "Parent-attested findings delivery must be cryptographically proven in this slice.",
        "bin": "Valid but Defer",
        "disposition": "The parent-context observation cannot be mechanically established without inventing a stronger protocol; qualify the claim now and defer hash binding."
      },
      {
        "concern": "The adapter must grow a full central dispatcher before this candidate can ship.",
        "bin": "Act Before Ship",
        "disposition": "The smaller required repair is mode/backend readback or an explicit downgrade of the adapter field from enforcement to operator protocol; a general orchestration engine is out of scope."
      },
      {
        "concern": "The current packet itself has already drifted because HEAD is newer than its resolved target.",
        "bin": "Over-Worry",
        "disposition": "The packet hash and supplied identity match, the named content hashes match target 1ce3de74, and the post-target HEAD commit only adds the packet artifacts."
      },
      {
        "concern": "The JSON-to-YAML stdout repair merely moved the output-channel failure, or the source/plugin mirrors already differ.",
        "bin": "Bundle Anyway",
        "disposition": "The worker/report tests consume YAML stdout and JSON durable files, and the checked source/plugin copies are byte-equal; retain one end-to-end channel assertion in the next proof."
      },
      {
        "concern": "The clean focused result proves host tier application, installed behavior, release publication, or hosted readback.",
        "bin": "Over-Worry",
        "disposition": "The packet and goal explicitly disclaim those claims; no such proof should be inferred."
      }
    ],
    "next_move": "Rebind the packet over the complete verdict-owning surface, repair end-to-end packet and runner-mode provenance, then rerun exact-target focused and changed-line evidence before accepting any fresh-eye approval.",
    "non_claims": [
      "No claim is made that the source/plugin mirrors currently differ; the checked target-tree copies matched.",
      "No claim is made that the supplied packet SHA-256 or reviewed-input identity SHA-256 is mismatched.",
      "This review does not establish host-confirmed tier/model application, installed or managed-update behavior, hosted/public readback, release publication, issue closure, Cautilus evaluation, or fresh-eye code approval.",
      "The bounded review does not establish the semantic correctness of any worker-produced finding."
    ]
  }
]
