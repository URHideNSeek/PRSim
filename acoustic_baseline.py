"""Transparent acoustic feature baseline with session-separated evaluation.

Experimental benchmark only. NOT a calibrated drone detector. Requires
independently measured real recordings, labels, and a session-separated holdout.
Uses two uncalibrated features: RMS dBFS and spectral centroid Hz.
"""
import csv
import io
import math
import numpy as np
from dataset_validation import wilson_interval

REQUIRED={"recording_session_id","target_present","rms_dbfs","spectral_centroid_hz"}
FEATURES=("rms_dbfs","spectral_centroid_hz")

def parse_feature_csv(text):
    reader=csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
        raise ValueError("Required columns: "+", ".join(sorted(REQUIRED)))
    records=[]
    for i,row in enumerate(reader,2):
        try:
            session=row["recording_session_id"].strip()
            label=int(row["target_present"])
            values=[float(row[key]) for key in FEATURES]
            sample_type=row.get("sample_type","R").strip().upper()
        except (ValueError,TypeError,AttributeError,KeyError) as exc:
            raise ValueError(f"Invalid acoustic feature record at line {i}") from exc
        if not session or label not in (0,1) or sample_type!="R" or not all(math.isfinite(x) for x in values):
            raise ValueError(f"Invalid real-recording label or feature at line {i}")
        records.append((session,label,values))
    if not records:
        raise ValueError("No acoustic features provided")
    return records

def evaluate_acoustic_baseline(records,holdout_session,target_pfa=.05):
    """Train on other sessions only; score a fully independent held-out session.

    Training target and background means define a fixed linear discriminant.
    Background training scores define the decision threshold. No holdout
    labels or features are used to fit, scale or select the threshold.
    """
    if not 0<target_pfa<1:raise ValueError("Target Pfa must be between 0 and 1")
    sessions={r[0] for r in records}
    if holdout_session not in sessions or len(sessions)<2:
        raise ValueError("Select an independent held-out recording session")
    train=[r for r in records if r[0]!=holdout_session]
    test=[r for r in records if r[0]==holdout_session]
    train_bg=np.asarray([v for _,label,v in train if label==0],dtype=float)
    train_target=np.asarray([v for _,label,v in train if label==1],dtype=float)
    test_bg=np.asarray([v for _,label,v in test if label==0],dtype=float)
    test_target=np.asarray([v for _,label,v in test if label==1],dtype=float)
    min_bg=max(20,math.ceil(1/target_pfa))
    if len(train_bg)<min_bg or len(train_target)<10 or len(test_bg)<5 or len(test_target)<5:
        raise ValueError(f"Need >= {min_bg} training backgrounds, 10 training targets, and 5 of each class in holdout")
    center=train_bg.mean(axis=0)
    scale=train_bg.std(axis=0)
    scale=np.where(scale<1e-9,1.0,scale)
    target_mean=(train_target.mean(axis=0)-center)/scale
    direction=target_mean/(np.linalg.norm(target_mean)+1e-12)
    if np.linalg.norm(target_mean)<1e-9:
        raise ValueError("Training classes have indistinguishable feature means")
    def scores(samples):
        return ((samples-center)/scale)@direction
    bg_scores=scores(train_bg)
    threshold=float(np.quantile(bg_scores,1-target_pfa))
    holdout_target_scores=scores(test_target)
    holdout_bg_scores=scores(test_bg)
    hits=int(np.count_nonzero(holdout_target_scores>threshold))
    false_alarms=int(np.count_nonzero(holdout_bg_scores>threshold))
    return {
        "model":"two-feature standardized linear baseline",
        "holdout_session":holdout_session,
        "train_target_count":len(train_target),
        "train_background_count":len(train_bg),
        "holdout_target_count":len(test_target),
        "holdout_background_count":len(test_bg),
        "target_pfa":target_pfa,
        "score_threshold":threshold,
        "holdout_pd":hits/len(test_target),
        "holdout_pfa":false_alarms/len(test_bg),
        "holdout_pd_ci95":wilson_interval(hits,len(test_target)),
        "holdout_pfa_ci95":wilson_interval(false_alarms,len(test_bg)),
        "note":"Exploratory session-separated feature baseline, not validated hardware performance. Repeated segments may be correlated."
    }
