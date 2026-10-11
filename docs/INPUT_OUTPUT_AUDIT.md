# PRSim input/output wiring audit

Scope: source-code inspection of PRSim.py, model.py, probability_demo.py,
bistatic_geometry.py and the four additional Streamlit pages. This is NOT
an executed browser test, a passing CI report, or sensor calibration.

## Main page

| Controls | Downstream outputs | Status |
|---|---|---|
| Weather | Radar/RF/acoustic heuristic scores, fused evidence, synthetic Pd | Connected; assumed multipliers |
| RCS m² | Radar score and radar synthetic Pd | Connected; arbitrary mapping, possible clipping |
| Target RF emits | RF score/Pd (N/A when off), fused evidence | Connected |
| Acoustic dB SPL | Acoustic score/Pd | Connected; reference distance unspecified |
| Target distance | All three scores/Pd; geometric Doppler | Connected; 0 m invalid for geometry |
| Ground speed and relative heading | Radial/transverse velocity; bistatic path rate/Doppler | Connected to geometry only; no Pd impact |
| Illuminator distance/bearing/frequency | Bistatic path rate/Doppler | Connected to geometry only; no Pd impact |
| Observation/update interval | Latency proxy | Connected; no Pd impact |
| Fusion contribution | Fused evidence/decision | Connected; does not alter individual sensor Pd |
| Common-mode outage | Availability | Connected; does not alter displayed Pd |
| Radar enable, illumination, reference, sync, clutter, noise, bandwidth, CNR | Radar evidence and downstream fusion | Connected, heuristic; radar off shows N/A Pd |
| Passive RF enable, sensitivity, interference, coverage, noise | RF evidence and downstream fusion | Connected if target emits; otherwise no effect |
| Acoustic enable, microphone quality/spacing, noise/wind/sync | Acoustic evidence and downstream fusion | Connected if acoustic enabled |
| Evidence threshold | Top-level YES/NO; individual synthetic Pd; synthetic Pfa | Connected |
| Target speed/heading | No detection probability | Deliberately unmodeled until calibrated |
| External illuminator geometry | No detection probability | Deliberately unmodeled until calibrated |

### Observed architectural issues

1. The top-level synthetic YES/NO is a deterministic threshold comparison,
   whereas the individual Pd values are tail probabilities from an assumed
   Gaussian score distribution. They are not the same statistical output.
2. False-alarm probability on the main page depends on threshold only, not
   weather or background clutter. This is a simplifying assumption.
3. Individual radar/RF/acoustic Pd do not include common-mode outage or
   sensor availability, so they are conditional rather than end-to-end
   detection probabilities. The UI should clarify this.
4. The fused evidence and fused availability are calculated, but there is no
   top-level fused Pd computed from a calibrated joint distribution.
5. Radar RCS and clutter values have physical units but enter heuristic
   transforms, and clipping can make some parameter adjustments appear inert.
6. Both a normalized clutter/interference index and a clutter CNR slider
   affect radar score, potentially double counting the same physical effect.
7. Zero distance is a permitted UI test endpoint but has undefined physical
   bistatic geometry.
8. Motion Calibration validates only uploaded CSV schema and class/session
   coverage. It does not fit a model or change any detection probability.

## Other pages

- Research Validation: seed, trials, Pfa target, correlation, synthetic
  separations, availability and interval affect its Monte Carlo outputs.
  Weather, RCS, RF-emission flag, acoustic SPL and distance affect a separate
  scenario preview only. Speed and heading affect metadata only.
- Design Space: random seed and trial count affect its independent sweep;
  changing these does not alter the main dashboard.
- Evidence Calibration: physical environmental inputs populate an export
  record; they do not modify detection results.
- Motion Calibration: uploaded data affect validation messages and counts
  only; they do not modify detection results.

## Required acceptance criteria

For every UI control, test minimum, default and maximum values, all toggles,
conditional inactivity, output changes at full precision, and Streamlit
rendering. Treat documented metadata-only controls separately from physics
inputs. Validate sensor performance against independent experimental data
before presenting probabilities as real-world detection estimates.
