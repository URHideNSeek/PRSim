"""E04: Receiver and Reference validation workspace."""
import streamlit as st
from experiment_pages import render_experiment
st.set_page_config(page_title="PRSim | E04 Receiver and Reference",layout="wide")
render_experiment("E04")
