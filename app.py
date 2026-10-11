"""PRSim Streamlit entrypoint; retains Community Cloud deployment path."""
import streamlit as st

pages = [
    st.Page("PRSim.py", title="PRSim · Simulator", icon=":material/radar:", default=True),
    st.Page("pages/08_Research_Evidence.py", title="Tools · References & Datasets", icon=":material/menu_book:"),
    st.Page("pages/01_Research_Validation.py", title="Tools · Research Validation", icon=":material/science:"),
    # Canonical E01–E12 order; legacy page filenames and parser IDs are retained.
    st.Page("pages/E04_Receiver_and_Reference.py", title="E01 · Receiver and Reference", icon=":material/science:"),
    st.Page("pages/09_Controlled_RF.py", title="E02 · Controlled RF Characterization", icon=":material/tune:"),
    st.Page("pages/E03_Passive_RF_Background.py", title="E03 · Passive RF Background", icon=":material/science:"),
    st.Page("pages/E01_Microphone_Characterization.py", title="E04 · Microphone Characterization", icon=":material/science:"),
    st.Page("pages/06_DDL_Acoustic_Intake.py", title="E05 · DDL Acoustic Intake", icon=":material/audio_file:"),
    st.Page("pages/07_Acoustic_Baseline.py", title="E06 · Acoustic Baseline", icon=":material/graphic_eq:"),
    st.Page("pages/E07_Environmental_Characterization.py", title="E07 · Environmental Characterization", icon=":material/science:"),
    st.Page("pages/E02_Aircraft_Acoustics.py", title="E08 · Aircraft Acoustics", icon=":material/science:"),
    st.Page("pages/E05_Radar_Background_and_Clutter.py", title="E09 · Radar Background and Clutter", icon=":material/science:"),
    st.Page("pages/E06_Target_Geometry_and_Motion.py", title="E10 · Target Geometry and Motion", icon=":material/science:"),
    st.Page("pages/04_Motion_Calibration.py", title="E11 · Motion Calibration", icon=":material/analytics:"),
    st.Page("pages/E08_Multisensor_Evaluation.py", title="E12 · Multisensor Evaluation", icon=":material/science:"),
]
navigation = st.navigation(pages)
navigation.run()
