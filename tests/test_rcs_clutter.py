from dataclasses import replace
import math
from model import Scenario,evaluate

def test_rcs_standard_reference_values_and_conversion():
    values=[round(10**(i/10),6) for i in range(-40,1,5)]
    assert values[0]==.0001 and values[-1]==1 and .01 in values
    assert abs(10*math.log10(.01)+20)<1e-9

def test_rcs_increases_radar_evidence():
    a=evaluate(Scenario(rcs_m2=.0001))["radar"]
    b=evaluate(Scenario(rcs_m2=1.))["radar"]
    assert b>a

def test_reflected_clutter_reduces_radar_evidence():
    low=evaluate(Scenario(clutter_cnr_db=-20))["radar"]
    high=evaluate(Scenario(clutter_cnr_db=40))["radar"]
    assert low>high

def test_clutter_does_not_directly_change_rf_or_audio():
    low=evaluate(Scenario(clutter_cnr_db=-20))
    high=evaluate(Scenario(clutter_cnr_db=40))
    assert low["rf"]==high["rf"] and low["acoustic"]==high["acoustic"]

def test_rcs_does_not_directly_change_rf_or_audio():
    low=evaluate(Scenario(rcs_m2=.0001))
    high=evaluate(Scenario(rcs_m2=1.))
    assert low["rf"]==high["rf"] and low["acoustic"]==high["acoustic"]
