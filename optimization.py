"""Synthetic design sweep using exactly the main PRSim probability contract.

No separate Monte Carlo detection distributions. 'trials' and 'seed' remain
accepted for API compatibility, but do not change analytic probabilities.
A stage changes normalized sensor-quality assumptions, not physical hardware.
"""
import numpy as np
import pandas as pd
from model import Scenario,WEATHER
from shared_probability import scenario_probabilities

def evaluate(seed=42,trials=1500,radar_levels=(.4,.6,.8),
             rf_levels=(.3,.6,.9),audio_levels=(.3,.6,.9),
             target_pfa=.05,threshold=.30):
    if not 0<target_pfa<1:raise ValueError("Target false-alarm rate must be between 0 and 1")
    if not 0<=threshold<=1:raise ValueError("Threshold must be between zero and one")
    rows=[]
    for r in radar_levels:
      for f in rf_levels:
       for a in audio_levels:
        for w in (0,.2,.4):
         pds=[];fas=[];avail=[]
         for weather in WEATHER:
          for emits in (False,True):
           s=Scenario(weather=weather,emits=emits,rcs_m2=.1,range_m=250,
                      reference=min(1.,r),rf_sensitivity=min(1.,f),
                      microphone_quality=min(1.,a),fusion_weight=w,
                      clutter=0.,threshold=threshold)
           out=scenario_probabilities(s,threshold)
           pds.append(out["fused_pd"] or 0.)
           fas.append(out["false_alarm_probability"])
           avail.append(out["fused_availability"])
         cost=(r+f+a)/3
         rows.append(dict(radar_quality=r,rf_quality=f,audio_quality=a,
              fusion_weight=w,synthetic_pd=float(np.mean(pds)),
              worst_case_pd=float(np.min(pds)),empirical_pfa=float(np.mean(fas)),
              availability=float(np.mean(avail)),relative_resource_index=cost,
              evidence_threshold=threshold,model="shared Gaussian scenario"))
    df=pd.DataFrame(rows)
    df["objective"]=.55*df.synthetic_pd+.25*df.worst_case_pd+.1*df.availability-.1*df.relative_resource_index
    return df.sort_values("objective",ascending=False).reset_index(drop=True)
