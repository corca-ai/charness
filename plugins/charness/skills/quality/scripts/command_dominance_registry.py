#!/usr/bin/env python3

"""What a command-dominance registry DECLARES, and how a declaration is read.

Split from `command_dominance_lib` on a concept boundary, not to dodge the length
cap: this file answers "what did an author declare, and is the declaration
well-formed", while the lib next door answers "is this command dominated". The two
fail differently and are owned differently -- a malformed registry is an authoring
error the operator repairs, while a dominated command is a finding about the repo.
Keeping the parser here also keeps the reader honest about its inputs: every field
the reader consults is constructed exactly once, by the functions below.

Stdlib only, and it opens no files. Callers hand in already-parsed data, which is
what keeps the whole family export-safe under `check_export_self_sufficiency.py`.
"""

from __future__ import annotations

from typing import NamedTuple

REGISTRY_VERSION = 1


class RegistryError(ValueError):
    """A registry that cannot be trusted to render a verdict."""


# NamedTuple rather than dataclass, and the reason is not style: this module is
# loaded by `runtime_bootstrap.load_path_module`, which execs a module that is
# never registered in `sys.modules`. `@dataclass` resolves its own annotations
# through `sys.modules[cls.__module__]` and raises `AttributeError: 'NoneType'`
# there. Measured, not assumed -- the first import of this file failed that way.
class DominanceRule(NamedTuple):
    rule_id: str
    program: str
    replacement: str
    reason: str
    broad_targets: tuple[str, ...] = ()
    value_flags: tuple[str, ...] = ()
    focus_flags: tuple[str, ...] = ()
    measured: str = ""


class Exemption(NamedTuple):
    exemption_id: str
    site: str
    rule_id: str
    reason: str


class Wrapper(NamedTuple):
    """A program that RUNS another program, plus how many of its own args to skip.

    Declared rather than inferred, and declared by the CONSUMING repo, because the
    shape is repo-local: charness queues every standing gate as
    `queue_selected "<label>" <command>`, so a resolver that stops at the first
    token resolves every queued command to `queue_selected` and the whole
    standing-gate arm reads clean while a dominated command sits inside it.

    RE-MEASURED 2026-08-16 by running the discovery, after a bounded reviewer
    counted the tree by hand and refuted the figure this docstring first carried:
    14 discovered snippets, 8 wrapped and 6 unwrapped. The original "13 of 14"
    was never counted -- it was inferred from a probe that showed 14 snippets and
    one pytest-bearing line. It is asserted now rather than asserted about, by
    `test_the_wrapped_snippet_ratio_this_repo_documents_is_the_measured_one`,
    so the next drift is a red test rather than a stale sentence.
    """

    program: str
    skip_args: int = 0


class Registry(NamedTuple):
    rules: tuple[DominanceRule, ...] = ()
    exemptions: tuple[Exemption, ...] = ()
    config_literals: tuple[dict[str, str], ...] = ()
    wrappers: tuple[Wrapper, ...] = ()

    def rule(self, rule_id: str) -> DominanceRule | None:
        return next((rule for rule in self.rules if rule.rule_id == rule_id), None)

    def exemption_for(self, site: str, rule_id: str) -> Exemption | None:
        return next(
            (
                item
                for item in self.exemptions
                if item.site == site and item.rule_id == rule_id
            ),
            None,
        )


class Finding(NamedTuple):
    rule_id: str
    site: str
    command: str
    replacement: str
    reason: str
    line: int | None = None
    exempt: bool = False
    exemption_id: str | None = None
    exemption_reason: str | None = None
    context: dict[str, str] | None = None

    def as_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "rule_id": self.rule_id,
            "site": self.site,
            "command": self.command,
            "replacement": self.replacement,
            "reason": self.reason,
            "exempt": self.exempt,
        }
        if self.line is not None:
            payload["line"] = self.line
        if self.exempt:
            payload["exemption_id"] = self.exemption_id
            payload["exemption_reason"] = self.exemption_reason
        if self.context:
            payload["context"] = dict(self.context)
        return payload


