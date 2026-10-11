"""Reproducible evaluation of independently supplied labeled detector scores.

This does not convert arbitrary scores into validated sensor performance.
Data must be genuinely measured, with independent ground-truth labels.
Threshold is selected using only target-absent training sessions; all metrics
are computed on separate held-out sessions.
"""
import csv
import io
import math
import numpy as np

FIELDS=("session_id","target_present","detector_score")
def parse_labeled_scores(text):
    reader=csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or not set(FIELDS).issubset(reader.fieldnames):
        raise ValueError("Required columns: session_id, target_present, detector_score")
    rows=[]
    for i,row in enumerate(reader,2):
        try:
            session=row["session_id"].strip()
            label=int(row["target_present"])
            score=float(row["detector_score"])
        except (ValueError,TypeError,AttributeError) as exc:
            raise ValueError(f"Invalid record on line {i}") from exc
        if not session or label not in (0,1) or not math.isfinite(score):
            raise ValueError(f"Invalid session, label or score on line {i}")
        rows.append((session,label,score))
    if not rows:
        raise ValueError("No observations found")
    return rows

def evaluate_holdout(rows,target_pfa=.05,holdout_session=None):
    if not 0<target_pfa<1:
        raise ValueError("Target false-alarm fraction must be between 0 and 1")
    sessions=sorted({r[0] for r in rows})
    if len(sessions)<2:
        raise ValueError("At least two independent sessions required")
    holdout_session=holdout_session or sessions[-1]
    if holdout_session not in sessions:
        raise ValueError("Unknown holdout session")
    train=[r for r in rows if r[0]!=holdout_session]
    test=[r for r in rows if r[0]==holdout_session]
    background=[score for _,label,score in train if label==0]
    target=[score for _,label,score in test if label==1]
    negative=[score for _,label,score in test if label==0]
    if len(background)<20 or not target or not negative:
        raise ValueError("Need >=20 training background scores and both classes in holdout session")
    # Empirical quantile; do not fit or tune on holdout data.
    threshold=float(np.quantile(background,1-target_pfa))
    hits=sum(score>threshold for score in target)
    alarms=sum(score>threshold for score in negative)
    return {"holdout_session":holdout_session,"training_background":len(background),
            "holdout_targets":len(target),"holdout_background":len(negative),
            "threshold":threshold,"holdout_pd":hits/len(target),
            "holdout_pfa":alarms/len(negative),
            "target_pfa":target_pfa,
            "note":"Empirical holdout statistics only; not transferable to other hardware or environments."}
