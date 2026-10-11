import json
from pathlib import Path
import pandas as pd
import streamlit as st
from experiment_intake import EXPERIMENTS,template,validate_csv,manifest

st.set_page_config(page_title="PRSim | Research Evidence",layout="wide")
st.title("Research Evidence & Collaboration")
tabs=st.tabs(["Published datasets","Evidence & collaboration","Experiment intake"])
with tabs[0]:
    sources=json.loads(Path("data/dataset_registry.json").read_text(encoding="utf-8"))
    st.dataframe(pd.DataFrame(sources)[["name","modality","download_status","license_status"]],hide_index=True)
    source=st.selectbox("Dataset",sources,format_func=lambda x:x["name"])
    st.markdown(f"[Open source]({source['url']})")
    st.write(source["limitations"])
with tabs[1]:
    st.markdown("This research tool requires independent measurements, documented calibration, provenance, uncertainty, and reviewer feedback.")
    st.markdown("[Academic review brief](https://github.com/URHideNSeek/PRSim/blob/main/docs/ACADEMIC_REVIEW_BRIEF.md)")
    st.info("Physical models and experimental validation remain incomplete. Published methods do not automatically validate detection probabilities.")
with tabs[2]:
    st.subheader("E01–E08 measurement intake")
    selected=st.selectbox("Experiment",list(EXPERIMENTS),format_func=lambda key:key+" — "+EXPERIMENTS[key][0])
    st.write("Suggested equipment:",EXPERIMENTS[selected][1])
    st.write("Required columns:",", ".join(EXPERIMENTS[selected][2]))
    st.download_button("CSV template",template(selected),file_name=selected+"_template.csv",mime="text/csv")
    uploaded=st.file_uploader("Upload observations CSV",type=["csv"])
    if uploaded is not None:
        try:
            if uploaded.size>10*1024*1024:raise ValueError("Upload exceeds 10 MB")
            rows=validate_csv(selected,uploaded.getvalue().decode("utf-8-sig"))
            st.success(f"Schema valid: {len(rows)} rows. Calibration not established.")
            st.dataframe(pd.DataFrame(rows).head(200),hide_index=True)
            st.download_button("Export validated manifest",json.dumps(manifest(selected,rows,uploaded.name),indent=2),file_name=selected+"_manifest.json")
            st.download_button("Export normalized CSV",pd.DataFrame(rows).to_csv(index=False),file_name=selected+"_observations.csv")
        except (ValueError,UnicodeError) as exc:
            st.error(str(exc))
st.caption("The intake checks schema and provenance only. It does not modify synthetic probabilities.")
