# Provenance

Generated from `.provenance/ledger.jsonl` by the operator tool; do not edit by hand. The ledger is the record of truth; per-file `PROVENANCE` headers mirror it, and the ledger wins on any disagreement.

Each ledger line is one JSON object with `path`, `blob`, `event` (`written` or `reviewed`), `by` (seat/model, or `unknown (pre-provenance)` for history whose author is not recorded), `date`, and either `commit` (written) or `verdict`, `head` and `record` (reviewed). Verdicts are `APPROVE`, `APPROVE_WITH_NITS` or `REJECT`.

`blob` is the git blob SHA-1 of the file after removing its PROVENANCE header block: the lines from the `PROVENANCE` line through the `END PROVENANCE` line inclusive, plus a directly enclosing `<!--` / `-->` line pair. A review applies only while the file's current `blob` equals the reviewed one; any content change makes it stale. A release needs current reviews from claude-code and grok-build; an author never reviews its own work.

Files tracked: 23 (excluding this summary and `.provenance/`). Inline headers: 16. Ledger-only: 7. Written entries current: 23/23. Current reviews: claude-code 21, grok-build 21. Current REJECTs: 0.

| path | header | written-by (current content) | claude-code | grok-build |
|---|---|---|---|---|
| `.github/workflows/test.yml` | inline | unknown (pre-provenance) | APPROVE | APPROVE |
| `.gitignore` | inline | unknown (pre-provenance) | APPROVE | APPROVE |
| `LICENSE` | ledger | unknown (pre-provenance) | APPROVE | APPROVE |
| `NOTICE` | ledger | unknown (pre-provenance) | APPROVE | APPROVE |
| `README.md` | inline | unknown (pre-provenance) | APPROVE | APPROVE |
| `SPEC.md` | inline | unknown (pre-provenance) | APPROVE | APPROVE |
| `examples/example-rules.toml` | inline | unknown (pre-provenance) | APPROVE | APPROVE |
| `pyproject.toml` | inline | unknown (pre-provenance) | APPROVE | APPROVE |
| `src/duty_map/__init__.py` | inline | unknown (pre-provenance) | APPROVE | APPROVE |
| `src/duty_map/__main__.py` | inline | unknown (pre-provenance) | APPROVE | APPROVE |
| `src/duty_map/cli.py` | inline | unknown (pre-provenance) | APPROVE | APPROVE |
| `src/duty_map/evaluator.py` | inline | codex/gpt-5.6-sol | - | - |
| `src/duty_map/exporters.py` | inline | unknown (pre-provenance) | APPROVE_WITH_NITS | APPROVE_WITH_NITS |
| `src/duty_map/loader.py` | inline | unknown (pre-provenance) | APPROVE | APPROVE |
| `templates/rules-template.toml` | inline | unknown (pre-provenance) | APPROVE | APPROVE |
| `tests/golden/sample.argdown` | ledger | unknown (pre-provenance) | APPROVE_WITH_NITS | APPROVE_WITH_NITS |
| `tests/golden/sample.creac` | ledger | unknown (pre-provenance) | APPROVE | APPROVE |
| `tests/golden/sample.irac` | ledger | unknown (pre-provenance) | APPROVE | APPROVE |
| `tests/golden/sample.mermaid` | ledger | unknown (pre-provenance) | APPROVE | APPROVE |
| `tests/golden/sample.rules` | ledger | unknown (pre-provenance) | APPROVE | APPROVE |
| `tests/test_evaluator.py` | inline | codex/gpt-5.6-sol | - | - |
| `tests/test_exporters.py` | inline | unknown (pre-provenance) | APPROVE | APPROVE |
| `tests/test_loader_cli.py` | inline | unknown (pre-provenance) | APPROVE | APPROVE |
