import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("re: Importing logic.engine...")
    from logic.engine import ReactorEngine, ReactorType
    print("re: Success.")

    print("re: Importing logic.visuals...")
    from logic.visuals import VisualGenerator
    print("re: Success.")

    print("re: Importing views.simulator...")
    from views import simulator
    print("re: Success.")

    print("re: Testing Engine Init...")
    eng = ReactorEngine()
    print("re: Units initialized: ", eng.units.keys())
    
    print("re: Testing RBMK Tick...")
    rbmk = eng.units["C"]
    print(f"re: Type: {rbmk.type}")
    rbmk.tick(1.0)
    print(f"re: Ticked. Flux: {rbmk.telemetry['flux']}")
    
    print("re: Testing Visual Generation...")
    svg = VisualGenerator.get_reactor_svg(rbmk.get_full_state()['telemetry'])
    print(f"re: SVG generated {len(svg)} bytes.")

    print("re: ALL TESTS PASSED.")

except Exception as e:
    print(f"re: ERROR: {e}")
    import traceback
    traceback.print_exc()
