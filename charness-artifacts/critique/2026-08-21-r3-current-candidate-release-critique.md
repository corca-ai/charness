# R3 Current Semantic Candidate Release Critique

Date: 2026-08-21

Fresh-eye satisfaction: accepted-unreviewed-under-round-cap (cap-signal: the bounded R3 review cap was consumed by round 2; no third review or same-agent substitute is claimed)

## Decision Under Review

Whether semantic candidate `502c8a8adbbe77781f1714cb6c4383a85d6e3683` may enter
version mutation. This record is a pre-version boundary critique, not release
approval. It does not select a version, tag, publication channel, issue close,
or host-runtime claim.

## Current Evidence Join

- Exact candidate range: `d9995e0079326ae9ad0a35f9ade64a9f951c4fbf..502c8a8adbbe77781f1714cb6c4383a85d6e3683`.
- Planner-selected target: `6.2.1` (`v6.2.1`); this is planning evidence only,
  and no version surface has been mutated.
- Exact prepare packet: `charness-artifacts/critique/2026-08-21-r3-delivery-provenance-repair-current-exact-packet.json`.
- Packet SHA256: `5a936834bce7fe68db1f894e5e6764de336d9b8dbd4e69fd26f472ab07632ef7`.
- Reviewed-input identity: `26f29ca25c71bf4d704854285c787734f9a1e99bc7d770a9df8674ee3778dfc2`.
- Changed-line proof: `status: clean`; 2 mapped changed-pool files; every changed line covered; `blocking_targets: {}`; standing pytest passed.
- Fresh-checkout probes: 5/5 passed on the current checkout.

## Findings And Disposition

1. The repaired source boundary now fails closed when Codex delivery is
   missing, malformed, stale, or mismatched after refresh. Same-version claims
   require content readback, and update-all aggregates blocking support/doctor
   phases. Disposition: repaired locally; keep installed and host proof open.
2. The current candidate is not yet a versioned release candidate. Version
   surfaces, release record, target-bound post-bump proof, and publication
   readback remain outstanding. Disposition: act before ship.
3. Real-host proof is required for this release delta. The target-bound
   checklist still owes managed `charness update`/`charness doctor` readback and
   the declared `nose` doctor/install/sync-support checks. Disposition: act
   before ship; no local fixture result substitutes for it.
4. Issues #681–#687 remain separately classified in the current requalification
   packet. Source repair is not tracker closure, and host-side #687 behavior is
   explicitly unclaimed. Disposition: retain per-issue closeout evidence until
   after publication/readback.

## Non-Claims

- No fresh-eye PASS or release approval is claimed; the round-cap state is
  explicitly accepted-unreviewed.
- No version mutation, release-candidate commit, tag, push, publication,
  managed install/update readback, hosted readback, or issue closure is claimed.
- The exact packet is deterministic prepare evidence; its shape and hash do not
  constitute semantic reviewer approval.

## Boundary Ownership

- Producer: source, export, release planner, and typed proof carriers.
- Consumer: maintainer deciding whether the exact candidate can cross version,
  install, publication, and tracker boundaries.
- Verdict: owned-correctly — local source proof and external release proof stay
  distinct and must be joined by current-candidate evidence.
