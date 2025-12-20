from logic.layers.reactivity import ReactivityLayer
from logic.layers.thermal import ThermalLayer
from logic.layers.safety import SafetyLayer
from logic.scenarios.historical import SCENARIOS
from enum import Enum
import math
import random

class ReactorType(Enum):
    PWR = "PWR"   # Pressurized Water Reactor (Negative Void coeff, Safe)
    BWR = "BWR"   # Boiling Water Reactor (Negative Void coeff, Steam voids)
    RBMK = "RBMK" # Channel Type (Positive Void coeff, Graphite Tip effect)

class ReactorConfig:
    def __init__(self, r_type=ReactorType.PWR):
        self.type = r_type
        
        # Base Physics Coefficients
        self.responsiveness = 1.0     
        self.thermal_inertia = 1.0    
        self.feedback_strength = 1.0  
        
        # Advanced Physics Quirks
        if r_type == ReactorType.RBMK:
            self.void_coefficient = 0.05      # POSITIVE! Bubbles = More Power
            self.doppler_coefficient = -0.01  # Small negative temp feedback
            self.xenon_burnout_rate = 1.2     # Fast xenon transients
            self.scram_insertion_speed = 0.5  # Slow rods (18s to insert)
            self.scram_tip_effect = True      # Graphite tip causes spike on insertion
        elif r_type == ReactorType.BWR:
            self.void_coefficient = -0.05     # Negative (Safety feature)
            self.doppler_coefficient = -0.03
            self.xenon_burnout_rate = 1.0
            self.scram_insertion_speed = 2.0  # Fast hydraulic
            self.scram_tip_effect = False
        else: # PWR
            self.void_coefficient = -0.02     # Negative (Bubble = less mod = less power)
            self.doppler_coefficient = -0.04  # Strong safety feedback
            self.xenon_burnout_rate = 1.0
            self.scram_insertion_speed = 3.0  # Very fast gravity drop
            self.scram_tip_effect = False

        # External Disturbances
        self.disturbance_flux = 0.0
        self.cooling_penalty = 1.0
        
        # Meta-Physics
        self.non_linearity = 0.2 if r_type == ReactorType.RBMK else 0.0
        self.coupling_strength = 0.5 if r_type == ReactorType.RBMK else 1.0
        self.safety_bias = 0.5

