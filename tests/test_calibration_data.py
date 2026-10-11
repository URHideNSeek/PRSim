import io
from calibration_data import validate_rows,read_csv

def test_valid_minimal_multisession_dataset():
    rows=[
        dict(measured_doppler_hz="12",target_present="1",detector_score=".8",session_id="A"),
        dict(measured_doppler_hz="0",target_present="0",detector_score=".2",session_id="B"),
    ]
    r=validate_rows(rows)
    assert r.valid and r.target_present==1 and r.target_absent==1 and r.sessions==2

def test_missing_target_absent_rejected():
    rows=[dict(measured_doppler_hz="12",target_present="1",detector_score=".8",session_id="A")]
    assert not validate_rows(rows).valid

def test_single_session_rejected():
    rows=[
        dict(measured_doppler_hz="12",target_present="1",detector_score=".8",session_id="A"),
        dict(measured_doppler_hz="0",target_present="0",detector_score=".2",session_id="A")]
    assert not validate_rows(rows).valid

def test_bad_numeric_rejected():
    rows=[
        dict(measured_doppler_hz="nan",target_present="1",detector_score=".8",session_id="A"),
        dict(measured_doppler_hz="0",target_present="0",detector_score=".2",session_id="B")]
    assert not validate_rows(rows).valid

def test_csv_reader():
    raw=io.StringIO("measured_doppler_hz,target_present,detector_score,session_id\n12,1,.8,A\n0,0,.2,B\n")
    assert read_csv(raw).valid
