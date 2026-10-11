"""Generate deterministic synthetic upload fixtures for all PRSim intake pages.

All samples are TEST DATA, not experimental measurements. Run:
    python scripts/generate_sample_uploads.py
"""
import csv
import io
from pathlib import Path
import wave
import zipfile
import numpy as np
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiment_intake import EXPERIMENTS

NUMERIC={"spacing_mm","reference_db_spl","measured_dbfs","range_m","rms_dbfs",
"center_frequency_hz","bandwidth_hz","noise_floor_dbm","frequency_hz",
"receiver_noise_dbm","sync_error_ns","clutter_cnr_db","ground_speed_mps",
"heading_relative_deg","altitude_m","wind_mps","rain_mm_per_hour",
"temperature_c","pressure_hpa","detector_score"}

def make_rows(experiment_id):
    fields=EXPERIMENTS[experiment_id][2]
    rows=[]
    count=240 if experiment_id=="E08" else 4
    for i in range(count):
        row={}
        for field in fields:
            if field=="timestamp_utc":value=f"2026-10-10T12:{i%60:02d}:{(i//60)%60:02d}Z"
            elif field in ("target_present","available"):value=str((i//2)%2 if field=="target_present" else 1)
            elif field in ("session_id","recording_session_id"):value="train" if i<count//2 else "holdout"
            elif field=="sensor_id":value="SENSOR_A"
            elif field=="target_id":value="TARGET_1"
            elif field=="station_id":value="WEATHER_1"
            elif field=="calibration_id":value="CAL_1"
            elif field=="detector_score":value=str(.15+(.7 if (i//2)%2 else 0)+.001*(i%10))
            elif field in NUMERIC:value=str({"spacing_mm":152.4,"range_m":150,"center_frequency_hz":2.4e9,"frequency_hz":10e9,"bandwidth_hz":1e6,"temperature_c":20,"pressure_hpa":1013.25,"noise_floor_dbm":-90,"receiver_noise_dbm":-100,"measured_dbfs":-25,"rms_dbfs":-35}.get(field,1.0))
            else:value="TEST"
            row[field]=value
        rows.append(row)
    return rows

def write_csv(path,fields,rows):
    with path.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def make_wav():
    samples=np.round(.2*np.sin(2*np.pi*440*np.arange(16000)/16000)*32767).astype("<i2")
    buffer=io.BytesIO()
    with wave.open(buffer,"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000)
        w.writeframes(samples.tobytes())
    return buffer.getvalue()

def generate(destination):
    destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=True)
    for key,(_,_,fields) in EXPERIMENTS.items():
        write_csv(destination/f"{key}_sample.csv",fields,make_rows(key))
    motion_fields=("measured_doppler_hz","target_present","detector_score","session_id")
    motion=[{"measured_doppler_hz":str(10+i),"target_present":str(i%2),
             "detector_score":str(.2+.6*(i%2)),"session_id":"A" if i<20 else "B"} for i in range(40)]
    write_csv(destination/"E09_motion_sample.csv",motion_fields,motion)
    audio_fields=("recording_session_id","target_present","rms_dbfs","spectral_centroid_hz","sample_type")
    audio=[]
    for session in ("train","holdout"):
        for i in range(120):
            for label in (0,1):
                audio.append(dict(recording_session_id=session,target_present=label,
                    rms_dbfs=-40+label*15+(i%5)*.1,
                    spectral_centroid_hz=350+label*500+(i%7)*2,sample_type="R"))
    write_csv(destination/"E11_acoustic_baseline_sample.csv",audio_fields,audio)
    wav=make_wav()
    with zipfile.ZipFile(destination/"E10_DDL_sample.zip","w") as z:
        for session in ("ABC123","ABC124"):
            for kind in ("MINI","XXXX"):
                name="1640995200000"+kind+"0901250502931RFL0001"+session+"000001.wav"
                z.writestr(name,wav)
    (destination/"README.txt").write_text(
        "SYNTHETIC TEST FIXTURES ONLY. Not real sensor observations or field detection evidence.\n"
        "E01–E08: upload each CSV to its matching page. E09: Motion Calibration CSV.\n"
        "E10: DDL ZIP intake. E11: Acoustic Baseline CSV.\n",encoding="utf-8")
    return destination

if __name__=="__main__":
    generate(Path("sample_uploads"))
    print("Created 11 synthetic upload fixtures in sample_uploads/")
