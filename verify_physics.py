from logic.engine import ReactorEngine, ReactorType

def test_rbmk_scram():
    print("re: Initializing RBMK Unit...")
    eng = ReactorEngine()
    rbmk = eng.units["C"]
    
    # Setup: High power, rods out
    rbmk.control_state["rods_pos"] = 0.0 # Fully out
    rbmk.telemetry["flux"] = 1.0
    rbmk.telemetry["temp"] = 300
    rbmk.config.scram_tip_effect = True
    
    print(f"re: Initial Reactivity: {rbmk.telemetry['reactivity']}")
    
    # Trigger SCRAM
    print("re: TRIGGERING SCRAM (AZ-5)...")
    rbmk.control_state["manual_scram"] = True
    
    # Step 1 second
    rbmk.tick(1.0)
    r1 = rbmk.telemetry['reactivity']
    print(f"re: T+1.0s Reactivity: {r1}")
    
    # Step another second
    rbmk.tick(1.0)
    r2 = rbmk.telemetry['reactivity']
    print(f"re: T+2.0s Reactivity: {r2}")
    
    if r1 > 0:
        print("re: SUCCESS: Positive Reactivity Spike Detected during SCRAM!")
    else:
        print("re: FAILURE: No positive spike detected.")

if __name__ == "__main__":
    test_rbmk_scram()
