# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-16 | 552b829
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | 47cf23f | add later-activated conflict regression test and provenance block
# END PROVENANCE
from duty_map import DutyMap, Provability, Rule, evaluate


def test_strict_rule_chain_is_definite():
    rules = (
        Rule("r1", "strict", ("a",), "b"),
        Rule("r2", "strict", ("b",), "c"),
    )
    result = evaluate(DutyMap((), rules), ["a"])
    assert result.status("c") is Provability.DEFINITELY_PROVABLE
    assert result.proof("c").rule_chain == ("r1", "r2")


def test_unopposed_defeasible_rule_and_missing_premise():
    rules = (Rule("r1", "defeasible", ("a",), "b"),)
    assert evaluate(DutyMap((), rules), ["a"]).status("b") is Provability.DEFEASIBLY_PROVABLE
    assert evaluate(DutyMap((), rules), []).status("b") is Provability.NOT_PROVABLE


def test_equal_conflict_proves_neither_side():
    rules = (
        Rule("yes", "defeasible", ("a",), "b"),
        Rule("no", "defeasible", ("a",), "~b"),
    )
    result = evaluate(DutyMap((), rules), ["a"])
    assert result.status("b") is Provability.NOT_PROVABLE
    assert result.status("~b") is Provability.NOT_PROVABLE


def test_equal_conflict_activated_by_later_derived_premise_proves_neither_side():
    rules = (
        Rule("yes", "defeasible", ("a",), "b"),
        Rule("derive_opposition", "defeasible", ("a",), "opposition"),
        Rule("no", "defeasible", ("opposition",), "~b"),
    )
    result = evaluate(DutyMap((), rules), ["a"])
    assert result.status("b") is Provability.NOT_PROVABLE
    assert result.status("~b") is Provability.NOT_PROVABLE


def test_superiority_resolves_conflict():
    rules = (
        Rule("yes", "defeasible", ("a",), "b"),
        Rule("no", "defeasible", ("a",), "~b"),
    )
    result = evaluate(DutyMap((), rules, (("yes", "no"),)), ["a"])
    assert result.status("b") is Provability.DEFEASIBLY_PROVABLE
    assert result.status("~b") is Provability.NOT_PROVABLE


def test_defeater_blocks_but_never_supports_its_conclusion():
    rules = (
        Rule("yes", "defeasible", ("a",), "b"),
        Rule("block", "defeater", ("a",), "~b"),
    )
    result = evaluate(DutyMap((), rules), ["a"])
    assert result.status("b") is Provability.NOT_PROVABLE
    assert result.status("~b") is Provability.NOT_PROVABLE


def test_superior_defeasible_rule_overcomes_defeater():
    rules = (
        Rule("yes", "defeasible", ("a",), "b"),
        Rule("block", "defeater", ("a",), "~b"),
    )
    result = evaluate(DutyMap((), rules, (("yes", "block"),)), ["a"])
    assert result.status("b") is Provability.DEFEASIBLY_PROVABLE
