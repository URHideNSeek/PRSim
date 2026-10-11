"""E03: Passive RF Background validation workspace."""
import streamlit as st
from experiment_pages import render_experiment
st.set_page_config(page_title="PRSim | E03 Passive RF Background",layout="wide")
render_experiment("E03")
