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
- `app.py` — Streamlit Cloud entrypoint and navigation; `PRSim.py` — main simulator UI
- `requirements.txt` — runtime dependencies

## Research validation page
Run the app and select **Research Validation** from the Streamlit page navigation. It provides reproducible synthetic Monte Carlo comparisons, ROC curves, 95% Wilson sampling intervals, and separate SAR/GMTI evidence checklists. Weather, RCS and dB choices on this page are metadata only; they are not mapped to calibrated propagation. Do not interpret synthetic Pd as measured performance.

## Parameter regression audit

The `tests/test_model.py` suite varies every one of the 28 fields in the scenario model independently, checks the expected response direction, and checks sensor-disable and RF-off invariants. `tests/test_optimization.py` checks sweep reproducibility, trial-count/seed sensitivity and bounded results. GitHub Actions runs these tests on each push.

**Scope limitation:** The Research Validation page's weather, RCS and acoustic dB controls currently record metadata only and do not affect the Monte Carlo output. The scenario page has a separate normalized heuristic model. The Design Space page's controls change the synthetic sampling experiment, not calibrated physical hardware. Therefore a complete end-to-end, physics-valid input/output acceptance test is not yet possible; calibration and UI interaction testing are still required.

Run locally: `python -m pip install -r requirements.txt pytest && python -m pytest -q tests/`.

## Distance control and detection finding
The main Streamlit page includes a target-distance selector from 0 to 500 m in 25 m increments (21 choices) and a prominent **AIRCRAFT DETECTED — YES/NO (SIMULATED)** verdict. This is a synthetic threshold decision, **not** a verified real-world detection prediction. `tests/test_distance.py` checks all 21 distances across six weather and three aircraft-size classes, as well as RF-off and sensor-off invariants. Run `python -m pytest -q tests/` to execute the full suite.

## Published evidence and calibration
The **Evidence Calibration** Streamlit page records physically dimensioned environmental inputs (GHz, mm/h, km, °C, hPa, g/m³, m/s) and the primary ITU-R P.838-3 / P.676-13 standards, and exports source-traceable JSON. It explicitly distinguishes published propagation *methods* from unvalidated radar-detection *performance*. The existing synthetic detection scores are intentionally unchanged; no standards-based attenuation calculation is claimed until validated implementation and correct path geometry are available.

## Motion and probability controls

The main Streamlit page and Research Validation page now include target speed (0–50 m/s, 1 m/s steps) and heading (0–360°, 15° steps). These are stored in the scenario and export, but **do not affect detection evidence or the Monte Carlo distributions** until a validated bistatic geometry and motion-response model is developed. A heading reference frame must be specified for physical Doppler calculations.

The Research Validation page prominently reports **synthetic detection probability** and **synthetic false-alarm probability** from repeated target-present and target-absent trials. These values are not validated for the selected aircraft, weather, distance, speed, or heading. The main dashboard continues to show a synthetic threshold decision rather than a physical detection claim.

Motion regression tests cover all allowed boundary values and representative headings, and assert that unsupported motion effects are not silently invented.

## UI control audit (October 2026)

- Target sensor-relative heading now uses 0–345° at 15° steps (24 unique directions; 360° duplicates 0°).
- Both Monte Carlo pages offer the same trial-count presets: 100, 500, 1,000, 1,500, 3,000, 5,000, with 1,500 as the default.
- Automated static widget checks cover valid min/max/default/step values, unique keyword arguments, matching presets, and warnings about controls that are not calibrated.
- Existing researcher-requested RCS (0.05–1 m² at 0.05 steps) and target distance (0–500 m at 25 m steps) are retained. The 0 m distance is a mathematical UI endpoint, not a valid propagation geometry.
- Weather, RCS, acoustic level, distance, speed, and heading still do not modify the separate Research Validation Monte Carlo distributions. A scenario preview responds to supported heuristic inputs, while motion remains recorded metadata.
- At low Monte Carlo sample counts, small target false-alarm probabilities have high uncertainty. No numeric output is evidence of field detection until independently validated.

