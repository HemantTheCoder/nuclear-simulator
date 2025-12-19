class ReactivityLayer:
    def __init__(self):
        self.reactivity = 0.0 # Delta K/K (0 = Critical)
        self.neutron_flux = 1.0 # Normalized (1.0 = 100% Power)
        self.period = 999.0 # Seconds (inf = stable)
        self.xenon_poisoning = 0.0 # Negative reactivity
        
        # Initial State
        self.control_rod_insertion = 50.0 # % (0 = Out, 100 = In)
        
    def update(self, rods_pos, temp, extra_k=0.0, dt=1.0):
        """
        Updates neutron flux based on reactivity sources.
        dt in seconds (simulated)
        """
        # 1. Control Rod Worth
        # Simple linear worth for now, can be cosine later
        # 0% rods = +0.05 reactivity (Supercritical)
        # 100% rods = -0.05 reactivity (Subcritical)
        rho_rods = (50.0 - rods_pos) * 0.002 # 0.1 total swing
        
        # 2. Thermal Feedback (Doppler + Moderator)
        # Negative feedback: Higher temp -> Lower reactivity
        temp_delta = temp - 300.0 # Base temp 300C
        rho_temp = -0.0001 * temp_delta 
        
        # 3. Xenon (Simplified)
        # Xenon grows with Flux, decays with time
        # Here we just treat it as a load that grows at high pow
        if self.neutron_flux > 1.2:
            self.xenon_poisoning += 0.00005 * dt
        else:
            self.xenon_poisoning *= 0.999 # Decay
            
        # Total Reactivity
        self.reactivity = rho_rods + rho_temp - self.xenon_poisoning + extra_k
        
        # Point Kinetics (Simplified)
        # dN/dt = (rho - beta)/L * N ... ignoring delayed for now for simpler UX
        # Exponential Period equation: P = P0 * e^(t/T)
        # Period T approx l / rho (simplified)
        
        if abs(self.reactivity) < 0.00001:
            self.period = 9999.0
        else:
            self.period = 0.08 / self.reactivity # 0.08 generation time approx
            
        # Flux Update
        # Limit exponential growth closely
        growth_factor = self.reactivity * dt * 5.0 # Tuned for playable speed
        self.neutron_flux *= (1.0 + growth_factor)
        
        # Clamp
        self.neutron_flux = max(0.0, self.neutron_flux)
        
        return self.neutron_flux
