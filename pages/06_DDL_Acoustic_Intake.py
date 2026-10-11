"""DDL audio dataset intake — metadata only, no WAV extraction."""
import io
import zipfile
import pandas as pd
import streamlit as st
from ddl_acoustic import SOURCE_URL,parse_zip_manifest,coverage,metadata_csv

st.set_page_config(page_title="PRSim | DDL Acoustic Intake",layout="wide")
st.title("DDL Acoustic Dataset Intake")
st.markdown(f"**Dataset:** [Safavi et al., DDL (Zenodo 6459183)]({SOURCE_URL}).")
st.warning("Metadata-only ingestion. No audio processing, acoustic detection, or calibrated SPL estimates are performed. Verify the dataset's reuse terms before redistribution.")
st.markdown("The DDL field-recording filenames encode sample class, target bearing, distance, altitude, temperature, sample type, flight session, recording session, and sequence. Upload a **small ZIP subset** of the real field recordings. The app reads filenames only and never extracts audio.")
uploaded=st.file_uploader("Upload a ZIP containing DDL WAV files",type=["zip"],help="Start with a small permitted subset. Streamlit Cloud is not intended for the complete 12.6 GB real-data archive.")
if uploaded is not None:
    try:
        if uploaded.size > 100 * 1024 * 1024:
            raise ValueError("ZIP subset exceeds the 100 MB metadata-intake limit. Use a smaller subset.")
        rows,rejected=parse_zip_manifest(io.BytesIO(uploaded.getvalue()))
        report=coverage(rows)
        c1,c2,c3=st.columns(3)
        c1.metric("Parsed WAV filenames",report["files"])
        c2.metric("Target-present labels",report["target_present"])
        c3.metric("Target-absent labels",report["target_absent"])
        c4,c5,c6=st.columns(3)
        c4.metric("Real samples",report["real_files"])
        c5.metric("Synthetic samples",report["synthetic_files"])
        c6.metric("Recording sessions",report["recording_sessions"])
        if rejected:
            st.warning(f"{len(rejected)} WAV filenames did not match the documented DDL field convention. They were excluded.")
        if report["ready_for_holdout"]:
            st.success("Preliminary metadata coverage: multiple recording sessions and both classes in real recordings.")
        else:
            st.info("Insufficient metadata coverage for independent target/background evaluation. This does not mean the recordings are unusable.")
        if rows:
            frame=pd.DataFrame(rows)
            st.dataframe(frame.head(1000),hide_index=True,use_container_width=True)
            st.download_button("Download parsed metadata CSV",metadata_csv(rows),file_name="ddl_acoustic_metadata.csv",mime="text/csv")
            st.caption("Use recording-session separation to reduce leakage. Confirm that adjacent segments from the same flight or source recording do not appear in both training and holdout data.")
    except (ValueError,zipfile.BadZipFile,UnicodeError) as exc:
        st.error(f"Unable to read DDL ZIP metadata: {exc}")
st.divider()
st.subheader("Next experimental step")
st.markdown("After metadata review, develop a documented audio feature extractor and a separately evaluated classifier. Use real background and target recordings, independent flight/recording sessions, and known recording geometry. Do not treat filename labels or acoustic feature magnitudes as validated detection probabilities.")
