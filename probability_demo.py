"""Illustrative detection-probability mapping for UI demonstration only.

Assumes target-absent evidence is N(0,1), target-present evidence is N(mu,1),
with mu=3*normalized evidence. At a fixed one-sided 5% false-alarm threshold,
the resulting analytic tail probability is a SYNTHETIC demonstration, not a
calibrated detector or a probability inferred from radar/acoustic physics.
"""
import math

FALSE_ALARM_RATE = 0.05
THRESHOLD_Z = 1.6448536269514722
SYNTHETIC_SHIFT_SCALE = 3.0

def synthetic_detection_probability(evidence, enabled=True):
    if not enabled:
        return None
    if not 0 <= evidence <= 1:
        raise ValueError("Evidence must be in [0, 1]")
    mu = SYNTHETIC_SHIFT_SCALE * evidence
    return 0.5 * math.erfc((THRESHOLD_Z - mu) / math.sqrt(2))
