"""Canonical numbering and measured-to-simulator comparison integration checks."""
from pathlib import Path
from experiment_registry import LEGACY_TO_CANONICAL, CANONICAL_NAMES, canonical_title
from controlled_rf import parse_controlled_rf, baseline_summary, REQUIRED

def test_twelve_unique_canonical_experiments():
    assert set(LEGACY_TO_CANONICAL.values()) == {f"E{i:02d}" for i in range(1,13)}
    assert len(CANONICAL_NAMES) == 12
    assert canonical_title("CONTROLLED_RF") == "E02 — Controlled RF Characterization"

def test_navigation_has_execution_order():
    source = Path("app.py").read_text()
    titles = [f'title="E{i:02d} · ' for i in range(1,13)]
    assert all(source.count(title) == 1 for title in titles)
    positions = [source.index(title) for title in titles]
    assert positions == sorted(positions)

def test_controlled_rf_link_is_descriptive_only():
    page = Path("pages/09_Controlled_RF.py").read_text()
    main = Path("PRSim.py").read_text()
    assert 'st.session_state["controlled_rf_intake"]' in page
    assert 'st.session_state.get("controlled_rf_intake")' in main
    assert 'synthetic probability inputs remain unchanged' in page.lower() or 'Synthetic probability inputs remain unchanged' in page
    assert "do NOT update radar evidence, Pd, or Pfa" in main

def test_sample_measurements_available_for_summary():
    row = "2026-10-10T00:00:00Z,s1,Keysight E8267D Option 520,1000000000,1000000,-40,5,baseline"
    data = ",".join(REQUIRED) + "\n" + "\n".join([row]*30) + "\n"
    summary = baseline_summary(parse_controlled_rf(data))
    assert summary["baseline_samples"] == 30
    assert summary["mean_power_dbm"] == -40
