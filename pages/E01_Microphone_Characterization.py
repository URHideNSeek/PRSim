"""E01: Microphone Characterization validation workspace."""
import streamlit as st
from experiment_pages import render_experiment
st.set_page_config(page_title="PRSim | E01 Microphone Characterization",layout="wide")
render_experiment("E01")
