import pytest
from probability_demo import synthetic_detection_probability, synthetic_false_alarm_probability, availability_adjusted_probability, availability_adjusted_false_alarm_probability

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
    assert "availability_adjusted_probability(score, threshold=threshold, availability=availability, enabled=enabled)" in src
    assert "availability_adjusted_false_alarm_probability(threshold,availability=1-fail)" in src

def test_outage_reduces_unconditional_probability():
    for score in [.1,.3,.8]:
        assert availability_adjusted_probability(score,.3,1.0)>availability_adjusted_probability(score,.3,.5)>availability_adjusted_probability(score,.3,0.0)
    assert availability_adjusted_false_alarm_probability(.3,0.0)==0

def test_zero_illuminator_availability_means_no_radar_detection_opportunity():
    assert availability_adjusted_probability(.4,.3,0.0)==0

def test_invalid_availability_rejected():
    for bad in [-.1,1.1]:
        with pytest.raises(ValueError):availability_adjusted_probability(.5,.3,bad)
