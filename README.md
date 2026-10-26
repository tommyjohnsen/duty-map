<!--
PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
written-by: unknown (pre-provenance) | 2026-10-16 | 552b829
modified-by: codex/gpt-5.6-sol | 2026-10-26 | 47cf23f | provenance block added
reviewed-by: claude-code/claude-opus-5-5 | 2026-10-26 | APPROVE
END PROVENANCE
-->
# duty-map

`duty-map` is a deterministic command-line tool for mapping duties, exceptions,
and priorities expressed in TOML. It validates a rule file, evaluates which
duties apply to supplied facts, and exports the map as Argdown, Mermaid, a rules
listing, or an IRAC/CREAC outline. It uses its own small defeasible evaluator;
no external reasoner, language model, or model API is used.

The rules shipped in this repository are synthetic examples. Write summaries in
your own words and include no quoted source text beyond short citations. Keep
real rule files outside this repository.

## Install

Python 3.11 or newer is required. From a local checkout, run:

```console
pip install .
```

## Usage

Validate a map, evaluate it against comma-separated facts, or export it:

```console
duty-map check examples/example-rules.toml
duty-map apply examples/example-rules.toml --facts member,has_card
duty-map export examples/example-rules.toml --format argdown
duty-map export examples/example-rules.toml --format mermaid --output policy.mmd
```

Export formats are `argdown`, `mermaid`, `rules`, `irac`, and `creac`. Argdown
and Mermaid are output formats, not dependencies. Without `--output`, an export
is written to standard output. `apply` writes JSON describing each applicable
duty and its rule chain.

The jurisdiction allow-list is configurable. It defaults to `US` and `US-WA`.
One or more repeated options replace that default for a command:

```console
duty-map check rules.toml --allow-jurisdiction US --allow-jurisdiction US-WA
```

Exit code `0` means the requested operation completed successfully. Exit code
`2` means command-line usage was invalid, the rule file failed validation or
loading, or an export could not be written.

### Short synthetic example

The fictional library map in `examples/example-rules.toml` says, in part, that
a member with a card may borrow an eligible item. To see the resulting duty:

```console
duty-map apply examples/example-rules.toml --facts member,has_card
```

Start a new map with `templates/rules-template.toml`. Rules may be `strict`,
`defeasible`, or `defeater`; `superiority` pairs identify which rule prevails
over another.

## Limits

- Results depend entirely on the completeness and accuracy of the supplied
  rules and facts; the tool does not research, interpret, or update sources.
- The evaluator handles the rule forms defined by this project, not every form
  of legal, policy, or argument reasoning.
- Exact atomic facts and explicit priorities drive evaluation; ambiguity and
  real-world judgment remain outside the program.

All output is a first pass and needs human verification before use.

## Dependencies and licenses

The installed program has no third-party runtime package dependencies. Python
and its standard library are distributed under the Python Software Foundation
License, a permissive license compatible with distributing this Apache-2.0
project. No external services are called and no data is fetched at runtime.

Development and build tooling is not installed as a runtime dependency:

- setuptools (MIT) is the build backend. Its permissive terms allow use and
  redistribution alongside Apache-2.0.
- pytest (MIT) runs the test suite. Its permissive terms allow development use
  alongside Apache-2.0.
- uv (Apache-2.0 and MIT) is used by the documented project test command. Both
  offered licenses are permissive and compatible with this Apache-2.0 project.

Argdown and Mermaid are independently available under the MIT License, but this
project neither bundles nor invokes them; it only emits their text formats.
Users who add external source material or connect downstream tools are
responsible for the applicable access, copyright, license, privacy, and service
terms. The repository's example sources and citations are invented.
