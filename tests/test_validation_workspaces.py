import ast
from pathlib import Path
from experiment_protocols import PROTOCOLS,EXTRA
from experiment_intake import EXPERIMENTS

def test_every_experiment_has_collection_protocol():
    assert set(PROTOCOLS)==set(EXPERIMENTS)
    assert set(EXTRA)=={"motion","ddl","baseline"}
    for protocol in list(PROTOCOLS.values())+list(EXTRA.values()):
        assert len(protocol)==5
        assert all(isinstance(field,str) and field.strip() for field in protocol)

def test_eight_tabs_and_unique_upload_keys():
    src=Path("pages/09_Experiment_Intake.py").read_text(encoding="utf-8")
    ast.parse(src)
    assert "st.tabs(" in src
    assert 'key="upload_"+selected' in src
    assert 'key="template_"+selected' in src
    assert "sensor_rows" in src

def test_measured_evidence_cannot_replace_synthetic_probabilities():
    src=Path("PRSim.py").read_text(encoding="utf-8")
    ast.parse(src)
    assert 'shared = scenario_probabilities(scenario,threshold)' in src
    assert 'st.session_state.get("validation_e08")' in src
    assert "Actual-data adjustment to main-page Pd: none." in src

def test_specialized_pages_have_protocols():
    for path in ("pages/04_Motion_Calibration.py","pages/06_DDL_Acoustic_Intake.py","pages/07_Acoustic_Baseline.py"):
        src=Path(path).read_text(encoding="utf-8")
        ast.parse(src)
        assert "from experiment_protocols import EXTRA" in src
        assert "Main-page probability impact:" in src
