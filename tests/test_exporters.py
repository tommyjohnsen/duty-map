# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-16 | 552b829
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | 47cf23f | provenance block added
# END PROVENANCE
from pathlib import Path

import pytest

from duty_map import Duty, DutyMap, Relations, Rule, evaluate, export, load_duties
from duty_map.cli import main


SAMPLE = DutyMap(
    duties=(
        Duty(
            "record",
            "Record the loan",
            "other",
            "Invented Guide 1",
            "part 1",
            "US",
            "Record an eligible loan.",
            ("eligible",),
            Relations(supports=("allow",)),
        ),
    ),
    rules=(
        Rule("allow", "defeasible", ("member",), "eligible"),
        Rule("block", "defeater", ("restricted",), "~eligible"),
    ),
    superiority=(("block", "allow"),),
)


@pytest.mark.parametrize("format_name", ["argdown", "mermaid", "rules", "irac", "creac"])
def test_export_matches_golden_file(format_name):
    golden = Path(__file__).parent / "golden" / f"sample.{format_name}"
    assert export(SAMPLE, format_name) == golden.read_text(encoding="utf-8")


def test_unknown_export_format_is_rejected():
    with pytest.raises(ValueError, match="unknown export format"):
        export(SAMPLE, "unknown")


def test_cli_exports_to_file(tmp_path):
    output = tmp_path / "rules.md"
    assert main([
        "export",
        "examples/example-rules.toml",
        "--format",
        "rules",
        "--output",
        str(output),
    ]) == 0
    assert output.read_text(encoding="utf-8").startswith("# Rules\n")


def test_fictional_example_exercises_exceptions_and_overrides():
    duty_map = load_duties("examples/example-rules.toml")
    ordinary = evaluate(duty_map, ["member", "has_card"])
    assert ordinary.applicable_duties == ("record_loan",)

    reference_item = evaluate(duty_map, ["member", "has_card", "reference_item"])
    assert "record_loan" not in reference_item.applicable_duties

    extended = evaluate(duty_map, ["item_borrowed", "extension_approved"])
    assert "return_on_due_date" not in extended.applicable_duties
    assert "return_on_extended_date" in extended.applicable_duties
