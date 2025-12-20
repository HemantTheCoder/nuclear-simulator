class Instructor:
    """
    The Instructor analyzes the reactor state and provides educational feedback,
    warnings, and context to the user, mimicking a senior operator or trainer.
    """
    
    @staticmethod
    def analyze(unit):
        """
        Returns a list of messages (tips/warnings) based on current state.
        Each message is a dict: {"type": "info"|"warning"|"danger", "msg": str}
        """
        messages = []
        t = unit.telemetry
        c = unit.control_state
        r_type = unit.type.value
        
        # 1. Xenon Pit Analysis
        # If Power is low but Xenon is high, explain the "Xenon Pit"
        if t["power_mw"] < 500 and t.get("xenon", 1.0) > 1.5:
             messages.append({
                 "type": "warning",
                 "msg": "🛑 **XENON PIT DETECTED**: Power is low, but Xenon poison is high. The reactor is 'poisoned out'. Attempting to raise power now is difficult and dangerous (potential for instability)."
             })

        # 2. Startup Rate (Period)
        period = t.get("period", 999)
        if 0 < period < 20:
            messages.append({
                "type": "danger",
                "msg": "⚠️ **FAST STARTUP**: Reactor period is under 20s. Power is rising exponentially fast. Insert rods immediately to stabilize."
            })
            
        # 3. DNBR (To be implemented in engine, but we check here)
        dnbr = t.get("dnbr", 3.0)
        if dnbr < 1.3:
            messages.append({
                "type": "danger",
                "msg": "🔥 **DNBR CRITICAL**: Departure from Nucleate Boiling Ratio is < 1.3. Fuel cladding is overheating. Increase Flow or Scram."
            })

        # 4. RBMK Specifics
        if r_type == "RBMK":
            if c["rods_pos"] < 10 and t["power_mw"] > 1000:
                messages.append({
                    "type": "warning",
                    "msg": "⚠️ **OPERATING MARGIN LOW**: Operational Reactivity Margin (ORM) is critical. Too many rods are withdrawn. SCRAM effectiveness is reduced."
                })
        
        # 5. Pressure / MSIV
        if not c.get("msiv_open", True) and t["pressure"] > 160:
             messages.append({
                 "type": "info",
                 "msg": "💡 **SYSTEM KNOWLEDGE**: With MSIV closed, steam has nowhere to go. Pressure rises until safety valves open. Open the Turbine Bypass or condenser."
             })

        return messages
