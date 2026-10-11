"""Illustrative Gaussian score distributions, NOT calibrated sensor performance.

Both target-present and target-absent scores are modeled with standard deviation
0.20 on the same normalized evidence scale used by the dashboard threshold.
Background mean = 0; target-present mean = the current modality evidence.
No fitted distributions, real-world detection rates, or ROC calibration implied.
"""
import math

SYNTHETIC_SCORE_SIGMA = 0.20

def _survival(threshold, mean):
    return 0.5 * math.erfc((threshold - mean) / (SYNTHETIC_SCORE_SIGMA * math.sqrt(2)))

def synthetic_detection_probability(evidence, threshold=0.30, enabled=True):
    if not enabled:
        return None
    if not 0 <= evidence <= 1:
        raise ValueError("Evidence must be in [0, 1]")
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be in [0, 1]")
    return _survival(threshold, evidence)

def synthetic_false_alarm_probability(threshold=0.30):
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be in [0, 1]")
    return _survival(threshold, 0.0)
