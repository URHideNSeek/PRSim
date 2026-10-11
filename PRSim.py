from model import Scenario, evaluate
from bistatic_geometry import Geometry, bistatic_observables
from probability_demo import synthetic_detection_probability, synthetic_false_alarm_probability, availability_adjusted_probability, availability_adjusted_false_alarm_probability
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
    heading_deg = st.slider("Target heading relative to sensor (degrees)", 0, 345, 0, 15, help="Direction of horizontal travel relative to the sensor-to-target line: 0° moves directly away from the sensor, 90° moves across its line of sight, and 180° moves directly toward it. This is not a compass bearing. 345° is the last unique 15° step; 360° equals 0°. Passive bistatic radar also requires illuminator geometry.")
    st.header("Idealized bistatic geometry")
    illuminator_distance_m = st.number_input("Illuminator distance from sensor (m)",min_value=1.0,max_value=100000.0,value=2000.0,step=100.0,help="Distance from the external RF illuminator to the passive radar receiver. This is a geometric research input, not measured coverage.")
    illuminator_bearing_deg = st.slider("Illuminator bearing relative to target line (degrees)",0,345,90,15,help="Direction from receiver to illuminator measured counterclockwise from receiver-to-target line. This is not target heading.")
    illuminator_frequency_ghz = st.number_input("Illuminator frequency (GHz)",min_value=8.0,max_value=12.0,value=10.0,step=0.1,help="External illuminator carrier frequency used for idealized Doppler calculation. Actual waveform availability and spectral characteristics are not modeled.")
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
    mic_spacing_mm = st.select_slider("Microphone spacing (mm)", options=[round(inches * 25.4, 1) for inches in range(1, 19)], value=round(6 * 25.4, 1), help="Distance between microphone centers, in millimeters. Choose from 1 inch (25.4 mm) to 18 inches (457.2 mm), in 1-inch (25.4 mm) increments. The current directional-evidence relationship is illustrative, not a calibrated array model.")
    st.caption(f"Microphone separation: {mic_spacing_mm / 25.4:.0f} in")
    audio_noise = st.slider("Background sound index", 0., 1., .3, .05, help="Other sounds such as traffic and machinery. Higher background noise reduces synthetic acoustic evidence.")
    wind_noise = st.slider("Microphone wind-noise index", 0., 1., .2, .05, help="Noise caused by wind around the microphones. Higher wind noise reduces synthetic acoustic evidence.")
    channel_sync = st.slider("Channel synchronization quality", 0., 1., .9, .05, help="How closely the two microphone channels agree in timing. Higher improves synthetic acoustic evidence.")

scenario = Scenario(weather=weather,rcs_m2=rcs_m2,clutter_cnr_db=clutter_cnr_db,emits=emits,audio=audio,range_m=range_m,speed_mps=speed_mps,heading_deg=heading_deg,
    observation=observation,update=update,fusion_weight=fusion_weight,fail=fail,
    radar_on=radar_on,illumination=illumination,reference=reference,sync_error=sync_error,
    clutter=0.0,radar_noise=radar_noise,bandwidth=bandwidth,rf_on=rf_on,
    rf_sensitivity=rf_sensitivity,rf_interference=rf_interference,rf_coverage=rf_coverage,
    rf_noise=rf_noise,acoustic_on=acoustic_on,microphone_quality=microphone_quality,
    mic_spacing=mic_spacing_mm / 1000.0,audio_noise=audio_noise,wind_noise=wind_noise,channel_sync=channel_sync)
out=evaluate(scenario)
radar,rf,acoustic,fused=out["radar"],out["rf"],out["acoustic"],out["fused"]
results=pd.DataFrame({"Radar only":out["radar_metrics"],"Fused":out["fused_metrics"]})
st.subheader("Synthetic detection decision", help="This is a threshold check of illustrative evidence, not an observed aircraft detection or calibrated probability.")
threshold = st.slider("Researcher-defined evidence threshold", .05, .95, .30, .05, help="Minimum synthetic fused evidence score needed for a YES finding. Higher thresholds make YES less likely.")
finding = evaluate(__import__("dataclasses").replace(scenario,threshold=threshold))["detected"]
if finding:
    st.success(f"**SYNTHETIC THRESHOLD MET — YES** | Target distance: {range_m:,} m | Evidence: {fused:.3f} ≥ threshold {threshold:.2f}")
else:
    st.error(f"**SYNTHETIC THRESHOLD MET — NO** | Target distance: {range_m:,} m | Evidence: {fused:.3f} < threshold {threshold:.2f}")
