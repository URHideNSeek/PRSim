import math
import pytest
from bistatic_geometry import Geometry,bistatic_observables,C_MPS

def g(**kwargs):
    params=dict(target_range_m=250,speed_mps=20,heading_deg=0,
                illuminator_distance_m=2000,illuminator_bearing_deg=90,frequency_ghz=10)
    params.update(kwargs)
    return Geometry(**params)

def test_stationary_target_zero_doppler():
    for bearing in [0,45,90,180,270,345]:
        o=bistatic_observables(g(speed_mps=0,illuminator_bearing_deg=bearing))
        assert o["valid"] and o["doppler_hz"]==pytest.approx(0)

def test_collinear_illuminator_beyond_target_cancels_motion():
    o=bistatic_observables(g(illuminator_bearing_deg=0))
    assert o["path_rate_mps"]==pytest.approx(0,abs=1e-10)

def test_collinear_illuminator_opposite_receiver_doubles_path_rate():
    o=bistatic_observables(g(illuminator_bearing_deg=180))
    assert o["path_rate_mps"]==pytest.approx(40,abs=1e-10)
    assert o["doppler_hz"]==pytest.approx(-40*10e9/C_MPS)

def test_reverse_heading_reverses_doppler():
    away=bistatic_observables(g(heading_deg=0))
    toward=bistatic_observables(g(heading_deg=180))
    assert away["doppler_hz"]==pytest.approx(-toward["doppler_hz"])

def test_doppler_scales_with_speed_and_frequency():
    a=bistatic_observables(g(speed_mps=10,frequency_ghz=8))
    b=bistatic_observables(g(speed_mps=20,frequency_ghz=8))
    c=bistatic_observables(g(speed_mps=20,frequency_ghz=12))
    assert b["doppler_hz"]==pytest.approx(2*a["doppler_hz"])
    assert c["doppler_hz"]==pytest.approx(1.5*b["doppler_hz"])

def test_zero_target_range_reports_undefined_geometry():
    o=bistatic_observables(g(target_range_m=0))
    assert not o["valid"] and o["doppler_hz"] is None

def test_illuminator_at_target_reports_undefined_geometry():
    o=bistatic_observables(g(illuminator_distance_m=250,illuminator_bearing_deg=0))
    assert not o["valid"]

def test_invalid_frequency_rejected():
    with pytest.raises(ValueError):bistatic_observables(g(frequency_ghz=13))

def test_ui_explains_motion_not_connected_to_detection_probability():
    from pathlib import Path
    src=Path("PRSim.py").read_text(encoding="utf-8")
    assert "bistatic_observables" in src
    assert "Idealized Doppler" in src
    assert "The synthetic probabilities below remain independent of target motion." in src
