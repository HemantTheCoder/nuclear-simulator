import random

class SimulationEngine:
    def __init__(self):
        # Default Earth Conditions
        self.earth_params = {
            "temp": 20, # Celsius
            "pressure": 1.0, # atm
            "co2": 0.04, # %
            "water": True,
            "soil_ph": 6.5,
            "radiation": 0 # Low
        }
        
        # Default Mars Conditions
        self.mars_params = {
            "temp": -60, # Celsius
            "pressure": 0.006, # atm
            "co2": 95.0, # %
            "water": False,
            "soil_ph": 8.0, # Alkaline
            "radiation": 100 # High
        }

        self.state = {
            "day": 0,
            "earth_health": 100,
            "mars_health": 100,
            "earth_height": 0,
            "mars_height": 0,
            "status_earth": "Healthy",
            "status_mars": "Healthy"
        }

    def reset(self):
        self.__init__()

    def tick(self, earth_current, mars_current):
        self.state["day"] += 7 # Advance by a week
        
        # Update Earth Plant
        self.state["earth_health"] = self._calculate_health(earth_current, is_mars=False)
        if self.state["earth_health"] > 0:
            self.state["earth_height"] += random.uniform(0.5, 1.5)
        
        # Update Mars Plant
        self.state["mars_health"] = self._calculate_health(mars_current, is_mars=True)
        if self.state["mars_health"] > 0:
            growth_factor = 0.1 if self.state["mars_health"] < 50 else random.uniform(0.2, 0.8)
            self.state["mars_height"] += growth_factor
            
        self._update_status()
        return self.state

    def _calculate_health(self, params, is_mars):
        health = self.state["mars_health"] if is_mars else self.state["earth_health"]
        damage = 0

        # Temperature Stress (Ideal: 15-25)
        if params["temp"] < 5 or params["temp"] > 35:
            damage += 10
        elif params["temp"] < -10 or params["temp"] > 45:
            damage += 30

        # Pressure Stress (Ideal: ~1atm)
        if params["pressure"] < 0.1:
            damage += 40
        
        # Water
        if not params["water"]:
            damage += 20
        
        # Radiation
        if params["radiation"] > 50:
            damage += 15
        
        return max(0, health - damage)

    def _update_status(self):
        for planet in ["earth", "mars"]:
            h = self.state[f"{planet}_health"]
            if h <= 0:
                self.state[f"status_{planet}"] = "Dead"
            elif h < 40:
                self.state[f"status_{planet}"] = "Critical"
            elif h < 70:
                self.state[f"status_{planet}"] = "Stressed"
            else:
                self.state[f"status_{planet}"] = "Healthy"
