# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-16 | 552b829
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | 47cf23f | provenance block added
# reviewed-by: claude-code/claude-opus-5-5 | 2026-10-26 | APPROVE_WITH_NITS
# END PROVENANCE
"""Deterministic text exporters for duty maps."""

from __future__ import annotations

from collections.abc import Callable

from .loader import Duty, DutyMap, Rule


def _literal(value: str) -> str:
    return f"not {value[1:]}" if value.startswith("~") else value


def _join(values: tuple[str, ...]) -> str:
    return ", ".join(_literal(value) for value in values) if values else "(none)"


def _argdown_text(value: str) -> str:
    return " ".join(value.replace("[", "(").replace("]", ")").split())


def to_argdown(duty_map: DutyMap) -> str:
    """Render an Argdown document without requiring the Argdown CLI."""
    lines = ["# Duty Map", "", "## Duties", ""]
    duty_ids = {duty.id for duty in duty_map.duties}
    def reference(value: str) -> str:
        kind = "Duty" if value in duty_ids else "Rule"
        return f"[{kind} {value}]"

    for duty in duty_map.duties:
        lines.extend(
            [
                f"[Duty {duty.id}]: {_argdown_text(duty.label)} — {_argdown_text(duty.summary)}",
                f"  - Source: {_argdown_text(duty.source)}, {_argdown_text(duty.pinpoint)}",
                f"  - Conditions: {_argdown_text(_join(duty.conditions))}",
            ]
        )
        for target_id in duty.relations.supports:
            lines.append(f"  +> {reference(target_id)}")
        for target_id in duty.relations.attacks:
            lines.append(f"  -> {reference(target_id)}")
        for target_id in duty.relations.exception_to:
            lines.append(f"  -> {reference(target_id)} (exception)")
        lines.append("")
    lines.extend(["## Rules", ""])
    for rule in duty_map.rules:
        arrow = {"strict": "->", "defeasible": "=>", "defeater": "~>"}[rule.kind]
        lines.append(
            f"[Rule {rule.id}]: ({_argdown_text(_join(rule.premises))}) "
            f"{arrow} {_argdown_text(_literal(rule.conclusion))} [{rule.kind}]"
        )
    if duty_map.superiority:
        lines.extend(["", "## Superiority", ""])
        lines.extend(f"[Rule {better}] +> [Rule {worse}]" for better, worse in duty_map.superiority)
    return "\n".join(lines).rstrip() + "\n"


