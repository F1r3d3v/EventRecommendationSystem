# fuzzy/custom_mamdani.py
import numpy as np
import matplotlib.pyplot as plt

class FuzzySet:
    """Represents a fuzzy set with a membership function"""
    def __init__(self, name, universe):
        self.name = name
        self.universe = universe
        self.membership_values = np.zeros_like(universe, dtype=float)
    
    def membership(self, x):
        """Get membership degree for a value using interpolation"""
        if x <= self.universe[0]:
            return self.membership_values[0]
        if x >= self.universe[-1]:
            return self.membership_values[-1]
        
        # Find closest points for interpolation
        idx = np.searchsorted(self.universe, x)
        x1, x2 = self.universe[idx-1], self.universe[idx]
        y1, y2 = self.membership_values[idx-1], self.membership_values[idx]
        
        # Linear interpolation
        return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    
    def triangular(self, a, b, c):
        """Define a triangular membership function"""
        self.membership_values = np.zeros_like(self.universe, dtype=float)
        for i, x in enumerate(self.universe):
            if x <= a or x >= c:
                self.membership_values[i] = 0.0
            elif a < x <= b:
                self.membership_values[i] = (x - a) / (b - a)
            elif b < x < c:
                self.membership_values[i] = (c - x) / (c - b)
        return self
    
    def trapezoidal(self, a, b, c, d):
        """Define a trapezoidal membership function"""
        self.membership_values = np.zeros_like(self.universe, dtype=float)
        for i, x in enumerate(self.universe):
            if x <= a or x >= d:
                self.membership_values[i] = 0.0
            elif a < x <= b:
                self.membership_values[i] = (x - a) / (b - a)
            elif b < x <= c:
                self.membership_values[i] = 1.0
            elif c < x < d:
                self.membership_values[i] = (d - x) / (d - c)
        return self
    
    def gaussian(self, mean, sigma):
        """Define a Gaussian membership function"""
        self.membership_values = np.exp(-((self.universe - mean) ** 2) / (2 * sigma ** 2))
        return self
    
    def plot(self, ax=None):
        """Plot the membership function"""
        if ax is None:
            _, ax = plt.subplots(figsize=(6, 4))
        ax.plot(self.universe, self.membership_values, label=self.name)
        ax.set_ylim([0, 1.1])
        ax.legend()
        return ax

