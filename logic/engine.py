from logic.layers.reactivity import ReactivityLayer
from logic.layers.thermal import ThermalLayer
from logic.layers.safety import SafetyLayer
from logic.scenarios.historical import SCENARIOS
import copy

class ReactorConfig:
    def __init__(self):
        # Physics Coefficients
        self.responsiveness = 1.0     # 0.5 (Sluggish) to 2.0 (Twitchy)
        self.thermal_inertia = 1.0    # 0.2 (Fast Heat) to 5.0 (Slow Heat)
        self.feedback_strength = 1.0  # 0.0 (Unstable) to 2.0 (Damped)
        
        # External Disturbances
        self.disturbance_flux = 0.0   # Additive reactivity noise
        self.cooling_penalty = 1.0    # Multiplier (1.0 = Normal, 0.5 = Blockage)
        
        # Meta-Physics (God Mode)
        self.non_linearity = 0.0      # 0.0 (Predictable) -> 1.0 (Chaotic)
        self.coupling_strength = 1.0  # 1.0 (Tight) -> 0.0 (Decoupled/Laggy)
        self.safety_bias = 0.5        # 0.0 (Forgiving) -> 1.0 (Strict)

class ReactorUnit:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.config = ReactorConfig()
        
        # Core Systems
        self.physics = ReactivityLayer()
        self.thermal = ThermalLayer()
        self.safety = SafetyLayer()
        
        # State
        self.control_state = {
            "rods_pos": 50.0, # 0-100
            "pump_speed": 100.0, # 0-100
            "cooling_eff": 100.0, # 0-100
            "manual_scram": False,
            "safety_enabled": True
        }
        
        self.telemetry = {
            "flux": 0.001,
            "power_mw": 0.0,
            "temp": 300.0,
            "reactivity": 0.0,
            "period": 999.0,
            "alerts": [],
            "scram": False,
            "stability_margin": 100.0,
            "health": 100.0, # Structural Integrity (0-100)
            "stability_margin": 100.0,
            "health": 100.0, # Structural Integrity (0-100)
            "risk_accumulated": 0.0, # Hidden risk metric
            # Derived Metrics
            "control_quality": 1.0,
            "escalation_momentum": 0.0,
            "irreversibility_score": 0.0
        }
        
        self.history = []
        self.time_seconds = 0

    def tick(self, dt=1.0):
        self.time_seconds += dt
        c = self.control_state
        
        # 1. Safety Check (Scram Override)
        self.safety.interlocks_active = c["safety_enabled"]
        is_scrammed = self.safety.check(
            self.telemetry["flux"], 
            self.telemetry["temp"], 
            c["pump_speed"],
            c["manual_scram"]
        )
        
        if is_scrammed:
            # Gravity Drop - Rods go in fast
            c["rods_pos"] = min(100.0, c["rods_pos"] + 10.0 * dt)
            c["manual_scram"] = False # Reset trigger, latch remains via checks
            
        # 2. Physics Update (Config-Aware)
        # We inject config params into the update call or modify state pre-update
        # Adjust rod effectiveness by responsiveness
        eff_rods = c["rods_pos"]
        
        # Apply Disturbance (Reactivity Spike)
        if self.config.disturbance_flux > 0:
            # Temporary flux spike
            pass 

        # Update Physics with Feedback Strength scaling
        # (For now, we pass standard, but in V2 logic we'd scale the feedback term)
        flux = self.physics.update(eff_rods, self.telemetry["temp"], dt)
        
        # Apply Glitch/Jitter to Flux based on responsiveness
        flux *= (1.0 + self.config.disturbance_flux)
        
        # 3. Thermal Update (Config-Aware)
        # config.cooling_penalty reduces pump effectiveness
        effective_cooling = c["cooling_eff"] * self.config.cooling_penalty
        
        # Thermal Lazy/Inertia is handled by scaling DT effectively for temp changes
        # High inertia = small dt effect = slow change
        thermal_dt = dt / self.config.thermal_inertia
        
        temp = self.thermal.update(flux, c["pump_speed"], effective_cooling, thermal_dt)
        
        # 4. Telemetry Update
        # Stability Margin Calculation (Abstract)
        stability = (1.5 * self.config.feedback_strength) - (abs(self.physics.reactivity) * 100)
        stability = max(0, min(100, stability * 100))
        
        self.telemetry.update({
            "flux": flux,
            "power_mw": flux * 2000.0,
            "temp": temp,
            "reactivity": self.physics.reactivity,
            "period": self.physics.period,
            "alerts": self.safety.alerts,
            "scram": is_scrammed,
            "stability_margin": stability
        })
        
        self._record_history()
        # Decay temporary disturbances
        # 5. Damage Accumulation (Simplified)
        if temp > 800:
            damage_rate = (temp - 800) * 0.01 * dt # 1000C = 2% per sec
            self.telemetry["health"] = max(0.0, self.telemetry["health"] - damage_rate)
            self.telemetry["risk_accumulated"] += damage_rate
        
        self.telemetry.update({
            "flux": flux,
            "power_mw": flux * 2000.0,
            "temp": temp,
            "reactivity": self.physics.reactivity,
            "period": self.physics.period,
            "alerts": self.safety.alerts,
            "scram": is_scrammed,
            "stability_margin": stability,
            "control_quality": max(0.0, 1.0 - (abs(self.physics.reactivity) * 500)),
            "escalation_momentum": (self.telemetry["temp"] - 300) / 1000.0 if self.telemetry["temp"] > 350 else 0.0,
            "irreversibility_score": (100.0 - self.telemetry["health"]) / 100.0
        })
        
        self._record_history()
        # Decay temporary disturbances
        self.config.disturbance_flux *= 0.9 # Decay spike quickly

    def apply_preset(self, preset_name):
        """Applies a named physics/context configuration."""
        if preset_name == "STABLE":
            self.config.responsiveness = 0.8  # Calm
            self.config.thermal_inertia = 2.0 # Slow heat
            self.config.feedback_strength = 1.5 # Strong damping
            
        elif preset_name == "VOLATILE":
            self.config.responsiveness = 1.8  # Twitchy
            self.config.thermal_inertia = 0.5 # Fast heat
            self.config.feedback_strength = 0.5 # Weak damping
            
        elif preset_name == "DEGRADED":
            self.config.responsiveness = 1.2
            self.config.feedback_strength = 0.2 # Near unstable
            self.telemetry["health"] = 75.0      # Pre-damaged
            self.telemetry["risk_accumulated"] = 50.0

    def set_state_override(self, telemetry_override):
        self.telemetry.update(telemetry_override)
        # Force history record for smoothness in replay
        self._record_history()

    def _record_history(self):
        # In scenario mode we might want higher freq, but keep 5s for now
        # or force it if called manually
        if len(self.history) == 0 or self.time_seconds - self.history[-1]["time"] >= 1.0:
            self.history.append({
                "time": self.time_seconds,
                "power": self.telemetry["power_mw"],
                "temp": self.telemetry["temp"],
                "reactivity": self.telemetry["reactivity"] * 10000
            })
            if len(self.history) > 100: self.history.pop(0)

    def get_full_state(self):
        return {
            "id": self.id,
            "name": self.name,
            "telemetry": self.telemetry,
            "controls": self.control_state,
            "history": self.history
        }

