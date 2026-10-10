"""Acoustic dB selector acceptance and hover-help regression tests."""
from dataclasses import replace
from pathlib import Path
import ast
from model import Scenario,evaluate

def test_acoustic_levels_exactly_0_to_75_in_fives():
    expected=list(range(0,76,5))
    assert len(expected)==16 and expected[0]==0 and expected[-1]==75
    for file in ["PRSim.py","pages/01_Research_Validation.py"]:
        text=Path(file).read_text(encoding="utf-8")
        assert "list(range(0, 76, 5))" in text or "list(range(0,76,5))" in text
        assert "help=" in text
        ast.parse(text)

def test_acoustic_score_non_decreasing_across_all_levels():
    values=[evaluate(replace(Scenario(),audio=db))["acoustic"] for db in range(0,76,5)]
    assert values[0]==0
    assert all(y>x for x,y in zip(values,values[1:]))

def test_acoustic_disabled_stays_zero_for_all_levels():
    for db in range(0,76,5):
        assert evaluate(replace(Scenario(acoustic_on=False),audio=db))["acoustic"]==0
