"""Source-traceable scientific inputs, deliberately separate from unvalidated detection model."""
import json
import streamlit as st
import pandas as pd
st.set_page_config(page_title="PRSim | Evidence & Calibration",layout="wide")
st.title("Published Evidence & Calibration")
st.warning("Published propagation standards do not validate a complete passive radar detector. This page records physical inputs and provenance; it does not convert them into aircraft-detection claims.")
SOURCES={
 "ITU-R P.838-3":{"url":"https://www.itu.int/rec/R-REC-P.838-3-200503-I","year":2005,"scope":"Rain-specific attenuation, with frequency/polarization-dependent coefficients."},
 "ITU-R P.676-13":{"url":"https://www.itu.int/rec/R-REC-P.676-13-202208-I","year":2022,"scope":"Atmospheric gaseous attenuation from oxygen and water vapor."}
}
st.subheader("1. Research environment inputs")
a,b=st.columns(2)
with a:
    frequency=st.number_input("Illumination frequency (GHz)",min_value=8.0,max_value=12.0,value=10.0,step=.1,help="Frequency of the external illuminator. A real system needs its actual measured frequency.")
    rain=st.number_input("Measured rain rate (mm/h)",min_value=0.0,max_value=200.0,value=0.0,step=1.0,help="Rainfall intensity. ITU-R P.838 uses mm/h, rather than qualitative rain categories.")
    polarization=st.selectbox("Polarization",["Horizontal","Vertical"],help="Affects the rain-attenuation coefficients in ITU-R P.838.")
    path_km=st.number_input("Illuminated path length (km)",min_value=0.0,max_value=100.0,value=.5,step=.1,help="The relevant radio propagation path, not necessarily the receiver-to-aircraft distance.")
with b:
    temp=st.number_input("Air temperature (°C)",min_value=-50.,max_value=60.,value=20.,step=1.)
    pressure=st.number_input("Atmospheric pressure (hPa)",min_value=500.,max_value=1100.,value=1013.25,step=1.)
    vapor=st.number_input("Water vapor density (g/m³)",min_value=0.,max_value=40.,value=7.5,step=.5)
    wind=st.number_input("Wind speed (m/s)",min_value=0.,max_value=60.,value=0.,step=1.)
st.subheader("2. Model provenance")
rows=[
 ("Rain-specific attenuation","ITU-R P.838-3","Published method","Requires frequency/polarization coefficient implementation and independent validation"),
 ("Atmospheric gas attenuation","ITU-R P.676-13","Published method","Requires validated spectral model implementation and atmospheric profile"),
 ("Aircraft RCS","None selected","Assumed","Need measured frequency/aspect/polarization-specific data"),
 ("Aircraft sound spectrum","None selected","Assumed","Need sound pressure, microphone distance, frequency spectrum, uncertainty"),
 ("RF emissions","None selected","Assumed","Need measured transmitter/emission and receiver conditions"),
 ("Receiver noise and synchronization","None selected","Assumed","Need hardware specifications or bench measurements"),
 ("Detection probability","None selected","Synthetic","Requires independent labeled target/no-target observations"),
 ("SAR and GMTI performance","None selected","Not implemented","Requires independent verification against solicitation criteria")
]
st.dataframe(pd.DataFrame(rows,columns=["Parameter","Source","Evidence status","Missing validation"]),hide_index=True,use_container_width=True)
st.subheader("3. Verified primary references")
for title,source in SOURCES.items():
    st.markdown(f"**[{title}]({source['url']})** ({source['year']}) — {source['scope']}")
st.info("The simulator's main-page synthetic weather coefficients have NOT been replaced with ITU-R propagation calculations. Doing so requires validated coefficients, correct path geometry and experimental comparison.")
st.subheader("4. Export research input record")
record={"frequency_ghz":frequency,"rain_mm_per_hour":rain,"polarization":polarization,
"propagation_path_km":path_km,"temperature_c":temp,"pressure_hpa":pressure,
"water_vapor_density_g_m3":vapor,"wind_m_s":wind,
"standards":SOURCES,"model_status":"inputs captured; published propagation calculations not yet integrated"}
st.download_button("Download inputs and citations (JSON)",json.dumps(record,indent=2),file_name="prsim_provenance.json",mime="application/json")
