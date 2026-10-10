"""Target distance input acceptance tests, using the same Scenario model as the UI."""
from dataclasses import replace
import pytest
from model import Scenario, evaluate

DISTANCES = list(range(50,3001,50))

def test_distance_selector_values():
    assert len(DISTANCES)==60
    assert DISTANCES[0]==50 and DISTANCES[-1]==3000
    assert all(b-a==50 for a,b in zip(DISTANCES,DISTANCES[1:]))

@pytest.mark.parametrize("weather",["Clear","Cloud (aircraft inside)","Light rain","Heavy rain","Snow","High wind"])
@pytest.mark.parametrize("rcs",["Small","Medium","Large"])
def test_all_50m_steps_nonincreasing_evidence(weather,rcs):
    baseline=Scenario(weather=weather,rcs=rcs,emits=True)
    outputs=[evaluate(replace(baseline,range_m=d)) for d in DISTANCES]
    for name in ["radar","rf","acoustic","fused"]:
        assert all(b[name]<=a[name]+1e-12 for a,b in zip(outputs,outputs[1:])), (weather,rcs,name)
    assert all(isinstance(out["detected"],bool) for out in outputs)

def test_distance_changes_finding_with_researcher_threshold():
    scenario=Scenario(weather="Clear",rcs="Large",emits=True,threshold=.20)
    near=evaluate(replace(scenario,range_m=50))
    far=evaluate(replace(scenario,range_m=3000))
    assert near["fused"]>far["fused"]
    assert near["detected"] and not far["detected"]

def test_distance_with_all_sensors_off():
    scenario=Scenario(radar_on=False,rf_on=False,acoustic_on=False)
    for d in DISTANCES:
        out=evaluate(replace(scenario,range_m=d))
        assert out["fused"]==0 and not out["detected"]

def test_distance_and_rf_off():
    scenario=Scenario(emits=False)
    for d in DISTANCES:
        assert evaluate(replace(scenario,range_m=d))["rf"]==0
