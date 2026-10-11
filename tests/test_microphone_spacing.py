"""Microphone-spacing UI and unit-conversion acceptance tests."""
import ast
from dataclasses import replace
from pathlib import Path
import pytest
from model import Scenario,evaluate

MM_CHOICES=[round(inches*25.4,1) for inches in range(1,19)]

def test_spacing_values():
    assert len(MM_CHOICES)==18
    assert MM_CHOICES[0]==25.4 and MM_CHOICES[-1]==457.2
    assert all(b-a==pytest.approx(25.4) for a,b in zip(MM_CHOICES,MM_CHOICES[1:]))

def test_mm_to_m_conversion_and_acoustic_response():
    scores=[]
    for mm in MM_CHOICES:
        meters=mm/1000.0
        assert meters*1000==pytest.approx(mm)
        scores.append(evaluate(replace(Scenario(),mic_spacing=meters))["acoustic"])
    assert all(b>a for a,b in zip(scores,scores[1:]))

def test_streamlit_control_label_and_conversion():
    source=Path("PRSim.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert '"Microphone spacing (mm)"' in source
    assert "range(1, 19)" in source
    assert "mic_spacing=mic_spacing_mm / 1000.0" in source
    assert "25.4 mm" in source
