# Cost Dominance

A **dominated** command buys the same evidence as a cheaper command this repo
already has. It is not a *wrong* command, and that is the whole problem: every
review angle a repo normally runs asks whether a claim matches the tree, and a
dominated instruction matches the tree perfectly. It just costs more than it
needs to, every time anyone follows it.

The recorded instance that produced this surface: a repo handoff prescribed a
whole-suite `pytest` run and stated its cost as a fact of nature. A measured,
budgeted, enforced parallel runner covering the same scope already shipped in the
same repo and was roughly fifteen times faster. The instruction passed fresh-eye
review three times, because it was true. Three slices paid the difference before
anyone asked the cost question.

## The two halves

**Detection is deterministic and narrow.** `command_dominance_lib.py` answers one
question — does this command match a shape this repo has *registered* as
dominated, and what does the registry say replaces it. `inventory_command_dominance.py`
runs it over the commands `standing_gate_discovery_lib.py` finds in your standing
gates, plus any config literals you declare.

**Judgement is yours and is not optional.** The registry is authored memory, not
measurement. Its blind spots are stated in the inventory's own `interpretation`
block and in the library's module docstring; the load-bearing one is that a slow
command nobody registered is invisible, so a clean report is not a cheap repo.
The consumer must answer first:
does the cheaper replacement give the SAME evidence this site needs, or does the
site genuinely need what the slower command provides — and if so, is that reason
written where the next reader meets the command?

## Authoring the registry arms one blocking surface

Read this before you create the file. Installing the plugin changes nothing on
its own — with no registry, the check below stays inert and cannot fail your
lane. Writing the registry is what arms it:

- **`check-command-dominance`** runs in the quality lane and **exits nonzero**
  on any non-exempt dominated command it finds in your standing-gate surfaces or
  your declared config literals. If your pre-push hook runs the quality lane, a
  dominated command there will refuse the push.

The check is not advisory. To see what a registry would catch before arming it,
draft it somewhere the gates do not read and point the inventory at it:

```bash
inventory_command_dominance.py --repo-root . --registry-path .agents/command-dominance.draft.yaml
```

That command is advisory by construction and always exits 0. Running the
inventory with no registry at the default path previews nothing — it reports
`registry_state: absent` and finds nothing — so the draft path is what makes the
preview real. Creating the file at the default path arms the blocking check at
that instant.

The `exemptions` block below is the escape for a site that genuinely needs the
slower command, and it requires a reason.

## Registry schema

`<repo-root>/.agents/command-dominance.yaml`, read by one owner. Absent is a legitimate
state: no registry means nothing is declared dominated, which the inventory
reports by name rather than as an empty finding list. Block style only — the
repo-side reader drops flow mappings and refuses rather than reading less.

```yaml
version: 1
dominated_commands:
  - id: bare-pytest-whole-suite
    program: pytest              # the RESOLVED program, after `python3 -m`, `env`,
                                 # `uv run`, and declared wrappers are stripped
    broad_targets:               # dominated only when its positional targets are
      - tests                    # these, or absent; a focused run is not dominated
    value_flags:                 # so `-m 'not release_only'` is not read as a target
      - -m
      - -k
    focus_flags:                 # flags that NARROW a run, consulted ONLY when there
      - -k                       # is no positional target. OMIT THIS AND FOCUSED RUNS
      - -m                       # ARE REPORTED DOMINATED: with no target and no focus
      - --deselect               # flag, "no target" reads as "everything", so
      - --last-failed            # `pytest -k smoke` is refused and the author is told
                                 # to run the whole suite. Do NOT list a flag that only
                                 # REORDERS (`--failed-first`) -- it excludes nothing,
                                 # and listing it lets a full run pass clean.
    replacement: python3 scripts/gates_support/run_standing_pytest.py
    reason: why the replacement is equivalent evidence
    measured: the evidence a human collected; nothing re-runs it
wrapper_programs:                # programs that RUN another program
  - program: queue_selected
    skip_args: 1
config_literals:                 # a literal a GATE reads and then spawns
  - path: cosmic-ray.toml
    key: test-command
exemptions:                      # keyed to a SITE, and a reason is REQUIRED
  - id: cosmic-ray-per-mutant-fallback
    site: cosmic-ray.toml:test-command
    rule: bare-pytest-whole-suite
    reason: why this site needs the slower command
```

Exemption granularity differs by seam, and the difference is real. A
`config_literals` site is `path:key`, so an exemption names one literal. A
standing-gate site is the whole FILE, so exempting one dominated command in a
runner exempts every dominated command in that file for that rule. Findings
carry `line` so the report shows which command was judged; write the reason so it
names that command.

What this cannot see is stated in `command_dominance_lib`'s module docstring and
in the inventory's own `interpretation.blind_spots`. Two limits matter most when
deciding whether a clean report means anything: the discovery scanner recognises
a fixed set of program names, so a repo whose expensive command is `tox`, `jest`,
`rspec`, `gradle`, or `bazel` gets no finding from a shell surface however it
registers it; and only five surface kinds are discovered at all
(`.githooks/pre-push`, `.husky/pre-push`, lefthook, `package.json`, `Makefile`),
so a repo driven purely by CI workflow files is scanned nowhere.

Two properties are pinned by tests rather than by this prose, because both are
the shape by which a cost gate usually becomes decorative. Declaring a
`replacement` does not silence a document that prescribes the original. And an
exemption changes a finding's `exempt` flag, never its presence — an exempt site
stays in the report with its reason attached, so "we decided this one is fine"
remains visible instead of becoming invisible.

## The review angle

`critique`'s `cost-dominance` angle covers what the registry cannot: the
commands nobody registered, which is most of them. It asks one question — is
there a cheaper path to the same evidence — of every command a change
prescribes, queues, or spawns, and of the proof the change proposes for itself.