class ReactorUnit:
    def __init__(self, id, name, r_type=ReactorType.PWR):
        self.id = id
        self.name = name
        self.type = r_type
        self.config = ReactorConfig(r_type)
        
        # Core Systems
        self.physics = ReactivityLayer()
        self.thermal = ThermalLayer()
        self.safety = SafetyLayer()
        
        # State
        self.control_state = {
            "rods_pos": 50.0, # 0 (Full Out) to 100 (Full In)
            "pump_speed": 100.0,
            "flow_rate_core": 100.0, # Actual flow
            "manual_scram": False,
            "safety_enabled": True,
            # Type specific
            # PWR
            "boron_concentration": 1000.0 if r_type == ReactorType.PWR else 0.0, # ppm
            "pressurizer_heaters": False, # On/Off
            "pressurizer_sprays": False,
            # BWR/RBMK
            "feedwater_flow": 100.0, # % Match steam flow to maintain level
            "turbine_bypass": 0.0, # % Steam dump
            # Emergency
            "manual_vent": False, 
            "eccs_active": False,
        }
        
        self.telemetry = {
            "flux": 0.001,
            "power_mw": 0.0,
            "temp": 300.0,
            "pressure": 155.0 if r_type == ReactorType.PWR else 70.0, # Bar
            "reactivity": 0.0,
            "period": 999.0,
            "alerts": [],
            "scram": False,
            "stability_margin": 100.0,
            "health": 100.0,
            "xenon": 1.0,  
            "iodine": 1.0,
            "void_fraction": 0.0, 
            # Advanced Telemetry
            "water_level": 5.0, # Meters (Nominal)
            "steam_flow": 0.0,
            "boron_ppm": 1000.0 if r_type == ReactorType.PWR else 0.0,
            # RBMK specific
            "graphite_tip_position": 0.0, 
            # Catastrophic State
            "melted": False,
            "containment_integrity": 100.0,
            "radiation_released": 0.0, # Sieverts
        }
        

        
        self.history = []
        self.event_log = [] # List of {"time": t, "event": str}
        self.failure_cause = None
        self.post_mortem_report = None
        
        self.time_seconds = 0
        self.reset() # Start in optimal state
    
    def reset(self):
        """Restores the reactor to an Optimal Operating State (Media Res)."""
        r_type = self.type
        
        # 1. OPTIMAL CONTROL STATE
        self.control_state = {
            "rods_pos": 80.0, # 20% Withdrawal - Running State
            "pump_speed": 100.0,
            "flow_rate_core": 100.0,
            "manual_scram": False,
            "safety_enabled": True,
            # Type specific
            # PWR
            "boron_concentration": 500.0 if r_type == ReactorType.PWR else 0.0, # Burned in
            "pressurizer_heaters": False,
            "pressurizer_sprays": False,
            # BWR/RBMK
            "feedwater_flow": 100.0,
            "turbine_bypass": 0.0,
            # Emergency
            "manual_vent": False, 
            "eccs_active": False,
        }
        
        # 2. OPTIMAL TELEMETRY
        # PWR: 315C, 155 Bar
        # BWR: 285C, 70 Bar
        # RBMK: 280C, 65 Bar
        
        target_temp = 315.0
        target_press = 155.0
        
        if r_type == ReactorType.BWR:
            target_temp = 285.0
            target_press = 70.0
        elif r_type == ReactorType.RBMK:
            target_temp = 280.0
            target_press = 65.0
            self.control_state["rods_pos"] = 70.0 # RBMK needs more withdrawal
            
        self.telemetry = {
            "flux": 1.0, # Full Power
            "power_mw": 1000.0,
            "temp": target_temp,
            "pressure": target_press, 
            "reactivity": 0.0,
            "period": 0.0, # Stable
            "alerts": [],
            "scram": False,
            "stability_margin": 100.0,
            "health": 100.0,
            "xenon": 1.0,  # Equilibrium Xe
            "iodine": 1.0,
            "void_fraction": 0.2 if r_type in [ReactorType.BWR, ReactorType.RBMK] else 0.0, 
            # Advanced Telemetry
            "water_level": 5.0,
            "steam_flow": 500.0,
            "boron_ppm": 500.0 if r_type == ReactorType.PWR else 0.0,
            # RBMK specific
            "graphite_tip_position": 0.0, 
            # Catastrophic State
            "melted": False,
            "containment_integrity": 100.0,
            "radiation_released": 0.0,
        }
        
        self.event_log = []
        self.failure_cause = None
        self.post_mortem_report = None
        self.safety.alerts = []
        self.history = []
        
        # Replay State
        self.replay_scenario = None
        self.is_replay = False
        self.replay_speed = 1.0
        
        # Reset physics layers if needed (simplified)
        self.physics.xenon_poisoning = 0.0

    def log_event(self, message):
        """Logs a critical event if it hasn't just happened."""
        # Simple debounce: don't log same msg within 5 seconds
        if self.event_log and self.event_log[-1]["event"] == message and (self.time_seconds - self.event_log[-1]["time"] < 5.0):
            return
        self.event_log.append({"time": self.time_seconds, "event": message})

    def tick(self, dt=1.0):
        if self.is_replay and self.replay_scenario:
            self._tick_replay(dt)
        else:
            self._tick_simulation(dt)

    def _tick_replay(self, dt):
        """Advances the simulation by interpolating historical phases."""
        self.time_seconds += dt * self.replay_speed
        phases = self.replay_scenario.phases
        
        # Find current and next phase
        current_phase = phases[0]
        next_phase = None
        
        for p in phases:
            if p['time'] <= self.time_seconds:
                current_phase = p
            else:
                next_phase = p
                break
        
        if not next_phase:
            # Reached end of history
            self.telemetry.update(current_phase['telemetry'])
            return

        # Interpolation factor
        total_gap = next_phase['time'] - current_phase['time']
        if total_gap <= 0:
             self.telemetry.update(next_phase['telemetry'])
             return
             
        progress = (self.time_seconds - current_phase['time']) / total_gap
        
        # Interpolate all numeric keys in telemetry
        for k, v_next in next_phase['telemetry'].items():
            if k in current_phase['telemetry']:
                v_curr = current_phase['telemetry'][k]
                if isinstance(v_next, (int, float)) and isinstance(v_curr, (int, float)):
                    self.telemetry[k] = v_curr + (v_next - v_curr) * progress
                else:
                    self.telemetry[k] = v_next # Non-numeric (bools, etc)
            else:
                self.telemetry[k] = v_next
        
        # Ensure health is checked for meltdown visual
        if self.telemetry.get("health", 100) <= 0:
            self.telemetry["melted"] = True

        # Log historical events
        if "label" in current_phase and not any(current_phase["label"] in e["event"] for e in self.event_log[-2:]):
            self.log_event(f"HISTORICAL: {current_phase['label']}")

        self._record_history()

    def _tick_simulation(self, dt=1.0):
        """Standard reactor physics tick."""
        self.time_seconds += dt
        c = self.control_state
        t = self.telemetry
        conf = self.config
        
        # --- 0. Control Response & Mechanics ---
        # Flow Logic & Water Inventory
        # Mass Balance: dM/dt = Feedwater - SteamFlow
        # Level approx M
        
        steam_production = t["power_mw"] / 20.0 # Arbitrary units
        t["steam_flow"] = steam_production
        
        feedwater_in = c["feedwater_flow"] / 100.0 * 160.0 # Scale to match max steam
        
        if self.type != ReactorType.PWR: # PWR usually has closed secondary, but let's simplify
             # Open loop for BWR/RBMK
             level_change = (feedwater_in - steam_production) * 0.01 * dt
             t["water_level"] = max(0.0, t["water_level"] + level_change)
             
             # Low level trip
             if t["water_level"] < 2.0: # Core uncovering
                 t["health"] -= 1.0 * dt
                 self.safety.alerts.append("LOW WATER LEVEL")
        
        target_flow = c["pump_speed"] * conf.cooling_penalty
        # Flow inertia
        c["flow_rate_core"] += (target_flow - c["flow_rate_core"]) * 0.1 * dt
        
        # PWR Pressure Logic
        if self.type == ReactorType.PWR:
            # P changes with Temp (expansion) + Heaters/Sprays
            # Ideal Gas-ish: P ~ T
            p_target = (t["temp"] / 300.0) * 150.0
            
            if c["pressurizer_heaters"]: p_target += 20.0
            if c["pressurizer_sprays"]: p_target -= 20.0
            
            
            # Inertia
            t["pressure"] += (p_target - t["pressure"]) * 0.1 * dt
            
        # Emergency Venting
        if c.get("manual_vent", False) and t["pressure"] > 5.0:
            vent_rate = 50.0 # Bar/s
            t["pressure"] = max(1.0, t["pressure"] - vent_rate * dt)
            t["water_level"] -= 0.1 * dt # Lose inventory
            t["radiation_released"] += 5.0 * dt # Massive release
            self.safety.alerts.append("VENTING RADS")

        # ECCS Injection
        if c.get("eccs_active", False):
            # Massive flow, cold water
            t["water_level"] += 0.5 * dt 
            t["temp"] -= 50.0 * dt # Rapid cooling
            t["boron_ppm"] += 100.0 * dt # ECCS water is heavily borated
            
            # Thermal Shock damage
            if t["temp"] > 800:
                t["health"] -= 2.0 * dt
                self.safety.alerts.append("THERMAL SHOCK")

        # Boron Logic (PWR)
        boron_reactivity = 0.0
        if self.type == ReactorType.PWR:
            # Mixing lag
            t["boron_ppm"] += (c["boron_concentration"] - t["boron_ppm"]) * 0.05 * dt
            # Worth: -10 pcm per ppm? Let's say -0.01 reactivity per 1000 ppm
            boron_reactivity = -(t["boron_ppm"] / 20000.0)
            
        # --- 1. Safety Check (Scram Override) ---
        self.safety.interlocks_active = c["safety_enabled"]
        is_scrammed = self.safety.check(t["flux"], t["temp"], c["flow_rate_core"], c["manual_scram"])
        
        if is_scrammed:
            # Rod movement logic
            # RBMK: Slow insertion + Tip Effect
            # PWR/BWR: Fast
            speed = conf.scram_insertion_speed * 10.0 # % per second base
            c["rods_pos"] = min(100.0, c["rods_pos"] + speed * dt)
            c["manual_scram"] = False # Latch handles state
            
        # --- 2. Advanced Physics Loop ---
        
        # A. Rod Worth & Tip Effect
        # Standard rod worth curve is cosine-like (most worth in center)
        # 100% in = -5.0 delta k, 0% in = +2.0 delta k (just roughly)
        raw_rod_pos = c["rods_pos"] / 100.0
        
        # RBMK Graphite Tip Effect Logic
        # If rods move IN from 0%, initially they displace water with graphite -> POSITIVE reactivity
        tip_reactivity = 0.0
        if conf.scram_tip_effect and is_scrammed:
        # If rods are moving in the top section (0-30%) - Fixed condition for start of movement
             if raw_rod_pos < 0.3 and raw_rod_pos >= 0.0:
                 tip_reactivity = 0.005 # Massive positive spike (+500 pcm)
        
        eff_rods = c["rods_pos"] 
        
        # B. Reactivity Feedbacks
        
        # Void Feedback (Steam)
        # More power -> More Temp -> More Voids
        # BWR/RBMK has boiling. PWR has subcooled boiling (rarely voids unless accident)
        void_fraction = 0.0
        if t["temp"] > 280: # Boiling onset
            void_fraction = min(1.0, (t["temp"] - 280) * 0.01) * (t["power_mw"]/3200.0)
        
        t["void_fraction"] = void_fraction
        
        feedback_void = void_fraction * conf.void_coefficient
        
        # Doppler Feedback (Fuel Temp)
        feedback_doppler = ((t["temp"] - 300) * 0.0001) * conf.doppler_coefficient
        
        # Xenon Poisoning (Simplified)
        # Flux burns Xenon. Low flux = Xenon builds up (transient).
        # We model 'xenon_poison' as negative reactivity
        xenon_production = 0.001 # constant decay from Iodine
        xenon_burnout = t["flux"] * 0.002 * conf.xenon_burnout_rate
        t["xenon"] = max(0.0, t["xenon"] + (xenon_production - xenon_burnout) * dt)
        feedback_xenon = (t["xenon"] - 1.0) * -0.01 # Excess xenon = neg reactivity
        
        # Total External Reactivity Addition
        disturbances = conf.disturbance_flux
        
        total_feedback = feedback_void + feedback_doppler + feedback_xenon + tip_reactivity + disturbances + boron_reactivity
        
        # Physics update
        # Pass total_feedback as extra_k
        current_flux = self.physics.update(eff_rods, t["temp"], extra_k=total_feedback, dt=dt)
        
        # Update period from physics layer
        t["period"] = self.physics.period
        t["reactivity"] = self.physics.reactivity
        
        # Apply visual jitter to flux
        t["flux"] = max(0, current_flux)
        
        # --- 3. Thermal Update ---
        # Cooling based on Flow
        cooling_factor = (c["flow_rate_core"] / 100.0) * conf.cooling_penalty
        
        # Thermal power generation
        t["power_mw"] = t["flux"] * 3200.0 # 3200MWth max
        
        # Heat transfer
        # Q_gen - Q_removed = M*Cp*dT/dt
        q_gen = t["power_mw"]
        q_removed = (t["temp"] - 20) * 10.0 * cooling_factor # Simple UA*(T-Tsink)
        
        delta_temp = (q_gen - q_removed) * 0.05 * (dt / conf.thermal_inertia)
        t["temp"] += delta_temp
        
        # --- 4. Health & Safety ---
        t["scram"] = is_scrammed
        t["alerts"] = self.safety.alerts
        
        # Stability Margin
        # Based on how close k is to Prompt Critical
        # And how much thermal margin is left
        t["stability_margin"] = max(0, 100 - (abs(self.physics.reactivity) * 50000) - ((t["temp"]/1000)*50))
        
        # Damage
        if t["temp"] > 900:
             # Fuel melting
             t["health"] -= 0.5 * dt
        
             t["health"] -= 1.0 * dt
             
        # Catastrophic Failure Logic
        if t["temp"] > 2800.0 and not t["melted"]:
            t["melted"] = True
            t["health"] = 0.0
            self.failure_cause = "Core Meltdown (Fuel Liquefaction)"
            self.log_event("CORE MELTDOWN TRIGGERED")
            self.generate_post_mortem()
        
        if t["pressure"] > 250.0 and t["containment_integrity"] > 0:
            t["containment_integrity"] = 0.0
            t["health"] = 0.0
            t["alerts"].append("CONTAINMENT BREACH")
            t["radiation_released"] += 1000.0 * dt
            self.failure_cause = "Containment Vessel Rupture (Overpressure)"
            self.log_event("CONTAINMENT BREACHED")
            self.generate_post_mortem()

        # Precursor Logging
        if t["temp"] > 2000 and not any("Fuel Temperature Critical" in e["event"] for e in self.event_log[-3:]):
            self.log_event(f"Fuel Temperature Critical: {t['temp']:.1f}C")
        if t["void_fraction"] > 0.8 and self.type == ReactorType.RBMK:
             self.log_event(f"Void Fraction Critical: {t['void_fraction']*100:.1f}%")
        if t["xenon"] > 2.0:
             self.log_event(f"Xenon Pit Depth Maximum: {t['xenon']:.2f}")

        self._record_history()
        
        # Decay disturbance
        if conf.disturbance_flux > 0: conf.disturbance_flux *= 0.9

    def generate_post_mortem(self):
        """Generates an educational report on why the reactor died."""
        t = self.telemetry
        c = self.control_state
        cause = self.failure_cause
        
        # 1. Root Cause Analysis
        explanation = ""
        tips = ""
        
        if self.type == ReactorType.RBMK:
            if t["void_fraction"] > 0.5 and t["flux"] > 1.5:
                explanation = "POSITIVE VOID COEFFICIENT DISASTER.\n\n" \
                              "In an RBMK, steam bubbles (voids) increase reactivity. " \
                              "As boiling increased, power rose, creating MORE steam, creating MORE power. " \
                              "This positive feedback loop caused a thermal runaway."
                tips = "Avoid low power operations where instability is high. Do not let the core boil uncontrollably."
                
                if t["graphite_tip_position"] > 0:
                    explanation += "\n\nCRITICAL DESIGN FLAW: GRAPHITE TIPS.\n" \
                                   "The SCRAM initially inserted graphite (moderator) tips, which displaced water (absorber). " \
                                   "This caused the final fatal power spike."
            else:
                 explanation = "Loss of Coolant / Dryout.\nFeedwater failure led to core uncovery."
        
        elif self.type == ReactorType.PWR:
            if cause == "Containment Vessel Rupture (Overpressure)":
                explanation = "HYDRAULIC RUPTURE.\n\n" \
                              "Water is incompressible. Without a steam bubble in the pressurizer (concave functionality), " \
                              "thermal expansion spiked the pressure instantly, bursting the vessel."
                tips = "Maintain the steam bubble in the pressurizer. Watch heating rates."
            else:
                explanation = "THERMAL MELTDOWN.\nDecay heat or lack of flow melted the fuel rods."
                
        elif self.type == ReactorType.BWR:
             explanation = "BOILING CRISIS.\nToo much steam blocked water from cooling the rods (Dryout), leading to clad failure."
        
        if c["safety_enabled"] == False:
            explanation += "\n\nNON-COMPLIANCE: SAFETY SYSTEMS DISABLED.\nThe automatic SCRAM meant to prevent this was manually bypassed."

        self.post_mortem_report = {
            "cause": cause,
            "explanation": explanation,
            "prevention": [tips] if isinstance(tips, str) else (tips if tips else []),
            "timeline": self.event_log[-10:] # Last 10 events
        }
        

    def apply_preset(self, preset_name):
        """Applies a named physics/context configuration."""
        if preset_name == "STABLE":
            self.config.responsiveness = 0.8
            self.config.disturbance_flux = 0
        elif preset_name == "VOLATILE":
            self.config.responsiveness = 1.5
            self.telemetry["xenon"] = 2.0 # High poison, hard to start
        elif preset_name == "DEGRADED":
            self.config.cooling_penalty = 0.8
            self.telemetry["health"] = 80.0

    def set_state_override(self, telemetry_override):
        self.telemetry.update(telemetry_override)
        
        # Try to infer control state for better 'Take Control' continuity
        # e.g. if power is high, rods are probably out
        if "power_mw" in telemetry_override:
            # Simple inverse rod logic: Power 3200 -> R0, Power 0 -> R100
            # (Just a guess to prevent immediate jump on handover)
            p_ratio = telemetry_override["power_mw"] / 3200.0
            self.control_state["rods_pos"] = max(0, min(100, 100 - (p_ratio * 100)))
            
        self._record_history()

    def _record_history(self):
        if len(self.history) == 0 or self.time_seconds - self.history[-1]["time_seconds"] >= 1.0:
            self.history.append({
                "time_seconds": self.time_seconds,
                "power_mw": self.telemetry["power_mw"],
                "temp": self.telemetry["temp"],
                "reactivity": self.telemetry["reactivity"] * 10000
            })
            if len(self.history) > 100: self.history.pop(0)

    def get_full_state(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "telemetry": self.telemetry,
            "controls": self.control_state,
            "history": self.history
        }

