"""Cross-page probability parity regression tests.

Both pages must use scenario_probabilities. The optimizer must reproduce the
same value for an identical scenario, rather than fitting a separate detector.
"""
from dataclasses import replace
from pathlib import Path
import pytest
from model import Scenario,WEATHER
from shared_probability import scenario_probabilities
from optimization import evaluate

@pytest.mark.parametrize("threshold",[.1,.3,.35,.6,.9])
@pytest.mark.parametrize("weather",list(WEATHER))
@pytest.mark.parametrize("emits",[False,True])
def test_same_scenario_produces_identical_probabilities(threshold,weather,emits):
    s=Scenario(weather=weather,emits=emits,rcs_m2=.1,range_m=250,
               reference=.8,rf_sensitivity=.6,microphone_quality=.9,
               fusion_weight=.2,clutter=0.)
    main=scenario_probabilities(s,threshold)
    design=scenario_probabilities(replace(s),threshold)
    for field in ("radar_pd","rf_pd","acoustic_pd","fused_pd",
                  "false_alarm_probability","fused_availability"):
        assert main[field]==design[field]

def test_design_space_candidate_equals_mean_of_main_page_scenarios():
    threshold=.35
    df=evaluate(radar_levels=(.8,),rf_levels=(.6,),audio_levels=(.9,),
                threshold=threshold)
    row=df[df.fusion_weight==.2].iloc[0]
    outputs=[]
    for weather in WEATHER:
        for emits in (False,True):
            s=Scenario(weather=weather,emits=emits,rcs_m2=.1,range_m=250,
                reference=.8,rf_sensitivity=.6,microphone_quality=.9,
                fusion_weight=.2,clutter=0.)
            outputs.append(scenario_probabilities(s,threshold))
    assert row.synthetic_pd==pytest.approx(sum(o["fused_pd"] for o in outputs)/len(outputs),abs=1e-12)
    assert row.empirical_pfa==pytest.approx(sum(o["false_alarm_probability"] for o in outputs)/len(outputs),abs=1e-12)

def test_both_pages_call_same_shared_engine():
    assert "scenario_probabilities(scenario,threshold)" in Path("PRSim.py").read_text()
    assert "scenario_probabilities(s,threshold)" in Path("optimization.py").read_text()
    assert "from shared_probability import scenario_probabilities" in Path("PRSim.py").read_text()
    assert "from shared_probability import scenario_probabilities" in Path("optimization.py").read_text()
