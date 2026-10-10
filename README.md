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
