import io
import math
import wave
import numpy as np
import pytest
from audio_features import wav_features

def pcm_wav(freq=440,rate=16000,seconds=.5,amplitude=.2,channels=1):
    t=np.arange(int(rate*seconds))/rate
    mono=np.round(amplitude*np.sin(2*np.pi*freq*t)*32767).astype("<i2")
    samples=np.repeat(mono[:,None],channels,axis=1).ravel()
    out=io.BytesIO()
    with wave.open(out,"wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(samples.tobytes())
    return out.getvalue()

def test_sine_frequency_and_duration():
    features=wav_features(pcm_wav())
    assert features["sample_rate_hz"]==16000
    assert features["duration_s"]==pytest.approx(.5)
    assert features["spectral_centroid_hz"]==pytest.approx(440,abs=5)
    assert features["rms_dbfs"]==pytest.approx(20*math.log10(.2/math.sqrt(2)),abs=.1)

def test_stereo_pcm_supported():
    features=wav_features(pcm_wav(channels=2))
    assert features["channels"]==2
    assert features["peak_dbfs"]<0

def test_silence_safe():
    data=pcm_wav(amplitude=0)
    features=wav_features(data)
    assert features["spectral_centroid_hz"]==0
    assert math.isfinite(features["rms_dbfs"])

def test_unsupported_bytes_rejected():
    with pytest.raises(ValueError):wav_features(b"not a wav")

def test_long_duration_rejected():
    with pytest.raises(ValueError):wav_features(pcm_wav(seconds=31))

def test_opposite_phase_stereo_does_not_cancel():
    rate=16000
    t=np.arange(rate//4)/rate
    left=np.round(.3*np.sin(2*np.pi*500*t)*32767).astype("<i2")
    stereo=np.column_stack((left,-left)).astype("<i2").ravel()
    buffer=io.BytesIO()
    with wave.open(buffer,"wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(stereo.tobytes())
    result=wav_features(buffer.getvalue())
    assert result["rms_dbfs"]>-20
    assert len(result["per_channel_rms_dbfs"])==2
    assert result["per_channel_rms_dbfs"][0]==pytest.approx(result["per_channel_rms_dbfs"][1],abs=.01)
