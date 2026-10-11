"""PRSim Streamlit entrypoint; retains the existing Community Cloud app.py deployment path."""
import streamlit as st

pages = [
    st.Page("PRSim.py", title="PRSim", icon=":material/radar:", default=True),
    st.Page("pages/01_Research_Validation.py", title="Research Validation", icon=":material/science:"),
    st.Page("pages/08_Research_Evidence.py", title="References & Datasets", icon=":material/menu_book:"),
    st.Page("pages/E01_Microphone_Characterization.py", title="E01 · Microphone Characterization", icon=":material/science:"),
    st.Page("pages/E02_Aircraft_Acoustics.py", title="E02 · Aircraft Acoustics", icon=":material/science:"),
    st.Page("pages/E03_Passive_RF_Background.py", title="E03 · Passive RF Background", icon=":material/science:"),
    st.Page("pages/E04_Receiver_and_Reference.py", title="E04 · Receiver and Reference", icon=":material/science:"),
    st.Page("pages/09_Controlled_RF.py", title="Controlled RF Lab", icon=":material/tune:"),
    st.Page("pages/E05_Radar_Background_and_Clutter.py", title="E05 · Radar Background and Clutter", icon=":material/science:"),
    st.Page("pages/E06_Target_Geometry_and_Motion.py", title="E06 · Target Geometry and Motion", icon=":material/science:"),
    st.Page("pages/E07_Environmental_Characterization.py", title="E07 · Environmental Characterization", icon=":material/science:"),
    st.Page("pages/E08_Multisensor_Evaluation.py", title="E08 · Multisensor Evaluation", icon=":material/science:"),
    st.Page("pages/04_Motion_Calibration.py", title="E09 · Motion Calibration", icon=":material/analytics:"),
    st.Page("pages/06_DDL_Acoustic_Intake.py", title="E10 · DDL Acoustic Intake", icon=":material/audio_file:"),
    st.Page("pages/07_Acoustic_Baseline.py", title="E11 · Acoustic Baseline", icon=":material/graphic_eq:"),
]
navigation = st.navigation(pages)
navigation.run()
