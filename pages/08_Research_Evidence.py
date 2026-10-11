"""Traceable research references, source material and datasets for PRSim."""
import json
import pandas as pd
import streamlit as st
from reference_catalog import REFERENCES

st.set_page_config(page_title="PRSim | References & Datasets",layout="wide")
st.title("Publications, References & Datasets")
st.markdown("This page documents the scientific publications, technical standards, statistical methods, external datasets, and **internal assumptions** behind PRSim. A citation is not proof that its equations or measurements have been integrated.")
st.info("Current detection evidence and probabilities are synthetic. No external dataset has yet been used to calibrate the live PRSim detection model.")

areas=["All"]+sorted({r["area"] for r in REFERENCES})
kinds=["All"]+sorted({r["kind"] for r in REFERENCES})
left,right=st.columns(2)
area=left.selectbox("Research area",areas,help="Filter references by sensing modality or methodology.")
kind=right.selectbox("Source type",kinds,help="Separate published standards and datasets from internal modeling assumptions.")
items=[r for r in REFERENCES if (area=="All" or r["area"]==area) and (kind=="All" or r["kind"]==kind)]
st.metric("References shown",len(items))
for record in items:
    with st.container(border=True):
        st.markdown(f"**[{record['title']}]({record['url']})**")
        st.caption(f"{record['kind']} · {record['area']} · {record['status']}")
        st.write("How PRSim uses it:",record["use"])
        st.write("Implementation:",record["location"])
        st.write("Limitations:",record["limitation"])

st.subheader("Evidence maturity")
summary=pd.DataFrame([{"Source":r["title"],"Category":r["kind"],"Status":r["status"],"Code reference":r["location"]} for r in REFERENCES])
st.dataframe(summary,hide_index=True,use_container_width=True)
st.download_button("Export reference catalog (CSV)",summary.to_csv(index=False),file_name="prsim_reference_catalog.csv",mime="text/csv")
st.download_button("Export reference catalog (JSON)",json.dumps(REFERENCES,indent=2),file_name="prsim_reference_catalog.json",mime="application/json")

st.subheader("Research documentation")
st.markdown("[Academic review brief](https://github.com/URHideNSeek/PRSim/blob/main/docs/ACADEMIC_REVIEW_BRIEF.md) · [Scientific remediation register](https://github.com/URHideNSeek/PRSim/blob/main/docs/SCIENTIFIC_REMEDIATION.md) · [PRSim source repository](https://github.com/URHideNSeek/PRSim)")
st.caption("Source and implementation statuses describe repository code, not an independent literature audit. Licensing and applicability of external datasets must be checked before use.")
