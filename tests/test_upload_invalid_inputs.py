"""Negative upload validation for all E01–E08 CSV schemas."""
import csv
import io
import pytest
from experiment_intake import EXPERIMENTS,NUMERIC,NONNEGATIVE,validate_csv
from scripts.generate_sample_uploads import make_rows

def as_csv(experiment,rows):
    buffer=io.StringIO()
    writer=csv.DictWriter(buffer,fieldnames=EXPERIMENTS[experiment][2])
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()

@pytest.mark.parametrize("experiment",list(EXPERIMENTS))
def test_every_upload_rejects_missing_required_values(experiment):
    base=make_rows(experiment)
    for field in EXPERIMENTS[experiment][2]:
        rows=[dict(base[0])]
        rows[0][field]=""
        with pytest.raises(ValueError):
            validate_csv(experiment,as_csv(experiment,rows))

@pytest.mark.parametrize("experiment",list(EXPERIMENTS))
def test_every_upload_rejects_nonfinite_or_nonnumeric_measurements(experiment):
    numeric=set(EXPERIMENTS[experiment][2])&NUMERIC
    for field in numeric:
        for bad in ("nan","inf","not-a-number"):
            rows=[dict(make_rows(experiment)[0])]
            rows[0][field]=bad
            with pytest.raises(ValueError):
                validate_csv(experiment,as_csv(experiment,rows))

@pytest.mark.parametrize("experiment",list(EXPERIMENTS))
def test_every_upload_rejects_negative_nonnegative_measurements(experiment):
    for field in set(EXPERIMENTS[experiment][2])&NONNEGATIVE:
        rows=[dict(make_rows(experiment)[0])]
        rows[0][field]="-1"
        with pytest.raises(ValueError):
            validate_csv(experiment,as_csv(experiment,rows))

@pytest.mark.parametrize("experiment",["E02","E03","E05","E08"])
def test_binary_labels_reject_nonbinary(experiment):
    for field in ("target_present","available"):
        if field not in EXPERIMENTS[experiment][2]:continue
        rows=[dict(make_rows(experiment)[0])]
        rows[0][field]="2"
        with pytest.raises(ValueError):
            validate_csv(experiment,as_csv(experiment,rows))
