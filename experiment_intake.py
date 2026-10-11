"""Experiment schemas and ingestion adapters for PRSim E01–E08.

CSV validation is deliberately conservative. All inputs are observations,
not automatically calibrated detector probabilities.
"""
import csv, io, json, math
from dataclasses import dataclass

EXPERIMENTS={
"E01":("Microphone calibration","Acoustic calibrator, microphones, audio interface",("timestamp_utc","sensor_id","spacing_mm","reference_db_spl","measured_dbfs","calibration_id")),
"E02":("Aircraft acoustics","Calibrated microphones, sound meter, GNSS",("timestamp_utc","sensor_id","target_present","range_m","rms_dbfs","recording_session_id")),
"E03":("Passive RF background","Spectrum analyzer or SDR, calibrated antenna",("timestamp_utc","sensor_id","center_frequency_hz","bandwidth_hz","noise_floor_dbm","target_present")),
"E04":("Receiver and reference","Signal generator, SDR, frequency reference",("timestamp_utc","sensor_id","frequency_hz","bandwidth_hz","receiver_noise_dbm","sync_error_ns")),
"E05":("Radar clutter","Authorized radar receiver and environmental logger",("timestamp_utc","sensor_id","clutter_cnr_db","target_present","session_id","frequency_hz")),
"E06":("Target motion","Independent GNSS/RTK, synchronized telemetry",("timestamp_utc","target_id","range_m","ground_speed_mps","heading_relative_deg","altitude_m")),
"E07":("Weather","Weather station, anemometer, rain gauge",("timestamp_utc","station_id","wind_mps","rain_mm_per_hour","temperature_c","pressure_hpa")),
"E08":("Multisensor evaluation","Synchronized radar/RF/acoustic and ground truth",("timestamp_utc","session_id","sensor_id","target_present","detector_score","available")),
}
NUMERIC={"spacing_mm","reference_db_spl","measured_dbfs","range_m","rms_dbfs","center_frequency_hz","bandwidth_hz","noise_floor_dbm","frequency_hz","receiver_noise_dbm","sync_error_ns","clutter_cnr_db","ground_speed_mps","heading_relative_deg","altitude_m","wind_mps","rain_mm_per_hour","temperature_c","pressure_hpa","detector_score"}
NONNEGATIVE={"spacing_mm","range_m","center_frequency_hz","bandwidth_hz","frequency_hz","ground_speed_mps","altitude_m","wind_mps","rain_mm_per_hour","sync_error_ns"}
def template(experiment_id):
    fields=EXPERIMENTS[experiment_id][2]
    return ",".join(fields)+"\n"

def validate_csv(experiment_id,text):
    if experiment_id not in EXPERIMENTS:raise ValueError("Unknown experiment ID")
    reader=csv.DictReader(io.StringIO(text))
    fields=EXPERIMENTS[experiment_id][2]
    if not reader.fieldnames or not set(fields).issubset(reader.fieldnames):
        raise ValueError("Missing columns: "+", ".join(sorted(set(fields)-set(reader.fieldnames or []))))
    rows=[]
    for line,row in enumerate(reader,2):
        if any(row.get(field) is None or not str(row[field]).strip() for field in fields):
            raise ValueError(f"Missing required field on row {line}")
        for field in fields:
            if field in NUMERIC:
                try: value=float(row[field])
                except ValueError as exc:raise ValueError(f"Invalid {field} on row {line}") from exc
                if not math.isfinite(value) or (field in NONNEGATIVE and value<0):
                    raise ValueError(f"Out-of-range {field} on row {line}")
            if field in ("target_present","available") and row[field] not in ("0","1"):
                raise ValueError(f"{field} must be 0 or 1 on row {line}")
        rows.append({key:row[key] for key in fields})
    if not rows:raise ValueError("No observations")
    return rows

def manifest(experiment_id,rows,source_filename,calibration_status="unverified"):
    return {"schema_version":"1.0","experiment_id":experiment_id,
            "experiment_name":EXPERIMENTS[experiment_id][0],
            "source_filename":source_filename,"records":len(rows),
            "calibration_status":calibration_status,
            "model_integration":"validated import only; no automatic probability calibration",
            "columns":list(EXPERIMENTS[experiment_id][2])}
