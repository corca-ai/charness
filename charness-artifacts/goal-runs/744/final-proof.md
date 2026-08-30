# Goal Run #744 Final Proof

Date: 2026-08-30
Provider: `corca-ai/charness`
Frozen draft SHA-256: `eec33587771e5f6abf0e06eb32b1291f475b5b549860c96f73f89218fda44e20`
Binding SHA-256: `2b5ac12a3722897bc5a11e88a881b45784adcbaab5e84840629ccd1d57421eb8`

## Outcome and boundary

The activation snapshot contained fourteen open issues: parent #744 and thirteen
direct Work Items. The Goal Run preserved four already-closed historical
children and established an exact seventeen-child graph. All seventeen children
now have issue-owned closeout evidence and provider `CLOSED` readback.

The original “move repository analysis to one typed Rust core” direction was
narrowed to the generic native capability slice that has independent evidence.
Charness provides composable capabilities and typed observations/refusals.
Consumer-repository agents own Git, submodule, worktree, and topology
composition. No release, exhaustive native migration, consumer export, or
consumer-topology correctness claim is made.

## Exact provider and CI observations

- Final material implementation SHA:
  `2ef6b357aeb7a2d32a4d710a33ba9e3df966d100`; Quality Core run
  `33301584557` succeeded for that exact SHA.
- Published final-evidence SHA:
  `40b084051729b9b32516cdc055290388b9f7e516`; Quality Core run
  `33302199291` succeeded for that exact SHA before parent close.
- Hosted Mutation Tests are not claimed. The operator-approved amendment
  `amendments/2026-08-30-ignore-mutation-test-proof.md` removed that proof
  obligation after runs `33296181601` and `33297693085` failed before
  mutation began.
- Final exact-graph observation
  `observations/goal-744-final-list-exact-graph-1.terminal.json` reports
  17 children, 17 completed, 0 open, no missing children, and no unexpected
  children against expected-child SHA-256
  `8c7d8a81f9fcb8d66977cca5ee569a8d8bbdd4632508f06fe980dd92a8f312b8`.
- The final uncapped open query before parent close returned only #744. No
  later-opened issue was observed.

## Activation-open issue outcomes

| Issue | Carrier / disposition | Behavior or decision evidence | CI classification | Provider state |
| ---: | --- | --- | --- | --- |
| #709 | [closeout](https://github.com/corca-ai/charness/issues/709#issuecomment-5467504330) | non-zero and zero summary projection fixtures | focused local behavior; final-main Quality Core | CLOSED |
| #731 | [closeout](https://github.com/corca-ai/charness/issues/731#issuecomment-5467577449) | 93 lifecycle/partial-output tests plus Luna review | focused local behavior; final-main Quality Core | CLOSED |
| #744 | guarded Goal Run close | this proof, exact graph, final-main CI, and final Luna review | final-main Quality Core | OPEN pending guarded close |
| #748 | [closeout](https://github.com/corca-ai/charness/issues/748#issuecomment-5467641984) | exact native inventory plus published parity/owner-removal evidence | provider-source behavior; final-main Quality Core | CLOSED |
| #749 | [not planned](https://github.com/corca-ai/charness/issues/749#issuecomment-5467646941) | no measured consumer JTBD or approved retained-Python delta | decision-only; no implementation claim | CLOSED |
| #751 | [closeout](https://github.com/corca-ai/charness/issues/751#issuecomment-5467497100) | 99 focused tests plus final Luna discriminator slice | focused local behavior; exact-main Quality Core | CLOSED |
| #752 | [closeout](https://github.com/corca-ai/charness/issues/752#issuecomment-5467501988) | false-ready, proved-ready, and force fixtures | focused current-main behavior | CLOSED |
| #753 | [not planned](https://github.com/corca-ai/charness/issues/753#issuecomment-5467644407) | JTBD audit and official tokei readback; no mutation non-regression claim | decision-only; no pruning claim | CLOSED |
| #756 | [closeout](https://github.com/corca-ai/charness/issues/756#issuecomment-5467529725) | backend-owner tests plus Luna discriminators | focused local behavior; exact-main Quality Core | CLOSED |
| #758 | [not planned](https://github.com/corca-ai/charness/issues/758#issuecomment-5467370038) | operator amendment and failed-before-mutation diagnosis | decision-only; Mutation Tests explicitly not green | CLOSED |
| #759 | [closeout](https://github.com/corca-ai/charness/issues/759#issuecomment-5467382508) | published-main deletion/pre-image and refusal controls | focused published-main behavior | CLOSED |
| #760 | [closeout](https://github.com/corca-ai/charness/issues/760#issuecomment-5467603610) | 75 agreement/identity tests plus Luna review | focused local behavior; exact-main Quality Core | CLOSED |
| #761 | [not planned](https://github.com/corca-ai/charness/issues/761#issuecomment-5467386536) | explicit product-ownership disposition | decision-only; no consumer topology claim | CLOSED |
| #762 | [closeout](https://github.com/corca-ai/charness/issues/762#issuecomment-5467637862) | 107 focused tests plus Luna committed-packet review | focused local behavior; final-main Quality Core | CLOSED |

The four historical children also remain closed with issue-owned evidence:
#743, #745, #746, and #747.

## Residuals and non-claims

- Parent body updates preserve every human-readable byte and may change only
  the hidden Goal Run metadata block. The approved Mutation Tests amendment
  therefore lives in an issue comment and durable artifact rather than in the
  human-readable parent contract. This carrier mismatch is a known residual;
  it is not represented as fixed.
- The failed first revision-11 cursor attempt changed no provider state. It
  was refused because an extra trailing newline altered a human-body byte; the
  corrected second attempt was verified by byte-identical readback.
- `CLOSED` and Quality Core are provider and gate observations, not substitutes
  for the per-issue behavior verdicts or typed dispositions linked above.
- No Mutation Tests success, release, installed-consumer result, consumer Git
  topology, or complete Rust migration is claimed.

## Final distinct observer

One bounded Luna fresh-eye returned `SHIP`. It independently matched the
draft, binding, membership, live 17/17 child graph, issue-owned evidence
identities, exact-SHA Quality Core, proof-policy amendment, consumer-topology
boundary, and parent revision-14 metadata. Its durable verdict is
`reviews/goal-744-final-fresh-eye.md`.
