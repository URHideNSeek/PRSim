"""Every user-selectable main model parameter has an explicit behavior test.

Tests use synthetic settings chosen away from clipping and compare raw model
outputs. They do not establish physical correctness or live browser behavior.
"""
from dataclasses import replace
import pytest
from model import Scenario,evaluate
from shared_probability import scenario_probabilities

BASE=Scenario(range_m=150,rcs_m2=.1,weather="Clear",clutter=0,
              threshold=.3,fail=.05,emits=True,radar_on=True,rf_on=True,
              acoustic_on=True)

# Parameter -> changed value -> expected observable
CASES=[
 ("weather","Heavy rain","radar"),
 ("rcs_m2",.8,"radar"),
 ("clutter_cnr_db",15.,"radar"),
 ("emits",False,"rf"),
 ("audio",20,"acoustic"),
 ("range_m",450,"radar"),
 ("observation",30,"latency"),
 ("update",3.,"latency"),
 ("fusion_weight",.1,"fused"),
 ("fail",.4,"availability"),
 ("radar_on",False,"radar"),
 ("illumination",.2,"radar"),
 ("reference",.2,"radar"),
 ("sync_error",.7,"radar"),
 ("clutter",.8,"radar"),
 ("radar_noise",.8,"radar"),
 ("bandwidth",.2,"radar"),
 ("rf_on",False,"rf"),
 ("rf_sensitivity",.2,"rf"),
 ("rf_interference",.8,"rf"),
 ("rf_coverage",.2,"rf"),
 ("rf_noise",.8,"rf"),
 ("acoustic_on",False,"acoustic"),
 ("microphone_quality",.2,"acoustic"),
 ("mic_spacing",.0254,"acoustic"),
 ("audio_noise",.8,"acoustic"),
 ("wind_noise",.8,"acoustic"),
 ("channel_sync",.2,"acoustic"),
]

def observable(out,key):
    if key=="latency":return out["fused_metrics"]["Latency proxy (s)"]
    if key=="availability":return out["fused_metrics"]["Availability index (0–1)"]
    return out[key]

@pytest.mark.parametrize("field,value,output",CASES)
def test_every_live_input_changes_expected_output(field,value,output):
    baseline=evaluate(BASE)
    modified=evaluate(replace(BASE,**{field:value}))
    assert observable(modified,output)!=pytest.approx(observable(baseline,output),abs=1e-8),field

@pytest.mark.parametrize("field,value",[
    ("speed_mps",20),("heading_deg",180)
])
def test_motion_inputs_change_geometry_not_synthetic_pd(field,value):
    scenario=replace(BASE,speed_mps=10,heading_deg=90)
    changed=replace(scenario,**{field:value})
    a=evaluate(scenario)
    b=evaluate(changed)
    assert a["motion"]["radial_speed_mps"]!=pytest.approx(b["motion"]["radial_speed_mps"])
    assert scenario_probabilities(scenario,.3)["fused_pd"]==scenario_probabilities(changed,.3)["fused_pd"]

def test_threshold_changes_decision_and_probability():
    low=scenario_probabilities(BASE,.05)
    high=scenario_probabilities(BASE,.95)
    assert low["fused_pd"]>high["fused_pd"]
    assert low["false_alarm_probability"]>high["false_alarm_probability"]
    assert low["evidence"]["detected"] and not high["evidence"]["detected"]

def test_disabled_modes_have_zero_evidence():
    for field,key in (("radar_on","radar"),("rf_on","rf"),("acoustic_on","acoustic")):
        assert evaluate(replace(BASE,**{field:False}))[key]==0
