"""PRSim Streamlit entrypoint; retains the existing Community Cloud app.py deployment path."""
import streamlit as st

pages = [
    st.Page("PRSim.py", title="PRSim", icon=":material/radar:", default=True),
    st.Page("pages/01_Research_Validation.py", title="Research Validation", icon=":material/science:"),
    st.Page("pages/02_Design_Space.py", title="Design Space", icon=":material/tune:"),
    st.Page("pages/03_Evidence_Calibration.py", title="Evidence Calibration", icon=":material/menu_book:"),
    st.Page("pages/04_Motion_Calibration.py", title="Motion Calibration", icon=":material/analytics:"),
]
navigation = st.navigation(pages)
navigation.run()
