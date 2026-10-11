"""Transparent normalized response model. NOT physically calibrated."""
from dataclasses import dataclass, replace
import math
WEATHER={"Clear":(1.,1.,1.),"Cloud (aircraft inside)":(.95,.96,.95),
"Light rain":(.82,.95,.86),"Heavy rain":(.60,.86,.70),"Snow":(.75,.89,.79),"High wind":(.55,.94,.75)}
SIZE={"Small":.55,"Medium":.75,"Large":.95}
def clip(x): return max(0.,min(1.,float(x)))
@dataclass(frozen=True)
class Scenario:
    weather:str="Clear"
    rcs:str="Medium"
    rcs_m2:float|None=None
    clutter_cnr_db:float=0.
    emits:bool=True
    audio:int=60
    range_m:int=500
    speed_mps:int=0
    heading_deg:int=0
    observation:int=10
    update:float=1.
    fusion_weight:float=.45
    fail:float=.05
    radar_on:bool=True
    illumination:float=.85
    reference:float=.8
    sync_error:float=.15
    clutter:float=.3
    radar_noise:float=.2
    bandwidth:float=.6
    rf_on:bool=True
    rf_sensitivity:float=.7
    rf_interference:float=.3
    rf_coverage:float=.8
    rf_noise:float=.2
    acoustic_on:bool=True
    microphone_quality:float=.75
    mic_spacing:float=.35
    audio_noise:float=.3
    wind_noise:float=.2
    channel_sync:float=.9
    threshold:float=.3
def evaluate(s:Scenario):
    wa,wr,wd=WEATHER[s.weather]
    distance=1/(1+(s.range_m/650)**1.35)
    # Engineering units are captured explicitly; mapping to score remains an UNCALIBRATED heuristic.
    size=SIZE[s.rcs] if s.rcs_m2 is None else clip(.75 + .20*math.log10(max(s.rcs_m2,1e-9)/.01))
    clutter_penalty=1/(1+10**(s.clutter_cnr_db/10)/10)
    radar=clip(size*distance*wd*s.illumination*s.reference*(1-.55*s.sync_error)*(1-.45*s.clutter)*(1-.35*s.radar_noise)*(.7+.3*s.bandwidth)*clutter_penalty) if s.radar_on else 0.
    rf=clip(distance*wr*s.rf_sensitivity*s.rf_coverage*(1-.55*s.rf_interference)*(1-.3*s.rf_noise)) if s.rf_on and s.emits else 0.
    # Spacing contributes to directional evidence quality, not independent acoustic range.
    directional=.8+.2*clip(s.mic_spacing/1.5)
    audio=clip((s.audio/75)*(1/(1+(s.range_m/280)**1.4))*wa*s.microphone_quality*s.channel_sync*(1-.55*s.audio_noise)*(1-.5*s.wind_noise)*directional) if s.acoustic_on else 0.
    fused=clip(radar+s.fusion_weight*max(rf,audio)*(1-radar))
    radar_avail=clip(s.illumination*(1-s.fail)) if s.radar_on else 0.
    # Combine normalized availability assumptions without double counting the outage.
    aux=clip(max(rf,audio))
    fused_avail=clip(((s.illumination if s.radar_on else 0.)+.35*aux)*(1-s.fail))
    def measures(score,availability):
        active=[(wd,s.radar_on),(wr,s.rf_on and s.emits),(wa,s.acoustic_on)]
        robustness=sum(v for v,on in active if on)/max(1,sum(on for _,on in active))
        return {"Detection evidence index (0–1)":round(score,3),
          "Latency proxy (s)":round(s.update+s.observation*(1-score),2),
          "Tracking uncertainty index (lower better)":round(1-.8*score,3),
          "Environmental retention index":round(robustness,3),
          "Availability index (0–1)":round(availability,3)}
    # Ground speed is horizontal; heading is relative to the sensor-target line:
    # 0° away, 90° transverse, 180° toward, 270° transverse. No illuminator bearing is known.
    radial_speed=s.speed_mps*math.cos(math.radians(s.heading_deg))
    transverse_speed=s.speed_mps*math.sin(math.radians(s.heading_deg))
    # The speed/heading fields are intentionally not mapped to detection evidence until
    # bistatic geometry and motion-response data are available.
    return {"radar":radar,"rf":rf,"acoustic":audio,"fused":fused,
            "motion":{"speed_mps":s.speed_mps,"heading_deg":s.heading_deg,"radial_speed_mps":radial_speed,"transverse_speed_mps":transverse_speed,"speed_definition":"horizontal ground speed","heading_reference":"sensor-target line, 0 away, 180 toward","model_status":"not calibrated"},
            "radar_metrics":measures(radar,radar_avail),
            "fused_metrics":measures(fused,fused_avail),
            "detected":fused>=s.threshold}
