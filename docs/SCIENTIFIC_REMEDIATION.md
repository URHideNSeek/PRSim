# Scientific remediation register (2026-10-10)

This document distinguishes changes implemented in code from work that requires experimental evidence.

| Finding | Current state | Required validation |
|---|---|---|
| Synthetic detection presented as actual aircraft detection | **Mitigated:** main UI now says synthetic threshold met / not met and actual detection NOT DETERMINED | Measured labeled detections and false alarms |
| RCS and clutter entered in standard units but converted heuristically | **Open:** m² and CNR dB inputs retained with explicit warning | Bistatic geometry, frequency/aspect-specific measured RCS and clutter data |
| Weather uses arbitrary multipliers | **Open:** assumptions clearly labeled; ITU standards listed separately | Implement/test attenuation with valid path geometry and coefficients |
| Acoustic SPL lacks reference distance | **Open:** explanatory tooltip; not a physical acoustic propagation model | Reference distance, spectral measurements, calibration |
| Two statistical models not unified | **Partially mitigated:** Research Validation now shows scenario-linked heuristic preview; Monte Carlo explicitly remains separate | One shared calibrated measurement model and independent holdout data |
| SAR/GMTI not implemented | **Open:** evidence checklists only | Actual waveform-level algorithms and independent tests |
| Sensor fusion lacks measured error covariance | **Open:** correlation in synthetic Monte Carlo is illustrative | Empirical covariance, ablation study, uncertainty calibration |

Do not report the app's synthetic threshold outcome as observed aircraft detection. Do not claim scientific validation from successful unit tests. The 0 m distance endpoint is mathematical, not a physically meaningful bistatic geometry.

## Validation gates

1. Unit tests and Streamlit smoke tests pass on pinned dependencies.
2. Each physically dimensioned parameter is associated with an explicit source and valid conditions.
3. Simulator matches independent measured data, with error and uncertainty intervals.
4. Detection metrics are evaluated on held-out target/no-target data at fixed false-alarm rates.
5. SAR and GMTI are tested independently of auxiliary sensor fusion.

## Academic reviewer request

Request critical feedback on equations, applicability of cited standards, calibration strategy, false-alarm definitions and uncertainty, without claiming author endorsement.
