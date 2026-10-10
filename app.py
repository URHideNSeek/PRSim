from model import Scenario, evaluate
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
    weather = st.selectbox("Weather", list(WEATHER), help="Choose conditions around the aircraft. These are simplified synthetic weather assumptions, not measured attenuation.")
    rcs_m2 = st.select_slider("Aircraft radar cross section (m²)", options=[round(i * 0.05, 2) for i in range(1, 21)], value=0.1, help="Effective radar-reflecting area in square meters, adjustable from 0.05 to 1.00 m² in steps of 0.05 m². Values are illustrative rather than measurements of a specific aircraft. RCS depends on frequency, polarization, and viewing angle.")
    st.caption(f"Equivalent: {10 * __import__('math').log10(rcs_m2):.0f} dBsm")
    emits = st.checkbox("Aircraft emits RF", value=True, help="Whether the aircraft transmits radio signals that passive RF listening could observe. Off means no target RF evidence in this model.")
    audio = st.selectbox("Acoustic signature at reference point (dB SPL)", list(range(0, 76, 5)), index=12, help="Aircraft sound level in decibels sound pressure level (dB SPL), from 0 to 75 in 5 dB steps. 0 dB SPL means the standard reference sound pressure, not complete silence; 75 dB is much louder. A reference measurement distance is not specified, so these are illustrative inputs rather than calibrated aircraft sound levels.")
    range_m = st.select_slider("Target distance from sensor (m)", options=list(range(0, 501, 25)), value=250, help="Separation between aircraft and sensor, from 0 to 500 m in 25 m steps. Greater distance reduces synthetic evidence; 0 m is a mathematical endpoint.")
    speed_mps = st.slider("Target ground speed (m/s)", 0, 50, 0, 1, help="Horizontal speed over the ground, from 0 to 50 m/s. This excludes vertical climb or descent. Stored for future motion studies; not yet used in detection calculations.")
    heading_deg = st.slider("Target heading relative to sensor (degrees)", 0, 360, 0, 15, help="Direction of horizontal travel relative to the sensor-to-target line: 0° moves directly away from the sensor, 90° moves across its line of sight, and 180° moves directly toward it. This is not a compass bearing. Passive bistatic radar also requires illuminator geometry.")
    st.header("Field test article")
    observation = st.slider("Observation window (s)", 1, 60, 10, help="How long the simulated system listens during an observation. This affects the latency proxy, not physical detection probability.")
    update = st.slider("Measurement update interval (s)", 0.1, 5.0, 1.0, 0.1, help="Time between simulated sensor updates. A larger interval increases the latency proxy.")
    fusion_weight = st.slider("Auxiliary fusion contribution (synthetic)", 0.0, 1.0, .45, .05, help="How much extra synthetic evidence RF and acoustic sensing can contribute alongside radar. Not a trained fusion weight.")
    fail = st.slider("Common-mode outage probability", 0.0, .5, .05, .01, help="Assumed chance that the whole sensor system becomes unavailable together. Higher values lower the availability estimate.")
    st.header("X-band passive radar")
    radar_on = st.checkbox("Enable radar", True, help="Include or exclude the X-band passive radar's synthetic evidence.")
    illumination = st.slider("Illuminator availability", 0., 1., .85, .05, help="Assumed fraction of time an external X-band signal is usable for passive radar. Zero means no radar evidence.")
    reference = st.slider("Reference-channel quality", 0., 1., .8, .05, help="How cleanly the receiver observes the external reference signal. Higher values improve synthetic radar evidence.")
    sync_error = st.slider("Synchronization error index", 0., 1., .15, .05, help="How poorly receiver timing and frequency align. Larger error reduces synthetic radar evidence.")
    clutter = st.slider("Clutter/interference index", 0., 1., .3, .05, help="Legacy normalized radar interference input. This is separate from background reflected clutter.")
    clutter_cnr_db = st.slider("Background reflected clutter CNR (dB)", -20, 40, 0, 5, help="Clutter-to-noise ratio in decibels: strength of reflections from terrain, buildings and vegetation relative to receiver noise. Larger values mean stronger unwanted reflections. Detection impact is still an uncalibrated heuristic.")
    radar_noise = st.slider("Receiver noise index", 0., 1., .2, .05, help="Extra noise from radar receiver electronics. Higher means worse synthetic radar evidence.")
    bandwidth = st.slider("Normalized processed bandwidth", 0.1, 1., .6, .1, help="Relative width of the radar signal being processed, not a frequency in hertz. Higher slightly increases the synthetic score.")
    st.header("Passive RF listening")
    rf_on = st.checkbox("Enable passive RF", True, help="Include or exclude listening for radio transmissions from the aircraft.")
    rf_sensitivity = st.slider("RF receiver sensitivity index", 0., 1., .7, .05, help="Relative ability to hear weak aircraft radio signals. Higher improves synthetic RF evidence when the aircraft emits RF.")
    rf_interference = st.slider("RF interference index", 0., 1., .3, .05, help="Competing radio activity that makes aircraft emissions harder to distinguish. Higher reduces synthetic RF evidence.")
    rf_coverage = st.slider("RF spectrum coverage fraction", 0., 1., .8, .05, help="How much of the assumed radio spectrum is monitored. Higher increases synthetic RF evidence.")
    rf_noise = st.slider("RF receiver noise index", 0., 1., .2, .05, help="Noise generated by the passive RF receiver. Higher reduces synthetic RF evidence.")
    st.header("Stereo acoustic")
    acoustic_on = st.checkbox("Enable stereo acoustic", True, help="Include or exclude evidence from two microphones listening for aircraft sounds.")
    microphone_quality = st.slider("Microphone quality index", 0., 1., .75, .05, help="Combined simplified microphone performance. Higher improves synthetic acoustic evidence.")
    mic_spacing = st.slider("Microphone spacing (m)", .05, 1.5, .35, .05, help="Distance between the two microphones. Here it changes a directional-evidence factor; it does not directly measure aircraft distance.")
    audio_noise = st.slider("Background sound index", 0., 1., .3, .05, help="Other sounds such as traffic and machinery. Higher background noise reduces synthetic acoustic evidence.")
    wind_noise = st.slider("Microphone wind-noise index", 0., 1., .2, .05, help="Noise caused by wind around the microphones. Higher wind noise reduces synthetic acoustic evidence.")
    channel_sync = st.slider("Channel synchronization quality", 0., 1., .9, .05, help="How closely the two microphone channels agree in timing. Higher improves synthetic acoustic evidence.")

