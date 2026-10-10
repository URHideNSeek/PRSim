"""Static Streamlit widget audit: bounds, increments, defaults and documented limitations."""
import ast
from pathlib import Path
import pytest

PAGES=["app.py","pages/01_Research_Validation.py","pages/02_Design_Space.py","pages/03_Evidence_Calibration.py"]
WIDGETS={"slider","select_slider","selectbox","number_input","checkbox"}

def literals(node):
    try:return ast.literal_eval(node)
    except (ValueError,TypeError):return None

def widgets(path):
    tree=ast.parse(Path(path).read_text(encoding="utf-8"))
    for call in ast.walk(tree):
        if not isinstance(call,ast.Call) or not isinstance(call.func,ast.Attribute):continue
        if call.func.attr not in WIDGETS:continue
        label=literals(call.args[0]) if call.args else None
        if not isinstance(label,str):continue
        kwargs={k.arg:literals(k.value) for k in call.keywords if k.arg}
        yield call.func.attr,label,call.args,kwargs

@pytest.mark.parametrize("path",PAGES)
def test_all_pages_parse_and_have_unique_keyword_arguments(path):
    tree=ast.parse(Path(path).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node,ast.Call):
            names=[k.arg for k in node.keywords if k.arg]
            assert len(names)==len(set(names)),path

@pytest.mark.parametrize("path",PAGES)
def test_numeric_slider_bounds_steps_and_defaults(path):
    for kind,label,args,kw in widgets(path):
        if kind not in {"slider","number_input"}:continue
        lo=kw.get("min_value",literals(args[1]) if len(args)>1 else None)
        hi=kw.get("max_value",literals(args[2]) if len(args)>2 else None)
        default=kw.get("value",literals(args[3]) if len(args)>3 else None)
        step=kw.get("step",literals(args[4]) if len(args)>4 else None)
        if lo is None or hi is None:continue
        assert lo<=hi,(path,label)
        if default is not None:assert lo<=default<=hi,(path,label,default)
        if step is not None:assert step>0,(path,label)
        if step is not None and default is not None:
            # Float tolerance avoids false failures for decimal increments.
            assert abs((default-lo)/step-round((default-lo)/step))<1e-6,(path,label)

def test_heading_uses_unique_directions_on_both_pages():
    for path in PAGES[:2]:
        matches=[(args,kw) for kind,label,args,kw in widgets(path)
                 if label=="Target heading relative to sensor (degrees)"]
        assert len(matches)==1
        args,kw=matches[0]
        assert [literals(x) for x in args[1:5]]==[0,345,0,15]

def test_monte_carlo_trial_presets_are_consistent():
    for path in PAGES[1:3]:
        source=Path(path).read_text(encoding="utf-8")
        assert "[100,500,1000,1500,3000,5000]" in source
        assert "value=1500" in source

def test_uncalibrated_inputs_are_explicitly_labeled():
    main=Path("app.py").read_text(encoding="utf-8")
    validation=Path("pages/01_Research_Validation.py").read_text(encoding="utf-8")
    assert "not yet used in detection calculations" in main
    assert "not yet connected to the detection model" in main
    assert "DO NOT incorporate these target inputs" in validation
