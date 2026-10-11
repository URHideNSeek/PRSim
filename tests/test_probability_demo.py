import math
import pytest
from probability_demo import synthetic_detection_probability, FALSE_ALARM_RATE

def test_no_signal_matches_false_alarm_rate():
    assert synthetic_detection_probability(0)==pytest.approx(FALSE_ALARM_RATE,abs=1e-10)

def test_probability_monotonic_and_bounded():
    values=[synthetic_detection_probability(i/100) for i in range(101)]
    assert all(0<=p<=1 for p in values)
    assert all(a<b for a,b in zip(values,values[1:]))

def test_disabled_modality_is_not_available():
    assert synthetic_detection_probability(0.5,enabled=False) is None

@pytest.mark.parametrize("score",[-.01,1.01])
def test_invalid_evidence_rejected(score):
    with pytest.raises(ValueError):synthetic_detection_probability(score)

def test_illustrative_examples():
    for score in [.19,.30,.34]:
        assert 0<synthetic_detection_probability(score)<1
