"""Regression check for Streamlit help tooltips and valid Python syntax."""
import ast
from pathlib import Path

def test_app_parses_and_has_no_duplicate_keyword_arguments():
    tree=ast.parse(Path("app.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node,ast.Call):
            names=[kw.arg for kw in node.keywords if kw.arg is not None]
            assert len(names)==len(set(names))

def test_selector_help_is_hover_only():
    tree=ast.parse(Path("app.py").read_text(encoding="utf-8"))
    controls={"selectbox","select_slider","slider","checkbox"}
    found=0
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Attribute):
            continue
        if node.func.attr in controls:
            found+=1
            assert any(k.arg=="help" and isinstance(k.value,ast.Constant) and k.value.value for k in node.keywords)
    assert found>=28
    assert "with st.expander" not in Path("app.py").read_text(encoding="utf-8")
