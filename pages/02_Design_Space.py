import streamlit as st
import pandas as pd
from optimization import evaluate
st.set_page_config(page_title="PRSim | Design Space",layout="wide")
st.title("Monte Carlo Design-Space Study")
st.warning("Synthetic sensitivity study only. These settings are NOT field-optimized hardware defaults.")
st.markdown("Compare 108 synthetic candidates across six environmental scenarios and RF-emitting / RF-silent targets. Fixed illustrative false-alarm threshold: 5%.")
seed=st.number_input("Random seed",0,999999,42)
trials=st.select_slider("Trials per class and scenario",[100,500,1000,1500,3000,5000],value=1500,help="Number of Monte Carlo trials per target-present and target-absent condition, matching Research Validation presets.")
desired_pd=st.slider("Desired synthetic detection probability (%)",50,99,80,1,help="Minimum mean synthetic detection fraction requested across the design-space scenarios. This is a screening goal, not a guaranteed real-world detection probability.")
@st.cache_data(show_spinner=False)
def compute(seed,trials):
    return evaluate(seed=int(seed),trials=int(trials))
if st.button("Run parameter sweep",type="primary"):
    with st.spinner("Running synthetic trials..."):
        df=compute(seed,trials)
    qualifying=df[df["synthetic_pd"]>=desired_pd/100]
    st.metric("Candidates meeting desired synthetic Pd",f"{len(qualifying)} / {len(df)}")
    if qualifying.empty:
        st.warning("No synthetic candidate meets the selected probability goal. Showing the highest-ranked candidates for comparison, not a compliant solution.")
    else:
        st.success("Some candidates meet the selected synthetic mean Pd goal. This does not establish field performance.")
    st.subheader("Best candidate meeting goal (if any)")
    st.dataframe(qualifying.head(1) if not qualifying.empty else df.head(1),hide_index=True,use_container_width=True)
    st.caption("Objective = 0.55 × mean synthetic Pd + 0.25 × worst-case Pd + 0.10 × availability − 0.10 × resource index.")
    st.subheader("Top 15 candidates")
    st.dataframe(qualifying.head(15) if not qualifying.empty else df.head(15),hide_index=True,use_container_width=True)
    st.subheader("Detection evidence vs. resource index")
    st.scatter_chart(df,x="relative_resource_index",y="synthetic_pd",color="fusion_weight")
    st.download_button("Export complete sweep CSV",df.to_csv(index=False),file_name="prsim_parameter_sweep.csv")
    st.info("Do not automatically transfer winning synthetic quality indices to receiver hardware settings. Validate with measured data first.")
else:
    st.info("Select Run parameter sweep to compute candidate ranking.")
