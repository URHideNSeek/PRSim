import ast
from pathlib import Path

def test_calibration_page_parses():
    ast.parse(Path("pages/03_Evidence_Calibration.py").read_text(encoding="utf-8"))

def test_provenance_and_units_present():
    source=Path("pages/03_Evidence_Calibration.py").read_text(encoding="utf-8")
    for term in ["P.838-3","P.676-13","mm/h","GHz","hPa","g/m³","Not implemented","not yet integrated"]:
        assert term in source
