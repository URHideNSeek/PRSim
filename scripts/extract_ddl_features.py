"""Offline DDL WAV feature extraction; run locally, not on Streamlit Cloud.

Usage:
  python scripts/extract_ddl_features.py subset.zip output.csv --max-files 500

Only uncompressed PCM WAV <=25 MB each is analyzed. No audio is extracted to
disk and no downloaded data is added to the repository.
"""
import argparse
import csv
import sys
import zipfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ddl_acoustic import parse_field_filename
from audio_features import wav_features,MAX_WAV_BYTES

def extract(archive_path,output_path,max_files=500):
    if not 1<=max_files<=10000:raise ValueError("max_files must be 1–10000")
    output_path=Path(output_path)
    if output_path.exists():raise FileExistsError("Output exists; choose a new path")
    rows=[]
    skipped=0
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            if len(rows)>=max_files:break
            if member.is_dir() or not member.filename.lower().endswith(".wav"):continue
            if member.file_size>MAX_WAV_BYTES:
                skipped+=1
                continue
            try:
                meta=parse_field_filename(member.filename)
                if meta["sample_type"]!="R":continue
                with archive.open(member) as source:
                    data=source.read(MAX_WAV_BYTES+1)
                features=wav_features(data)
                rows.append({**meta,**features})
            except (ValueError,EOFError,zipfile.BadZipFile):
                skipped+=1
    if not rows:raise ValueError("No compatible real WAV recordings found")
    with output_path.open("x",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return len(rows),skipped

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive",type=Path)
    parser.add_argument("output",type=Path)
    parser.add_argument("--max-files",type=int,default=500)
    args=parser.parse_args()
    count,skipped=extract(args.archive,args.output,args.max_files)
    print(f"Extracted {count} real WAV feature rows; skipped {skipped} incompatible files.")
