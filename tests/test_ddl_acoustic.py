import io
import zipfile
import pytest
from ddl_acoustic import parse_field_filename,parse_zip_manifest,coverage,metadata_csv

def name(kind="MINI",sample="R",session="ABC123",seq="000001"):
    return "1640995200000"+kind+"090"+"125"+"050"+"2931"+sample+"FL0001"+session+seq+".wav"

def test_published_filename_fields():
    row=parse_field_filename(name())
    assert row["sample_class"]=="MINI"
    assert row["target_present"]==1
    assert row["bearing_deg"]==90
    assert row["range_m"]==125
    assert row["altitude_agl_m"]==50
    assert row["temperature_k"]==pytest.approx(293.1)
    assert row["recording_session_id"]=="ABC123"

def test_background_label_and_synthetic_flag():
    row=parse_field_filename(name("XXXX","S"))
    assert row["target_present"]==0
    assert row["sample_type"]=="S"

def test_invalid_filename_rejected():
    for candidate in ("bad.wav",name().replace("090","999",1),name("ABCD")):
        with pytest.raises(ValueError):parse_field_filename(candidate)

def test_zip_reads_names_without_extraction():
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,"w") as archive:
        archive.writestr("real/"+name(),"not real audio")
        archive.writestr("real/"+name("XXXX",session="ABC124"),"not real audio")
        archive.writestr("notes.txt","ignored")
        archive.writestr("bad.wav","ignored")
    buffer.seek(0)
    rows,rejected=parse_zip_manifest(buffer)
    assert len(rows)==2 and rejected==["bad.wav"]
    report=coverage(rows)
    assert report["ready_for_holdout"]
    assert report["has_both_classes"]
    assert "recording_session_id" in metadata_csv(rows)

def test_zip_member_limit():
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,"w") as archive:
        archive.writestr(name(),"x")
        archive.writestr(name("XXXX"),"x")
    buffer.seek(0)
    with pytest.raises(ValueError):parse_zip_manifest(buffer,limit=1)
