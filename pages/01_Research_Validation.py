import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PRSim Research Validation",layout="wide")
st.title("PRSim | Monte Carlo Research Validation")
st.warning("Synthetic statistical demonstration only. No calibrated physical detection model or verified SAR/GMTI performance.")
with st.sidebar:
    st.header("Scenario")
    weather=st.selectbox("Weather",["Clear","Inside cloud","Light rain","Heavy rain","Snow","High wind"])
    rcs=st.selectbox("Radar cross-section class",["Small","Medium","Large"])
    rf_emits=st.checkbox("Aircraft emits RF",False)
    acoustic_dbspl=st.selectbox("Acoustic signature (dB SPL)",[45,60,75])
    st.header("Experiment")
    seed=st.number_input("Reproducible random seed",0,999999,42)
    n=st.select_slider("Trials per class",[100,500,1000,3000,5000],value=1000)
    target_pfa=st.select_slider("Target false-alarm rate",[.01,.02,.05,.10,.20],value=.05)
    correlation=st.slider("Shared background correlation",0.,.9,.2,.05)
    st.header("Synthetic sensor quality")
    rsep=st.slider("Radar signal separation",0.,3.,1.1,.1)
    fsep=st.slider("Passive RF signal separation",0.,3.,.7,.1)
    asep=st.slider("Acoustic signal separation",0.,3.,.6,.1)
    rav=st.slider("Radar availability",0.,1.,.85,.05)
    fav=st.slider("RF availability",0.,1.,.75,.05)
    aav=st.slider("Acoustic availability",0.,1.,.8,.05)
    interval=st.slider("Measurement interval (s)",.2,5.,1.,.2)

rng=np.random.default_rng(int(seed))
def generate(present):
    shared=rng.normal(size=n)
    def channel(separation,availability):
        available=rng.random(n)<availability
        value=correlation*shared+np.sqrt(1-correlation**2)*rng.normal(size=n)
        if present: value=value+separation
        return np.where(available,value,0),available
    r,rm=channel(rsep,rav)
    f,fm=channel(fsep,fav if rf_emits else 0.)
    a,am=channel(asep,aav)
    return (r,f,a),(rm,fm,am)
negative=generate(False)
positive=generate(True)
configs={"Radar only":(.999,0.,0.),"Radar + RF":(.8,.2,0.),
         "Radar + audio":(.8,0.,.2),"Full fusion":(.7,.15,.15)}
def evaluate(dataset,weights):
    signals,masks=dataset
    score=sum(w*s for w,s in zip(weights,signals))
    available=np.logical_or.reduce([m for w,m in zip(weights,masks) if w>0])
    return score,available
def wilson(k,total):
    z=1.96;p=k/total;d=1+z*z/total
    c=(p+z*z/(2*total))/d
    h=z*np.sqrt(p*(1-p)/total+z*z/(4*total*total))/d
    return max(0,c-h),min(1,c+h)
rows=[];curves=[]
for name,weights in configs.items():
    noise,nmask=evaluate(negative,weights)
    signal,smask=evaluate(positive,weights)
    active=noise[nmask]
    threshold=float(np.quantile(active,1-target_pfa)) if len(active) else float("inf")
    hits=int(np.sum((signal>=threshold)&smask))
    alarms=int(np.sum((noise>=threshold)&nmask))
    lo,hi=wilson(hits,n)
    pd_hat=hits/n
    rows.append({"Configuration":name,"Synthetic Pd":pd_hat,"95% CI lower":lo,
                 "95% CI upper":hi,"Empirical Pfa":alarms/n,
                 "Availability":float(smask.mean()),"Latency proxy (s)":interval/max(pd_hat,.01),
                 "Tracking uncertainty proxy":1-pd_hat})
    for q in np.linspace(.01,.99,40):
        t=float(np.quantile(active,1-q)) if len(active) else float("inf")
        curves.append({"Configuration":name,"False alarm":float(np.mean((noise>=t)&nmask)),
                       "Detection":float(np.mean((signal>=t)&smask))})
results=pd.DataFrame(rows)
st.subheader("1. Detection probability at a controlled false-alarm threshold")
st.dataframe(results,use_container_width=True,hide_index=True)
st.caption("95% Wilson intervals represent Monte Carlo sampling uncertainty only. Pfa may differ from the requested value when sensors are unavailable.")
st.subheader("2. Receiver operating characteristic")
st.line_chart(pd.DataFrame(curves).pivot_table(index="False alarm",columns="Configuration",values="Detection"))
st.subheader("3–5. Latency, tracking uncertainty and availability")
st.bar_chart(results.set_index("Configuration")[["Latency proxy (s)","Tracking uncertainty proxy","Availability"]])
delta=results.iloc[-1]["Synthetic Pd"]-results.iloc[0]["Synthetic Pd"]
st.subheader("Finding")
st.info(f"At the selected synthetic assumptions, full fusion changes the detection fraction by {delta:+.1%} versus radar-only. This is not a field detection claim.")
st.subheader("Independent SAR / GMTI verification")
c1,c2=st.columns(2)
with c1:
    st.markdown("**SAR evidence requirements**")
    for x in ["Waveform and geometry characterized","Synchronization quantified","Image focus/resolution evaluated","Measured-data validation completed"]:
        st.checkbox(x,key="sar_"+x)
with c2:
    st.markdown("**GMTI evidence requirements**")
    for x in ["Clutter and motion cases defined","Position/velocity errors evaluated","False-alarm and track metrics evaluated","Measured-data validation completed"]:
        st.checkbox(x,key="gmti_"+x)
st.caption("Checklists do not assert SAR or GMTI compliance. Weather, RCS and acoustic dB selections are metadata only until empirically calibrated models are added.")
st.download_button("Download experiment CSV",results.to_csv(index=False),file_name="prsim_monte_carlo.csv")
import json
st.download_button("Download scenario JSON",json.dumps({"weather":weather,"rcs":rcs,"rf_emits":rf_emits,"acoustic_dbspl":acoustic_dbspl,"seed":int(seed),"trials":n,"target_pfa":target_pfa},indent=2),file_name="prsim_scenario.json")