def _require_text(mapping: dict, key: str, where: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RegistryError(f"{where}: `{key}` is required and must be non-empty text")
    return value.strip()


def _require_list(mapping: dict, key: str, where: str) -> tuple[str, ...]:
    """A list-valued field must arrive as a LIST, or the registry is refused.

    Not defensive programming — this is the failure that reached a green gate
    during this slice. One of the two readers of this file is a hand-rolled
    block-YAML parser that turns an inline sequence `[tests]` into the STRING
    "[tests]" without complaint. Iterating a string yields its characters, so
    `broad_targets` silently became seven single-character targets, no command
    ever matched, and the gate reported a clean tree over a dominated literal.
    Coercing with `str(item) for item in ...` is what made that silent; refusing
    the shape is what makes it loud.
    """
    value = mapping.get(key)
    if value is None:
        return ()
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        raise RegistryError(
            f"{where}: `{key}` must be a list, got {type(value).__name__} {value!r}. "
            "Use block-style YAML entries; an inline `[a, b]` sequence is read as a "
            "bare string by this repo's adapter parser and would silently match nothing."
        )
    return tuple(str(item) for item in value)


def _entries(data: dict, key: str) -> list[tuple[str, dict]]:
    """The list under `key`, each entry paired with the label errors will name.

    Every section of this registry validates the same two things before its own
    rules apply -- the section is a list, and each entry is a mapping -- so they
    are checked once here rather than four times with four slightly different
    messages.
    """
    raw = data.get(key) or []
    if not isinstance(raw, list):
        raise RegistryError(f"`{key}` must be a list")
    entries = []
    for index, item in enumerate(raw):
        where = f"{key}[{index}]"
        if not isinstance(item, dict):
            raise RegistryError(f"{where}: entry must be a mapping")
        entries.append((where, item))
    return entries


def _parse_rules(data: dict) -> tuple[DominanceRule, ...]:
    rules: list[DominanceRule] = []
    for where, raw in _entries(data, "dominated_commands"):
        rule = DominanceRule(
            rule_id=_require_text(raw, "id", where),
            program=_require_text(raw, "program", where),
            replacement=_require_text(raw, "replacement", where),
            reason=_require_text(raw, "reason", where),
            broad_targets=_require_list(raw, "broad_targets", where),
            value_flags=_require_list(raw, "value_flags", where),
            focus_flags=_require_list(raw, "focus_flags", where),
            measured=str(raw.get("measured") or "").strip(),
        )
        if any(existing.rule_id == rule.rule_id for existing in rules):
            raise RegistryError(f"{where}: duplicate rule id {rule.rule_id!r}")
        rules.append(rule)
    return tuple(rules)


def _parse_exemptions(data: dict, known_ids: set[str]) -> tuple[Exemption, ...]:
    exemptions: list[Exemption] = []
    for where, raw in _entries(data, "exemptions"):
        rule_id = _require_text(raw, "rule", where)
        if rule_id not in known_ids:
            raise RegistryError(
                f"{where}: exempts unknown rule {rule_id!r}; an exemption naming no "
                "live rule is a hole nothing can close"
            )
        exemptions.append(
            Exemption(
                exemption_id=_require_text(raw, "id", where),
                site=_require_text(raw, "site", where),
                rule_id=rule_id,
                reason=_require_text(raw, "reason", where),
            )
        )
    return tuple(exemptions)


def _parse_config_literals(data: dict) -> tuple[dict[str, str], ...]:
    return tuple(
        {"path": _require_text(raw, "path", where), "key": _require_text(raw, "key", where)}
        for where, raw in _entries(data, "config_literals")
    )


def _parse_wrappers(data: dict) -> tuple[Wrapper, ...]:
    wrappers: list[Wrapper] = []
    for where, raw in _entries(data, "wrapper_programs"):
        skip = raw.get("skip_args", 0)
        if not isinstance(skip, int) or isinstance(skip, bool) or skip < 0:
            raise RegistryError(f"{where}: `skip_args` must be a non-negative integer")
        wrappers.append(Wrapper(program=_require_text(raw, "program", where), skip_args=skip))
    return tuple(wrappers)


def parse_registry(data: object) -> Registry:
    """Turn registry data into rules, refusing anything that cannot render a verdict.

    A reasonless rule or exemption is REFUSED rather than defaulted. An exemption
    is the one place this mechanism accepts "a human decided this is fine", so an
    exemption whose reason is absent is a silent hole in a proof surface, and the
    cheapest possible response to a red gate. It has to cost a sentence.
    """
    if not isinstance(data, dict):
        raise RegistryError("registry must be a mapping")
    version = data.get("version")
    if version != REGISTRY_VERSION:
        raise RegistryError(
            f"registry version {version!r} is not the version this reader "
            f"understands ({REGISTRY_VERSION})"
        )
    rules = _parse_rules(data)
    return Registry(
        rules=rules,
        exemptions=_parse_exemptions(data, {rule.rule_id for rule in rules}),
        config_literals=_parse_config_literals(data),
        wrappers=_parse_wrappers(data),
    )
