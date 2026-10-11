"""Controlled RF experiment intake; no instrument automation or radiated test control."""
import json
import pandas as pd
import streamlit as st
from controlled_rf import REQUIRED, parse_controlled_rf, baseline_summary

st.set_page_config(page_title="PRSim | Controlled RF", layout="wide")
st.title("E02 — Controlled RF Characterization")
st.caption("Conducted, shielded receiver characterization using a known source; measurements remain separate from synthetic probabilities.")
st.info("Keysight E8267D Option 520: nominal RF coverage 250 kHz–20 GHz. Installed modulation/baseband options are unverified. This page does not connect to or control an instrument.")
st.warning("A laboratory RF source is not an ambient passive illuminator. Captured measurements do not establish passive-radar detection capability.")
st.subheader("Measurement CSV")
st.write("Required columns: " + ", ".join(REQUIRED))
template = ",".join(REQUIRED) + "\n"
st.download_button("Download controlled RF CSV template", template, file_name="controlled_rf_template.csv", mime="text/csv")
upload = st.file_uploader("Upload controlled RF receiver measurements", type=["csv"])
if upload is not None:
    try:
        if upload.size > 10 * 1024 * 1024:
            raise ValueError("Upload exceeds 10 MB")
        rows = parse_controlled_rf(upload.getvalue().decode("utf-8-sig"))
        df = pd.DataFrame(rows)
        st.success(f"Validated {len(rows)} records (schema only; calibration unverified)")
        st.dataframe(df, hide_index=True)
        plot = df.copy()
        plot["receiver_power_dbm"] = pd.to_numeric(plot["receiver_power_dbm"])
        st.subheader("Measured receiver power over observation order")
        st.line_chart(plot["receiver_power_dbm"])
        result = baseline_summary(rows)
        st.metric("Baseline samples", result["baseline_samples"])
        if result["minimum_sample_count_met"]:
            st.info("Illustrative minimum sample count reached. Baseline stability, independence, and false alarm rates are NOT established.")
        else:
            st.info("Illustrative collection gate not met; collect more independent baseline observations.")
        st.caption(result["note"])
        st.download_button("Export validated summary",json.dumps(result,indent=2),file_name="controlled_rf_summary.json",mime="application/json")
        st.session_state["controlled_rf_intake"] = {"records":len(rows),"status":"schema validated; not calibrated", "summary":result, "rows":rows, "experiment_id":"E02"}
        st.success("Measurements linked to PRSim for descriptive comparison. Synthetic probability inputs remain unchanged.")
    except (UnicodeError,ValueError) as exc:
        st.error(str(exc))
