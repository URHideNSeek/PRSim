"""Explicit audit of the main PRSim input-to-output contract.

Every Scenario field is classified as a live model input, a decision-only input,
or metadata awaiting physics. The audit deliberately fails if a field is added
without classification. This is NOT empirical validation of sensor performance.
"""
from dataclasses import fields, replace
from model import Scenario, evaluate
from probability_demo import synthetic_detection_probability, synthetic_false_alarm_probability

LIVE = {
    "weather","rcs","rcs_m2","clutter_cnr_db","emits","audio","range_m",
    "observation","update","fusion_weight","fail","radar_on","illumination",
    "reference","sync_error","clutter","radar_noise","bandwidth","rf_on",
    "rf_sensitivity","rf_interference","rf_coverage","rf_noise","acoustic_on",
    "microphone_quality","mic_spacing","audio_noise","wind_noise","channel_sync"
}
DECISION_ONLY = {"threshold"}
UNMODELED = {"speed_mps","heading_deg"}

def test_every_scenario_field_has_explicit_status():
    names={field.name for field in fields(Scenario)}
    assert names==LIVE|DECISION_ONLY|UNMODELED
    assert not (LIVE&DECISION_ONLY or LIVE&UNMODELED or DECISION_ONLY&UNMODELED)

def test_ground_speed_and_heading_are_not_claimed_as_probability_drivers():
    baseline=Scenario(rcs_m2=.1)
    ref=evaluate(baseline)
    for speed in range(0,51):
        for heading in range(0,346,15):
            result=evaluate(replace(baseline,speed_mps=speed,heading_deg=heading))
            assert result["motion"]["speed_mps"]==speed
            assert result["motion"]["heading_deg"]==heading
            assert result["motion"]["model_status"]=="not calibrated"
            for key in ("radar","rf","acoustic","fused"):
                assert result[key]==ref[key],(speed,heading,key)
            for key in ("radar","rf","acoustic"):
                assert synthetic_detection_probability(result[key],.3)==synthetic_detection_probability(ref[key],.3)

def test_probability_outputs_follow_live_sensor_scores_and_threshold():
    baseline=Scenario(rcs_m2=.1)
    scenarios=[
        baseline,
        replace(baseline,rcs_m2=1),
        replace(baseline,clutter_cnr_db=30),
        replace(baseline,emits=False),
        replace(baseline,audio=75),
        replace(baseline,range_m=500),
        replace(baseline,weather="Heavy rain"),
    ]
    for scenario in scenarios:
        out=evaluate(scenario)
        for key in ("radar","rf","acoustic"):
            assert 0<=synthetic_detection_probability(out[key],.3)<=1
    for score in (.1,.3,.8):
        assert synthetic_detection_probability(score,.1)>synthetic_detection_probability(score,.9)
    assert synthetic_false_alarm_probability(.1)>synthetic_false_alarm_probability(.9)

def test_disabled_modalities_have_no_evidence():
    for name,key in (("radar_on","radar"),("rf_on","rf"),("acoustic_on","acoustic")):
        assert evaluate(replace(Scenario(),**{name:False}))[key]==0
    assert evaluate(Scenario(emits=False))["rf"]==0
