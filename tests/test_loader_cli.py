from pathlib import Path

import pytest

from duty_map import DutyMapError, load_duties
from duty_map.cli import main


BASE = """
superiority = []
[[duties]]
id = "d1"
label = "A made-up duty"
category = "other"
source = "Invented Policy 1"
pinpoint = "part 3"
jurisdiction = "{jurisdiction}"
summary = "Take the stated action."
conditions = ["ready"]
[duties.relations]
supports = []
attacks = []
exception_to = []
[[rules]]
id = "r1"
kind = "strict"
premises = ["start"]
conclusion = "ready"
"""


def write_map(tmp_path: Path, jurisdiction: str = "US") -> Path:
    path = tmp_path / "duties.toml"
    path.write_text(BASE.format(jurisdiction=jurisdiction), encoding="utf-8")
    return path


def test_default_jurisdictions_and_application(tmp_path, capsys):
    path = write_map(tmp_path)
    loaded = load_duties(path)
    assert loaded.duties[0].id == "d1"
    assert main(["check", str(path)]) == 0
    assert "valid: 1 duties, 1 rules" in capsys.readouterr().out
    assert main(["apply", str(path), "--facts", "start"]) == 0
    output = capsys.readouterr().out
    assert '"id": "d1"' in output
    assert '"rule_chain"' in output


def test_jurisdiction_rejected_by_default(tmp_path):
    path = write_map(tmp_path, "ZZ")
    with pytest.raises(DutyMapError, match="not allowed"):
        load_duties(path)


def test_jurisdiction_allow_list_is_configurable(tmp_path):
    path = write_map(tmp_path, "ZZ")
    assert load_duties(path, allowed_jurisdictions={"ZZ"}).duties[0].jurisdiction == "ZZ"
    assert main(["check", str(path), "--allow-jurisdiction", "ZZ"]) == 0


def test_empty_allow_list_is_rejected(tmp_path):
    with pytest.raises(DutyMapError, match="non-empty"):
        load_duties(write_map(tmp_path), allowed_jurisdictions=[])
