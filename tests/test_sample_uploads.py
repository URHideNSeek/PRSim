"""End-to-end sample ingestion smoke tests for all eleven validation workspaces.

Tests use generated synthetic files and the actual application parsing
functions. They do not assert real sensor performance or browser uploads.
"""
import csv
import io
import zipfile
from pathlib import Path
import pytest
from scripts.generate_sample_uploads import generate
from experiment_intake import EXPERIMENTS,validate_csv,manifest
from calibration_data import validate_rows
from ddl_acoustic import parse_zip_manifest,coverage
from audio_features import wav_features
from acoustic_baseline import parse_feature_csv,evaluate_acoustic_baseline
from dataset_validation import evaluate_holdout

@pytest.fixture(scope="module")
def samples(tmp_path_factory):
    return generate(tmp_path_factory.mktemp("prsim_uploads"))

@pytest.mark.parametrize("experiment",list(EXPERIMENTS))
def test_each_experiment_csv_upload_and_manifest(samples,experiment):
    path=samples/(experiment+"_sample.csv")
    data=path.read_text(encoding="utf-8")
    rows=validate_csv(experiment,data)
    assert rows and len(rows)>=4
    assert manifest(experiment,rows,path.name)["records"]==len(rows)
    assert set(EXPERIMENTS[experiment][2]).issubset(rows[0])
    with pytest.raises(ValueError):
        validate_csv(experiment,"bad_header\nnot_valid\n")

def test_e08_real_evaluation_code_with_synthetic_fixture(samples):
    rows=validate_csv("E08",(samples/"E08_sample.csv").read_text())
    scores=[(r["session_id"],int(r["target_present"]),float(r["detector_score"]))
            for r in rows if r["available"]=="1" and r["sensor_id"]=="SENSOR_A"]
    result=evaluate_holdout(scores,.05,"holdout")
    assert result["holdout_targets"]>0
    assert result["holdout_background"]>0
    assert 0<=result["holdout_pd"]<=1
    assert 0<=result["holdout_pfa"]<=1

def test_e09_motion_csv_upload(samples):
    with (samples/"E09_motion_sample.csv").open() as handle:
        report=validate_rows(list(csv.DictReader(handle)))
    assert report.valid and report.sessions==2
    assert report.target_present>0 and report.target_absent>0

def test_e10_ddl_zip_and_wav_processing(samples):
    with (samples/"E10_DDL_sample.zip").open("rb") as handle:
        rows,rejected=parse_zip_manifest(handle)
    assert len(rows)==4 and not rejected
    assert coverage(rows)["ready_for_holdout"]
    with zipfile.ZipFile(samples/"E10_DDL_sample.zip") as archive:
        result=wav_features(archive.read(archive.namelist()[0]))
    assert result["sample_rate_hz"]==16000
    assert result["duration_s"]==pytest.approx(1.0)

def test_e11_acoustic_baseline_csv_upload(samples):
    rows=parse_feature_csv((samples/"E11_acoustic_baseline_sample.csv").read_text())
    result=evaluate_acoustic_baseline(rows,"holdout",.05)
    assert result["train_background_count"]>=20
    assert result["holdout_target_count"]>=5
    assert 0<=result["holdout_pd"]<=1

def test_all_page_entrypoints_compile():
    import ast
    root=Path(__file__).resolve().parents[1]
    for key in EXPERIMENTS:
        paths=list((root/"pages").glob(key+"_*.py"))
        assert len(paths)==1
        ast.parse(paths[0].read_text())
    for name in ("04_Motion_Calibration.py","06_DDL_Acoustic_Intake.py","07_Acoustic_Baseline.py"):
        ast.parse((root/"pages"/name).read_text())
    ast.parse((root/"experiment_pages.py").read_text())
