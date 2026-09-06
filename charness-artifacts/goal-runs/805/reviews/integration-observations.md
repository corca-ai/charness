# Goal 805 integration observations

Date: 2026-09-06

## Changed-line and broad observations

At `d325c9fdd24f59f8c74468b8b6425c9cf5e86756`, closeout changed-line
coverage passed against `23a9eaa6`: all 16 changed production owners were
analyzed, none orphaned, no blocking lines. Producer duration was 130.4s;
its selected standing run took 125.4s. The following complete standing run
passed 9,219 tests in 96.70s.

The subsequent full read-only lane did **not** pass: 79 gates passed, four
failed, five were explicitly not run, total 163.0s. Failures were skill length,
skill ergonomics, static command reconstruction in a new test, and two
generic-api-key findings. These are integration rework, not pilot results.

## Bounded repair

- Subject defect: debug and retro repeated output schemas already owned by
  their scaffolds; retro also repeated its counterfactual selection rule.
  Deleted those copies without moving overflow into references. Core still
  owns selection, diagnosis, uncertainty, no-write precedence, recurrence and
  handoff. Debug keeps the literal risk/handoff vocabulary. The evidence-led
  selector is named by its actual option; its subject-preserving bootstrap and
  contract-change fallback remain. Bodies are now 194 and 191 lines.
- Scope-too-broad observation: the command scanner dropped a dynamic subcommand
  from three test invocations and then judged subcommand flags against top-level
  help. One test helper now exposes both concrete CLI entrypoints and shares
  their identical arguments. Both commands still execute for every original
  stimulus; no parser, checker, or acceptance assertion was weakened.
- False-positive observation: the secret matches are ordinary oracle prose and
  an old observer's SHA256. The latter independently equals the current
  `skills/public/impl/references/external-api-contract.md` content digest.
  Frozen protocol and historical observer bytes remain unchanged. A narrow
  config exception is being verified; no whole-file exclusion is accepted.

Ruff and the skill creator's two frontmatter validations passed. The combined
CLI, debug scaffold/artifact, retro artifact/plan and skill-contract selection
passed 144 tests in 3.42s. The focused gate rerun passed skill validity,
ergonomics, semantic-contract pins and documented-command flags. Secrets still
reported the protocol sentence, so that rerun is four passes and one failure,
not a completed integration.

The first independent secret-control fixture used only the isolated sentence,
then a different secret-rule family in an adjacent file. Those observations do
not establish the full protocol's exact-path generic-key behavior. The parent
requested the complete original file, same scanner command and exact-path
negative control before accepting a repair. No candidate package or comparison
cell has been frozen or executed yet.

The complete protocol reproduced the remaining false positive. Its actual
matched value is the ordinary label `collision/duplicate`; the anchored
full-sentence exception did not fit the scanner's observed match. Final config
binds that exact matched value to the exact protocol path. Parent independently
ran the real directory scanner: original protocol passed, while the complete
protocol plus a synthetic API-key assignment in the same file failed with
`generic-api-key` at the added line. No test credential value is retained here.
The repository-owned secret gate then passed in 10.1s. Config SHA256:
`e5d9f859b5be52b60c78a87980df8f5b086e5f14c467bebea3e6058e216ff1b9`.

Verification-cost attribution: the separate standing run followed by a full
lane containing pytest follows this repository's explicit development rule,
not a new consumer-plugin requirement. These runs overlapped in protected
subject coverage, but their full input equivalence has not been established.
Discovering cheap length/CLI failures only after that cost was the executing
agent's sequencing miss. Packet/review preparation also delayed the usefulness
pilot; counts alone do not establish which independent boundaries were
redundant. Existing release scheduling removes one demonstrated duplicate
subject execution while retaining final-state proof. Broader policy changes
are not part of the pre-comparison repair; assess remaining high-cost repeats
in the existing final retro after observing the pilot.
