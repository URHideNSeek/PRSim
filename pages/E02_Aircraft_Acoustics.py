"""E02: Aircraft Acoustics validation workspace."""
import streamlit as st
from experiment_pages import render_experiment
st.set_page_config(page_title="PRSim | E02 Aircraft Acoustics",layout="wide")
render_experiment("E02")
