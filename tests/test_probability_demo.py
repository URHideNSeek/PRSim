import pytest
from probability_demo import synthetic_detection_probability, synthetic_false_alarm_probability

def test_no_signal_matches_false_alarm_rate():
    for threshold in [.05,.3,.6,.95]:
        assert synthetic_detection_probability(0,threshold)==pytest.approx(synthetic_false_alarm_probability(threshold),abs=1e-12)

def test_evidence_increases_detection_probability():
    for threshold in [.05,.3,.6,.95]:
        values=[synthetic_detection_probability(i/100,threshold) for i in range(101)]
        assert all(0<=p<=1 for p in values)
        assert all(a<b for a,b in zip(values,values[1:]))

def test_higher_threshold_reduces_pd_and_false_alarms():
    for score in [.19,.30,.34,.8]:
        assert synthetic_detection_probability(score,.1)>synthetic_detection_probability(score,.3)>synthetic_detection_probability(score,.9)
    assert synthetic_false_alarm_probability(.1)>synthetic_false_alarm_probability(.3)>synthetic_false_alarm_probability(.9)

def test_disabled_modality_is_not_available():
    assert synthetic_detection_probability(.5,threshold=.3,enabled=False) is None

@pytest.mark.parametrize("score",[-.01,1.01])
def test_invalid_evidence_rejected(score):
    with pytest.raises(ValueError):synthetic_detection_probability(score)

@pytest.mark.parametrize("threshold",[-.01,1.01])
def test_invalid_threshold_rejected(threshold):
    with pytest.raises(ValueError):synthetic_detection_probability(.5,threshold)
    with pytest.raises(ValueError):synthetic_false_alarm_probability(threshold)

def test_ui_uses_shared_threshold():
    from pathlib import Path
    src=Path("PRSim.py").read_text(encoding="utf-8")
    assert "synthetic_detection_probability(score, threshold=threshold, enabled=enabled)" in src
    assert "synthetic_false_alarm_probability(threshold)" in src
