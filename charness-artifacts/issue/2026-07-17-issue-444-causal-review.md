# Causal Review — corca-ai/charness#444 (2026-07-17)

Bounded fresh-eye causal reviewer (parent-delegated, high-leverage tier), run
before fix design per the issue skill bug-class contract. Reviewer spawned as
the typed read-only `bounded-reviewer`; the repo's standing `gpt-5.6-terra` +
`medium` request is not exposed by this host's Agent tool (host-defaulted).
Rail-1 boundary fingerprint verified clean after return (`drift: []`).

- JTBD: As the resolving agent, durably commit a pausing resolution brief
  without fabricating a closeout ledger, and have the hook read the brief's
  classification as the owning template renders it.

- Classification confirmation: bug — confirmed. Two owning contracts diverge
  in real use; the hook refused legitimate commits (two workarounds in
  history).

- Root cause: confirmed at two loci.
  1. No pause/brief carve-out: `_issue_closeout_artifacts`
     (`scripts/check_issue_closeout_commit_msg.py:84-100`) promotes any staged
     `charness-artifacts/issue/*.md` carrying an issue ref to a full closeout
     carrier; it never inspects a pause marker. Disconfirmer run:
     `brief_artifact_relpath` (`skills/public/issue/scripts/issue_brief.py:52-56`)
     emits a stable `...-issue-<n>-brief.md` suffix — a cheap discriminator the
     hook ignores; "can't tell it apart" is refuted.
  2. Bold-blind classification: `_CLASSIFICATION_RE`
     (`check_issue_closeout_commit_msg.py:14-17`) allows only
     `(?:[-*]\s*)?classification:`; the template renders
     `**Classification**: deferred-work`
     (`skills/public/issue/references/resolution-brief.md:21`), so the regex
     fails and `_infer_classification` falls through to the `bug` default,
     demanding root_cause/debug_artifact/siblings. Reproduces the reported
     three-step refusal.
  Over-reach check: the code-level bottoms are accurate; the systemic why
  (no shared "is this a closeout carrier?" predicate) is real but the fix
  point stays these two loci.

- Debug artifact: cite-only — this artifact carries the RCA; the multi-locus
  evidence is fully in the issue body plus the file:line cites above.

- Invariant proof: applies to the bold half — producer (brief template
  `**Classification**:`) → final consumer (hook `_infer_classification`
  regex); rendered form diverges from the parser at the propagation boundary.
  The pause carve-out half is a contract conflict, not a propagation bug.

- Detection gap: gates that exist —
  `tests/test_check_issue_closeout_commit_msg_inprocess.py` and
  `tests/quality_gates/test_issue_closeout_commit_msg_hook.py`. Neither covers
  a brief-persistence path nor a bold classification form (the in-process pin
  uses plain `Classification: question` only). Smallest fires: (a) a
  `_infer_classification` unit pin with `**Classification**: deferred-work`
  input; (b) an integration pin staging a `-brief.md` artifact and asserting
  no premature ledger demand. Over-reach check: one bold-form unit pin plus
  one brief-path integration pin suffice; a full property matrix is
  unwarranted.

- Sibling search (four-axis, static scan only):
  - `_bare_classification` reuses the bold-blind `_CLASSIFICATION_RE` — same
    class, diagnostic-only (input is plain commit messages).
  - `_FIELD_RE` (`issue_verify_closeout_body.py:44`) and `_BEHAVIOR_LINE_RE`
    (`:102`) share the no-bold model; latent, fed plain commit bodies —
    intentional plain-text boundary for now.
  - `_issue_closeout_artifacts` is the only "staged artifact ⇒ closeout"
    over-fire; `issue_close.py` takes classification as a param (no
    inference) — same class, fix now, localized.
  - `plugins/charness/scripts/check_issue_closeout_commit_msg.py` is the
    generated twin carrying both bugs — same bug, fix now (sync).
  Over-reach check: do not widen every `(?:[-*]\s*)?` regex to accept bold;
  most read plain commit text. Target the brief-reading consumer only.

- Bundle vs Defer:
  - Bundle now (cheap, one fix-unit): pause/brief carve-out; bold-aware
    classification read; plugins/ twin sync; the two regression pins.
  - Defer (diagnostic-only): `_bare_classification` / `_FIELD_RE` /
    `_BEHAVIOR_LINE_RE` bold-blindness — same class, latent on plain inputs.

- Fresh-Eye Satisfaction: parent-delegated
