<!--
PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
written-by: unknown (pre-provenance) | 2026-10-16 | 552b829
modified-by: codex/gpt-5.6-sol | 2026-10-26 | 47cf23f | provenance block added
reviewed-by: claude-code/claude-opus-5-5 | 2026-10-26 | APPROVE
END PROVENANCE
-->
# duty-map: spec

Stdlib-only Python engine that turns a rules file (duties, exceptions, overrides) for any rulebook or policy into Argdown, Mermaid and defeasible rules, and answers which duties apply to a scenario.

## Input
- A duties file in TOML (stdlib `tomllib`). Each duty: id, label, category (competence, confidentiality, communication, fees, supervision, candor, other), source (short cite only), pinpoint, jurisdiction (validated against a configurable allowed list; the shipped default allows `US` and `US-WA`), a summary in the user's own words, conditions (facts), and relations (supports, attacks, exception_to).
- Rules: strict, defeasible and defeater rules over atomic facts, plus a superiority relation.

## Engine (module `duty_map`, console script `duty-map`)
- A small built-in defeasible evaluator (no Carneades, no SPINdle, no external reasoner): strict rules, defeasible rules, defeaters, superiority, conflicting conclusions resolved by superiority; reports definitely provable, defeasibly provable, and not provable, with the rule chain for each.
- `duty-map check FILE` validates the file. `duty-map apply FILE --facts a,b,c` lists the duties that apply and why.
- Exports: Argdown (`.argdown`), Mermaid flowchart (`.mmd`), a rules listing, and an IRAC/CREAC outline (Markdown). The Argdown CLI (MIT) and Mermaid (MIT) are not dependencies; the tool only writes their text formats.

## Content rule
- The repo ships only `examples/example-rules.toml`: a neutral, made-up ruleset (a fictional community library borrowing policy) with invented sources, plus an empty template. No real rule, policy or opinion text of any kind goes in the repo; users keep real rule files outside the repo.

## Rules for all parts
- Deterministic only: rule-based parsing and exact or fuzzy matching against authoritative sources. No LLM or model makes any pass/fail call, and nothing calls a model API at runtime. Output is a first pass that a human verifies.
- License Apache-2.0 (LICENSE and NOTICE are already here; keep them as they are). pyproject.toml: `license = "Apache-2.0"`, requires-python >=3.11.
- Tests use pytest and must pass with this exact command run from this directory (network is off; the uv cache is pre-warmed):
  `UV_OFFLINE=1 UV_CACHE_DIR=$UVC uv run --no-project --with pytest pytest -q`
  where $UVC is the pre-warmed cache path given in the job prompt. Put `[tool.pytest.ini_options]` with `pythonpath = ["src"]` and `testpaths = ["tests"]` in pyproject.toml. Use a src/ layout.
- All network access in tests is mocked (unittest.mock on the stdlib HTTP layer). No live calls in tests or CI.
- Synthetic fixtures only (synthetic citations and DOIs; no real drafts or notes). No hostnames other than the public API hosts named here, no IPs, local paths, usernames, real emails (use `you@example.com`; contact email only from env `CONTACT_EMAIL` or a config file, never hardcoded), account details, real data or secrets.
- Tokens and contact emails come only from environment variables read at runtime. Never print, log, cache or write their values.
- The README must state that all output needs human verification before use.
- Do not copy text from The Bluebook or any licensed or library source. Do not bundle CSL styles.
- Work only inside this directory. Do not read or copy anything from other directories.