class ReactorEngine:
    def __init__(self):
        self.reinitialize_fleet()
        self.global_time = 0
        self.active_scenario = None
        self.scenario_time = 0.0
        self.current_phase = None
        
    def reinitialize_fleet(self):
        """Restores the standard training units (A=PWR, B=BWR, C=RBMK)."""
        self.units = {
            "A": ReactorUnit("A", "UNIT-1 (PWR)", ReactorType.PWR),
            "B": ReactorUnit("B", "UNIT-2 (BWR)", ReactorType.BWR),
            "C": ReactorUnit("C", "UNIT-3 (RBMK)", ReactorType.RBMK)
        }
        
    def load_scenario(self, scenario_id):
        if scenario_id in SCENARIOS:
            self.active_scenario = SCENARIOS[scenario_id]
            self.scenario_time = 0.0
            # Unit A becomes the Replay Actor
            # We must set correct type for scenario
            scen_type = ReactorType.RBMK if "Chernobyl" in self.active_scenario.title else ReactorType.PWR
            
            self.units["A"] = ReactorUnit("A", self.active_scenario.title, scen_type)
            # Set Initial State
            initial_phase = self.active_scenario.phases[0]
            self.current_phase = initial_phase
            self.units["A"].set_state_override(initial_phase["telemetry"])
            self.units["A"].history = []
            
    def unload_scenario(self):
        self.active_scenario = None
        self.units["A"] = ReactorUnit("A", "UNIT-1 (PWR)", ReactorType.PWR)

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
        active_p = self.active_scenario.phases[0]
        for p in self.active_scenario.phases:
            if self.scenario_time >= p["time"]:
                active_p = p
        
        self.current_phase = active_p
        
        # 2. Apply State
        # In scenario mode, we override physics significantly
        target = active_p["telemetry"]
        self.units["A"].set_state_override(target)
            
    def update_controls(self, unit_id, controls):
        if self.active_scenario and unit_id == "A":
            return 
            
        if unit_id in self.units:
            self.units[unit_id].control_state.update(controls)

    def update_config(self, unit_id, config_dict):
        if unit_id in self.units:
            u_conf = self.units[unit_id].config
            for k, v in config_dict.items():
                if hasattr(u_conf, k):
                    setattr(u_conf, k, v)
    
    def inject_disturbance(self, unit_id, type="SPIKE"):
        if unit_id in self.units:
            u_conf = self.units[unit_id].config
            if type == "SPIKE":
                u_conf.disturbance_flux = 0.5 
            elif type == "COOLING_FAIL":
                u_conf.cooling_penalty = 0.2
            elif type == "RESET":
                u_conf.disturbance_flux = 0
                u_conf.cooling_penalty = 1.0
            
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
