class ResourceLayer:
    def __init__(self):
        self.water_stored = 1000.0 # Liters
        self.power_usage = 0.0 # MW
        self.water_loss = 0.0 # L/day
        
        # Soil Properties
        self.soil_moisture = 50.0 # %
        self.salinity = 1.0 # % (Earth ~0.5, Mars ~10+)
        self.npk_index = 0.5 # 0.0 to 1.0 (Nutrient richness)

    def calculate_consumption(self, habitat_type, heating_demand, pressure_support, controls={}):
        """
        Calculates resource usage based on detailed controls.
        """
        self.power_usage = 0.0
        
        # 1. Power Cost
        # Heating is expensive
        self.power_usage += heating_demand * 1.5 
        
        # Pressurization
        if pressure_support > 0:
            self.power_usage += 20 * pressure_support
            
        # Water Recycling / Pumps
        if controls.get("water_enabled"):
            self.power_usage += 5
            
        # Scrubbers
        if controls.get("scrubber_enabled"):
            self.power_usage += 15
            
        # 2. Water / Soil Dynamics
        # Input
        water_in = controls.get("daily_water_ml", 500) / 1000.0 # L/day -> Sim is weekly tick? Assuming daily input total
        
        # Loss (Drainage + Evap)
        drainage_eff = controls.get("drainage_eff", 0.5)
        temp_factor = 1.0 + (heating_demand / 40.0) # Hotter = more evap
        
        self.water_loss = (1.0 - drainage_eff) * 2.0 * temp_factor 
        if controls.get("pressure_enabled") == False:
             self.water_loss *= 10 # Boil off
             
        # Soil Moisture Update
        # Moisture = In - Out
        net_change = (water_in - self.water_loss) / 5.0 # Arbitrary volume factor
        self.soil_moisture += net_change
        self.soil_moisture = max(0, min(100, self.soil_moisture))
        
        # Salinity Accumulation
        # If water evaps but salts stay -> Salinity UP
        # If drainage is high -> Salinity DOWN (Flushing)
        if self.water_loss > water_in:
            self.salinity += 0.1
        if drainage_eff > 0.7:
            self.salinity -= 0.2
        self.salinity = max(0, self.salinity)

        return self.power_usage
