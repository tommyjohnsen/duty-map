# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-16 | 552b829
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | 47cf23f | provenance block added
# reviewed-by: claude-code/claude-opus-5-5 | 2026-10-26 | APPROVE
# END PROVENANCE
"""Command line interface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .evaluator import evaluate
from .exporters import EXPORTERS, export
from .loader import DutyMapError, load_duties


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="duty-map")
    commands = result.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="validate a duties file")
    check.add_argument("file")
    check.add_argument(
        "--allow-jurisdiction",
        action="append",
        dest="jurisdictions",
        help="replace the default jurisdiction allow-list (repeatable)",
    )
    apply = commands.add_parser("apply", help="evaluate duties for facts")
    apply.add_argument("file")
    apply.add_argument("--facts", default="", help="comma-separated atomic facts")
    apply.add_argument(
        "--allow-jurisdiction",
        action="append",
        dest="jurisdictions",
        help="replace the default jurisdiction allow-list (repeatable)",
    )
    export_command = commands.add_parser("export", help="export a duties file")
    export_command.add_argument("file")
    export_command.add_argument("--format", choices=tuple(EXPORTERS), required=True)
    export_command.add_argument("--output", help="write to a file instead of standard output")
    export_command.add_argument(
        "--allow-jurisdiction",
        action="append",
        dest="jurisdictions",
        help="replace the default jurisdiction allow-list (repeatable)",
    )
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        duty_map = load_duties(args.file, allowed_jurisdictions=args.jurisdictions)
    except DutyMapError as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 2
    if args.command == "check":
        print(f"valid: {len(duty_map.duties)} duties, {len(duty_map.rules)} rules")
        return 0

    if args.command == "export":
        rendered = export(duty_map, args.format)
        if args.output:
            try:
                Path(args.output).write_text(rendered, encoding="utf-8")
            except OSError as exc:
                print(f"cannot write export: {exc}", file=sys.stderr)
                return 2
        else:
            sys.stdout.write(rendered)
        return 0

    facts = tuple(item.strip() for item in args.facts.split(",") if item.strip())
    result = evaluate(duty_map, facts)
    by_id = {duty.id: duty for duty in duty_map.duties}
    output = []
    for duty_id in result.applicable_duties:
        duty = by_id[duty_id]
        output.append(
            {
                "id": duty.id,
                "label": duty.label,
                "why": [
                    {
                        "condition": condition,
                        "level": result.proof(condition).level.value,
                        "rule_chain": list(result.proof(condition).rule_chain),
                    }
                    for condition in duty.conditions
                ],
            }
        )
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
