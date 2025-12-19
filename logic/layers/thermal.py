class ThermalLayer:
    def __init__(self):
        self.core_temp = 300.0 # deg C (Base)
        self.coolant_temp_out = 280.0
        self.coolant_flow = 100.0 # %
        self.heat_exchange_eff = 1.0 
        self.status = "Stable"
        
    def update(self, flux, pump_speed_pct, cooling_eff_pct, dt=1.0):
        """
        Heat Balance:
        Heat In = Flux * Power_Constant
        Heat Out = Flow * (T_core - T_sink) * Eff
        """
        power_mw = flux * 2000.0 # 2000MWth at 1.0 flux
        
        # Cooling Cap
        flow_factor = (pump_speed_pct / 100.0)
        eff_factor = (cooling_eff_pct / 100.0)
        
        heat_removal_capacity = flow_factor * eff_factor * 2500.0 # Capacity > Generation
        
        # Heat Balance
        # Q = m * Cp * dT
        # Simplified: Change in core temp
        net_heat = power_mw - (heat_removal_capacity * (self.core_temp / 600.0)) # Higher temp = easier to shed
        
        temp_rise = net_heat * 0.05 * dt # thermal mass factor
        self.core_temp += temp_rise
        
        # Ambient loss
        self.core_temp -= (self.core_temp - 25.0) * 0.001 * dt
        
        self.core_temp = max(25.0, self.core_temp)
        
        # Evaluate Status
        if self.core_temp > 600: self.status = "MELTDOWN"
        elif self.core_temp > 450: self.status = "CRITICAL"
        elif self.core_temp > 350: self.status = "Unstable"
        else: self.status = "Nominal"
            
        return self.core_temp
