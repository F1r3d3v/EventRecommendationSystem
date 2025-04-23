# fuzzy/fuzzy_system.py
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class EventFuzzySystem:
    """
    Mamdani fuzzy inference system for event recommendations
    """
    def __init__(self):
        # Input variables
        self.interest_match = ctrl.Antecedent(np.arange(0, 101, 1), 'interest_match')
        self.location_proximity = ctrl.Antecedent(np.arange(0, 101, 1), 'location_proximity')
        self.time_overlap = ctrl.Antecedent(np.arange(0, 101, 1), 'time_overlap')
        self.budget_alignment = ctrl.Antecedent(np.arange(0, 101, 1), 'budget_alignment')
        
        # Output variable
        self.recommendation = ctrl.Consequent(np.arange(0, 101, 1), 'recommendation')
        
        # Define fuzzy sets for each variable
        self._define_fuzzy_sets()
        
        # Define fuzzy rules
        self._define_rules()
        
        # Create control system
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)
        
    def _define_fuzzy_sets(self):
        """Define the fuzzy sets for each variable"""
        # Interest/Category Match
        self.interest_match['low'] = fuzz.trimf(self.interest_match.universe, [0, 0, 40])
        self.interest_match['medium'] = fuzz.trimf(self.interest_match.universe, [20, 50, 80])
        self.interest_match['high'] = fuzz.trimf(self.interest_match.universe, [60, 100, 100])
        
        # Location Proximity (higher value = closer location)
        self.location_proximity['far'] = fuzz.trimf(self.location_proximity.universe, [0, 0, 40])
        self.location_proximity['moderate'] = fuzz.trimf(self.location_proximity.universe, [20, 50, 80])
        self.location_proximity['near'] = fuzz.trimf(self.location_proximity.universe, [60, 100, 100])
        
        # Time Range Overlap
        self.time_overlap['no_overlap'] = fuzz.trimf(self.time_overlap.universe, [0, 0, 30])
        self.time_overlap['partial'] = fuzz.trimf(self.time_overlap.universe, [20, 50, 80])
        self.time_overlap['complete'] = fuzz.trimf(self.time_overlap.universe, [70, 100, 100])
        
        # Budget Alignment (higher value = better budget fit)
        self.budget_alignment['over_budget'] = fuzz.trimf(self.budget_alignment.universe, [0, 0, 30])
        self.budget_alignment['at_limit'] = fuzz.trimf(self.budget_alignment.universe, [20, 50, 80])
        self.budget_alignment['within_budget'] = fuzz.trimf(self.budget_alignment.universe, [70, 100, 100])
        
        # Recommendation Score
        self.recommendation['low'] = fuzz.trimf(self.recommendation.universe, [0, 15, 30])
        self.recommendation['medium'] = fuzz.trimf(self.recommendation.universe, [20, 45, 70])
        self.recommendation['high'] = fuzz.trimf(self.recommendation.universe, [60, 80, 100])

    def _define_rules(self):
        """Define the fuzzy rules for the inference system"""
        self.rules = [
            # High priority rules
            ctrl.Rule(self.interest_match['high'] & self.location_proximity['near'] & 
                     self.time_overlap['complete'] & self.budget_alignment['within_budget'], 
                     self.recommendation['high']),
            
            ctrl.Rule(self.interest_match['high'] & self.location_proximity['near'] & 
                     self.time_overlap['complete'] & self.budget_alignment['at_limit'], 
                     self.recommendation['high']),
            
            ctrl.Rule(self.interest_match['high'] & self.location_proximity['near'] & 
                     self.time_overlap['partial'] & self.budget_alignment['within_budget'], 
                     self.recommendation['high']),
            
            # Medium priority rules
            ctrl.Rule(self.interest_match['medium'] & self.location_proximity['near'] & 
                     self.time_overlap['complete'] & self.budget_alignment['within_budget'], 
                     self.recommendation['high']),
            
            ctrl.Rule(self.interest_match['high'] & self.location_proximity['moderate'] & 
                     self.time_overlap['partial'] & self.budget_alignment['within_budget'], 
                     self.recommendation['medium']),
            
            ctrl.Rule(self.interest_match['medium'] & self.location_proximity['moderate'] & 
                     self.time_overlap['partial'] & self.budget_alignment['at_limit'], 
                     self.recommendation['medium']),
            
            # Low recommendation rules
            ctrl.Rule(self.interest_match['low'] | self.time_overlap['no_overlap'] |
                     self.budget_alignment['over_budget'], self.recommendation['low']),
            
            ctrl.Rule(self.interest_match['low'] & self.location_proximity['far'], 
                     self.recommendation['low']),
            
            # Additional balanced rules
            ctrl.Rule(self.interest_match['medium'] & self.location_proximity['moderate'] & 
                     self.time_overlap['partial'] & self.budget_alignment['within_budget'], 
                     self.recommendation['medium']),
                     
            ctrl.Rule(self.interest_match['high'] & self.location_proximity['far'] & 
                     self.time_overlap['partial'] & self.budget_alignment['within_budget'], 
                     self.recommendation['medium']),
        ]
    
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
        # Input values to the simulation
        self.simulation.input['interest_match'] = interest
        self.simulation.input['location_proximity'] = proximity
        self.simulation.input['time_overlap'] = time_overlap
        self.simulation.input['budget_alignment'] = budget
        
        # Compute output
        self.simulation.compute()
        
        if self.simulation.output == {}:
            self.simulation.output['recommendation'] = 0
        
        # Return recommendation score
        return self.simulation.output['recommendation']
    
    def visualize_sets(self):
        """Return the fuzzy set visualizations for UI display"""
        self.interest_match.view()
        self.location_proximity.view()
        self.time_overlap.view()
        self.budget_alignment.view()
        self.recommendation.view()