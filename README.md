# PRSim — Passive Radar Multisensor Research Simulator

Phase I **synthetic** research demonstrator for comparing X-band passive radar, passive RF listening and stereo acoustics. No operational range claims, real signal processing, SAR imaging, or GMTI verification are implemented.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

Choose weather (clear, aircraft inside cloud, light/heavy rain, snow, high wind), radar-cross-section class, RF emission status, acoustic level, and sensor / FTA parameters. Compare radar-only and fused outputs for detection probability at fixed false-alarm rate, latency, tracking uncertainty, environmental robustness, and availability. A simple finding is based on synthetic threshold tests.

**Scientific limitations:** Scores are illustrative normalized indices, not physically calibrated detection probabilities. RF-off sources cannot be credited with RF detection. Stereo acoustic measurements do not independently supply range. The app is a scenario/design review tool and must not be used to claim field performance. Future versions need literature-calibrated propagation, measured sensor responses, empirical covariance, ROC curves, confidence intervals, independent SAR/GMTI evaluation, and field validation.

## Files
- `app.py` — Streamlit UI and synthetic assessment engine
- `requirements.txt` — runtime dependencies

## Research validation page
Run the app and select **Research Validation** from the Streamlit page navigation. It provides reproducible synthetic Monte Carlo comparisons, ROC curves, 95% Wilson sampling intervals, and separate SAR/GMTI evidence checklists. Weather, RCS and dB choices on this page are metadata only; they are not mapped to calibrated propagation. Do not interpret synthetic Pd as measured performance.

## Parameter regression audit

The `tests/test_model.py` suite varies every one of the 28 fields in the scenario model independently, checks the expected response direction, and checks sensor-disable and RF-off invariants. `tests/test_optimization.py` checks sweep reproducibility, trial-count/seed sensitivity and bounded results. GitHub Actions runs these tests on each push.

**Scope limitation:** The Research Validation page's weather, RCS and acoustic dB controls currently record metadata only and do not affect the Monte Carlo output. The scenario page has a separate normalized heuristic model. The Design Space page's controls change the synthetic sampling experiment, not calibrated physical hardware. Therefore a complete end-to-end, physics-valid input/output acceptance test is not yet possible; calibration and UI interaction testing are still required.

Run locally: `python -m pip install -r requirements.txt pytest && python -m pytest -q tests/`.

## Distance control and detection finding
The main Streamlit page includes a target-distance selector from 0 to 500 m in 25 m increments (21 choices) and a prominent **AIRCRAFT DETECTED — YES/NO (SIMULATED)** verdict. This is a synthetic threshold decision, **not** a verified real-world detection prediction. `tests/test_distance.py` checks all 21 distances across six weather and three aircraft-size classes, as well as RF-off and sensor-off invariants. Run `python -m pytest -q tests/` to execute the full suite.
