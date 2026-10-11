import math
import pytest
from dataclasses import replace
from model import Scenario,evaluate

@pytest.mark.parametrize("speed,heading,radial,transverse",[
    (0,0,0,0),
    (20,0,20,0),
    (20,90,0,20),
    (20,180,-20,0),
    (20,270,0,-20),
    (20,345,20*math.cos(math.radians(345)),20*math.sin(math.radians(345))),
])
def test_motion_components(speed,heading,radial,transverse):
    m=evaluate(replace(Scenario(),speed_mps=speed,heading_deg=heading))["motion"]
    assert m["radial_speed_mps"]==pytest.approx(radial,abs=1e-10)
    assert m["transverse_speed_mps"]==pytest.approx(transverse,abs=1e-10)
    assert math.hypot(m["radial_speed_mps"],m["transverse_speed_mps"])==pytest.approx(speed)

def test_ui_discloses_motion_probability_limitation():
    from pathlib import Path
    src=Path("PRSim.py").read_text(encoding="utf-8")
    assert "Radial ground speed" in src
    assert "Transverse ground speed" in src
    assert "do NOT change radar/RF/acoustic detection probabilities" in src
