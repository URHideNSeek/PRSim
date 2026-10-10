"""Exhaustive direction/behavior contract for every selectable scenario input."""
from dataclasses import fields, replace
import pytest
from model import Scenario, evaluate, WEATHER, SIZE

BASE=Scenario(weather="Clear",emits=True,radar_on=True,rf_on=True,acoustic_on=True)
# Each pair varies exactly one control and asserts expected synthetic response.
CASES=[
 ("weather","Clear","Heavy rain","fused","down"),
 ("rcs","Small","Large","radar","up"),
 ("rcs_m2",0.05,1.0,"radar","up"),
 ("clutter_cnr_db",-20,40,"radar","down"),
 ("emits",False,True,"rf","up"),
 ("audio",45,75,"acoustic","up"),
 ("range_m",100,1500,"fused","down"),
 ("speed_mps",0,50,"motion.speed_mps","up"),
 ("heading_deg",0,360,"motion.heading_deg","up"),
 ("observation",1,60,"fused_metrics.Latency proxy (s)","up"),
 ("update",.1,5.,"fused_metrics.Latency proxy (s)","up"),
 ("fusion_weight",0.,1.,"fused","up"),
 ("fail",0.,.5,"fused_metrics.Availability index (0–1)","down"),
 ("radar_on",False,True,"radar","up"),
 ("illumination",0.,1.,"radar","up"),
 ("reference",0.,1.,"radar","up"),
 ("sync_error",0.,1.,"radar","down"),
 ("clutter",0.,1.,"radar","down"),
 ("radar_noise",0.,1.,"radar","down"),
 ("bandwidth",.1,1.,"radar","up"),
 ("rf_on",False,True,"rf","up"),
 ("rf_sensitivity",0.,1.,"rf","up"),
 ("rf_interference",0.,1.,"rf","down"),
 ("rf_coverage",0.,1.,"rf","up"),
 ("rf_noise",0.,1.,"rf","down"),
 ("acoustic_on",False,True,"acoustic","up"),
 ("microphone_quality",0.,1.,"acoustic","up"),
 ("mic_spacing",.05,1.5,"acoustic","up"),
 ("audio_noise",0.,1.,"acoustic","down"),
 ("wind_noise",0.,1.,"acoustic","down"),
 ("channel_sync",0.,1.,"acoustic","up"),
 ("threshold",.05,.95,"detected","nonincrease"),
]
def get(out,path):
    for key in path.split("."):out=out[key]
    return out
@pytest.mark.parametrize("name,low,high,output,direction",CASES,ids=[x[0] for x in CASES])
def test_every_selectable_control(name,low,high,output,direction):
    a=get(evaluate(replace(BASE,**{name:low})),output)
    b=get(evaluate(replace(BASE,**{name:high})),output)
    if direction=="up":assert b>a,(name,a,b)
    elif direction=="down":assert b<a,(name,a,b)
    else:assert int(b)<=int(a),(name,a,b)

def test_contract_covers_every_field():
    assert {f.name for f in fields(Scenario)}=={row[0] for row in CASES}

@pytest.mark.parametrize("weather",list(WEATHER))
@pytest.mark.parametrize("rcs",list(SIZE))
@pytest.mark.parametrize("emits",[False,True])
def test_all_scenarios_bounded(weather,rcs,emits):
    out=evaluate(replace(BASE,weather=weather,rcs=rcs,emits=emits))
    for k in ("radar","rf","acoustic","fused"):assert 0<=out[k]<=1
    assert out["fused"]>=out["radar"]
    if not emits:assert out["rf"]==0

@pytest.mark.parametrize("field,signal",[
    ("radar_on","radar"),("rf_on","rf"),("acoustic_on","acoustic")])
def test_sensor_disable_removes_own_evidence(field,signal):
    assert evaluate(replace(BASE,**{field:False}))[signal]==0

def test_all_sensors_off_yields_no_detection():
    out=evaluate(replace(BASE,radar_on=False,rf_on=False,acoustic_on=False))
    assert out["fused"]==0 and out["detected"] is False

def test_zero_fusion_matches_radar():
    out=evaluate(replace(BASE,fusion_weight=0))
    assert out["fused"]==out["radar"]

def test_researcher_threshold_changes_finding():
    assert evaluate(replace(BASE,threshold=.05))["detected"]
    assert not evaluate(replace(BASE,threshold=.95))["detected"]