scenario = Scenario(weather=weather,rcs_m2=rcs_m2,clutter_cnr_db=clutter_cnr_db,emits=emits,audio=audio,range_m=range_m,speed_mps=speed_mps,heading_deg=heading_deg,
    observation=observation,update=update,fusion_weight=fusion_weight,fail=fail,
    radar_on=radar_on,illumination=illumination,reference=reference,sync_error=sync_error,
    clutter=clutter,radar_noise=radar_noise,bandwidth=bandwidth,rf_on=rf_on,
    rf_sensitivity=rf_sensitivity,rf_interference=rf_interference,rf_coverage=rf_coverage,
    rf_noise=rf_noise,acoustic_on=acoustic_on,microphone_quality=microphone_quality,
    mic_spacing=mic_spacing,audio_noise=audio_noise,wind_noise=wind_noise,channel_sync=channel_sync)
out=evaluate(scenario)
radar,rf,acoustic,fused=out["radar"],out["rf"],out["acoustic"],out["fused"]
results=pd.DataFrame({"Radar only":out["radar_metrics"],"Fused":out["fused_metrics"]})
st.caption(f"Motion scenario: ground speed {speed_mps} m/s, relative heading {heading_deg}° (0° away; 180° toward sensor). Motion is recorded but is not yet connected to the detection model.")
st.subheader("Synthetic detection decision", help="This is a threshold check of illustrative evidence, not an observed aircraft detection or calibrated probability.")
threshold = st.slider("Researcher-defined evidence threshold", .05, .95, .30, .05, help="Minimum synthetic fused evidence score needed for a YES finding. Higher thresholds make YES less likely.")
finding = evaluate(__import__("dataclasses").replace(scenario,threshold=threshold))["detected"]
if finding:
    st.success(f"**SYNTHETIC THRESHOLD MET — YES** | Target distance: {range_m:,} m | Evidence: {fused:.3f} ≥ threshold {threshold:.2f}")
else:
    st.error(f"**SYNTHETIC THRESHOLD MET — NO** | Target distance: {range_m:,} m | Evidence: {fused:.3f} < threshold {threshold:.2f}")
c1, c2, c3 = st.columns(3)
c1.metric("Radar evidence", f"{radar:.2f}", help="Normalized synthetic radar signal score, from zero to one. Not a measured detection probability.")
c2.metric("RF evidence", f"{rf:.2f}", help="Normalized synthetic evidence from aircraft radio emissions. It is zero if the aircraft emits no RF.")
c3.metric("Acoustic evidence", f"{acoustic:.2f}", help="Normalized synthetic evidence from microphone measurements. Not a measured sound-detection range.")
st.subheader("Five comparative outputs", help="Radar-only versus fused results. These are simplified indicators, not field measurements.")
st.dataframe(results, use_container_width=True)
st.caption("Output guide: Detection evidence = normalized synthetic score; latency = illustrative time proxy; tracking uncertainty = confidence proxy; environmental retention = assumed weather resilience; availability = modeled uptime. These are not measured sensor performance.")
st.caption("Hover over the ⓘ icons next to the selectors and results for plain-language explanations.")
st.subheader("Evidence comparison", help="Visual comparison of radar-only and fused synthetic evidence scores.")
st.bar_chart(pd.DataFrame({"Radar only": [radar], "Radar + RF + stereo audio": [fused]}, index=["Synthetic score"]).T)

st.info("Actual aircraft detection: NOT DETERMINED. Calibrated probability of detection and false-alarm probability: NOT AVAILABLE on this page. Use Research Validation for separately simulated Monte Carlo estimates.")
st.caption("No target-emission RF credit when RF is disabled. Stereo audio does not independently establish range. RCS in m² and clutter CNR in dB are converted to scores using heuristic equations, not validated physics. SAR and GMTI remain unimplemented.")
st.download_button("Export scenario results CSV", results.to_csv().encode(), file_name="prsim_results.csv", mime="text/csv", help="Download the displayed synthetic result table as a CSV file.")
