import csv
import io
import wave
import zipfile
import numpy as np
import pytest
from scripts.extract_ddl_features import extract

def test_offline_feature_extraction(tmp_path):
    archive=tmp_path/"samples.zip"
    name="1640995200000MINI0901250502931RFL0001ABC123000001.wav"
    audio=io.BytesIO()
    with wave.open(audio,"wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(np.zeros(1600,dtype="<i2").tobytes())
    with zipfile.ZipFile(archive,"w") as z:
        z.writestr(name,audio.getvalue())
    output=tmp_path/"features.csv"
    count,skipped=extract(archive,output)
    assert count==1 and skipped==0
    with output.open() as handle:
        rows=list(csv.DictReader(handle))
    assert rows[0]["sample_class"]=="MINI"
    assert rows[0]["recording_session_id"]=="ABC123"
    assert rows[0]["sample_rate_hz"]=="16000"
    with pytest.raises(FileExistsError):extract(archive,output)

def test_offline_max_files_guard(tmp_path):
    with pytest.raises(ValueError):extract(tmp_path/"missing.zip",tmp_path/"output.csv",max_files=10001)
