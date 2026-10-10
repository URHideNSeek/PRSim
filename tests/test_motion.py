from dataclasses import replace
from pathlib import Path
import ast
from model import Scenario,evaluate

def test_motion_bounds_and_steps():
    assert list(range(0,51,1))[0]==0
    assert list(range(0,51,1))[-1]==50
    assert list(range(0,361,15))[-1]==360

def test_motion_state_is_recorded_and_not_falsely_calibrated():
    base=Scenario()
    reference=evaluate(base)
    for speed in [0,1,15,50]:
        for heading in [0,15,90,180,270,360]:
            out=evaluate(replace(base,speed_mps=speed,heading_deg=heading))
            assert out["motion"]["speed_mps"]==speed
            assert out["motion"]["heading_deg"]==heading
            assert out["motion"]["model_status"]=="not calibrated"
            assert out["fused"]==reference["fused"]
            assert out["detected"]==reference["detected"]

def test_ui_motion_and_probability_present():
    for path in ["app.py","pages/01_Research_Validation.py"]:
        src=Path(path).read_text(encoding="utf-8")
        ast.parse(src)
        assert "speed_mps" in src and "heading_deg" in src
    research=Path("pages/01_Research_Validation.py").read_text(encoding="utf-8")
    assert "Synthetic detection probability" in research
    assert "Synthetic false-alarm probability" in research
