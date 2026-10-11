"""Validation data contract for motion-dependent radar detection.

CSV fields:
  measured_doppler_hz: signed, measured bistatic Doppler
  target_present: 0 or 1 ground-truth label
  detector_score: numeric output from an independently defined detector
  session_id: independent recording/session identifier

Additional waveform, noise, clutter and hardware provenance is required in
the accompanying measurement documentation. No physical Pd can be inferred
from the geometry alone.
"""
from dataclasses import dataclass
from pathlib import Path
import csv
import math

REQUIRED = ("measured_doppler_hz","target_present","detector_score","session_id")

@dataclass(frozen=True)
class CalibrationReport:
    valid: bool
    message: str
    samples: int
    target_present: int
    target_absent: int
    sessions: int

def validate_rows(rows):
    rows=list(rows)
    if not rows:
        return CalibrationReport(False,"No observations provided.",0,0,0,0)
    for idx,row in enumerate(rows,1):
        if not all(k in row and str(row[k]).strip() for k in REQUIRED):
            return CalibrationReport(False,f"Row {idx} is missing a required field.",len(rows),0,0,0)
        try:
            doppler=float(row["measured_doppler_hz"])
            score=float(row["detector_score"])
        except (TypeError,ValueError):
            return CalibrationReport(False,f"Row {idx} has a nonnumeric measurement.",len(rows),0,0,0)
        if not math.isfinite(doppler) or not math.isfinite(score) or str(row["target_present"]) not in ("0","1"):
            return CalibrationReport(False,f"Row {idx} has invalid labels or nonfinite values.",len(rows),0,0,0)
    yes=sum(str(r["target_present"])=="1" for r in rows)
    no=len(rows)-yes
    sessions=len({str(r["session_id"]) for r in rows})
    if not yes or not no:
        return CalibrationReport(False,"Both target-present and target-absent observations are required.",len(rows),yes,no,sessions)
    if sessions<2:
        return CalibrationReport(False,"At least two independent sessions are required for calibration and holdout testing.",len(rows),yes,no,sessions)
    return CalibrationReport(True,"Schema and basic coverage passed. This does not establish calibration or physical validity.",len(rows),yes,no,sessions)

def read_csv(fileobj):
    reader=csv.DictReader(fileobj)
    return validate_rows(reader)
