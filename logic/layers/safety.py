class SafetyLayer:
    def __init__(self):
        self.scram_status = False
        self.alerts = []
        self.interlocks_active = True
        
        # Thresholds
        self.max_temp = 420.0
        self.max_flux = 1.15
        self.min_flow = 10.0
        
    def check(self, flux, temp, flow, manual_scram=False):
        self.alerts = []
        triggered = False
        
        if manual_scram:
            self.scram_status = True
            self.alerts.append("MANUAL SCRAM INITIATED")
            triggered = True
            
        if self.interlocks_active:
            if temp > self.max_temp:
                self.scram_status = True
                self.alerts.append(f"TEMP HIGH TRIP ({temp:.0f}C)")
                triggered = True
                
            if flux > self.max_flux:
                self.scram_status = True
                self.alerts.append(f"FLUX HIGH TRIP ({flux*100:.0f}%)")
                triggered = True
                
            if flow < self.min_flow and flux > 0.1:
                self.scram_status = True
                self.alerts.append("LOSS OF FLOW TRIP")
                triggered = True
                
        return self.scram_status
