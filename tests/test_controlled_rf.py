import pytest
from controlled_rf import parse_controlled_rf, baseline_summary, REQUIRED

def csv_for(n, condition="baseline", model="Keysight E8267D Option 520", freq=1000000000):
    h=",".join(REQUIRED)
    rows=[f"2026-10-10T00:00:{i%60:02d}Z,s1,{model},{freq},1000000,-40,5,{condition}" for i in range(n)]
    return h+"\n"+"\n".join(rows)+"\n"

def test_parse_valid():
    assert len(parse_controlled_rf(csv_for(2))) == 2

def test_no_records():
    with pytest.raises(ValueError,match="No measurement"):parse_controlled_rf(",".join(REQUIRED)+"\n")

def test_missing_column():
    with pytest.raises(ValueError,match="Missing columns"):parse_controlled_rf("timestamp_utc\na\n")

def test_nonfinite_rejected():
    with pytest.raises(ValueError,match="Non-finite"):parse_controlled_rf(csv_for(1).replace(",-40,",",nan,"))

def test_option_520_limit():
    with pytest.raises(ValueError,match="Option 520"):parse_controlled_rf(csv_for(1,freq=21000000000))

def test_invalid_condition():
    with pytest.raises(ValueError,match="Invalid condition"):parse_controlled_rf(csv_for(1,condition="unknown"))

def test_baseline_gate_not_calibration():
    summary=baseline_summary(parse_controlled_rf(csv_for(30)))
    assert summary["minimum_sample_count_met"]
    assert summary["baseline_samples"] == 30
    assert "NOT proof" in summary["note"]

def test_changed_samples_do_not_count_as_baseline():
    assert baseline_summary(parse_controlled_rf(csv_for(31,"changed")))["baseline_samples"] == 0
