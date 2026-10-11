import json
from pathlib import Path
import pytest
from dataset_validation import parse_labeled_scores,evaluate_holdout

def rows():
    result=[]
    for session in ("train","holdout"):
        for i in range(30):
            result.append((session,0,i/100))
            result.append((session,1,.6+i/100))
    return result

def test_registry_has_sources_and_no_false_import_claims():
    registry=json.loads(Path("data/dataset_registry.json").read_text(encoding="utf-8"))
    assert len(registry)>=3
    assert all(x["url"].startswith("https://") and x["license_status"] for x in registry)
    assert all("not imported" in x["download_status"].lower() or "not integrated" in x["download_status"].lower() for x in registry)

def test_holdout_perfectly_separated():
    report=evaluate_holdout(rows(),.05,"holdout")
    assert report["holdout_pd"]==1.0
    assert 0<=report["holdout_pfa"]<=1
    assert report["training_background"]==30

def test_missing_holdout_class_rejected():
    data=[r for r in rows() if r[0]=="train" or r[1]==1]
    with pytest.raises(ValueError):evaluate_holdout(data,.05,"holdout")

def test_no_cross_session_holdout_leakage():
    a=evaluate_holdout(rows(),.05,"holdout")
    altered=[(session,label,score+100 if session=="holdout" else score) for session,label,score in rows()]
    b=evaluate_holdout(altered,.05,"holdout")
    assert a["threshold"]==b["threshold"]

def test_parse_csv_and_reject_invalid_label():
    text="session_id,target_present,detector_score\ntrain,0,0.1\nholdout,1,0.8\n"
    assert len(parse_labeled_scores(text))==2
    with pytest.raises(ValueError):parse_labeled_scores(text.replace("holdout,1","holdout,2"))

def test_wilson_intervals_bounded_and_cover_estimates():
    from dataset_validation import wilson_interval
    for n in [1,10,30,100,1000]:
        for hits in [0,n//2,n]:
            lo,hi=wilson_interval(hits,n)
            assert 0<=lo<=hits/n<=hi<=1

def test_holdout_report_includes_confidence_intervals():
    report=evaluate_holdout(rows(),.05,"holdout")
    assert "holdout_pd_ci95" in report
    assert "holdout_pfa_ci95" in report

def test_one_percent_false_alarm_requires_more_background_samples():
    with pytest.raises(ValueError,match="100 training background"):
        evaluate_holdout(rows(),.01,"holdout")
