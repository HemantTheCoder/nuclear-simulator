
import pandas as pd
from services.reporting import ReportGenerator

# Mock objects to simulate views/incidents.py (Updated)
class MockConfig:
     def __init__(self):
         self.nominal_power_mw = 1000
         self.nominal_temp = 300
         self.fuel_limit_temp = 2800
         self.void_coefficient = -0.01
         self.doppler_coefficient = -0.002

mock_unit = type('Mock', (), {
    'name': "Test Scenario",
    'id': 'TEST_PLAYBACK',
    'type': type('Type', (), {'name': "TEST_TYPE", 'value': "TEST_TYPE"}),
    'config': MockConfig(),
    'telemetry': {"temp": 300, "power_mw": 0, "pressure": 150, "scram": False},
    'control_state': {"eccs_active": False, "msiv_open": True, "auto_rod_control": False, "turbine_load_mw": 1000},
    'event_log': [{"time": 0, "event": "Test Event " * 50}], # Long event to test wrapping
    'post_mortem_report': {
        'explanation': "Test Explanation",
        'prevention': ["Prevention 1"]
    },
    'history': [{"time_seconds": 0, "power_mw": 0, "temp": 300}]
})()

print("--- TEST: INCIDENT REPORT GENERATION (Long Event Logs) ---")
try:
    pdf = ReportGenerator.generate_pdf(mock_unit, mock_unit.history)
    print(f"SUCCESS: Incident PDF generated ({len(pdf)} bytes)")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"FAILURE: {e}")
