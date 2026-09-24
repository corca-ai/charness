# Goal 844 integration observations (WI-12)

- WI-11 attempt 4 went quiet for ~30 min in exec (xhigh reasoning, live API
  wait confirmed via established sockets); a steer sequencing nudge was
  delivered and the lane completed validated-partial. Lesson: quiet exec
  with live sockets is thinking, not stuck; steer nudges land at turn
  boundaries.
- Changed-line proof is brittle to unrelated failures: one pre-existing (at
  WI-11 time) offender elsewhere in the focused set yields no-verdict for
  the slice. Parent coverage (topical + siblings, 100% on the new module)
  substituted with the gap recorded.
- The WI-8b lane created `task_run_dag.py` with a JSON-stdout print against
  the older YAML contract; slice verification did not run the contract
  suite. Follow-up: run the contract suite in every lane receipt that adds
  a command-shaped module, or exempt/migrate dag output explicitly.
- The read-only verification lane caught exactly this class of issue (one
  FAIL with a file pointer). Keep it: cheap (60s) and it reads the
  integrated tree, not lane claims.
- Closeout ledger floors are exact: `Behavior #N:`, `AI provenance:`,
  JTBD/boundary/resolution/implementation/prevention, close keyword, and
  the carrier body (commit message for direct-commit, file for pr-body)
  must all agree. Draft the ledger before closing, not after.
