import streamlit as st
from calibration_data import validate_rows
import csv
import io

st.set_page_config(page_title="PRSim | Motion Calibration",layout="wide")
st.title("Motion Detection Calibration")
st.info("The geometry model already predicts idealized Doppler. This page accepts experimental detector observations needed before speed and heading can be used to estimate defensible detection probabilities.")
st.markdown("Upload a CSV containing **measured_doppler_hz**, **target_present** (0 or 1), **detector_score**, and **session_id**. Include both target-present and target-absent observations from multiple independent sessions.")
uploaded=st.file_uploader("Upload labeled measurement CSV",type=["csv"],help="Only use data you are authorized to process. Do not upload restricted or sensitive recordings to a public deployment.")
if uploaded is not None:
    try:
        text=uploaded.getvalue().decode("utf-8-sig")
        rows=list(csv.DictReader(io.StringIO(text)))
        report=validate_rows(rows)
        st.metric("Observations",report.samples)
        a,b,c=st.columns(3)
        a.metric("Target-present",report.target_present)
        b.metric("Target-absent",report.target_absent)
        c.metric("Independent sessions",report.sessions)
        if report.valid:st.success(report.message)
        else:st.error(report.message)
        st.warning("A passing schema check does not calibrate the model. Detector definition, measurement conditions, session-separated validation, and uncertainty analysis are still required.")
    except (UnicodeError,csv.Error) as exc:
        st.error(f"Unable to parse CSV: {exc}")
st.subheader("Required validation evidence")
st.markdown("Record the external illuminator waveform and availability, receiver timing/noise characteristics, measured clutter statistics, ground-truth target trajectory, calibration methods, and independent holdout evaluation. Report detection probability at a fixed false-alarm rate with uncertainty intervals.")
st.caption("This page does not change PRSim's synthetic detection probabilities. They remain uncalibrated until the required evidence is collected and verified.")