st.subheader("Illustrative detection probabilities", help="These are assumed Gaussian-score probabilities, adjusted for modeled availability. Not calibrated sensor performance.")
sensor_data = [
    ("Radar", radar, radar_on, illumination * (1-fail)),
    ("RF", rf, rf_on and emits, (1-fail)),
    ("Acoustic", acoustic, acoustic_on, (1-fail)),
]
pcols = st.columns(4)
for col, (name, score, enabled, availability) in zip(pcols[:3], sensor_data):
    probability = availability_adjusted_probability(score, threshold=threshold, availability=availability, enabled=enabled)
    col.metric(f"{name} detection probability", "N/A" if probability is None else f"{probability:.1%}",
        help="Synthetic probability per observation opportunity: assumed uptime × Gaussian probability of exceeding the selected threshold. Radar uptime includes illuminator availability. RF/acoustic uptime currently includes common outage only. Not field validated.")
pcols[3].metric("False-alarm probability", f"{availability_adjusted_false_alarm_probability(threshold,availability=1-fail):.1%}",
    help="Synthetic false-alarm fraction per observation opportunity with common outage included. It is NOT a calibrated fusion false-alarm rate and does not model clutter-dependent background statistics.")
st.subheader("Sensor evidence", help="Normalized synthetic evidence scores from 0 to 1, not probabilities.")
ecols = st.columns(3)
for col, (name, score, enabled, availability) in zip(ecols, sensor_data):
    col.metric(f"{name} evidence", f"{score:.2f}" if enabled else "N/A",
        help="Normalized synthetic evidence score. Not a calibrated signal measurement or detection probability.")
st.caption("Model: Gaussian score SD 0.20, with independent availability adjustment. Radar availability = illuminator availability × (1 − common outage); RF/acoustic = 1 − common outage. The displayed false-alarm value is a common-outage-adjusted background proxy, not a fused Pfa. These assumptions are uncalibrated.")
st.caption(f"Motion scenario: ground speed {speed_mps} m/s, relative heading {heading_deg}° (0° away; 180° toward sensor).")
motion=out["motion"]
motion_cols=st.columns(2)
motion_cols[0].metric("Radial ground speed (m/s)",f'{motion["radial_speed_mps"]:+.2f}',help="Ground-speed component along the sensor-to-target line. Positive means moving away; negative means moving toward the sensor. This is geometry, not radar Doppler.")
motion_cols[1].metric("Transverse ground speed (m/s)",f'{motion["transverse_speed_mps"]:+.2f}',help="Ground-speed component perpendicular to the sensor-to-target line. Sign distinguishes opposite transverse directions.")
geometry=bistatic_observables(Geometry(target_range_m=range_m,speed_mps=speed_mps,heading_deg=heading_deg,
    illuminator_distance_m=illuminator_distance_m,illuminator_bearing_deg=illuminator_bearing_deg,
    frequency_ghz=illuminator_frequency_ghz))
st.subheader("Idealized passive bistatic motion observables",help="Derived from transmitter/target/receiver positions and target ground velocity. This is a geometric calculation, not a detection-performance model.")
if geometry["valid"]:
    g1,g2=st.columns(2)
    g1.metric("Bistatic path rate (m/s)",f'{geometry["path_rate_mps"]:+.2f}',help="Time derivative of transmitter-to-target plus target-to-receiver path length.")
    g2.metric("Idealized Doppler (Hz)",f'{geometry["doppler_hz"]:+.1f}',help="Negative path rate divided by RF wavelength, using a stationary transmitter and receiver. Sign convention is stated in the model.")
else:
    st.info("Bistatic geometry unavailable: "+geometry["reason"])
st.caption("Motion observables are geometric predictions. For measured motion-dependent detection performance, use the Motion Calibration page. The synthetic probabilities below remain independent of target motion.")
st.subheader("Five comparative outputs", help="Radar-only versus fused results. These are simplified indicators, not field measurements.")
st.dataframe(results, use_container_width=True)
st.caption("Output guide: Detection evidence = normalized synthetic score; latency = illustrative time proxy; tracking uncertainty = confidence proxy; environmental retention = assumed weather resilience; availability = modeled uptime. These are not measured sensor performance.")
st.caption("Hover over the ⓘ icons next to the selectors and results for plain-language explanations.")
st.subheader("Evidence comparison", help="Visual comparison of radar-only and fused synthetic evidence scores.")
st.bar_chart(pd.DataFrame({"Radar only": [radar], "Radar + RF + stereo audio": [fused]}, index=["Synthetic score"]).T)

st.info("Actual aircraft detection: NOT DETERMINED. The probabilities above are illustrative Gaussian-model outputs, not calibrated sensor performance. Research Validation contains a separate synthetic Monte Carlo study.")
st.caption("No RF-emission credit when RF is disabled. Stereo audio does not independently establish range. RCS and clutter CNR map to heuristic scores. The duplicate legacy clutter control was removed; measured clutter statistics and fused detection remain unimplemented.")
st.download_button("Export scenario results CSV", results.to_csv().encode(), file_name="prsim_results.csv", mime="text/csv", help="Download the displayed synthetic result table as a CSV file.")
