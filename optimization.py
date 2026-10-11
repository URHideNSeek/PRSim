"""Synthetic Monte Carlo parameter sweep; NOT a field-hardware optimizer."""
import numpy as np
import pandas as pd
WEATHER={'Clear':(1,1,1),'Inside cloud':(.95,.96,.95),'Light rain':(.82,.95,.86),'Heavy rain':(.60,.86,.70),'Snow':(.75,.89,.79),'High wind':(.55,.94,.75)}
def evaluate(seed=42,trials=1500,radar_levels=(.4,.6,.8),rf_levels=(.3,.6,.9),audio_levels=(.3,.6,.9),target_pfa=.05):
    if not 0<target_pfa<1:raise ValueError("Target false-alarm rate must be between 0 and 1")
    rows=[]
    for r in radar_levels:
      for f in rf_levels:
       for a in audio_levels:
        for w in [0,.2,.4]:
         pds=[];fas=[];avail=[]
         for wi,(weather,(ar,fr,rr)) in enumerate(WEATHER.items()):
          for emits in [False,True]:
           rng=np.random.default_rng(seed+wi*10+int(emits))
           common=rng.normal(size=(2,trials))
           noise=rng.normal(size=(2,trials,3))
           samples=.2*common[:,:,None]+np.sqrt(1-.2**2)*noise
           samples[1]+=np.array([r*rr,f*fr if emits else 0,a*ar])
           mask=rng.random((2,trials,3))<np.array([.85,.75 if emits else 0,.8])
           samples*=mask
           score=samples[:,:,0]+w*(samples[:,:,1]+samples[:,:,2])/2
           valid=mask[:,:,0] | ((mask[:,:,1]|mask[:,:,2]) if w else False)
           null=score[0][valid[0]]
           threshold=np.quantile(null,1-target_pfa) if len(null) else np.inf
           pds.append(np.mean((score[1]>=threshold)&valid[1]))
           fas.append(np.mean((score[0]>=threshold)&valid[0]))
           avail.append(np.mean(valid[1]))
         cost=(r+f+a)/3
         rows.append(dict(radar_quality=r,rf_quality=f,audio_quality=a,fusion_weight=w,synthetic_pd=np.mean(pds),worst_case_pd=np.min(pds),empirical_pfa=np.mean(fas),availability=np.mean(avail),relative_resource_index=cost))
    df=pd.DataFrame(rows)
    df['objective']=.55*df.synthetic_pd+.25*df.worst_case_pd+.1*df.availability-.1*df.relative_resource_index
    return df.sort_values('objective',ascending=False).reset_index(drop=True)
