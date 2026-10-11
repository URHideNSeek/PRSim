import ast
from pathlib import Path
import pytest
from experiment_intake import EXPERIMENTS,template,validate_csv,manifest

def test_eight_experiment_schemas():
    assert set(EXPERIMENTS)=={"E01","E02","E03","E04","E05","E06","E07","E08"}
    for key,(_,_,fields) in EXPERIMENTS.items():
        assert fields and len(fields)==len(set(fields))
        assert template(key).strip()==",".join(fields)

def test_all_experiment_uploads_and_manifest():
    for key,(_,_,fields) in EXPERIMENTS.items():
        values={field:("1" if field in ("target_present","available") else "2.5" if field in ("spacing_mm","reference_db_spl","measured_dbfs","range_m","rms_dbfs","center_frequency_hz","bandwidth_hz","noise_floor_dbm","frequency_hz","receiver_noise_dbm","sync_error_ns","clutter_cnr_db","ground_speed_mps","heading_relative_deg","altitude_m","wind_mps","rain_mm_per_hour","temperature_c","pressure_hpa","detector_score") else "test") for field in fields}
        text=",".join(fields)+"\n"+",".join(values[f] for f in fields)+"\n"
        rows=validate_csv(key,text)
        assert len(rows)==1
        assert manifest(key,rows,"example.csv")["experiment_id"]==key

def test_missing_columns_rejected():
    for key in EXPERIMENTS:
        with pytest.raises(ValueError):validate_csv(key,"wrong_column\nabc\n")

def test_pages_parse_and_navigation_is_consolidated():
    for path in ("pages/08_Research_Evidence.py","pages/01_Research_Validation.py"):
        ast.parse(Path(path).read_text(encoding="utf-8"))
    navigation=Path("app.py").read_text(encoding="utf-8")
    assert "08_Research_Evidence.py" in navigation
    assert "E01_Microphone_Characterization.py" in navigation
    assert "E08_Multisensor_Evaluation.py" in navigation
    assert "E11 · Motion Calibration" in navigation
    assert "E05 · DDL Acoustic Intake" in navigation
    assert "E06 · Acoustic Baseline" in navigation
    assert "References & Datasets" in navigation
    assert "05_Published_Datasets.py" not in navigation
    assert "03_Evidence_Calibration.py" not in navigation
    assert "02_Design_Space.py" not in navigation
