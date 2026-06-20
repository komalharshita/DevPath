import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import json
from utils.recommender import get_recommendations, score_single_project, ml_similarity_score, parse_skills
from utils.data_loader import load_all_projects

projects = load_all_projects()

def run_test_inputs(skills, level, interest, time):
    user_skills = parse_skills(skills)
    scored = []
    for p in projects:
        r_score = score_single_project(p, user_skills, level, interest, time)
        sim_score = ml_similarity_score(p, user_skills, level, interest, time, projects)
        final = r_score + sim_score
        # Check matches
        project_skills = [s.lower() for s in p.get("skills", [])]
        matched = sum(1 for s in user_skills if s in project_skills)
        scored.append({
            "id": p.get("id"),
            "title": p.get("title"),
            "matched_skills": matched,
            "rule_score": r_score,
            "sim_score": sim_score,
            "final": final
        })
    scored.sort(key=lambda x: x["final"], reverse=True)
    print(f"INPUTS: skills={skills}, level={level}, interest={interest}, time={time}")
    for item in scored[:5]:
        print(f"  ID {item['id']} ({item['title']}): matched={item['matched_skills']}, rule={item['rule_score']:.2f}, sim={item['sim_score']:.2f}, final={item['final']:.2f}")
    print()

run_test_inputs("python", "Beginner", "Web", "Medium")
run_test_inputs("react, css", "Intermediate", "Web", "High")
run_test_inputs("rust", "Advanced", "System", "High")