class ReactorEngine:
    def __init__(self):
        self.units = {
            "A": ReactorUnit("A", "UNIT-1 (PWR)"),
            "B": ReactorUnit("B", "UNIT-2 (BWR)")
        }
        self.global_time = 0
        self.active_scenario = None
        self.scenario_time = 0.0
        self.current_phase = None
        
    def load_scenario(self, scenario_id):
        if scenario_id in SCENARIOS:
            self.active_scenario = SCENARIOS[scenario_id]
            self.scenario_time = 0.0
            # Unit A becomes the Replay Actor
            self.units["A"] = ReactorUnit("A", self.active_scenario.title)
            # Set Initial State
            initial_phase = self.active_scenario.phases[0]
            self.current_phase = initial_phase
            self.units["A"].set_state_override(initial_phase["telemetry"])
            # Clear history
            self.units["A"].history = []
            
    def unload_scenario(self):
        self.active_scenario = None
        self.units["A"] = ReactorUnit("A", "UNIT-1 (PWR)")

    def tick(self, dt=1.0):
        if self.active_scenario:
            self.tick_scenario(dt)
        else:
            self.global_time += dt
            for u in self.units.values():
                u.tick(dt)
            
    def tick_scenario(self, dt):
        self.scenario_time += dt
        self.units["A"].time_seconds = self.scenario_time
        
        # 1. Determine Phase
        # Find the latest phase that has started
        active_p = self.active_scenario.phases[0]
        for p in self.active_scenario.phases:
            if self.scenario_time >= p["time"]:
                active_p = p
        
        self.current_phase = active_p
        
        # 2. Apply State (Interpolate or Snap)
        # For now, simply snap to phase target values to ensure we hit critical points
        # In a real future version, we would interpolate between phases.
        target = active_p["telemetry"]
        
        # Add some jitter or smoothing if needed, but strict adherence is better for education
        self.units["A"].set_state_override(target)
            
    def update_controls(self, unit_id, controls):
        if self.active_scenario and unit_id == "A":
            return # Locked controls in replay mode
            
        if unit_id in self.units:
            self.units[unit_id].control_state.update(controls)

    def update_config(self, unit_id, config_dict):
        """Dynamic tuning of physics engine"""
        if unit_id in self.units:
            u_conf = self.units[unit_id].config
            # Bulk update
            for k, v in config_dict.items():
                if hasattr(u_conf, k):
                    setattr(u_conf, k, v)
    
    def inject_disturbance(self, unit_id, type="SPIKE"):
        if unit_id in self.units:
            u_conf = self.units[unit_id].config
            if type == "SPIKE":
                u_conf.disturbance_flux = 0.5 # 50% Flux Jump
            elif type == "COOLING_FAIL":
                u_conf.cooling_penalty = 0.2 # 80% loss of cooling
            elif type == "RESET":
                u_conf.disturbance_flux = 0
                u_conf.cooling_penalty = 1.0
                u_conf.non_linearity = 0.0
            elif type == "EARTHQUAKE":
                u_conf.disturbance_flux = 0.2 # Shaking
                u_conf.cooling_penalty = 0.8  # Pipe Stress
                u_conf.non_linearity = 0.8    # Chaos
            elif type == "FLOOD":
                u_conf.cooling_penalty = 0.4  # Massive cooling loss
            
    def get_all_states(self):
        states = {uid: u.get_full_state() for uid, u in self.units.items()}
        if self.active_scenario:
            states["scenario_meta"] = {
                "active": True,
                "title": self.active_scenario.title,
                "time": self.scenario_time,
                "phase": self.current_phase["label"],
                "desc": self.current_phase["desc"],
                "analysis": self.current_phase["analysis"]
            }
        else:
            states["scenario_meta"] = {"active": False}
        return states
