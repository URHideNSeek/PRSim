# PRSim — Independent Academic Review Brief

**Status:** Invitation draft and internal code-review findings. No author has reviewed or endorsed PRSim.

**Repository:** https://github.com/URHideNSeek/PRSim

## Requested external review

Please assess the validity and limitations of the current synthetic simulation, focusing on:
1. Whether the modeled observables and geometry correspond to a physically plausible passive bistatic radar experiment.
2. Which published datasets and standards are appropriate for X-band illumination, clutter and propagation.
3. Whether acoustic and passive RF observations can be represented without overstating information content.
4. How to evaluate uncertainty, false alarms, repeatability and independent validation.
5. Which tests would be necessary before any SAR, GMTI or aircraft-detection claim.

Please distinguish **fatal flaws**, **important revisions**, **nice-to-have improvements**, and **items requiring measured data**. We welcome negative findings.

## Internal findings — NOT external reviewer comments

- Critical: Main dashboard YES/NO uses a synthetic evidence threshold, not empirically calibrated detection probability.
- Critical: Aircraft RCS is input in square meters but maps to a heuristic score; no measured bistatic RCS/aspect data.
- High: ITU-R P.838 and P.676 are listed for provenance but not implemented in the detection calculation.
- High: Acoustic dB SPL has no reference distance, spectrum, or uncertainty.
- High: Monte Carlo validation page does not consume the main dashboard's weather, RCS, distance or acoustic settings.
- High: SAR and GMTI processing/verification are not implemented.
- High: Fusion confidence and cross-sensor correlation have not been validated with measurements.
- Medium: Distinguish incident illumination, environmental radar clutter and target-generated RF emissions explicitly.

## Reference families for reviewer selection

- ITU-R P.838-3: rain-specific attenuation; https://www.itu.int/rec/R-REC-P.838-3-200503-I
- ITU-R P.676-13: atmospheric gas attenuation; https://www.itu.int/rec/R-REC-P.676-13-202208-I
- Published passive bistatic radar, satellite illuminator, passive SAR/GMTI, and multisensor counter-UAS literature cited in the proposal. Verify author names, contact details, DOI and paper scope before sending personalized invitations.

## Suggested feedback format

| Category | Severity | Code/page reference | Evidence or paper | Suggested corrective experiment | Confidence |
|---|---|---|---|---|---|
| Example: acoustic source calibration | High | model.py | Reference SPL measurement method | Repeat with known reference distance | Medium |

## External-review controls

Do not describe a literature-based critique as an actual author review. Do not send invitations without approval. Do not provide unpublished, restricted or export-controlled technical information in external correspondence. Keep reviewer feedback attributable only to researchers who actually provide it.