Run `python -m pytest -q tests/` and check GitHub Actions before treating the build as tested.

The navigation now labels the main page **PRSim** while keeping `app.py` as the deployment entrypoint. No Streamlit Cloud configuration change is required.

## Idealized bistatic motion geometry

The main PRSim page now includes illuminator distance, illuminator bearing relative to the receiver-to-target line, and X-band carrier frequency. It computes the idealized bistatic path-length rate and Doppler shift using target ground speed and sensor-relative heading, assuming a stationary illuminator and receiver and a 2D flat geometry. At zero target range, or coincident illuminator/target positions, the geometry is marked undefined.

These are **geometric observables, not detection probabilities**. The three per-sensor synthetic detection probabilities intentionally remain unchanged with motion; modeling motion-dependent Pd requires a verified illuminator waveform, bistatic clutter/noise distributions, receiver characteristics and experimental calibration. See `bistatic_geometry.py` and `tests/test_bistatic_geometry.py`.

## Availability and clutter audit remediation

Main-page per-modality synthetic Pd now uses conditional Gaussian-score probability multiplied by an assumed modality availability: radar = illuminator availability × (1 − common outage), RF/acoustic = (1 − common outage). This is a simplifying independence assumption; individual RF and acoustic uptime are not characterized. The displayed false-alarm proxy includes common outage but does not incorporate clutter-dependent score distributions and is **not fused Pfa**. No validated fused Pd is presented.

The duplicate normalized radar clutter/interference slider was removed from the main UI; the remaining reflected clutter CNR (dB) control still uses an uncalibrated mapping. The legacy model field remains for backward compatibility and test coverage, fixed to zero by the main UI. The top-level threshold decision remains a deterministic heuristic and should not be conflated with these statistical probabilities.

Scientific integration of the main and Monte Carlo models, measured false-alarm statistics, and field calibration remain outstanding.

## Published dataset registry and empirical evaluation

The **Published Datasets** Streamlit page catalogs external acoustic, radar RCS, RF, and atmospheric references in `data/dataset_registry.json`. No raw external datasets are checked into this repository, and license/measurement applicability reviews are still required.

A new `dataset_validation.py` evaluator accepts independently supplied CSV rows with `session_id,target_present,detector_score`, selects a decision threshold using training-session target-absent observations only, and computes target-present detection and target-absent false-alarm fractions on a separate held-out session. This is an initial validation workflow, not physical calibration. It deliberately does not change the main page's synthetic Pd values. For defensible use, ensure detector scores, ground truth, session independence, environmental conditions, and confidence intervals are documented.

Sources: https://zenodo.org/records/6459183 ; https://zenodo.org/records/15405530 ; https://github.com/kitoweeknd/RFUAV ; ITU-R P.838-3 and P.676-13.

## DDL acoustic subset intake

The **DDL Acoustic Intake** page reads filenames from a small ZIP subset (maximum 100 MB) of the published DDL field-recording archive, without extracting or processing audio. The parser follows the published 49-character filename layout (timestamp, drone/background class, bearing, range, altitude, temperature, real/synthetic flag, flight/recording session, sequence). It exports parsed metadata CSV and flags insufficient class/session coverage. No raw DDL audio is bundled with PRSim, and no classifier has been trained or validated.

Source: https://zenodo.org/records/6459183 . The complete record lists approximately 12.6 GB of real data and 4.6 GB of synthesized data. Review reuse permissions and confirm that filenames in the selected archive match the published convention. Do not upload the full archive to Streamlit Cloud.

Next: select a permitted subset containing drone and background recordings from independent sessions; verify metadata; build and validate an acoustic feature-extraction and classification pipeline with holdout recordings. Avoid claiming calibrated SPL or range-based detection from filename metadata alone.

## DDL audio feature inspection and uncertainty reporting

The DDL Acoustic Intake page can optionally read at most 20 real WAV files from an uploaded ZIP subset and extract **uncalibrated** RMS dBFS, peak dBFS, spectral centroid, clipping fraction, duration and sample rate. It supports bounded uncompressed integer PCM WAV (mono/stereo, 8/16/24/32-bit). A 25 MB/file and 30-second duration cap limits memory use. Exported features preserve class labels, distance, bearing, flight and recording-session identifiers. **dBFS is not dB SPL**, and these generic features are not a trained detector or a detection probability.

