"""Research-only acoustic baseline from independently supplied WAV features."""
import json
import streamlit as st
from experiment_protocols import EXTRA
from acoustic_baseline import parse_feature_csv,evaluate_acoustic_baseline

st.set_page_config(page_title="PRSim | Acoustic Baseline",layout="wide")
st.title("E11 — Acoustic Baseline")
protocol=EXTRA["baseline"]
st.markdown("**Collection procedure:** "+protocol[1])
st.markdown("**Required data:** "+protocol[2])
st.markdown("**Instruments:** "+protocol[3])
st.info("Main-page probability impact: "+protocol[4])
st.warning("Exploratory benchmark only. The model is not calibrated for actual microphone sensitivity, drone detection range, or field probability of detection.")
st.markdown("Upload the **WAV feature inspection CSV** exported from DDL Acoustic Intake, or an equivalent dataset of measured recordings. Required columns: `recording_session_id`, `target_present`, `rms_dbfs`, `spectral_centroid_hz`. Include independent real recording sessions with target-present and target-absent clips. The 20-file DDL preview limit usually will not provide enough training observations; use a separately processed and validated dataset for this benchmark.")
st.download_button("Download input CSV template","recording_session_id,target_present,rms_dbfs,spectral_centroid_hz\\n".replace("\\n","\n"),file_name="acoustic_features_template.csv",mime="text/csv")
uploaded=st.file_uploader("Upload acoustic features CSV",type=["csv"],help="Only permitted, nonrestricted recordings. No raw audio is needed for this evaluation.")
pfa=st.select_slider("Target false-alarm fraction",options=[.01,.02,.05,.10,.20],value=.05,help="Selects a threshold using training-session background features only.")
if uploaded is not None:
    try:
        rows=parse_feature_csv(uploaded.getvalue().decode("utf-8-sig"))
        sessions=sorted({r[0] for r in rows})
        holdout=st.selectbox("Independent held-out recording session",sessions)
        if st.button("Evaluate baseline",type="primary"):
            report=evaluate_acoustic_baseline(rows,holdout,pfa)
            a,b,c=st.columns(3)
            a.metric("Held-out detection fraction",f"{report['holdout_pd']:.1%}")
            b.metric("Held-out false-alarm fraction",f"{report['holdout_pfa']:.1%}")
            c.metric("Training decision threshold",f"{report['score_threshold']:.3f}")
            dlo,dhi=report["holdout_pd_ci95"]
            flo,fhi=report["holdout_pfa_ci95"]
            st.caption(f"95% Wilson intervals: detection {dlo:.1%}–{dhi:.1%}; false alarms {flo:.1%}–{fhi:.1%}. Assumes independent observations.")
            st.info(report["note"])
            st.download_button("Export baseline evaluation JSON",json.dumps(report,indent=2,default=float),file_name="prsim_acoustic_baseline.json",mime="application/json")
    except (ValueError,UnicodeError) as exc:
        st.error(str(exc))
st.caption("The classifier is a simple standardized two-feature linear discriminant. It does not incorporate sound propagation, microphone spacing, weather, or hardware calibration. Results do not update the main simulator's synthetic detection probabilities.")
