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
                "label": "Preparation",
                "desc": "Reactor power reduced for safety test. Xenon poisoning begins to accumulate due to rapid power drop.",
                "telemetry": {"power_mw": 1600, "temp": 280, "flux": 0.5, "rods": 30, "reactivity": -0.001, "period": 999},
                "analysis": "Xenon-135 acts as a neutron absorber. Operators struggle to maintain power."
            },
            {
                "time": 40,
                "label": "Instability",
                "desc": "Power falls too low (30 MW). Operators withdraw nearly all control rods to compensate, violating safety protocols.",
                "telemetry": {"power_mw": 30, "temp": 250, "flux": 0.05, "rods": 5, "reactivity": 0.000, "period": 60},
                "analysis": "Core is now extremely unstable. Positive void coefficient dominates."
            },
            {
                "time": 80,
                "label": "Test Start",
                "desc": "Turbine test begins. Coolant pumps slow down. Water boils to steam -> Void effect increases reactivity.",
                "telemetry": {"power_mw": 200, "temp": 320, "flux": 0.15, "rods": 5, "reactivity": 0.002, "period": 10},
                "analysis": "Building positive feedback loop. Automatic control cannot compensate."
            },
            {
                "time": 100,
                "label": "The Surge",
                "desc": "Power skyrockets. AZ-5 button pressed (SCRAM). Graphite tips of rods displace water, adding MORE reactivity.",
                "telemetry": {"power_mw": 3000, "temp": 600, "flux": 2.0, "rods": 50, "reactivity": 0.015, "period": 0.5},
                "analysis": "Prompt Criticality reached. Fuel pellets shatter."
            },
            {
                "time": 110,
                "label": "Explosion",
                "desc": "Steam explosion destroys the reactor vessel. Graphite fire begins.",
                "telemetry": {"power_mw": 30000, "temp": 2000, "flux": 0.0, "rods": 100, "reactivity": 0.0, "period": 0},
                "analysis": "TOTAL SYSTEM LOSS. CATASTROPHIC FAILURE."
            }
        ]
    ),
    "tmi": HistoricalScenario(
        id="tmi",
        title="Three Mile Island Unit 2 (1979)",
        description="A partial meltdown caused by a stuck-open relief valve and confusing instrumentation.",
        details=[
            "Reactor Type: PWR (Pressurized Water Reactor)",
            "Root Cause: stuck Pilot-Operated Relief Valve (PORV)",
            "Outcome: Partial alignment meltdown, minimal release"
        ],
        phases=[
            {
                "time": 0,
                "label": "Trip",
                "desc": "Feedwater pumps fail. Turbine trips. Reactor SCRAMs automatically.",
                "telemetry": {"power_mw": 0, "temp": 300, "flux": 0.0, "rods": 100, "reactivity": -0.05, "period": 999},
                "analysis": "Safety systems worked as designed initially."
            },
            {
                "time": 20,
                "label": "Valve Error",
                "desc": "PORV opens to relieve pressure but gets stuck open. Operators think it is closed.",
                "telemetry": {"power_mw": 0, "temp": 320, "flux": 0.0, "rods": 100, "reactivity": -0.05, "period": 999},
                "analysis": "Loss of Coolant Accident (LOCA) begins invisibly."
            },
            {
                "time": 60,
                "label": "Confusion",
                "desc": "Pressurizer fills with water (relief tank). Operators stop safety injection pumps to prevent 'filling solid'.",
                "telemetry": {"power_mw": 0, "temp": 450, "flux": 0.0, "rods": 100, "reactivity": -0.05, "period": 999},
                "analysis": "Critical error: Core is actually boiling dry while operators think it's full."
            },
            {
                "time": 120,
                "label": "Meltdown",
                "desc": "Top of core is uncovered. Zirconium cladding reacts with steam (Hydrogen bubble).",
                "telemetry": {"power_mw": 0, "temp": 1200, "flux": 0.0, "rods": 100, "reactivity": -0.05, "period": 999},
                "analysis": "Fuel melts. Containment vessel holds."
            }
        ]
    ),
    "fukushima": HistoricalScenario(
        id="fukushima",
        title="Fukushima Daiichi (2011)",
        description="Station Blackout caused by Tsunami leads to loss of cooling and meltdown.",
        details=[
            "Reactor Type: BWR (Boiling Water Reactors)",
            "Root Cause: External Event (Tsunami flooding diesel generators)",
            "Outcome: Hydrogen Explosions, Meltdown of Units 1-3"
        ],
        phases=[
            {
                "time": 0,
                "label": "Earthquake",
                "desc": "9.0 Earthquake detected. Automatic SCRAM successful.",
                "telemetry": {"power_mw": 0, "temp": 280, "flux": 0.0, "rods": 100, "reactivity": -0.05, "period": 999},
                "analysis": "Grid power lost. Diesel generators start."
            },
            {
                "time": 50,
                "label": "Tsunami",
                "desc": "14m Tsunami strikes. Seawalls breached. Diesel generators flood and fail.",
                "telemetry": {"power_mw": 0, "temp": 300, "flux": 0.0, "rods": 100, "reactivity": -0.05, "period": 999},
                "analysis": "Station Blackout (SBO). Only batteries remain for monitoring."
            },
            {
                "time": 150,
                "label": "Boil Off",
                "desc": "Isolation Condensers fail/stop. Water boils off. Core uncovered.",
                "telemetry": {"power_mw": 0, "temp": 800, "flux": 0.0, "rods": 100, "reactivity": -0.05, "period": 999},
                "analysis": "Decay heat raising temp unchecked."
            },
             {
                "time": 200,
                "label": "Hydrogen",
                "desc": "Zirconium-Steam reaction generates Hydrogen. Venting fails.",
                "telemetry": {"power_mw": 0, "temp": 2000, "flux": 0.0, "rods": 100, "reactivity": -0.05, "period": 999},
                "analysis": "Hydrogen explosion blows roof off reactor building."
            }
        ]
    )
}
