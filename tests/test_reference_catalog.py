import ast
from pathlib import Path
from reference_catalog import REFERENCES

def test_reference_catalog_provenance():
    assert len(REFERENCES)>=8
    assert len({r["title"] for r in REFERENCES})==len(REFERENCES)
    for r in REFERENCES:
        assert r["url"].startswith("https://")
        assert r["status"] and r["location"] and r["limitation"]
    assert any("not imported" in r["status"].lower() for r in REFERENCES)
    assert any("implemented" in r["status"].lower() for r in REFERENCES)

def test_reference_page_and_intake_parse():
    for path in ("pages/08_Research_Evidence.py","pages/09_Experiment_Intake.py"):
        ast.parse(Path(path).read_text(encoding="utf-8"))
    references=Path("pages/08_Research_Evidence.py").read_text(encoding="utf-8")
    intake=Path("pages/09_Experiment_Intake.py").read_text(encoding="utf-8")
    assert "from reference_catalog import REFERENCES" in references
    assert "EXPERIMENTS" not in references
    assert "from experiment_intake import EXPERIMENTS" in intake
