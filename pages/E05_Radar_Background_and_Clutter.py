"""E05: Radar Background and Clutter validation workspace."""
import streamlit as st
from experiment_pages import render_experiment
st.set_page_config(page_title="PRSim | E05 Radar Background and Clutter",layout="wide")
render_experiment("E05")
