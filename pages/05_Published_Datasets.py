"""Published dataset registry and measured-score evaluation interface."""
import json
from pathlib import Path
import streamlit as st
import pandas as pd
from dataset_validation import parse_labeled_scores,evaluate_holdout

st.set_page_config(page_title="PRSim | Published Datasets",layout="wide")
st.title("Published Datasets & Validation")
st.caption("External research sources are cataloged, not downloaded or treated as calibrated PRSim measurements.")
registry=json.loads(Path("data/dataset_registry.json").read_text(encoding="utf-8"))
st.dataframe(pd.DataFrame(registry)[["name","modality","download_status","license_status","limitations"]],hide_index=True,use_container_width=True)
source=st.selectbox("Inspect dataset source",registry,format_func=lambda d:d["name"])
st.markdown(f"**Source:** [{source['url']}]({source['url']})")
st.write("Intended use:",source["use"])
st.write("Format:",source["data_format"])
st.warning("Verify license, measurement conditions, ground truth and permissions before downloading, redistributing or drawing performance conclusions.")
st.divider()
st.subheader("Independent labeled-score validation")
st.markdown("Upload a **CSV of real detector observations**, not raw audio or RF. Required fields: `session_id,target_present,detector_score`. Use one session as a held-out test set. The remaining sessions supply the background threshold. Do not select or tune a threshold using held-out results.")
file=st.file_uploader("Upload detector-score CSV",type=["csv"],help="Use only authorized, nonrestricted datasets. Uploaded data are processed in this app session.")
target_pfa=st.select_slider("Target false-alarm fraction",options=[.01,.02,.05,.10,.20],value=.05,help="Sets a threshold from training-session background scores only.")
if file is not None:
    try:
        rows=parse_labeled_scores(file.getvalue().decode("utf-8-sig"))
        sessions=sorted({r[0] for r in rows})
        selected=st.selectbox("Held-out session",sessions)
        report=evaluate_holdout(rows,target_pfa,selected)
        a,b,c=st.columns(3)
        a.metric("Held-out detection fraction",f"{report['holdout_pd']:.1%}")
        b.metric("Held-out false-alarm fraction",f"{report['holdout_pfa']:.1%}")
        c.metric("Training threshold",f"{report['threshold']:.3f}")
        st.caption(f"Training background observations: {report['training_background']}; held-out target observations: {report['holdout_targets']}; held-out background observations: {report['holdout_background']}.")
        pd_lo,pd_hi=report["holdout_pd_ci95"]
        fa_lo,fa_hi=report["holdout_pfa_ci95"]
        st.caption(f"95% Wilson interval — detection: {pd_lo:.1%}–{pd_hi:.1%}; false alarm: {fa_lo:.1%}–{fa_hi:.1%}. Assumes independent trials.")
        st.info(report["note"])
        st.download_button("Download evaluation JSON",json.dumps(report,indent=2),file_name="prsim_holdout_report.json",mime="application/json")
    except (UnicodeError,ValueError) as exc:
        st.error(str(exc))
st.caption("This page does not automatically update the main PRSim synthetic probability displays. A detector-specific calibration and applicability review are required before connecting models.")
