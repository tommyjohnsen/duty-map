# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-16 | 552b829
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | pending | fix order-dependent conflict resolution and add provenance block
# END PROVENANCE
"""A compact, deterministic defeasible evaluator."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .loader import DutyMap, Rule


class Provability(str, Enum):
    DEFINITELY_PROVABLE = "definitely provable"
    DEFEASIBLY_PROVABLE = "defeasibly provable"
    NOT_PROVABLE = "not provable"


@dataclass(frozen=True)
class Proof:
    literal: str
    level: Provability
    rule_chain: tuple[str, ...] = ()


@dataclass(frozen=True)
class Evaluation:
    proofs: dict[str, Proof]
    applicable_duties: tuple[str, ...]

    def proof(self, literal: str) -> Proof:
        key = normalize_literal(literal)
        return self.proofs.get(key, Proof(key, Provability.NOT_PROVABLE))

    def status(self, literal: str) -> Provability:
        return self.proof(literal).level


def normalize_literal(value: str) -> str:
    value = value.strip()
    if value.startswith("not "):
        return "~" + value[4:].strip()
    if value.startswith("!"):
        return "~" + value[1:].strip()
    return value


def opposite(literal: str) -> str:
    literal = normalize_literal(literal)
    return literal[1:] if literal.startswith("~") else "~" + literal


def evaluate(duty_map: DutyMap, facts: Iterable[str] = ()) -> Evaluation:
    """Evaluate *duty_map* under *facts* and retain one proof chain per result."""
    rules = tuple(
        Rule(rule.id, rule.kind, tuple(normalize_literal(p) for p in rule.premises), normalize_literal(rule.conclusion))
        for rule in duty_map.rules
    )
    definite: dict[str, tuple[str, ...]] = {
        normalize_literal(fact): () for fact in facts if normalize_literal(fact)
    }

    changed = True
    while changed:
        changed = False
        for rule in rules:
            if rule.kind != "strict" or rule.conclusion in definite:
                continue
            if all(premise in definite for premise in rule.premises):
                definite[rule.conclusion] = _chain(rule, definite)
                changed = True

    rank = _superiority_closure(duty_map.superiority)
    reachable = set(definite)
    changed = True
    while changed:
        changed = False
        for rule in rules:
            if not all(premise in reachable for premise in rule.premises):
                continue
            if rule.kind != "defeater" and rule.conclusion not in reachable:
                reachable.add(rule.conclusion)
                changed = True

    activated = [rule for rule in rules if all(p in reachable for p in rule.premises)]
    supported = dict(definite)
    changed = True
    while changed:
        changed = False
        for rule in activated:
            if rule.kind == "defeater" or rule.conclusion in supported:
                continue
            if not all(premise in supported for premise in rule.premises):
                continue
            if opposite(rule.conclusion) in definite:
                continue
            opponents = [other for other in activated if other.conclusion == opposite(rule.conclusion)]
            if all(_is_superior(rule.id, other.id, rank) for other in opponents):
                supported[rule.conclusion] = _chain(rule, supported)
                changed = True

    proofs: dict[str, Proof] = {}
    candidates = set(definite) | set(supported)
    candidates.update(rule.conclusion for rule in rules)
    candidates.update(opposite(rule.conclusion) for rule in rules)
    for literal in sorted(candidates):
        if literal in definite:
            proofs[literal] = Proof(literal, Provability.DEFINITELY_PROVABLE, definite[literal])
        elif literal in supported:
            proofs[literal] = Proof(literal, Provability.DEFEASIBLY_PROVABLE, supported[literal])
        else:
            proofs[literal] = Proof(literal, Provability.NOT_PROVABLE)

    applicable_duties = tuple(
        duty.id
        for duty in duty_map.duties
        if all(normalize_literal(condition) in supported for condition in duty.conditions)
    )
    return Evaluation(proofs, applicable_duties)


def _chain(rule: Rule, proofs: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    chain: list[str] = []
    for premise in rule.premises:
        for item in proofs[premise]:
            if item not in chain:
                chain.append(item)
    chain.append(rule.id)
    return tuple(chain)


def _superiority_closure(pairs: tuple[tuple[str, str], ...]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for superior, inferior in pairs:
        result.setdefault(superior, set()).add(inferior)
    changed = True
    while changed:
        changed = False
        for superior, inferiors in list(result.items()):
            expanded = set(inferiors)
            for inferior in inferiors:
                expanded.update(result.get(inferior, ()))
            if expanded != inferiors:
                result[superior] = expanded
                changed = True
    return result


def _is_superior(candidate: str, opponent: str, closure: dict[str, set[str]]) -> bool:
    return opponent in closure.get(candidate, set())
