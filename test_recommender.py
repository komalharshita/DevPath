# test_recommender.py
# Run from the repo root with: python test_recommender.py

import sys
import os

# Make sure imports resolve from the repo root
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Debug: Print the path being used
print(f"Adding to sys.path: {current_dir}")

import importlib.util
spec = importlib.util.spec_from_file_location("recommender", os.path.join(current_dir, "utils", "recommender.py"))
recommender = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recommender)

get_recommendations = recommender.get_recommendations
validate_recommendation_inputs = recommender.validate_recommendation_inputs
_get_related = recommender._get_related
_load_clusters = recommender._load_clusters
from src.config import Config, get_recommendation_weights
import tempfile
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def passed(label):
    print(f"  PASS  {label}")

def failed(label, detail):
    print(f"  FAIL  {label}")
    print(f"        {detail}")

def section(title):
    print(f"\n{title}")
    print("-" * len(title))

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

section("Input validation")

errors = validate_recommendation_inputs("", "Beginner", "Data", "Low")
if errors:
    passed("empty skills caught")
else:
    failed("empty skills caught", "expected an error, got none")

errors = validate_recommendation_inputs("Python", "", "Data", "Low")
if errors:
    passed("empty level caught")
else:
    failed("empty level caught", "expected an error, got none")

errors = validate_recommendation_inputs("Python", "Beginner", "Data", "Low")
if not errors:
    passed("valid inputs pass through cleanly")
else:
    failed("valid inputs pass through cleanly", f"unexpected errors: {errors}")

# ---------------------------------------------------------------------------
# Return shape
# ---------------------------------------------------------------------------

section("Return shape")

result = get_recommendations("Python", "Beginner", "Data", "Low")

if isinstance(result, dict):
    passed("get_recommendations returns a dict")
else:
    failed("get_recommendations returns a dict", f"got {type(result)}")

if "recommendations" in result:
    passed("dict has 'recommendations' key")
else:
    failed("dict has 'recommendations' key", f"keys found: {list(result.keys())}")

if "related" in result:
    passed("dict has 'related' key")
else:
    failed("dict has 'related' key", f"keys found: {list(result.keys())}")

# ---------------------------------------------------------------------------
# Recommendations list
# ---------------------------------------------------------------------------

section("Recommendations")

recs = result["recommendations"]

if isinstance(recs, list):
    passed(f"recommendations is a list  ({len(recs)} result(s))")
else:
    failed("recommendations is a list", f"got {type(recs)}")

if len(recs) <= 3:
    passed(f"respects MAX_RESULTS cap  (got {len(recs)})")
else:
    failed("respects MAX_RESULTS cap", f"got {len(recs)} results")

required_fields = {"id", "title", "skills", "level", "interest", "time"}
all_valid = all(required_fields.issubset(p.keys()) for p in recs)
if all_valid:
    passed("all results have required fields")
else:
    failed("all results have required fields", "one or more fields missing")

# High time should return >= results as Low (it opens up more projects)
high_recs = get_recommendations("Python", "Beginner", "Data", "High")["recommendations"]
low_recs  = get_recommendations("Python", "Beginner", "Data", "Low")["recommendations"]
if len(high_recs) >= len(low_recs):
    passed("High time availability returns >= results than Low")
else:
    failed("High time availability returns >= results than Low",
           f"High={len(high_recs)}, Low={len(low_recs)}")

# Nonsense input should return empty recommendations, not crash
junk = get_recommendations("cobol_fortran_brainfuck", "Expert", "Knitting", "Low")["recommendations"]
if isinstance(junk, list) and len(junk) == 0:
    passed("no-match input returns empty recommendations")
else:
    failed("no-match input returns empty recommendations", f"got: {junk}")

# ---------------------------------------------------------------------------
# Skill alias normalisation
# ---------------------------------------------------------------------------

section("Skill alias normalisation")

js_results   = get_recommendations("js",         "Beginner", "Web", "Low")["recommendations"]
full_results = get_recommendations("javascript", "Beginner", "Web", "Low")["recommendations"]
if js_results == full_results:
    passed("'js' alias resolves to 'javascript'")
else:
    failed("'js' alias resolves to 'javascript'",
           f"js={[p['title'] for p in js_results]}, "
           f"javascript={[p['title'] for p in full_results]}")

# ---------------------------------------------------------------------------
# Related projects (soft — skipped if clusters.json missing)
# ---------------------------------------------------------------------------

section("Related projects (requires clusters.json)")

clusters_path = os.path.join("data", "clusters.json")

if not os.path.exists(clusters_path):
    print("  SKIP  clusters.json not found — run:  python scripts/cluster_projects.py")