class FuzzyVariable:
    """Represents a fuzzy variable with multiple fuzzy sets"""
    def __init__(self, name, universe_min, universe_max, num_points=100):
        self.name = name
        self.universe = np.linspace(universe_min, universe_max, num_points)
        self.sets = {}
    
    def add_set(self, name, set_type, *params):
        """Add a fuzzy set to this variable"""
        fuzzy_set = FuzzySet(name, self.universe)
        
        if set_type == "triangular":
            fuzzy_set.triangular(*params)
        elif set_type == "trapezoidal":
            fuzzy_set.trapezoidal(*params)
        elif set_type == "gaussian":
            fuzzy_set.gaussian(*params)
        else:
            raise ValueError(f"Unknown set type: {set_type}")
            
        self.sets[name] = fuzzy_set
        return fuzzy_set
    
    def fuzzify(self, crisp_value):
        """Convert a crisp value to fuzzy membership degrees"""
        result = {}
        for name, fuzzy_set in self.sets.items():
            result[name] = fuzzy_set.membership(crisp_value)
        return result
    
    def plot(self, ax=None):
        """Plot all membership functions for this variable"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 4))
        
        for name, fuzzy_set in self.sets.items():
            fuzzy_set.plot(ax)
            
        ax.set_title(f"{self.name} Membership Functions")
        ax.set_xlabel(self.name)
        ax.set_ylabel("Membership Degree")
        ax.grid(True)
        
        return ax

class FuzzyRule:
    """Represents a fuzzy rule"""
    def __init__(self, antecedent, consequent, weight=1.0):
        """
        Initialize a fuzzy rule
        
        Args:
            antecedent: Dictionary mapping variables to sets and operations
                        Example: {"temperature": "hot", "humidity": "high", "op": "AND"}
            consequent: Dictionary mapping output variable to set
                        Example: {"fan_speed": "fast"}
            weight: Rule weight between 0 and 1
        """
        self.antecedent = antecedent
        self.consequent = consequent
        self.weight = weight
    
    def evaluate(self, fuzzified_inputs):
        """
        Evaluate the rule based on fuzzified inputs
        
        Args:
            fuzzified_inputs: Dictionary mapping variables to their fuzzified values
                              Example: {"temperature": {"hot": 0.7, "cold": 0.1}, 
                                       "humidity": {"high": 0.8, "low": 0.2}}
        
        Returns:
            Dictionary mapping output variables to inferred fuzzy sets and firing strengths
        """
        # Find the firing strength of the rule
        strengths = []
        
        for var_name, set_name in self.antecedent.items():
            if var_name != "op":  # Skip the operation key
                var_fuzzified = fuzzified_inputs.get(var_name, {})
                set_strength = var_fuzzified.get(set_name, 0.0)
                strengths.append(set_strength)
        
        # Apply the fuzzy operation (default to AND)
        op = self.antecedent.get("op", "AND").upper()
        if op == "AND":
            firing_strength = min(strengths) if strengths else 0.0
        elif op == "OR":
            firing_strength = max(strengths) if strengths else 0.0
        else:
            raise ValueError(f"Unknown operation: {op}")
            
        # Apply rule weight
        firing_strength *= self.weight
        
        # Return the output with the firing strength
        result = {}
        for out_var, out_set in self.consequent.items():
            result[out_var] = {out_set: firing_strength}
            
        return result
    
    def __str__(self):
        """String representation of the rule"""
        antecedent_str = []
        for var, val in self.antecedent.items():
            if var != "op":
                antecedent_str.append(f"{var} IS {val}")
        
        op = self.antecedent.get("op", "AND").upper()
        antecedent_text = f" {op} ".join(antecedent_str)
        
        consequent_str = []
        for var, val in self.consequent.items():
            consequent_str.append(f"{var} IS {val}")
        consequent_text = " AND ".join(consequent_str)
        
        return f"IF {antecedent_text} THEN {consequent_text}"

class MamdaniFuzzySystem:
    """Custom implementation of a Mamdani fuzzy inference system"""
    def __init__(self):
        self.input_variables = {}
        self.output_variables = {}
        self.rules = []
        
    def add_input_variable(self, name, min_val, max_val, num_points=100):
        """Add an input variable to the system"""
        variable = FuzzyVariable(name, min_val, max_val, num_points)
        self.input_variables[name] = variable
        return variable
    
    def add_output_variable(self, name, min_val, max_val, num_points=100):
        """Add an output variable to the system"""
        variable = FuzzyVariable(name, min_val, max_val, num_points)
        self.output_variables[name] = variable
        return variable
    
    def add_rule(self, antecedent, consequent, weight=1.0):
        """Add a rule to the system"""
        rule = FuzzyRule(antecedent, consequent, weight)
        self.rules.append(rule)
        return rule
    
    def evaluate(self, inputs):
        """
        Evaluate the fuzzy system with the given inputs
        
        Args:
            inputs: Dictionary mapping input variables to crisp values
                  Example: {"temperature": 25, "humidity": 60}
                  
        Returns:
            Dictionary mapping output variables to crisp values
        """
        # Fuzzification step
        fuzzified_inputs = {}
        for var_name, crisp_value in inputs.items():
            if var_name in self.input_variables:
                fuzzified_inputs[var_name] = self.input_variables[var_name].fuzzify(crisp_value)
        
        # Rule evaluation and aggregation
        aggregated_outputs = {}
        for output_var_name, output_var in self.output_variables.items():
            # Initialize aggregated output for each set to zeros
            aggregated_outputs[output_var_name] = {}
            for set_name in output_var.sets.keys():
                aggregated_outputs[output_var_name][set_name] = 0.0
        
        # Evaluate each rule and aggregate results
        for rule in self.rules:
            rule_output = rule.evaluate(fuzzified_inputs)
            
            for out_var_name, out_sets in rule_output.items():
                if out_var_name in aggregated_outputs:
                    for set_name, firing_strength in out_sets.items():
                        # Maximum aggregation method for Mamdani
                        aggregated_outputs[out_var_name][set_name] = max(
                            aggregated_outputs[out_var_name].get(set_name, 0.0),
                            firing_strength
                        )
        
        # Defuzzification step using Center of Area (COA) method
        crisp_outputs = {}
        
        for var_name, var_sets in aggregated_outputs.items():
            output_var = self.output_variables[var_name]
            universe = output_var.universe
            
            # Initialize aggregated membership function
            aggregated_mf = np.zeros_like(universe, dtype=float)
            
            # Aggregate all output fuzzy sets based on their firing strengths
            for set_name, firing_strength in var_sets.items():
                if firing_strength > 0:
                    # Apply firing strength (implication) by truncating each set
                    truncated_mf = np.minimum(
                        output_var.sets[set_name].membership_values,
                        firing_strength
                    )
                    # Aggregate using maximum
                    aggregated_mf = np.maximum(aggregated_mf, truncated_mf)
            
            # Center of Area defuzzification
            if np.sum(aggregated_mf) > 0:
                crisp_outputs[var_name] = np.sum(universe * aggregated_mf) / np.sum(aggregated_mf)
            else:
                # Default to middle of universe if no rules fire
                crisp_outputs[var_name] = (universe[0] + universe[-1]) / 2.0
        
        return crisp_outputs
    
    def plot_variables(self):
        """Plot all fuzzy variables in the system"""
        input_count = len(self.input_variables)
        output_count = len(self.output_variables)
        
        fig, axes = plt.subplots(nrows=input_count+output_count, figsize=(10, 4*(input_count+output_count)))
        
        if input_count + output_count == 1:
            axes = [axes]
        
        # Plot input variables
        for i, (name, var) in enumerate(self.input_variables.items()):
            var.plot(axes[i])
            axes[i].set_title(f"Input: {name}")
        
        # Plot output variables
        for i, (name, var) in enumerate(self.output_variables.items()):
            var.plot(axes[i+input_count])
            axes[i+input_count].set_title(f"Output: {name}")
        
        plt.tight_layout()
        return fig
    
    def plot_surface(self, input_var1, input_var2, output_var, resolution=20):
        """Plot a 3D control surface for two input variables and one output"""
        if input_var1 not in self.input_variables or input_var2 not in self.input_variables:
            raise ValueError("Input variables not found in the system")
        if output_var not in self.output_variables:
            raise ValueError("Output variable not found in the system")
        
        var1 = self.input_variables[input_var1]
        var2 = self.input_variables[input_var2]
        
        # Generate grid points
        x = np.linspace(var1.universe[0], var1.universe[-1], resolution)
        y = np.linspace(var2.universe[0], var2.universe[-1], resolution)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)
        
        # Default values for other inputs
        default_inputs = {}
        for var_name in self.input_variables.keys():
            if var_name != input_var1 and var_name != input_var2:
                var = self.input_variables[var_name]
                default_inputs[var_name] = (var.universe[0] + var.universe[-1]) / 2.0
        
        # Evaluate system at each grid point
        for i in range(resolution):
            for j in range(resolution):
                inputs = default_inputs.copy()
                inputs[input_var1] = X[i, j]
                inputs[input_var2] = Y[i, j]
                
                outputs = self.evaluate(inputs)
                Z[i, j] = outputs[output_var]
        
        # Create the 3D plot
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', antialiased=True)
        
        ax.set_xlabel(input_var1)
        ax.set_ylabel(input_var2)
        ax.set_zlabel(output_var)
        ax.set_title(f"Control Surface: {output_var} = f({input_var1}, {input_var2})")
        
        fig.colorbar(surf)
        
        return fig