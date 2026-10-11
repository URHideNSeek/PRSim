import pytest
from design_closure import seek_goal

def test_bounded_search_always_terminates():
    result=seek_goal(desired_pd=.99,target_pfa=.05,seed=42,trials=100,max_stages=1)
    assert len(result["stages"])==1
    assert result["status"] in ("closed_synthetic","not_feasible_within_bounds")
    assert len(result["candidates"])==108

def test_expanded_search_does_not_exceed_stage_cap():
    result=seek_goal(desired_pd=.99,target_pfa=.05,seed=42,trials=100,max_stages=3)
    assert 1<=len(result["stages"])<=3
    assert len(result["candidates"])<=324

def test_goal_closure_meets_both_constraints():
    result=seek_goal(desired_pd=.5,target_pfa=.05,seed=42,trials=100,max_stages=3)
    if result["status"]=="closed_synthetic":
        winner=result["winner"]
        assert winner["synthetic_pd"]>=.5
        assert winner["empirical_pfa"]<=.05+max(.01,2/100)
        assert result["gap"]==0
    else:
        assert result["winner"] is None
        assert result["gap"]>=0

def test_invalid_goals_rejected():
    for goal in (-.1,0,1.1):
        with pytest.raises(ValueError):seek_goal(desired_pd=goal)
    with pytest.raises(ValueError):seek_goal(max_stages=4)

def test_search_is_reproducible():
    a=seek_goal(desired_pd=.8,seed=9,trials=100,max_stages=2)
    b=seek_goal(desired_pd=.8,seed=9,trials=100,max_stages=2)
    assert a["status"]==b["status"]
    assert a["stages"]==b["stages"]