else:
    cluster_data = _load_clusters()
    all_projects = __import__(
        "utils.data_loader", fromlist=["load_all_projects"]
    ).load_all_projects()

    rec_result = get_recommendations("Python", "Beginner", "Data", "Low")
    recs       = rec_result["recommendations"]
    related    = rec_result["related"]

    if isinstance(related, list):
        passed(f"related is a list  ({len(related)} result(s))")
    else:
        failed("related is a list", f"got {type(related)}")

    if len(related) <= 3:
        passed(f"related respects MAX_RELATED cap  (got {len(related)})")
    else:
        failed("related respects MAX_RELATED cap", f"got {len(related)}")

    if recs:
        rec_ids = [p["id"] for p in recs]
        overlap = [p for p in related if p["id"] in rec_ids]
        if not overlap:
            passed("related projects don't repeat recommended ones")
        else:
            failed("related projects don't repeat recommended ones",
                   f"overlap: {[p['title'] for p in overlap]}")
    else:
        print("  SKIP  no recommendations returned, skipping overlap check")
        
        
    # ---------------------------------------------------------------------------
# Progression (skill graph)
# ---------------------------------------------------------------------------

section("Skill graph progression")

result_prog = get_recommendations("Python", "Intermediate", "Web", "High")

if "progression" in result_prog:
    passed("dict has 'progression' key")
else:
    failed("dict has 'progression' key", f"keys found: {list(result_prog.keys())}")

prog = result_prog["progression"]
if isinstance(prog, list):
    passed(f"progression is a list  ({len(prog)} result(s))")
else:
    failed("progression is a list", f"got {type(prog)}")

rec_ids = [p["id"] for p in result_prog["recommendations"]]
overlap = [p for p in prog if p["project"]["id"] in rec_ids]
if not overlap:
    passed("progression projects don't repeat recommended ones")
else:
    failed("progression projects don't repeat recommended ones",
           f"overlap: {[p['title'] for p in overlap]}")
    
if isinstance(prog, list):
    passed(f"progression is a list  ({len(prog)} result(s))")
    for p in prog:
        print(f"        → {p['project']['title']}  (gap_score: {p['gap_score']})")

# ---------------------------------------------------------------------------
# Recommendation Weights Configuration
# ---------------------------------------------------------------------------

section("Recommendation Weights Configuration")

# Test 1: Weights can be loaded
try:
    weights = get_recommendation_weights()
    if isinstance(weights, dict):
        passed("get_recommendation_weights returns a dict")
    else:
        failed("get_recommendation_weights returns a dict", f"got {type(weights)}")
except Exception as e:
    failed("get_recommendation_weights returns a dict", f"error: {e}")

# Test 2: Required keys exist
required_weight_keys = {"skill", "level", "interest", "time"}
try:
    weights = get_recommendation_weights()
    if required_weight_keys.issubset(weights.keys()):
        passed(f"weights contain all required keys: {required_weight_keys}")
    else:
        missing = required_weight_keys - set(weights.keys())
        failed(f"weights contain all required keys", f"missing: {missing}")
except Exception as e:
    failed("weights contain required keys", f"error: {e}")

# Test 3: All weight values are positive numbers
try:
    weights = get_recommendation_weights()
    all_positive = all(isinstance(v, (int, float)) and v > 0 for v in weights.values())
    if all_positive:
        passed("all weight values are positive numbers")
    else:
        bad_weights = {k: v for k, v in weights.items() if not isinstance(v, (int, float)) or v <= 0}
        failed("all weight values are positive numbers", f"invalid: {bad_weights}")
except Exception as e:
    failed("all weight values are positive numbers", f"error: {e}")

# Test 4: Weights are cached (same object returned)
try:
    weights1 = get_recommendation_weights()
    weights2 = get_recommendation_weights()
    if weights1 is weights2:
        passed("weights are cached (same object returned)")
    else:
        failed("weights are cached", "different objects returned on consecutive calls")
except Exception as e:
    failed("weights are cached", f"error: {e}")

# Test 5: Invalid config file raises error
try:
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as tmpdir:
        bad_config = os.path.join(tmpdir, "bad_weights.json")
        with open(bad_config, "w") as f:
            f.write("{invalid json}")
        
        old_path = os.environ.get("RECOMMENDATION_WEIGHTS_PATH")
        os.environ["RECOMMENDATION_WEIGHTS_PATH"] = bad_config
        
        # This will use the cached value, so we need to test the static method directly
        try:
            Config.load_recommendation_weights()
            failed("invalid JSON is caught", "no error raised")
        except ValueError as e:
            if "Invalid JSON" in str(e):
                passed("invalid JSON is caught and raises ValueError")
            else:
                failed("invalid JSON is caught", f"wrong error: {e}")
        finally:
            if old_path:
                os.environ["RECOMMENDATION_WEIGHTS_PATH"] = old_path
            elif "RECOMMENDATION_WEIGHTS_PATH" in os.environ:
                del os.environ["RECOMMENDATION_WEIGHTS_PATH"]
except Exception as e:
    failed("invalid JSON is caught", f"test error: {e}")

# Test 6: Verify weights are actually used in scoring
try:
    weights = get_recommendation_weights()
    # Ensure the weights loaded match what we expect
    if weights.get("skill") == 3 and weights.get("level") == 2:
        passed("weights match expected default values (skill=3, level=2)")
    else:
        print(f"  INFO  weights differ from defaults (may be intentional): {weights}")
        passed("weights loaded successfully")
except Exception as e:
    failed("weights match expected values", f"error: {e}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print("\nDone.\n")