The Published Datasets page now reports 95% Wilson confidence intervals for held-out detection and false-alarm fractions. These intervals assume independent trials; adjacent clips and correlated observations can violate that assumption. No public dataset recordings have been downloaded, added to GitHub, or used to calibrate PRSim.

The next work depends on acquiring a legally usable subset of real recordings and verifying its actual filename format, labels, microphone setup and license. A validated acoustic detector requires a documented score algorithm, separate sessions for training and evaluation, and independent replication.

## Acoustic intake hardening and quality gates

- ZIP metadata ingestion rejects oversized uncompressed WAV members (25 MB each) and archives with more than 250 MB total uncompressed WAV content, even if ZIP compression makes the upload appear small.
- The metadata coverage gate now requires at least two separate flight/recording sessions each containing real target-present and real background samples. This is a preliminary structural gate, not a proof of statistical independence.
- WAV features are computed separately for each channel to avoid cancellation when stereo channels are opposite in phase. Features remain uncalibrated dBFS and spectral descriptors, not SPL or drone classification scores.
- Empirical holdout evaluation now requires at least `ceil(1 / requested_Pfa)` training background observations (minimum 20). At a 1% target Pfa this means at least 100 background observations. This minimum is a coarse guardrail, not enough to establish precise low false-alarm rates.
- All related regression tests have been committed, but CI and live Streamlit operation must be verified before release.

**External-data dependency:** No licensed DDL audio has yet been ingested or evaluated. Actual acoustic detection performance cannot be claimed until source licensing, microphone conditions, labeling, independent sessions, and validation have been confirmed.

## Experimental acoustic baseline and offline workflow

The **Acoustic Baseline** page accepts a CSV of real recording features and performs a transparent two-feature standardized linear benchmark (RMS dBFS and spectral centroid), with training-only normalization/threshold and a separate recording-session holdout. It reports held-out detection and false-alarm fractions and Wilson intervals. This is an **exploratory benchmark**, not a calibrated drone detector or an operational detection probability. A session-held-out split alone cannot rule out correlated flights, repeated source recordings, domain shifts, or label errors.

For larger legally usable DDL subsets, run locally:

```bash
python scripts/extract_ddl_features.py path/to/ddl_subset.zip acoustic_features.csv --max-files 500
```

This extracts bounded generic features from real PCM WAV recordings and preserves class, range, bearing and session provenance. The CLI refuses to overwrite existing output. Upload the resulting CSV to the Acoustic Baseline page. Do not commit source audio or private/restricted recordings to GitHub.

**Known blockers:** We have not obtained, inspected, or licensed a real DDL subset; the published filename convention has not been verified against actual files in this environment; no baseline has been trained on real data. End-to-end Streamlit execution and passing CI remain unverified. Once real data are available, validate metadata parsing first, then evaluate on independent recording and flight sessions, document uncertainty, and compare results with a held-out baseline.

## Goal-seeking Design Space closure

The Design Space page now has a bounded staged search with a researcher-defined desired mean synthetic Pd (50–99%), false-alarm target, Monte Carlo trial count, and maximum of three stages. Each stage evaluates 81 configurations, expanding assumed radar/RF/acoustic signal separation only when the target is not met. It terminates with either `closed_synthetic` (a candidate met both the mean Pd goal and finite-sample false-alarm tolerance) or `not_feasible_within_bounds` (the search was exhausted). It reports stages, best candidate, gap to goal, and a downloadable candidate CSV.

**Important:** Expanded signal separation represents assumed statistical distinguishability, not automatically achievable hardware quality. A synthetic goal closure is not proof of real-world detection. Meeting mean Pd does not guarantee meeting worst-case Pd, and a false-alarm tolerance of max(1 percentage point, 2/trials) is a finite-sample screening allowance rather than a validated statistical confidence bound. No indefinite optimization or fabricated convergence is used.
