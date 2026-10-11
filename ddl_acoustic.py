"""DDL acoustic dataset metadata adapter, following Zenodo record 6459183.

This module parses the published field-recording filename convention only.
It does not read WAV samples, infer calibrated SPL, or produce detector scores.
"""
from pathlib import PurePath
import csv
import io
import re
import zipfile

SOURCE_URL="https://zenodo.org/records/6459183"
FIELDS=("filename","sample_class","target_present","bearing_deg","range_m",
        "altitude_agl_m","temperature_k","sample_type","flight_session_id",
        "recording_session_id","sequence_id")
MAX_ARCHIVE_MEMBERS=50000

def parse_field_filename(filename):
    stem=PurePath(filename.replace("\\","/")).name.rsplit(".",1)[0]
    if len(stem)!=49:
        raise ValueError("Expected 49-character DDL field-recording stem")
    timestamp=stem[0:13]
    sample_class=stem[13:17]
    bearing=stem[17:20]
    distance=stem[20:23]
    altitude=stem[23:26]
    temperature=stem[26:30]
    sample_type=stem[30:31]
    flight=stem[31:37]
    recording=stem[37:43]
    sequence=stem[43:49]
    if not (timestamp.isdigit() and bearing.isdigit() and distance.isdigit()
            and altitude.isdigit() and temperature.isdigit()
            and re.fullmatch(r"[A-Za-z0-9]{4}",sample_class)
            and sample_type in ("R","S")
            and all(re.fullmatch(r"[A-Za-z0-9]{6}",v) for v in (flight,recording,sequence))):
        raise ValueError("Filename does not match published field-recording fields")
    if int(bearing)>359:
        raise ValueError("Bearing must be 0–359 degrees")
    # DDL uses XXXX for no drone. Do not infer non-XXXX classes beyond those documented.
    if sample_class not in ("MINI","PRO4","XXXX"):
        raise ValueError("Unknown DDL sample class; verify dataset version")
    return {
        "filename":filename,
        "sample_class":sample_class,
        "target_present":int(sample_class!="XXXX"),
        "bearing_deg":int(bearing),
        "range_m":int(distance),
        "altitude_agl_m":int(altitude),
        "temperature_k":int(temperature)/10.0,
        "sample_type":sample_type,
        "flight_session_id":flight,
        "recording_session_id":recording,
        "sequence_id":sequence,
    }

def parse_zip_manifest(fileobj,limit=MAX_ARCHIVE_MEMBERS):
    """Read names from a ZIP central directory; never extract archive members."""
    with zipfile.ZipFile(fileobj) as archive:
        members=[i for i in archive.infolist() if not i.is_dir() and i.filename.lower().endswith(".wav")]
        if len(members)>limit:
            raise ValueError(f"Archive has too many WAV members (>{limit})")
        valid=[];rejected=[]
        for member in members:
            try:valid.append(parse_field_filename(member.filename))
            except ValueError:rejected.append(member.filename)
    return valid,rejected

def metadata_csv(rows):
    output=io.StringIO()
    writer=csv.DictWriter(output,fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()

def coverage(rows):
    sessions={r["recording_session_id"] for r in rows}
    real=[r for r in rows if r["sample_type"]=="R"]
    return {
        "files":len(rows),"real_files":len(real),
        "synthetic_files":len(rows)-len(real),
        "target_present":sum(r["target_present"] for r in rows),
        "target_absent":sum(not r["target_present"] for r in rows),
        "recording_sessions":len(sessions),
        "has_both_classes":any(r["target_present"] for r in real) and any(not r["target_present"] for r in real),
        "ready_for_holdout":len({r["recording_session_id"] for r in real})>=2 and
            any(r["target_present"] for r in real) and any(not r["target_present"] for r in real),
    }
