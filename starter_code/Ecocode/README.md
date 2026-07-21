# 🍀 EcoCode — Static Carbon Footprint Linter

EcoCode is a lightweight, zero-dependency command-line interface (CLI) tool designed to make **Green Software Engineering** practical and accessible. By leveraging static code analysis, EcoCode scans the structural architecture of Python files and predicts their carbon footprint ($CO_2$ emissions in milligrams) **instally without executing a single line of code**.

Traditional runtime profiling tools (like `CodeCarbon`) require running code to measure hardware power draw, which exposes systems to execution risks and wastes energy just to measure it. EcoCode acts as a proactive, security-safe "Linter for Carbon," shifting sustainability to the left so developers can fix high-emission code structures (like nested loops) right in their terminal while writing code.

---

## 🚀 Key Features

* **Static Analysis Engine:** Employs Python's native `ast` (Abstract Syntax Tree) module to parse code structures without runtime safety hazards.
* **Algorithmic Weighting Heuristic:** Calculates carbon scores using an exponential complexity tracking model based on loop nesting depths ($10^{\text{LoopDepth}}$).
* **Double-Count Prevention:** Custom node-visitor optimization isolates assignment actions to prevent multi-layered lines (e.g., `x = function()`) from skewing results.
* **Actionable Developer Feedback:** Emits instant terminal status reviews (`🌱 Eco-Friendly` vs `⚠️ High Consumption`) with contextual optimization suggestions.

---

## 🛠️ How It Works

EcoCode evaluates script complexity by breaking source text down into an Abstract Syntax Tree. It traverses nodes using a single-pass `NodeVisitor` logic:

1. **Assignments (`visit_Assign`):** Assessed at a base unit score scaled by the current nesting depth.
2. **Function Calls (`visit_Call`):** Tracked with an operational overhead multiplier ($2 \times 10^{\text{LoopDepth}}$).
3. **Control Flows (`visit_For` / `visit_While`):** Increments the active tracking loop depth variables, scaling structural energy impact exponentially:

$$E = \sum_{i=1}^{n} \left( \text{BaseCost}_{op} \times 10^{\text{LoopDepth}} \right)$$

The final score ($E$) is passed through a localization mapping factor to estimate carbon volume against regional computing energy criteria:

$$\text{Estimated } CO_2\text{ (mg)} = E \times 0.0005$$

---

## 💻 Installation & Usage

Because EcoCode utilizes Python's built-in standard library, it requires **zero external dependencies** (`pip install` blocks are not necessary).

### Running the Linter

Navigate to your workspace directory and execute `ecocode.py` targeting the script you wish to analyze:

```bash
python starter_code/ecocode.py path/to/your_target_script.py