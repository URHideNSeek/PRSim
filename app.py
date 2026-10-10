import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PRSim | Research Lab", layout="wide")
st.title("PRSim — Multisensor Research Lab")
st.caption("Synthetic design-space demonstrator · NOT a validated detection model, radar processor, or SAR/GMTI verification")

WEATHER = {
    "Clear": (1.00, 1.00, 1.00),
    "Cloud (aircraft inside)": (.95, .96, .95),
    "Light rain": (.82, .95, .86),
    "Heavy rain": (.60, .86, .70),
    "Snow": (.75, .89, .79),
    "High wind": (.55, .94, .75),
}
with st.sidebar:
    st.header("Scenario")
    weather = st.selectbox("Weather", list(WEATHER))
    rcs = st.selectbox("Aircraft radar cross-section class", ["Small", "Medium", "Large"], index=1,
                       help="Relative synthetic classes; no calibrated m² or aircraft dimensions.")
    emits = st.checkbox("Aircraft emits RF", value=True)
    audio = st.selectbox("Acoustic signature at reference point (dB SPL)", [45, 60, 75], index=1)
    st.header("Field test article")
    range_m = st.slider("Illustrative separation (m)", 50, 3000, 500, 50)
    observation = st.slider("Observation window (s)", 1, 60, 10)
    update = st.slider("Measurement update interval (s)", 0.1, 5.0, 1.0, 0.1)
    fusion_weight = st.slider("Auxiliary fusion contribution (synthetic)", 0.0, 1.0, .45, .05)
    fail = st.slider("Common-mode outage probability", 0.0, .5, .05, .01)
    st.header("X-band passive radar")
    radar_on = st.checkbox("Enable radar", True)
    illumination = st.slider("Illuminator availability", 0., 1., .85, .05)
    reference = st.slider("Reference-channel quality", 0., 1., .8, .05)
    sync_error = st.slider("Synchronization error index", 0., 1., .15, .05)
    clutter = st.slider("Clutter/interference index", 0., 1., .3, .05)
    radar_noise = st.slider("Receiver noise index", 0., 1., .2, .05)
    bandwidth = st.slider("Normalized processed bandwidth", 0.1, 1., .6, .1)
    st.header("Passive RF listening")
    rf_on = st.checkbox("Enable passive RF", True)
    rf_sensitivity = st.slider("RF receiver sensitivity index", 0., 1., .7, .05)
    rf_interference = st.slider("RF interference index", 0., 1., .3, .05)
    rf_coverage = st.slider("RF spectrum coverage fraction", 0., 1., .8, .05)
    rf_noise = st.slider("RF receiver noise index", 0., 1., .2, .05)
    st.header("Stereo acoustic")
    acoustic_on = st.checkbox("Enable stereo acoustic", True)
    microphone_quality = st.slider("Microphone quality index", 0., 1., .75, .05)
    mic_spacing = st.slider("Microphone spacing (m)", .05, 1.5, .35, .05)
    audio_noise = st.slider("Background sound index", 0., 1., .3, .05)
    wind_noise = st.slider("Microphone wind-noise index", 0., 1., .2, .05)
    channel_sync = st.slider("Channel synchronization quality", 0., 1., .9, .05)

def clamp(x):
    return max(0., min(1., float(x)))

w_a, w_rf, w_r = WEATHER[weather]
size = {"Small": .55, "Medium": .75, "Large": .95}[rcs]
# Heuristic scores only. These are NOT detection physics, measured Pd, or operational ranges.
distance_factor = 1 / (1 + (range_m / 650) ** 1.35)
radar = clamp(size * distance_factor * w_r * illumination * reference *
              (1 - .55 * sync_error) * (1 - .45 * clutter) *
              (1 - .35 * radar_noise) * (.7 + .3 * bandwidth)) if radar_on else 0.
rf = clamp(distance_factor * w_rf * rf_sensitivity * rf_coverage *
           (1 - .55 * rf_interference) * (1 - .3 * rf_noise)) if rf_on and emits else 0.
acoustic = clamp((audio / 75) * (1 / (1 + (range_m / 280) ** 1.4)) *
                 w_a * microphone_quality * channel_sync *
                 (1 - .55 * audio_noise) * (1 - .5 * wind_noise)) if acoustic_on else 0.
# Fusion demonstration: conservative weighted evidence, without assuming independence.
fused = clamp(radar + fusion_weight * (max(rf, acoustic) * (1 - radar)))
radar_availability = illumination * (1 - fail) if radar_on else 0
fused_availability = clamp((radar_availability + .35 * max(rf, acoustic)) * (1 - fail))
robustness = clamp((w_r * (radar > 0) + w_rf * (rf > 0) + w_a * (acoustic > 0)) /
                   max(1, int(radar > 0) + int(rf > 0) + int(acoustic > 0)))
# Proxy indicators, not physical latency or position covariance.
def metrics(score, avail):
    return {
        "Detection evidence index (0–1)": round(score, 3),
        "Latency proxy (s)": round(update + observation * (1 - score), 2),
        "Tracking uncertainty index (lower better)": round(1 - score * .8, 3),
        "Environmental retention index": round(robustness, 3),
        "Availability index (0–1)": round(avail, 3),
    }
results = pd.DataFrame({"Radar only": metrics(radar, radar_availability),
                        "Fused": metrics(fused, fused_availability)})
c1, c2, c3 = st.columns(3)
c1.metric("Radar evidence", f"{radar:.2f}")
c2.metric("RF evidence", f"{rf:.2f}")
c3.metric("Acoustic evidence", f"{acoustic:.2f}")
st.subheader("Five comparative outputs")
st.dataframe(results, use_container_width=True)
st.subheader("Evidence comparison")
st.bar_chart(pd.DataFrame({"Radar only": [radar], "Radar + RF + stereo audio": [fused]}, index=["Synthetic score"]).T)
st.subheader("Simple finding")
threshold = st.slider("Researcher-defined evidence threshold", .05, .95, .30, .05)
if fused >= threshold:
    st.success("SIMULATED: Evidence exceeds the selected threshold. Candidate detection in this synthetic scenario.")
else:
    st.warning("SIMULATED: Evidence does not exceed the selected threshold. No detection indicated by this synthetic model.")
st.info("This is NOT a measured probability of detection, calibrated range prediction, or assurance that the FTA would detect an aircraft.")
st.caption("No RF-emission credit is assigned when RF is disabled. Stereo audio does not establish absolute range. Radar SAR and GMTI remain independent, unimplemented verification workstreams.")
st.download_button("Export scenario results CSV", results.to_csv().encode(), file_name="prsim_results.csv", mime="text/csv")
