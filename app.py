from model import Scenario, evaluate
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PRSim | Research Lab", layout="wide")
st.title("PRSim — Multisensor Research Lab")
st.caption("Synthetic design-space demonstrator · NOT a validated detection model, radar processor, or SAR/GMTI verification")
range_m = st.select_slider("Target distance from sensor (m)", options=list(range(0, 501, 25)), value=250, help="0–500 meters in exactly 25 m increments. This controls the synthetic range-response model.")

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

scenario = Scenario(weather=weather,rcs=rcs,emits=emits,audio=audio,range_m=range_m,
    observation=observation,update=update,fusion_weight=fusion_weight,fail=fail,
    radar_on=radar_on,illumination=illumination,reference=reference,sync_error=sync_error,
    clutter=clutter,radar_noise=radar_noise,bandwidth=bandwidth,rf_on=rf_on,
    rf_sensitivity=rf_sensitivity,rf_interference=rf_interference,rf_coverage=rf_coverage,
    rf_noise=rf_noise,acoustic_on=acoustic_on,microphone_quality=microphone_quality,
    mic_spacing=mic_spacing,audio_noise=audio_noise,wind_noise=wind_noise,channel_sync=channel_sync)
out=evaluate(scenario)
radar,rf,acoustic,fused=out["radar"],out["rf"],out["acoustic"],out["fused"]
results=pd.DataFrame({"Radar only":out["radar_metrics"],"Fused":out["fused_metrics"]})
c1, c2, c3 = st.columns(3)
c1.metric("Radar evidence", f"{radar:.2f}")
c2.metric("RF evidence", f"{rf:.2f}")
c3.metric("Acoustic evidence", f"{acoustic:.2f}")
st.subheader("Five comparative outputs")
st.dataframe(results, use_container_width=True)
st.subheader("Evidence comparison")
st.bar_chart(pd.DataFrame({"Radar only": [radar], "Radar + RF + stereo audio": [fused]}, index=["Synthetic score"]).T)
st.subheader("Detection finding")
threshold = st.slider("Researcher-defined evidence threshold", .05, .95, .30, .05)
finding = evaluate(__import__("dataclasses").replace(scenario,threshold=threshold))["detected"]
if finding:
    st.success(f"**AIRCRAFT DETECTED — YES (SIMULATED)** | Target distance: {range_m:,} m | Evidence: {fused:.3f} ≥ threshold {threshold:.2f}")
else:
    st.error(f"**AIRCRAFT DETECTED — NO (SIMULATED)** | Target distance: {range_m:,} m | Evidence: {fused:.3f} < threshold {threshold:.2f}")
st.info("This is NOT a measured probability of detection, calibrated range prediction, or assurance that the FTA would detect an aircraft.")
st.caption("No RF-emission credit is assigned when RF is disabled. Stereo audio does not establish absolute range. Radar SAR and GMTI remain independent, unimplemented verification workstreams.")
st.download_button("Export scenario results CSV", results.to_csv().encode(), file_name="prsim_results.csv", mime="text/csv")
