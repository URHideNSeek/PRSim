"""Idealized two-dimensional bistatic path-rate and Doppler geometry.

Coordinates: receiver at (0,0), target at (range_m,0), illuminator
at distance illuminator_distance_m from receiver with bearing
illuminator_bearing_deg counterclockwise from the receiver->target axis.
Target heading: 0 degrees away from receiver, 180 degrees toward.
No propagation, SNR, clutter, waveform ambiguity, or detection probability.
"""
from dataclasses import dataclass
import math

C_MPS = 299792458.0

@dataclass(frozen=True)
class Geometry:
    target_range_m: float
    speed_mps: float
    heading_deg: float
    illuminator_distance_m: float
    illuminator_bearing_deg: float
    frequency_ghz: float

def bistatic_observables(g: Geometry):
    if g.target_range_m <= 0 or g.illuminator_distance_m <= 0:
        return {"valid":False,"reason":"Both target range and illuminator distance must be positive.","path_rate_mps":None,"doppler_hz":None}
    if not 0 <= g.speed_mps <= 50 or not 0 <= g.heading_deg < 360:
        raise ValueError("Speed must be 0–50 m/s and heading must be 0–359.999°")
    if not 8 <= g.frequency_ghz <= 12:
        raise ValueError("Frequency must be in the selected 8–12 GHz X-band study range")
    a=math.radians(g.illuminator_bearing_deg)
    ix=g.illuminator_distance_m*math.cos(a)
    iy=g.illuminator_distance_m*math.sin(a)
    dx=g.target_range_m-ix
    dy=-iy
    rt=math.hypot(dx,dy)
    if rt < 1e-9:
        return {"valid":False,"reason":"Target and illuminator positions coincide.","path_rate_mps":None,"doppler_hz":None}
    theta=math.radians(g.heading_deg)
    vx=g.speed_mps*math.cos(theta)
    vy=g.speed_mps*math.sin(theta)
    # Derivative of illuminator->target + target->receiver path length.
    path_rate=vx*(dx/rt+1)+vy*(dy/rt)
    wavelength=C_MPS/(g.frequency_ghz*1e9)
    doppler=-path_rate/wavelength
    return {"valid":True,"reason":None,"path_rate_mps":path_rate,"doppler_hz":doppler,
            "illuminator_target_distance_m":rt,"wavelength_m":wavelength,
            "model_status":"idealized geometry only; no detection probability"}
