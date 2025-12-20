
# Operator Manual Content Strategy

MANUAL_CONTENT = {
    "intro": {
        "title": "Welcome to the Control Room",
        "body": """
        **MISSION BRIEFING**
        You are now the Chief Operator of a multi-reactor nuclear facility. Your goal is to manage three distinct reactor types (PWR, BWR, RBMK) under various conditions.
        
        **HOW TO OPERATE**
        1.  **Select Unit**: Use the top bar to switch between Unit A (PWR), Unit B (BWR), and Unit C (RBMK).
        2.  **Navigation**: 
            -   **Monitor Mode**: View-only. Safe for observation.
            -   **Control Panel**: Unlock controls to make changes.
        3.  **Simulation**:
            -   **Auto Run**: Toggles continuous real-time simulation.
            -   **Step**: Advances time by 1 second manually.
        
        **SAFETY SYSTEMS**
        -   **Siren Warning**: A rising tone indicates you have left the "Green Zone" (Nominal Parameters). Correct the issue immediately.
        -   **Klaxon Alarm**: Indicates Critical Failure (SCRAM or Meltdown). Evacuate immediately.
        """
    },
    "pwr": {
        "title": "Unit A: Pressurized Water Reactor (PWR)",
        "desc": "The workhorse of the industry. Stable, safe, and reliable.",
        "specs": """
        -   **Coolant**: Liquid Water (High Pressure)
        -   **Moderator**: Liquid Water
        -   **Stability**: Negative Void Coefficient (Self-stabilizing)
        """,
        "limits": """
        **GREEN ZONE (NOMINAL)**
        -   **Temperature**: 300°C - 350°C
        -   **Pressure**: 140 Bar - 170 Bar
        """,
        "tips": """
        -   **Pressure Control**: Use Heaters to raise pressure, Sprays to lower it.
        -   **Reactivity**: Use Boron for long-term power changes, Rods for short-term.
        """,
        "controls": """
        **PRIMARY CONTROLS**
        -   **Control Rods**: Main reactivity control. Pull **OUT** (higher number) to increase power. Push **IN** to shut down.
        -   **Boron (PPM)**: Chemical shim. **LOWER** concentration to increase reactivity (long-term burnup compensation).
        -   **Pressurizer Heaters**: Turn **ON** to boil water in the pressurizer and **increase** system pressure.
        -   **Pressurizer Spray**: Turn **ON** to condense steam and **decrease** system pressure.
        -   **RCP Pumps**: Main coolant flow. Keep matched to power level to maintain Delta-T.
        """
    },
    "bwr": {
        "title": "Unit B: Boiling Water Reactor (BWR)",
        "desc": "Direct cycle system. Steam is produced directly in the core.",
        "specs": """
        -   **Coolant**: Boiling Water / Steam
        -   **Moderator**: Liquid Water
        -   **Stability**: Negative Void Coefficient
        """,
        "limits": """
        **GREEN ZONE (NOMINAL)**
        -   **Temperature**: 270°C - 300°C
        -   **Pressure**: 60 Bar - 90 Bar
        """,
        "tips": """
        -   **Level Control**: Keep water covering the core! Feedwater flow must match Steam flow.
        -   **Turbine Trip**: If the turbine trips, open Bypass immediately to prevent overpressure.
        """,
        "controls": """
        **PRIMARY CONTROLS**
        -   **Control Rods**: Bottom-entry rods. Pull **OUT** to increase power. Also affects axial flux shape.
        -   **Recirculation Pumps**: **INCREASE** flow to sweep away steam voids, adding reactivity (Spectral Shift). **DECREASE** flow to lower power.
        -   **Feedwater**: Controls Reactor Water Level. Must match steam output.
        -   **Turbine Bypass**: Steam dump valve. Open to lower pressure if the turbine cannot accept steam (Trip).
        """
    },
    "rbmk": {
        "title": "Unit C: RBMK-1000 (Channel Type)",
        "desc": "High power graphite-moderated reactor. Powerful but temperamental.",
        "specs": """
        -   **Coolant**: Boiling Water
        -   **Moderator**: Graphite Blocks
        -   **Stability**: POSITIVE Void Coefficient (Unstable at low power)
        """,
        "limits": """
        **GREEN ZONE (NOMINAL)**
        -   **Temperature**: 270°C - 300°C
        -   **Pressure**: 60 Bar - 90 Bar
        -   **Void Fraction**: < 40%
        """,
        "tips": """
        -   **DANGER**: Do not operate at low power (< 700MW).
        -   **AZ-5**: The Emergency Scram button. Note: Early rod insertion may spike power (Tip Effect).
        """,
        "controls": """
        **PRIMARY CONTROLS**
        -   **Control Rods**: Main reactivity control. Pull **OUT** to increase power. **CAUTION**: Graphite followers cause positive scram effect.
        -   **Main Circ Pumps**: Coolant flow. **INCREASE** flow to reduce voids and lower localized power (danger of cavitation if too high).
        -   **Feedwater**: Controls Drum Level. Essential for natural circulation stability.
        """
    }
}
