# Spec Loop

`impl` is allowed to teach `spec`, but it must do so explicitly.

`impl` does not require that `spec` have happened as a separate step. When no
formal spec artifact exists, `impl` may bootstrap the current slice inline and
then maintain that contract honestly.

## Update The Contract When

Update the canonical artifact when implementation reveals:

- a probe is resolved
- a success criterion needs sharper wording
- an acceptance check changes
- a fixed decision turns out false
- a fixed decision is not actually delivered and must be deferred or
  reclassified durably

If there was no prior canonical artifact, record the contract source clearly in
the implementation closeout.

## Escalate Back Upstream When

Route back to `spec` or `ideation` when implementation reveals:

- the real user or operator is different
- the wedge or system shape changed materially
- the current slice no longer matches the claimed problem

That is not normal implementation learning. It is concept or contract drift.

## Closeout Re-read

Before stopping a contract-backed slice:

- re-read `Fixed Decisions` and named acceptance checks
- confirm each item is reflected in the delivered slice or durably reclassified
  in the contract
- do not leave a silently dropped bullet as chat-only residue
