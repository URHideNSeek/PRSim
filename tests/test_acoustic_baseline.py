import pytest
from acoustic_baseline import parse_feature_csv,evaluate_acoustic_baseline

def example_rows():
    rows=[]
    for session in ("trainA","trainB","holdout"):
        for i in range(130):
            rows.append((session,0,[-25+(i%11)*.1,300+(i%7)*2]))
            rows.append((session,1,[-13+(i%11)*.1,900+(i%7)*2]))
    return rows

def test_baseline_separated_data():
    report=evaluate_acoustic_baseline(example_rows(),"holdout",.01)
    assert report["holdout_pd"]==1
    assert report["holdout_pfa"]<=.01
    assert report["train_background_count"]==260
    assert report["holdout_target_count"]==130

def test_holdout_label_changes_do_not_affect_threshold():
    rows=example_rows()
    a=evaluate_acoustic_baseline(rows,"holdout")
    altered=[(s,1-label,v) if s=="holdout" else (s,label,v) for s,label,v in rows]
    b=evaluate_acoustic_baseline(altered,"holdout")
    assert a["score_threshold"]==b["score_threshold"]

def test_no_cross_session_leakage_from_holdout_features():
    rows=example_rows()
    a=evaluate_acoustic_baseline(rows,"holdout")
    changed=[(s,label,[x+1000 for x in v]) if s=="holdout" else (s,label,v) for s,label,v in rows]
    b=evaluate_acoustic_baseline(changed,"holdout")
    assert a["score_threshold"]==b["score_threshold"]

def test_small_background_rejected():
    rows=[r for r in example_rows() if r[0]=="holdout" or r[1]==1 or r[2][1]<302]
    with pytest.raises(ValueError):evaluate_acoustic_baseline(rows,"holdout",.01)

def test_csv_parser():
    raw="recording_session_id,target_present,rms_dbfs,spectral_centroid_hz,sample_type\na,0,-25,300,R\nb,1,-10,900,R\n"
    assert len(parse_feature_csv(raw))==2
    with pytest.raises(ValueError):parse_feature_csv(raw.replace("b,1","b,2"))
    with pytest.raises(ValueError):parse_feature_csv(raw.replace("b,1,-10,900,R","b,1,-10,900,S"))
