class HistoricalScenario:
    def __init__(self, id, title, description, details, phases):
        self.id = id
        self.title = title
        self.description = description
        self.details = details # List of bullet points
        self.phases = phases   # List of dicts {time, label, state_overrides, analysis}

SCENARIOS = {
    "chernobyl": HistoricalScenario(
        id="chernobyl",
        title="Chernobyl Unit 4 (1986)",
        description="The catastrophic failure of an RBMK-1000 reactor during a safety test, leading to the worst nuclear disaster in history.",
        details=[
            "Reactor Type: RBMK-1000 (Graphite Moderated, Water Cooled)",
            "Root Cause: Flawed Control Rod Design + Operator Error",
            "Outcome: Prompt Criticality Excursion & Steam Explosion"
        ],
        phases=[
            {
                "time": 0,
                "label": "Test Preparation",
                "desc": "Power lowered to 700 MW for the test. Xenon poisoning builds up due to delays. Operators withdraw rods to maintain power.",
                "telemetry": {"power_mw": 700, "temp": 280, "pressure": 65, "flux": 0.2, "rods": 15, "health": 100.0, "radiation_released": 0.0},
                "analysis": "The ORM (Operational Reactivity Margin) is dangerously low as too many rods are out."
            },
            {
                "time": 30,
                "label": "Test Start",
                "desc": "01:23:04 - Turbine stop valves closed. Coolant pumps slow down. Water starts boiling in the channels.",
                "telemetry": {"power_mw": 200, "temp": 285, "pressure": 67, "flux": 0.1, "rods": 8, "health": 100.0, "radiation_released": 0.0},
                "analysis": "Void effect begins adding positive reactivity. Boiling increases because flow is dropping."
            },
            {
                "time": 40,
                "label": "Prompt Jump",
                "desc": "01:23:40 - Power starts rising uncontrollably. Positive feedback loop between steam and power kicks in.",
                "telemetry": {"power_mw": 500, "temp": 350, "pressure": 75, "flux": 0.5, "rods": 8, "health": 95.0, "radiation_released": 0.1},
                "analysis": "RBMK's positive void coefficient is now dominating the reactor physics."
            },
            {
                "time": 43,
                "label": "AZ-5 Pressed",
                "desc": "01:23:40 - SCRAM button pressed. Rods begin to enter, but graphite tips reach the core first.",
                "telemetry": {"power_mw": 1500, "temp": 600, "pressure": 90, "flux": 2.0, "rods": 50, "health": 80.0, "radiation_released": 0.5},
                "analysis": "The 'Positive Scram' effect: Graphite tips displace water at the bottom, adding more reactivity."
            },
            {
                "time": 48,
                "label": "Explosion",
                "desc": "01:23:45 - Power peaks at over 30,000 MW. Fuel shatters, causing a massive steam explosion.",
                "telemetry": {"power_mw": 33000, "temp": 3500, "pressure": 300, "flux": 50.0, "rods": 100, "health": 0.0, "radiation_released": 500.0, "melted": True},
                "analysis": "The reactor is destroyed. Steam explosion followed by a nuclear-grade graphite fire."
            }
        ]
    ),
    "tmi": HistoricalScenario(
        id="tmi",
        title="Three Mile Island Unit 2 (1979)",
        description="A partial meltdown caused by a stuck-open relief valve and confusing instrumentation.",
        details=[
            "Reactor Type: PWR (Pressurized Water Reactor)",
            "Root Cause: Stuck Pilot-Operated Relief Valve (PORV)",
            "Outcome: Partial core meltdown, containment preserved"
        ],
        phases=[
            {
                "time": 0,
                "label": "Primary Trip",
                "desc": "04:00:00 - Main feedwater pumps fail. Turbine trips. Reactor SCRAMs correctly.",
                "telemetry": {"power_mw": 0, "temp": 300, "pressure": 155, "rods": 100, "health": 100.0, "radiation_released": 0.0},
                "analysis": "The safety system responded correctly. Decay heat is handled by steam generators."
            },
            {
                "time": 15,
                "label": "PORV Stuck",
                "desc": "04:00:03 - Relief valve opens to bleed pressure but fails to close. Pilot light says 'Closed'.",
                "telemetry": {"power_mw": 0, "temp": 305, "pressure": 140, "rods": 100, "health": 100.0, "radiation_released": 0.0},
                "analysis": "Operators are unaware that primary coolant is leaking into the containment sump."
            },
            {
                "time": 45,
                "label": "The Surge",
                "desc": "04:05:00 - Pressurizer level rises. Operators think system is 'solid' and stop water injection.",
                "telemetry": {"power_mw": 0, "temp": 350, "pressure": 110, "rods": 100, "health": 90.0, "radiation_released": 0.05},
                "analysis": "Steam voids in the core are pushing water into the pressurizer, creating a false level reading."
            },
            {
                "time": 120,
                "label": "Core Uncovered",
                "desc": "06:15:00 - Top of the core is exposed to steam. Temperatures skyrocket. Zirc-water reaction starts.",
                "telemetry": {"power_mw": 0, "temp": 1200, "pressure": 90, "rods": 100, "health": 50.0, "radiation_released": 1.0},
                "analysis": "Hydrogen gas is being generated as the fuel cladding oxidizes."
            },
            {
                "time": 180,
                "label": "Meltdown",
                "desc": "07:50:00 - Significant core melt. Corium pools at the bottom of the vessel.",
                "telemetry": {"power_mw": 0, "temp": 2800, "pressure": 80, "rods": 100, "health": 20.0, "radiation_released": 2.0, "melted": True},
                "analysis": "Half of the core has melted, but the pressure vessel and containment thankfully hold."
            }
        ]
    ),
    "fukushima": HistoricalScenario(
        id="fukushima",
        title="Fukushima Daiichi Unit 1 (2011)",
        description="Station Blackout caused by Tsunami leads to loss of cooling and meltdown.",
        details=[
            "Reactor Type: BWR (Boiling Water Reactor)",
            "Root Cause: External Event (Tsunami flooding diesel generators)",
            "Outcome: Hydrogen Explosion, Total Core Melt"
        ],
        phases=[
            {
                "time": 0,
                "label": "14:46 Earthquake",
                "desc": "9.0 Mag Earthquake. Reactor SCRAMs. Diesel generators start to provide cooling power.",
                "telemetry": {"power_mw": 0, "temp": 280, "pressure": 70, "rods": 100, "health": 100.0, "radiation_released": 0.0},
                "analysis": "Automatic systems worked perfectly. Isolation Condenser is managing decay heat."
            },
            {
                "time": 51,
                "label": "15:37 Tsunami",
                "desc": "14m wave hits. Generators flooded. Station Blackout (SBO) declared. All cooling lost.",
                "telemetry": {"power_mw": 0, "temp": 300, "pressure": 72, "rods": 100, "health": 100.0, "radiation_released": 0.0},
                "analysis": "The IC (Isolation Condenser) valves closed due to power loss. Cooling has stopped."
            },
            {
                "time": 150,
                "label": "Boil Off",
                "desc": "Water level falls below the fuel. Steam pressure rises. Temperatures hit 1000C.",
                "telemetry": {"power_mw": 0, "temp": 1000, "pressure": 85, "rods": 100, "health": 60.0, "radiation_released": 10.0},
                "analysis": "Unveiling fuel causes rapid heating. Zirconium reaction creates hydrogen gas."
            },
            {
                "time": 240,
                "label": "Hydrogen Melt",
                "desc": "Venting attempted. Hydrogen escapes into the reactor building. Core begins to melt into vessel.",
                "telemetry": {"power_mw": 0, "temp": 2850, "pressure": 75, "rods": 100, "health": 10.0, "radiation_released": 150.0, "melted": True},
                "analysis": "Complete station blackout left the operators blind and powerless. Total core melt."
            },
            {
                "time": 300,
                "label": "Explosion",
                "desc": "Hydrogen explosion destroys the secondary building. Massive radiological release.",
                "telemetry": {"power_mw": 0, "temp": 3000, "pressure": 50, "rods": 100, "health": 0.0, "radiation_released": 500.0, "melted": True, "containment_integrity": 0.0},
                "analysis": "Secondary containment is gone. Environmental impact is maximized."
            }
        ]
    )
}

