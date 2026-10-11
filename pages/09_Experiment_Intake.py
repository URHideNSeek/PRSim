"""Experiment E01–E08 CSV intake, separate from reference bibliography."""
import json
import pandas as pd
import streamlit as st
from experiment_intake import EXPERIMENTS,template,validate_csv,manifest
from dataset_validation import evaluate_holdout

st.set_page_config(page_title="PRSim | Experiment Intake",layout="wide")
st.title("Experimental Data Intake")
st.caption("Collect and validate E01–E08 measurement records. Schema checks do not establish calibration or update the live synthetic model.")
selected=st.selectbox("Experiment",list(EXPERIMENTS),format_func=lambda key:key+" — "+EXPERIMENTS[key][0])
st.write("Suggested measurement devices:",EXPERIMENTS[selected][1])
st.write("Required CSV fields:",", ".join(EXPERIMENTS[selected][2]))
st.download_button("Download CSV template",template(selected),file_name=selected+"_template.csv",mime="text/csv")
uploaded=st.file_uploader("Upload observations CSV",type=["csv"])
if uploaded is not None:
    try:
        if uploaded.size>10*1024*1024:raise ValueError("Upload exceeds 10 MB")
        rows=validate_csv(selected,uploaded.getvalue().decode("utf-8-sig"))
        st.success(f"Schema valid: {len(rows)} observations. Measurement calibration remains unverified.")
        st.dataframe(pd.DataFrame(rows).head(200),hide_index=True)
        st.download_button("Export validated manifest",json.dumps(manifest(selected,rows,uploaded.name),indent=2),file_name=selected+"_manifest.json")
        st.download_button("Export normalized observations",pd.DataFrame(rows).to_csv(index=False),file_name=selected+"_observations.csv")
        if selected=="E08":
            st.subheader("E08 independent score evaluation")
            sessions=sorted({r["session_id"] for r in rows})
            if len(sessions)>1:
                holdout=st.selectbox("Held-out session",sessions)
                pfa=st.select_slider("Target false-alarm fraction",[.01,.02,.05,.10,.20],value=.05)
                if st.button("Evaluate held-out scores"):
                    try:
                        scores=[(r["session_id"],int(r["target_present"]),float(r["detector_score"])) for r in rows if r["available"]=="1"]
                        report=evaluate_holdout(scores,pfa,holdout)
                        a,b=st.columns(2)
                        a.metric("Held-out detection fraction",f'{report["holdout_pd"]:.1%}')
                        b.metric("Held-out false-alarm fraction",f'{report["holdout_pfa"]:.1%}')
                        st.download_button("Export E08 evaluation",json.dumps(report,indent=2),file_name="E08_evaluation.json")
                    except ValueError as exc:st.error(str(exc))
            else:st.info("At least two independent sessions required for E08 evaluation.")
    except (ValueError,UnicodeError) as exc:
        st.error(str(exc))
