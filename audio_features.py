"""Bounded acoustic WAV feature extraction for controlled research data.

Features are generic signal descriptors, NOT drone detection algorithms.
They do not measure calibrated dB SPL and must not be treated as detector
scores without a separately specified and validated classifier.
"""
import io
import math
import wave
import numpy as np

MAX_WAV_BYTES=25*1024*1024
MAX_DURATION_S=30
MAX_CHANNELS=2
MAX_SAMPLE_RATE=192000

def wav_features(data):
    if len(data)>MAX_WAV_BYTES:
        raise ValueError("WAV exceeds 25 MB limit")
    try:
        with wave.open(io.BytesIO(data),"rb") as wf:
            rate=wf.getframerate()
            channels=wf.getnchannels()
            width=wf.getsampwidth()
            frames=wf.getnframes()
            compression=wf.getcomptype()
            if compression!="NONE" or channels not in (1,2) or width not in (1,2,3,4):
                raise ValueError("Only uncompressed mono/stereo integer PCM WAV is supported")
            if not 8000<=rate<=MAX_SAMPLE_RATE or frames<=0 or frames/rate>MAX_DURATION_S:
                raise ValueError("WAV rate or duration outside supported bounds")
            raw=wf.readframes(frames)
    except (wave.Error,EOFError) as exc:
        raise ValueError("Invalid or unsupported WAV") from exc
    if len(raw)!=frames*channels*width:
        raise ValueError("Truncated WAV data")
    if width==1:
        samples=(np.frombuffer(raw,dtype=np.uint8).astype(np.float64)-128)/128
    elif width==2:
        samples=np.frombuffer(raw,dtype="<i2").astype(np.float64)/32768
    elif width==4:
        samples=np.frombuffer(raw,dtype="<i4").astype(np.float64)/2147483648
    else:
        bytes3=np.frombuffer(raw,dtype=np.uint8).reshape(-1,3).astype(np.int32)
        value=bytes3[:,0]|(bytes3[:,1]<<8)|(bytes3[:,2]<<16)
        signed=np.where(value & 0x800000,value-0x1000000,value)
        samples=signed.astype(np.float64)/8388608
    channels_data=samples.reshape(frames,channels)
    channel_rms=np.sqrt(np.mean(channels_data**2,axis=0))
    channel_peak=np.max(np.abs(channels_data),axis=0)
    # Analyze channel 1 rather than averaging opposite-phase stereo channels.
    signal=channels_data[:,0]
    rms=float(channel_rms[0])
    peak=float(channel_peak[0])
    # Frequency descriptors from the first second, avoiding unbounded FFT memory.
    segment=signal[:min(frames,rate)]
    spectrum=np.abs(np.fft.rfft(segment*np.hanning(len(segment))))**2
    freqs=np.fft.rfftfreq(len(segment),1/rate)
    total=float(spectrum.sum())
    centroid=float(np.dot(freqs,spectrum)/total) if total>1e-20 else 0.0
    return {"sample_rate_hz":rate,"channels":channels,"duration_s":round(frames/rate,3),
            "rms_dbfs":round(20*math.log10(max(rms,1e-12)),2),
            "peak_dbfs":round(20*math.log10(max(peak,1e-12)),2),
            "spectral_centroid_hz":round(centroid,1),
            "per_channel_rms_dbfs":[round(20*math.log10(max(float(x),1e-12)),2) for x in channel_rms],
            "per_channel_peak_dbfs":[round(20*math.log10(max(float(x),1e-12)),2) for x in channel_peak],
            "clipped_fraction":round(float(np.mean(np.abs(signal)>=.999)),6),
            "status":"Uncalibrated generic audio features, not dB SPL or detection score"}
