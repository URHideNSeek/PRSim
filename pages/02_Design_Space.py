import streamlit as st
import pandas as pd
from design_closure import seek_goal

st.set_page_config(page_title="PRSim | Design Space",layout="wide")
st.title("Goal-Seeking Design Space")
st.caption("Uses the exact same synthetic probability calculation as the main PRSim dashboard for identical scenario inputs.")
st.warning("Synthetic sensitivity study only. A closed synthetic goal is not a validated aircraft detection capability.")
st.markdown("The search starts with 81 configurations and expands assumed normalized sensor-quality settings only if the goal is not met. It stops when the target is reached or the configured search bounds are exhausted. Repeating identical settings does not create new physical evidence.")

seed=st.number_input("Random seed",0,999999,42,help="Reproducible random generator seed.")
trials=st.select_slider("Trials per class and scenario",[100,500,1000,1500,3000,5000],value=1500,help="Legacy setting retained for compatibility. Shared analytic probability calculations do not depend on trial count.")
threshold=st.slider("Researcher-defined evidence threshold",.05,.95,.35,.05,help="Same normalized evidence threshold used on the main dashboard. The false-alarm constraint must also be satisfied.")
desired_pd=st.slider("Desired synthetic detection probability (%)",50,99,80,1,help="Required mean detection fraction across scenarios. This is an assumed-model goal, not field performance.")
target_pfa=st.select_slider("Maximum target false-alarm rate",[.01,.02,.05,.10,.20],value=.05,help="Training background quantile target; empirical Pfa is separately checked with finite-sample tolerance.")
max_stages=st.select_slider("Maximum search stages",[1,2,3],value=3,help="1 = original assumptions only; 2 = expanded; 3 = exploratory upper bounds. Search always terminates.")

@st.cache_data(show_spinner=False)
def compute(seed,trials,desired_pd,target_pfa,max_stages,threshold):
    return seek_goal(desired_pd=desired_pd/100,target_pfa=target_pfa,seed=int(seed),trials=int(trials),max_stages=max_stages,threshold=threshold)

if st.button("Run goal-seeking search",type="primary"):
    with st.spinner("Evaluating bounded synthetic design space..."):
        result=compute(seed,trials,desired_pd,target_pfa,max_stages,threshold)
    st.session_state["design_closure_result"]=result
    st.session_state["design_closure_inputs"]=(seed,trials,desired_pd,target_pfa,max_stages,threshold)

if "design_closure_result" in st.session_state:
    if st.session_state.get("design_closure_inputs")!=(seed,trials,desired_pd,target_pfa,max_stages):
        st.info("Inputs changed. Run the search again to evaluate the new goal.")
    else:
        result=st.session_state["design_closure_result"]
        st.subheader("Closure result")
        a,b,c=st.columns(3)
        a.metric("Status","GOAL MET" if result["status"]=="closed_synthetic" else "NOT FEASIBLE")
        b.metric("Stages evaluated",len(result["stages"]))
        c.metric("Gap to desired mean Pd",f'{result["gap"]:.1%}')
        if result["status"]=="closed_synthetic":st.success(result["message"])
        else:st.warning(result["message"])
        st.dataframe(pd.DataFrame(result["stages"]),hide_index=True,use_container_width=True)
        candidate=result.get("winner") or result.get("best")
        st.subheader("Selected candidate or closest available result")
        st.dataframe(pd.DataFrame([candidate]),hide_index=True,use_container_width=True)
        st.caption("Normalized sensor quality is a synthetic assumption, not a verified receiver setting. Larger assumed separations cannot be claimed without measured evidence.")
        st.subheader("Candidate comparison")
        candidates=result["candidates"]
        st.scatter_chart(candidates,x="relative_resource_index",y="synthetic_pd",color="stage_name")
        st.download_button("Export full candidate search",candidates.to_csv(index=False),file_name="prsim_design_closure.csv",mime="text/csv")
        st.info("Mean Pd is averaged over weather and RF-emission scenarios. Worst-case Pd is separately reported; meeting the mean does not imply meeting the goal in every scenario.")
else:
    st.info("Select Run goal-seeking search to evaluate feasibility and stop at the first successful stage.")
