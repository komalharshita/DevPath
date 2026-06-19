# test_recommender.py
# Run from the repo root with: python test_recommender.py

import sys
import os

# Make sure imports resolve from the repo root regardless of where Python
# looks by default.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from utils.recommender import (
    get_recommendations,
    validate_recommendation_inputs,
    _get_related,
    _load_clusters,
)

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
        print(f"        -> {p['project']['title']}  (gap_score: {p['gap_score']})")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print("\nDone.\n")