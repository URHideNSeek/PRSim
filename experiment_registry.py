"""Canonical experiment labels in execution order; legacy IDs identify stored schemas."""
LEGACY_TO_CANONICAL = {
    "E04": "E01", "CONTROLLED_RF": "E02", "E03": "E03",
    "E01": "E04", "DDL": "E05", "ACOUSTIC_BASELINE": "E06",
    "E07": "E07", "E02": "E08", "E05": "E09",
    "E06": "E10", "MOTION": "E11", "E08": "E12",
}
CANONICAL_NAMES = {
    "E01": "Receiver and Reference",
    "E02": "Controlled RF Characterization",
    "E03": "Passive RF Background",
    "E04": "Microphone Characterization",
    "E05": "DDL Acoustic Intake",
    "E06": "Acoustic Baseline",
    "E07": "Environmental Characterization",
    "E08": "Aircraft Acoustics",
    "E09": "Radar Background and Clutter",
    "E10": "Target Geometry and Motion",
    "E11": "Motion Calibration",
    "E12": "Multisensor Evaluation",
}
def canonical_id(legacy):
    return LEGACY_TO_CANONICAL[legacy]

def canonical_title(legacy):
    code = canonical_id(legacy)
    return code + " — " + CANONICAL_NAMES[code]
