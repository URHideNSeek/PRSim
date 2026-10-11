"""E08: Multisensor Evaluation validation workspace."""
import streamlit as st
from experiment_pages import render_experiment
st.set_page_config(page_title="PRSim | E08 Multisensor Evaluation",layout="wide")
render_experiment("E08")