def _mermaid_text(value: str) -> str:
    replacements = {
        "&": "and",
        '"': "'",
        "<": "(",
        ">": ")",
        "[": "(",
        "]": ")",
        "{": "(",
        "}": ")",
        "|": "/",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return " ".join(value.split())


def to_mermaid(duty_map: DutyMap) -> str:
    """Render a Mermaid flowchart using generated, syntax-safe node ids."""
    lines = ["flowchart TD"]
    duty_nodes = {duty.id: f"d{index}" for index, duty in enumerate(duty_map.duties, 1)}
    rule_nodes = {rule.id: f"r{index}" for index, rule in enumerate(duty_map.rules, 1)}
    fact_names = sorted(
        {literal.removeprefix("~") for rule in duty_map.rules for literal in (*rule.premises, rule.conclusion)}
        | {condition.removeprefix("~") for duty in duty_map.duties for condition in duty.conditions}
    )
    fact_nodes = {fact: f"f{index}" for index, fact in enumerate(fact_names, 1)}
    for fact, node in fact_nodes.items():
        lines.append(f'  {node}["{_mermaid_text(fact)}"]')
    for duty in duty_map.duties:
        lines.append(f'  {duty_nodes[duty.id]}["Duty: {_mermaid_text(duty.label)}"]')
    for rule in duty_map.rules:
        lines.append(f'  {rule_nodes[rule.id]}{{"{_mermaid_text(rule.id)} ({rule.kind})"}}')
    for rule in duty_map.rules:
        rule_node = rule_nodes[rule.id]
        for premise in rule.premises:
            label = "not" if premise.startswith("~") else "premise"
            lines.append(f"  {fact_nodes[premise.removeprefix('~')]} -->|{label}| {rule_node}")
        conclusion = rule.conclusion
        label = "defeats" if rule.kind == "defeater" else ("not" if conclusion.startswith("~") else "concludes")
        lines.append(f"  {rule_node} -->|{label}| {fact_nodes[conclusion.removeprefix('~')]}")
    for duty in duty_map.duties:
        for condition in duty.conditions:
            fact_node = fact_nodes.get(condition.removeprefix("~"))
            if fact_node:
                label = "requires not" if condition.startswith("~") else "requires"
                lines.append(f"  {fact_node} -->|{label}| {duty_nodes[duty.id]}")
        for relation, label in (
            (duty.relations.supports, "supports"),
            (duty.relations.attacks, "attacks"),
            (duty.relations.exception_to, "exception to"),
        ):
            for target in relation:
                target_node = duty_nodes.get(target) or rule_nodes.get(target)
                if target_node:
                    lines.append(f"  {duty_nodes[duty.id]} -.->|{label}| {target_node}")
    for better, worse in duty_map.superiority:
        lines.append(f"  {rule_nodes[better]} -.->|overrides| {rule_nodes[worse]}")
    lines.extend(["  classDef duty fill:#eef,stroke:#446;", "  classDef rule fill:#efe,stroke:#464;"])
    if duty_nodes:
        lines.append(f"  class {','.join(duty_nodes.values())} duty;")
    if rule_nodes:
        lines.append(f"  class {','.join(rule_nodes.values())} rule;")
    return "\n".join(lines) + "\n"


def to_rules(duty_map: DutyMap) -> str:
    """Render a compact, readable rules listing."""
    lines = ["# Rules", ""]
    for rule in duty_map.rules:
        lines.extend(
            [
                f"## {rule.id}",
                f"- Kind: {rule.kind}",
                f"- If: {_join(rule.premises)}",
                f"- Then: {_literal(rule.conclusion)}",
                "",
            ]
        )
    lines.extend(["# Superiority", ""])
    if duty_map.superiority:
        lines.extend(f"- {better} overrides {worse}" for better, worse in duty_map.superiority)
    else:
        lines.append("- (none)")
    return "\n".join(lines).rstrip() + "\n"


def _outline(duty_map: DutyMap, style: str) -> str:
    section_names = (
        ("Conclusion", "Rule", "Application", "Conclusion")
        if style == "CREAC"
        else ("Issue", "Rule", "Application", "Conclusion")
    )
    lines = [f"# {style} Outline", ""]
    for duty in duty_map.duties:
        lines.extend([f"## {duty.label} (`{duty.id}`)", ""])
        if style == "CREAC":
            summary = duty.summary.rstrip(".?!")
            opening = f"State whether the duty to {summary[:1].lower() + summary[1:]} applies."
        else:
            opening = f"Does the duty apply when these conditions hold: {_join(duty.conditions)}?"
        content = (
            opening,
            f"{duty.summary} Source: {duty.source}, {duty.pinpoint} ({duty.jurisdiction}).",
            f"Compare the verified facts with: {_join(duty.conditions)}. Address exceptions and overrides shown in the rules listing.",
            "State the verified result and any unresolved facts.",
        )
        for heading, paragraph in zip(section_names, content):
            lines.extend([f"### {heading}", "", paragraph, ""])
    return "\n".join(lines).rstrip() + "\n"


def to_irac(duty_map: DutyMap) -> str:
    return _outline(duty_map, "IRAC")


def to_creac(duty_map: DutyMap) -> str:
    return _outline(duty_map, "CREAC")


EXPORTERS: dict[str, Callable[[DutyMap], str]] = {
    "argdown": to_argdown,
    "mermaid": to_mermaid,
    "rules": to_rules,
    "irac": to_irac,
    "creac": to_creac,
}


def export(duty_map: DutyMap, format_name: str) -> str:
    """Export *duty_map* in one of the supported named formats."""
    try:
        renderer = EXPORTERS[format_name]
    except KeyError as exc:
        raise ValueError(f"unknown export format: {format_name}") from exc
    return renderer(duty_map)
