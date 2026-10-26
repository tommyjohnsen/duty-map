# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-16 | 552b829
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | 47cf23f | provenance block added
# reviewed-by: claude-code/claude-opus-5-5 | 2026-10-26 | APPROVE
# reviewed-by: grok-build/grok-4.7 | 2026-10-26 | APPROVE
# END PROVENANCE
"""TOML loader and validation for duty maps."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping
import tomllib

DEFAULT_JURISDICTIONS = frozenset({"US", "US-WA"})
CATEGORIES = frozenset(
    {"competence", "confidentiality", "communication", "fees", "supervision", "candor", "other"}
)
RULE_KINDS = frozenset({"strict", "defeasible", "defeater"})


class DutyMapError(ValueError):
    """Raised when a duties file is malformed."""


@dataclass(frozen=True)
class Relations:
    supports: tuple[str, ...] = ()
    attacks: tuple[str, ...] = ()
    exception_to: tuple[str, ...] = ()


@dataclass(frozen=True)
class Duty:
    id: str
    label: str
    category: str
    source: str
    pinpoint: str
    jurisdiction: str
    summary: str
    conditions: tuple[str, ...]
    relations: Relations = field(default_factory=Relations)


@dataclass(frozen=True)
class Rule:
    id: str
    kind: str
    premises: tuple[str, ...]
    conclusion: str


@dataclass(frozen=True)
class DutyMap:
    duties: tuple[Duty, ...]
    rules: tuple[Rule, ...]
    superiority: tuple[tuple[str, str], ...] = ()


def _text(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DutyMapError(f"{location} must be a non-empty string")
    return value.strip()


def _strings(value: Any, location: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise DutyMapError(f"{location} must be an array of strings")
    result = tuple(_text(item, f"{location}[]") for item in value)
    if len(result) != len(set(result)):
        raise DutyMapError(f"{location} must not contain duplicates")
    return result


def _table_list(data: Mapping[str, Any], singular: str, plural: str) -> list[Any]:
    if singular in data and plural in data:
        raise DutyMapError(f"use either '{singular}' or '{plural}', not both")
    value = data.get(plural, data.get(singular, []))
    if not isinstance(value, list):
        raise DutyMapError(f"'{plural}' must be an array of tables")
    return value


def load_duties(
    path: str | Path, allowed_jurisdictions: Iterable[str] | None = None
) -> DutyMap:
    """Load and validate a duty map from *path*.

    ``allowed_jurisdictions`` replaces the shipped allow-list when supplied.
    """
    allowed = frozenset(
        DEFAULT_JURISDICTIONS if allowed_jurisdictions is None else allowed_jurisdictions
    )
    if not allowed or any(not isinstance(item, str) or not item for item in allowed):
        raise DutyMapError("allowed jurisdictions must be non-empty strings")
    try:
        with Path(path).open("rb") as stream:
            data = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise DutyMapError(f"cannot load duties file: {exc}") from exc

    duties: list[Duty] = []
    for index, raw in enumerate(_table_list(data, "duty", "duties"), 1):
        where = f"duties[{index}]"
        if not isinstance(raw, dict):
            raise DutyMapError(f"{where} must be a table")
        category = _text(raw.get("category"), f"{where}.category")
        if category not in CATEGORIES:
            raise DutyMapError(f"{where}.category is not recognized: {category}")
        jurisdiction = _text(raw.get("jurisdiction"), f"{where}.jurisdiction")
        if jurisdiction not in allowed:
            raise DutyMapError(f"{where}.jurisdiction is not allowed: {jurisdiction}")
        relation_data = raw.get("relations", {})
        if not isinstance(relation_data, dict):
            raise DutyMapError(f"{where}.relations must be a table")
        unknown_relations = set(relation_data) - {"supports", "attacks", "exception_to"}
        if unknown_relations:
            raise DutyMapError(f"{where}.relations has unknown keys: {', '.join(sorted(unknown_relations))}")
        duties.append(
            Duty(
                id=_text(raw.get("id"), f"{where}.id"),
                label=_text(raw.get("label"), f"{where}.label"),
                category=category,
                source=_text(raw.get("source"), f"{where}.source"),
                pinpoint=_text(raw.get("pinpoint"), f"{where}.pinpoint"),
                jurisdiction=jurisdiction,
                summary=_text(raw.get("summary"), f"{where}.summary"),
                conditions=_strings(raw.get("conditions"), f"{where}.conditions"),
                relations=Relations(
                    supports=_strings(relation_data.get("supports", []), f"{where}.relations.supports"),
                    attacks=_strings(relation_data.get("attacks", []), f"{where}.relations.attacks"),
                    exception_to=_strings(
                        relation_data.get("exception_to", []), f"{where}.relations.exception_to"
                    ),
                ),
            )
        )

    rules: list[Rule] = []
    for index, raw in enumerate(_table_list(data, "rule", "rules"), 1):
        where = f"rules[{index}]"
        if not isinstance(raw, dict):
            raise DutyMapError(f"{where} must be a table")
        kind_value = raw.get("kind", raw.get("type"))
        kind = _text(kind_value, f"{where}.kind")
        if kind not in RULE_KINDS:
            raise DutyMapError(f"{where}.kind is not recognized: {kind}")
        premises_value = raw.get("premises", raw.get("conditions"))
        rules.append(
            Rule(
                id=_text(raw.get("id"), f"{where}.id"),
                kind=kind,
                premises=_strings(premises_value, f"{where}.premises"),
                conclusion=_text(raw.get("conclusion"), f"{where}.conclusion"),
            )
        )

    ids = [item.id for item in duties] + [item.id for item in rules]
    if len(ids) != len(set(ids)):
        raise DutyMapError("duty and rule ids must be unique")

    raw_superiority = data.get("superiority", [])
    if not isinstance(raw_superiority, list):
        raise DutyMapError("superiority must be an array")
    pairs: list[tuple[str, str]] = []
    rule_ids = {rule.id for rule in rules}
    for index, raw in enumerate(raw_superiority, 1):
        if isinstance(raw, list) and len(raw) == 2:
            superior, inferior = raw
        elif isinstance(raw, dict):
            superior, inferior = raw.get("superior"), raw.get("inferior")
        else:
            raise DutyMapError(f"superiority[{index}] must be a two-item array or table")
        pair = (_text(superior, f"superiority[{index}].superior"), _text(inferior, f"superiority[{index}].inferior"))
        if pair[0] == pair[1]:
            raise DutyMapError(f"superiority[{index}] cannot refer to the same rule twice")
        if not set(pair) <= rule_ids:
            raise DutyMapError(f"superiority[{index}] refers to an unknown rule")
        pairs.append(pair)
    if len(pairs) != len(set(pairs)):
        raise DutyMapError("superiority must not contain duplicate pairs")
    _validate_superiority(pairs)
    return DutyMap(tuple(duties), tuple(rules), tuple(pairs))


def _validate_superiority(pairs: list[tuple[str, str]]) -> None:
    edges: dict[str, set[str]] = {}
    for superior, inferior in pairs:
        edges.setdefault(superior, set()).add(inferior)

    def visit(node: str, active: set[str], done: set[str]) -> None:
        if node in active:
            raise DutyMapError("superiority relation must be acyclic")
        if node in done:
            return
        active.add(node)
        for child in edges.get(node, ()):
            visit(child, active, done)
        active.remove(node)
        done.add(node)

    done: set[str] = set()
    for node in edges:
        visit(node, set(), done)
