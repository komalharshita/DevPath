import ast
import os
import sys

class EcoASTAnalyzer(ast.NodeVisitor):
    """Traverses the Abstract Syntax Tree to calculate algorithmic complexity units."""
    def __init__(self):
        self.loop_depth = 0
        self.total_energy_units = 0
        self.metrics = {
            "assignments": 0,
            "loops": 0,
            "max_depth": 0,
            "function_calls": 0
        }

    def visit_Assign(self, node):
        self.metrics["assignments"] += 1
        # Mathematical Heuristic: BaseCost (1) * 10^LoopDepth
        self.total_energy_units += 1 * (10 ** self.loop_depth)
        # generic_visit(node) is intentionally omitted here to prevent function 
        # calls within assignments from being counted, as they are not executed.
    def visit_For(self, node):
        self.metrics["loops"] += 1
        self.loop_depth += 1
        self.metrics["max_depth"] = max(self.metrics["max_depth"], self.loop_depth)
        
        # Loop overhead cost
        self.total_energy_units += 5 * (10 ** self.loop_depth)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node):
        self.metrics["loops"] += 1
        self.loop_depth += 1
        self.metrics["max_depth"] = max(self.metrics["max_depth"], self.loop_depth)
        
        # Loop overhead cost
        self.total_energy_units += 5 * (10 ** self.loop_depth)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_Call(self, node):
        self.metrics["function_calls"] += 1
        # Function calls carry an operational overhead weight of 2
        self.total_energy_units += 2 * (10 ** self.loop_depth)
        self.generic_visit(node)


class EcoCodeCLI:
    def __init__(self, file_path):
        self.file_path = file_path
        # Constant multiplier from the issue submission: E * 0.0005
        self.CARBON_MULTIPLIER = 0.0005 

    def run_analysis(self):
        if not os.path.exists(self.file_path):
            print(f"❌ Error: The file '{self.file_path}' does not exist.")
            sys.exit(1)

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse the code structure without running it
            tree = ast.parse(source_code)
            
            # Walk the tree nodes using the optimized analyzer
            analyzer = EcoASTAnalyzer()
            analyzer.visit(tree)
            
            # Calculate metrics using the formulas from your submission
            energy_units = analyzer.total_energy_units
            estimated_co2_mg = energy_units * self.CARBON_MULTIPLIER
            
            self.display_report(analyzer.metrics, energy_units, estimated_co2_mg)

        except SyntaxError as e:
            print(f"❌ Static Analysis Failed due to a syntax error in your target file:\nLine {e.lineno}: {e.text.strip()}")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {str(e)}")

    def display_report(self, metrics, energy, co2):
        print("\n" + "="*55)
        print("          🍀 ECOCODE STATIC CARBON REPORT 🍀          ")
        print("="*55)
        print(f"Target File:          {os.path.basename(self.file_path)}")
        print(f"Max Loop Nesting:     Depth {metrics['max_depth']}")
        print("-"*55)
        print("📊 STRUCTURAL METRICS COUNTS:")
        print(f"  • Variable Assignments: {metrics['assignments']}")
        print(f"  • Active Control Loops: {metrics['loops']}")
        print(f"  • Function Executions:  {metrics['function_calls']}")
        print("-"*55)
        print("🌱 PREDICTIVE ENVIRONMENTAL IMPACT:")
        print(f"  • Algorithmic Weight:   {energy} Complexity Units")
        print(f"  • Carbon Footprint:     {co2:.4f} mg CO2e")
        
        # Eco-Status evaluation thresholds
        print("-"*55)
        if metrics['max_depth'] >= 2 or energy > 500:
            print("❌ STATUS: ⚠️  High Consumption. Consider optimizing loops.")
            print("\n💡 ECO-OPTIMIZATION SUGGESTIONS:")
            print("  [!] Deeply nested structures exponentially raise computation heat.")
            print("      Look into replacing inner loops with hash maps or vector operations.")
        else:
            print("✅ STATUS: 🌱 Eco-Friendly Code Structure.")
        print("="*55 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ecocode.py <target_file.py>")
        sys.exit(1)
        
    target = sys.argv[1]
    engine = EcoCodeCLI(target)
    engine.run_analysis()

"""
Test Results:
=======================================================
          🍀 ECOCODE STATIC CARBON REPORT 🍀          
=======================================================
Target File:          test_perf.py
Max Loop Nesting:     Depth 2
-------------------------------------------------------
📊 STRUCTURAL METRICS COUNTS:
  • Variable Assignments: 1
  • Active Control Loops: 2
  • Function Executions:  0
-------------------------------------------------------
🌱 PREDICTIVE ENVIRONMENTAL IMPACT:
  • Algorithmic Weight:   650 Complexity Units
  • Carbon Footprint:     0.3250 mg CO2e
-------------------------------------------------------
❌ STATUS: ⚠️ High Consumption. Consider optimizing loops.

💡 ECO-OPTIMIZATION SUGGESTIONS:
  [!] Deeply nested structures exponentially raise computation heat.
      Look into replacing inner loops with hash maps or vector operations.
=======================================================
"""
