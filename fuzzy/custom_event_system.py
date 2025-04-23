# fuzzy/custom_event_system.py
from fuzzy.custom_mamdani import MamdaniFuzzySystem

class CustomEventFuzzySystem:
    """Event recommendation system using our custom Mamdani implementation"""
    def __init__(self):
        self.system = MamdaniFuzzySystem()
        
        # Define input variables
        self.interest_match = self.system.add_input_variable("interest_match", 0, 100)
        self.location_proximity = self.system.add_input_variable("location_proximity", 0, 100)
        self.time_overlap = self.system.add_input_variable("time_overlap", 0, 100)
        self.budget_alignment = self.system.add_input_variable("budget_alignment", 0, 100)
        
        # Define output variable
        self.recommendation = self.system.add_output_variable("recommendation", 0, 100)
        
        # Define fuzzy sets for each variable
        self._define_fuzzy_sets()
        
        # Define rules
        self._define_rules()
    
    def _define_fuzzy_sets(self):
        """Define the fuzzy sets for all variables"""
        # Interest/Category Match
        self.interest_match.add_set("low", "triangular", 0, 0, 40)
        self.interest_match.add_set("medium", "triangular", 20, 50, 80)
        self.interest_match.add_set("high", "triangular", 60, 100, 100)
        
        # Location Proximity (higher value = closer location)
        self.location_proximity.add_set("far", "triangular", 0, 0, 40)
        self.location_proximity.add_set("moderate", "triangular", 20, 50, 80)
        self.location_proximity.add_set("near", "triangular", 60, 100, 100)
        
        # Time Range Overlap
        self.time_overlap.add_set("no_overlap", "triangular", 0, 0, 30)
        self.time_overlap.add_set("partial", "triangular", 20, 50, 80)
        self.time_overlap.add_set("complete", "triangular", 70, 100, 100)
        
        # Budget Alignment (higher value = better budget fit)
        self.budget_alignment.add_set("over_budget", "triangular", 0, 0, 30)
        self.budget_alignment.add_set("at_limit", "triangular", 20, 50, 80)
        self.budget_alignment.add_set("within_budget", "triangular", 70, 100, 100)
        
        # Recommendation Score
        self.recommendation.add_set("low", "triangular", 0, 15, 30)
        self.recommendation.add_set("medium", "triangular", 20, 45, 70)
        self.recommendation.add_set("high", "triangular", 60, 80, 100)
    
    def _define_rules(self):
        """Define the fuzzy rules for the system"""
        # High priority rules
        self.system.add_rule(
            {"interest_match": "high", "location_proximity": "near", 
             "time_overlap": "complete", "budget_alignment": "within_budget", "op": "AND"},
            {"recommendation": "high"}
        )
        
        self.system.add_rule(
            {"interest_match": "high", "location_proximity": "near", 
             "time_overlap": "complete", "budget_alignment": "at_limit", "op": "AND"},
            {"recommendation": "high"}
        )
        
        self.system.add_rule(
            {"interest_match": "high", "location_proximity": "near", 
             "time_overlap": "partial", "budget_alignment": "within_budget", "op": "AND"},
            {"recommendation": "high"}
        )
        
        # Medium priority rules
        self.system.add_rule(
            {"interest_match": "medium", "location_proximity": "near", 
             "time_overlap": "complete", "budget_alignment": "within_budget", "op": "AND"},
            {"recommendation": "high"}
        )
        
        self.system.add_rule(
            {"interest_match": "high", "location_proximity": "moderate", 
             "time_overlap": "partial", "budget_alignment": "within_budget", "op": "AND"},
            {"recommendation": "medium"}
        )
        
        self.system.add_rule(
            {"interest_match": "medium", "location_proximity": "moderate", 
             "time_overlap": "partial", "budget_alignment": "at_limit", "op": "AND"},
            {"recommendation": "medium"}
        )
        
        # Low recommendation rules
        self.system.add_rule(
            {"interest_match": "low", "op": "OR"},
            {"recommendation": "low"}
        )
        
        self.system.add_rule(
            {"time_overlap": "no_overlap", "op": "OR"},
            {"recommendation": "low"}
        )
        
        self.system.add_rule(
            {"budget_alignment": "over_budget", "op": "OR"},
            {"recommendation": "low"}
        )
        
        self.system.add_rule(
            {"interest_match": "low", "location_proximity": "far", "op": "AND"},
            {"recommendation": "low"}
        )
        
        # Additional balanced rules
        self.system.add_rule(
            {"interest_match": "medium", "location_proximity": "moderate", 
             "time_overlap": "partial", "budget_alignment": "within_budget", "op": "AND"},
            {"recommendation": "medium"}
        )
        
        self.system.add_rule(
            {"interest_match": "high", "location_proximity": "far", 
             "time_overlap": "partial", "budget_alignment": "within_budget", "op": "AND"},
            {"recommendation": "medium"}
        )
    
    def evaluate(self, interest, proximity, time_overlap, budget):
        """
        Evaluate an event through the fuzzy system
        
        Args:
            interest: Interest/category match score (0-100)
            proximity: Location proximity score (0-100, higher = closer)
            time_overlap: Time range overlap score (0-100)
            budget: Budget alignment score (0-100, higher = better fit)
            
        Returns:
            Recommendation score (0-100)
        """
        # Prepare inputs
        inputs = {
            "interest_match": interest,
            "location_proximity": proximity,
            "time_overlap": time_overlap,
            "budget_alignment": budget
        }
        
        # Evaluate and return output
        outputs = self.system.evaluate(inputs)
        return outputs.get("recommendation", 50)  # Default to 50 if no output
    
    def plot_variables(self):
        """Plot all fuzzy variables in the system"""
        return self.system.plot_variables()
    
    def plot_surface(self, input_var1="interest_match", input_var2="location_proximity"):
        """Plot a 3D control surface for two input variables"""
        return self.system.plot_surface(input_var1, input_var2, "recommendation")