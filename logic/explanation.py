class ExplanationEngine:
    @staticmethod
    def analyze(state):
        explanations = []
        
        temp = state.get('temp', 300)
        flux = state.get('flux', 0.0)
        
        # 1. Thermal Analysis
        if temp > 450:
             explanations.append({
                "type": "Critical",
                "title": "Fuel Cladding Failure Risk",
                "cause": f"Core temp ({temp:.0f}C) exceeds zirconium limits.",
                "effect": "Release of fission products into coolant loop.",
                "action": "SCRAM reactor immediately and maximize cooling."
            })
            
        # 2. Reactivity Analysis
        if flux > 1.1:
             explanations.append({
                "type": "Warning",
                "title": "Overpower Transient",
                "cause": "Reactivity insertion exceeds delayed neutron fraction.",
                "effect": "Rapid power excursion (Prompt Critical risk).",
                "action": "Insert control rods to reduce flux."
            })
            
        return explanations
