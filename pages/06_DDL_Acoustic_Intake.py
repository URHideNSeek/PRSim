"""DDL audio dataset intake — metadata only, no WAV extraction."""
import io
import zipfile
import pandas as pd
import streamlit as st
from experiment_protocols import EXTRA
from ddl_acoustic import SOURCE_URL,parse_zip_manifest,coverage,metadata_csv,parse_field_filename
from audio_features import wav_features,MAX_WAV_BYTES

st.set_page_config(page_title="PRSim | DDL Acoustic Intake",layout="wide")
st.title("E10 — DDL Acoustic Intake")
protocol=EXTRA["ddl"]
st.markdown("**Collection procedure:** "+protocol[1])
st.markdown("**Required data:** "+protocol[2])
st.markdown("**Instruments:** "+protocol[3])
st.info("Main-page probability impact: "+protocol[4])
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
        st.caption("Sessions with both real target and background recordings: "+str(report["both_class_sessions"]))
        if rejected:
            st.warning(f"{len(rejected)} WAV filenames did not match the documented DDL field convention. They were excluded.")
        if report["ready_for_holdout"]:
            st.success("Preliminary metadata coverage: two or more independent sessions each contain real target and background recordings. This is necessary but not sufficient for validation.")
        else:
            st.info("Not enough independent sessions containing both real target and background recordings for the simple holdout design. Other evaluation designs may be possible.")
        if rows:
            frame=pd.DataFrame(rows)
            st.dataframe(frame.head(1000),hide_index=True,use_container_width=True)
            st.download_button("Download parsed metadata CSV",metadata_csv(rows),file_name="ddl_acoustic_metadata.csv",mime="text/csv")
            st.caption("Use recording-session separation to reduce leakage. Confirm that adjacent segments from the same flight or source recording do not appear in both training and holdout data.")
            st.divider()
            st.subheader("Experimental WAV feature inspection")
            st.caption("This optional operation reads up to 20 real WAV recordings from the uploaded ZIP and extracts generic uncalibrated audio features alongside recording metadata. It does not train a drone detector or calculate detection probability.")
            if st.button("Extract generic WAV features (max 20)",help="Inspect RMS dBFS, peak dBFS, spectral centroid, clipping, sample rate, and duration. No calibration to dB SPL."):
                features=[]
                errors=[]
                with zipfile.ZipFile(io.BytesIO(uploaded.getvalue())) as archive:
                    real_meta={r["filename"]:r for r in rows if r["sample_type"]=="R"}
                    real_names=set(real_meta)
                    candidates=[member for member in archive.infolist() if member.filename in real_names and member.file_size<=MAX_WAV_BYTES]
                    for member in candidates[:20]:
                        try:
                            with archive.open(member) as stream:
                                wav=stream.read(MAX_WAV_BYTES+1)
                            meta=real_meta[member.filename]
                            features.append({"filename":member.filename,"target_present":meta["target_present"],"sample_class":meta["sample_class"],"range_m":meta["range_m"],"bearing_deg":meta["bearing_deg"],"flight_session_id":meta["flight_session_id"],"recording_session_id":meta["recording_session_id"],**wav_features(wav)})
                        except (ValueError,EOFError,zipfile.BadZipFile) as exc:
                            errors.append(f"{member.filename}: {exc}")
                if features:
                    st.dataframe(pd.DataFrame(features),hide_index=True,use_container_width=True)
                    st.download_button("Export WAV feature inspection CSV",pd.DataFrame(features).to_csv(index=False),file_name="ddl_audio_features.csv",mime="text/csv")
                if errors:
                    st.warning(f"{len(errors)} WAV files were skipped due to invalid or unsupported format.")

    except (ValueError,zipfile.BadZipFile,UnicodeError) as exc:
        st.error(f"Unable to read DDL ZIP metadata: {exc}")
st.divider()
st.subheader("Next experimental step")
st.markdown("After metadata review, develop a documented audio feature extractor and a separately evaluated classifier. Use real background and target recordings, independent flight/recording sessions, and known recording geometry. Do not treat filename labels or acoustic feature magnitudes as validated detection probabilities.")
