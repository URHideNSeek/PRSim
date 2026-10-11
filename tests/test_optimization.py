import pandas as pd
from optimization import evaluate

def test_optimizer_candidate_count_and_order():
    df=evaluate(seed=42,trials=100)
    assert len(df)==81
    assert df.objective.is_monotonic_decreasing
    assert df[['synthetic_pd','worst_case_pd','empirical_pfa','availability']].apply(lambda col:col.between(0,1).all()).all()

def test_optimizer_seed_reproducibility():
    a=evaluate(seed=5,trials=100)
    b=evaluate(seed=5,trials=100)
    pd.testing.assert_frame_equal(a,b)

def test_optimizer_seed_does_not_change_analytic_probabilities():
    a=evaluate(seed=5,trials=100)
    b=evaluate(seed=6,trials=100)
    pd.testing.assert_frame_equal(a,b)

def test_optimizer_trial_count_does_not_change_analytic_probabilities():
    a=evaluate(seed=5,trials=100)
    b=evaluate(seed=5,trials=120)
    assert not a.equals(b)
