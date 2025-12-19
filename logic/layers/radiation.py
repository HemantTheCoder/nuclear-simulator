class RadiationLayer:
    def __init__(self, ambient_radiation=0.0):
        self.sieverts_per_day = ambient_radiation
        self.accumulated_dose = 0.0
        self.dna_damage_score = 0.0 # 0 to 100
        self.status = "Safe"

    def update(self, shielding_factor):
        # Shielding reduces incoming radiation
        # Shielding 0.0 (None) -> 1.0 (Lead/Regolith)
        effective_dose = self.sieverts_per_day * (1.0 - shielding_factor)
        self.accumulated_dose += effective_dose
        
        # DNA Damage accumulation logic
        # Repair mechanisms exist (subtract small amount daily), but overwhelm at high doses
        repair_rate = 0.01 
        damage_surge = effective_dose * 10
        self.dna_damage_score = max(0, min(100, self.dna_damage_score + damage_surge - repair_rate))
        
        self._evaluate_status()
        return self.dna_damage_score

    def _evaluate_status(self):
        if self.dna_damage_score > 80:
            self.status = "Genetic Collapse"
        elif self.dna_damage_score > 40:
            self.status = "High Mutation Risk"
        else:
            self.status = "Stable"
