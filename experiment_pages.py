"""Reusable E01–E08 research experiment page renderer."""
import json
import pandas as pd
import streamlit as st
from experiment_intake import EXPERIMENTS,template,validate_csv,manifest
from dataset_validation import evaluate_holdout
from experiment_protocols import PROTOCOLS

def render_experiment(selected):
    st.title(selected+" — "+EXPERIMENTS[selected][0])
    st.caption("Measurement intake; schema checks do not establish calibration or modify the live synthetic model.")
    title,procedure,measurements,instruments,impact=PROTOCOLS[selected]
    st.subheader(title)
    st.write("Collection procedure:",procedure)
    st.write("Measurements:",measurements)
    st.write("Instruments:",instruments)
    st.info("Main-page impact: "+impact)
    st.write("Suggested measurement devices:",EXPERIMENTS[selected][1])
    st.write("Required CSV fields:",", ".join(EXPERIMENTS[selected][2]))
    st.download_button("Download CSV template",template(selected),file_name=selected+"_template.csv",mime="text/csv",key="template_"+selected)
    uploaded=st.file_uploader("Upload observations CSV",type=["csv"],key="upload_"+selected)
    if uploaded is not None:
        try:
            if uploaded.size>10*1024*1024:raise ValueError("Upload exceeds 10 MB")
            rows=validate_csv(selected,uploaded.getvalue().decode("utf-8-sig"))
            st.success(f"Schema valid: {len(rows)} observations. Measurement calibration remains unverified.")
            st.session_state["intake_"+selected]={"records":len(rows),"filename":uploaded.name,"status":"schema validated; not calibrated"}
            st.dataframe(pd.DataFrame(rows).head(200),hide_index=True)
            st.download_button("Export validated manifest",json.dumps(manifest(selected,rows,uploaded.name),indent=2),file_name=selected+"_manifest.json",key="manifest_"+selected)
            st.download_button("Export normalized observations",pd.DataFrame(rows).to_csv(index=False),file_name=selected+"_observations.csv",key="observations_"+selected)
            if selected=="E08":
                st.subheader("E08 independent score evaluation")
                sensor=st.selectbox("Sensor ID",sorted({r["sensor_id"] for r in rows}),key="e08_sensor")
                sensor_rows=[r for r in rows if r["sensor_id"]==sensor]
                sessions=sorted({r["session_id"] for r in sensor_rows})
                if len(sessions)>1:
                    holdout=st.selectbox("Held-out session",sessions,key="e08_holdout")
                    pfa=st.select_slider("Target false-alarm fraction",[.01,.02,.05,.10,.20],value=.05,key="e08_pfa")
                    if st.button("Evaluate held-out scores",key="e08_run"):
                        try:
                            scores=[(r["session_id"],int(r["target_present"]),float(r["detector_score"])) for r in sensor_rows if r["available"]=="1"]
                            report=evaluate_holdout(scores,pfa,holdout)
                            st.session_state["validation_e08"]={**report,"source":"E08","scope":"available observations; session-held-out","sensor_id":sensor}
                            a,b=st.columns(2)
                            a.metric("Held-out detection fraction",f'{report["holdout_pd"]:.1%}')
                            b.metric("Held-out false-alarm fraction",f'{report["holdout_pfa"]:.1%}')
                            st.download_button("Export E08 evaluation",json.dumps(report,indent=2),file_name="E08_evaluation.json",key="e08_export")
                        except ValueError as exc:st.error(str(exc))
                else:st.info("At least two independent sessions required for E08 evaluation.")
        except (ValueError,UnicodeError) as exc:
            st.error(str(exc))
