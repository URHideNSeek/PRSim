"""Conservative ingestion of conducted, controlled RF receiver measurements.

Only validates records; does not command a signal generator or calibrate Pd.
"""
import csv
import io
import math

REQUIRED = ("timestamp_utc", "session_id", "source_model", "frequency_hz",
            "bandwidth_hz", "receiver_power_dbm", "sync_error_ns", "condition")
CONDITIONS = {"baseline", "changed"}

def parse_controlled_rf(text):
    reader = csv.DictReader(io.StringIO(text))
    missing = set(REQUIRED) - set(reader.fieldnames or [])
    if missing:
        raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
    records = []
    for line, row in enumerate(reader, 2):
        if any(not (row.get(field) or "").strip() for field in REQUIRED):
            raise ValueError(f"Missing value on row {line}")
        if row["condition"] not in CONDITIONS:
            raise ValueError(f"Invalid condition on row {line}")
        for field in ("frequency_hz", "bandwidth_hz", "receiver_power_dbm", "sync_error_ns"):
            try:
                value = float(row[field])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid {field} on row {line}") from exc
            if not math.isfinite(value):
                raise ValueError(f"Non-finite {field} on row {line}")
            if field in ("frequency_hz", "bandwidth_hz") and value <= 0:
                raise ValueError(f"{field} must be positive on row {line}")
            if field == "sync_error_ns" and value < 0:
                raise ValueError(f"sync_error_ns must be nonnegative on row {line}")
        if row["source_model"].strip() == "Keysight E8267D Option 520" and not (250_000 <= float(row["frequency_hz"]) <= 20_000_000_000):
            raise ValueError(f"Frequency outside Option 520 range on row {line}")
        records.append({field: row[field].strip() for field in REQUIRED})
    if not records:
        raise ValueError("No measurement records")
    return records

def baseline_summary(rows, min_samples=30):
    """Descriptive summary only; no anomaly/detection-performance claims."""
    baseline = [r for r in rows if r["condition"] == "baseline"]
    sessions = {r["session_id"] for r in baseline}
    powers = [float(r["receiver_power_dbm"]) for r in baseline]
    return {"baseline_samples": len(baseline),
            "baseline_sessions": len(sessions),
            "minimum_sample_count_met": len(baseline) >= min_samples,
            "mean_power_dbm": sum(powers)/len(powers) if powers else None,
            "note": "Count threshold is an illustrative collection gate, NOT proof of baseline stability or anomaly readiness."}
