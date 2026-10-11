"""One synthetic probability contract shared by PRSim and Design Space.

The normalized evidence scores come from model.evaluate. An illustrative
Gaussian-score assumption and explicit modality availability produce per-
opportunity probabilities. Fused availability is the model's own heuristic
availability index; no empirical joint detector is claimed.
"""
from dataclasses import replace
from model import Scenario,evaluate
from probability_demo import availability_adjusted_probability,availability_adjusted_false_alarm_probability

def scenario_probabilities(scenario:Scenario,threshold:float):
    if not 0<=threshold<=1:raise ValueError("Threshold outside [0,1]")
    out=evaluate(replace(scenario,threshold=threshold))
    common=1-scenario.fail
    radar_av=scenario.illumination*common if scenario.radar_on else 0
    rf_enabled=scenario.rf_on and scenario.emits
    acoustic_enabled=scenario.acoustic_on
    fused_av=out["fused_metrics"]["Availability index (0–1)"]
    # Avoid rounding-derived drift: the model's availability metric is rounded
    # to 3 decimals; this is the same published value used by both pages.
    result={
        "radar_pd":availability_adjusted_probability(out["radar"],threshold,radar_av,scenario.radar_on),
        "rf_pd":availability_adjusted_probability(out["rf"],threshold,common,rf_enabled),
        "acoustic_pd":availability_adjusted_probability(out["acoustic"],threshold,common,acoustic_enabled),
        "fused_pd":availability_adjusted_probability(out["fused"],threshold,fused_av,radar_av>0 or rf_enabled or acoustic_enabled),
        "false_alarm_probability":availability_adjusted_false_alarm_probability(threshold,common),
        "fused_availability":fused_av,
        "evidence":out,
        "threshold":threshold,
        "model_status":"illustrative Gaussian; fused score and availability are heuristic; not calibrated",
    }
    return result
