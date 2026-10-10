import streamlit as st
import pandas as pd
from optimization import evaluate
st.set_page_config(page_title="PRSim | Design Space",layout="wide")
st.title("Monte Carlo Design-Space Study")
st.warning("Synthetic sensitivity study only. These settings are NOT field-optimized hardware defaults.")
st.markdown("Compare 108 synthetic candidates across six environmental scenarios and RF-emitting / RF-silent targets. Fixed illustrative false-alarm threshold: 5%.")
seed=st.number_input("Random seed",0,999999,42)
trials=st.select_slider("Trials per class and scenario",[300,600,1500,3000],value=1500)
@st.cache_data(show_spinner=False)
def compute(seed,trials):
    return evaluate(seed=int(seed),trials=int(trials))
if st.button("Run parameter sweep",type="primary"):
    with st.spinner("Running synthetic trials..."):
        df=compute(seed,trials)
    st.subheader("Best candidate under illustrative objective")
    st.dataframe(df.head(1),hide_index=True,use_container_width=True)
    st.caption("Objective = 0.55 × mean synthetic Pd + 0.25 × worst-case Pd + 0.10 × availability − 0.10 × resource index.")
    st.subheader("Top 15 candidates")
    st.dataframe(df.head(15),hide_index=True,use_container_width=True)
    st.subheader("Detection evidence vs. resource index")
    st.scatter_chart(df,x="relative_resource_index",y="synthetic_pd",color="fusion_weight")
    st.download_button("Export complete sweep CSV",df.to_csv(index=False),file_name="prsim_parameter_sweep.csv")
    st.info("Do not automatically transfer winning synthetic quality indices to receiver hardware settings. Validate with measured data first.")
else:
    st.info("Select Run parameter sweep to compute candidate ranking.")
