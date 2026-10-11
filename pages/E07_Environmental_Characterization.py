"""E07: Environmental Characterization validation workspace."""
import streamlit as st
from experiment_pages import render_experiment
st.set_page_config(page_title="PRSim | E07 Environmental Characterization",layout="wide")
render_experiment("E07")
