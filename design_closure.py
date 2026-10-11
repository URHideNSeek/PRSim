"""Goal-seeking design-space closure for the SYNTHETIC PRSim optimizer.

Each stage expands allowed signal-separation assumptions. A target is closed
only when mean synthetic Pd meets the target AND empirical Pfa is within the
specified tolerance. Failure after the last stage is an explicit infeasible
result, not a reason to loop forever. Not hardware optimization.
"""
from optimization import evaluate
import pandas as pd

STAGES=(
    ("Original assumptions",(0.4,0.6,0.8),(0.3,0.6,0.9),(0.3,0.6,0.9)),
    ("Expanded assumptions",(0.8,1.2,1.6),(0.6,1.0,1.4),(0.6,1.0,1.4)),
    ("Exploratory upper bounds",(1.6,2.2,3.0),(1.4,2.2,3.0),(1.4,2.2,3.0)),
)
def seek_goal(desired_pd=.8,target_pfa=.05,seed=42,trials=1500,max_stages=3):
    if not 0<desired_pd<=1 or not 0<target_pfa<1:
        raise ValueError("Probabilities must be between zero and one")
    if max_stages not in (1,2,3):
        raise ValueError("max_stages must be 1, 2 or 3")
    stages=[]
    frames=[]
    for index,(label,r,f,a) in enumerate(STAGES[:max_stages],1):
        df=evaluate(seed=seed,trials=trials,radar_levels=r,rf_levels=f,audio_levels=a,target_pfa=target_pfa)
        df=df.assign(stage=index,stage_name=label)
        frames.append(df)
        feasible=df[(df.synthetic_pd>=desired_pd)&(df.empirical_pfa<=target_pfa+max(.01,2/trials))]
        stages.append({"stage":index,"name":label,"candidates":len(df),
                       "best_mean_pd":float(df.synthetic_pd.max()),
                       "best_worst_case_pd":float(df.worst_case_pd.max()),
                       "feasible":len(feasible)})
        if len(feasible):
            all_df=pd.concat(frames,ignore_index=True)
            winner=feasible.sort_values(["relative_resource_index","synthetic_pd"],ascending=[True,False]).iloc[0]
            return {"status":"closed_synthetic","winner":winner.to_dict(),"stages":stages,
                    "candidates":all_df,"gap":0.0,
                    "message":"Synthetic goal reached under assumed signal separations. Not validated field performance."}
    all_df=pd.concat(frames,ignore_index=True)
    best=all_df.sort_values("synthetic_pd",ascending=False).iloc[0]
    return {"status":"not_feasible_within_bounds","winner":None,"best":best.to_dict(),
            "stages":stages,"candidates":all_df,
            "gap":max(0.0,desired_pd-float(best.synthetic_pd)),
            "message":"Search exhausted. The target was not met within the stated synthetic assumptions and availability limits."}
