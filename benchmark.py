import time
import math
import re
from collections import Counter
from src.utils.data_loader import load_all_projects
from src.utils.recommender import (
    score_single_project, 
    _tokenize, 
    _project_text, 
    _user_text, 
    _idf, 
    _tfidf_vector, 
    _cosine_similarity, 
    parse_skills,
    get_recommendations as get_recommendations_optimized
)

# Re-implement the unoptimized version locally for benchmarking
def ml_similarity_score_unoptimized(project, user_skills, level, interest, time_availability, all_projects):
    project_documents = [_tokenize(_project_text(p)) for p in all_projects]
    user_tokens = _tokenize(_user_text(user_skills, level, interest, time_availability))

    idf_scores = _idf(project_documents + [user_tokens])

    user_vector = _tfidf_vector(user_tokens, idf_scores)
    project_vector = _tfidf_vector(_tokenize(_project_text(project)), idf_scores)

    return _cosine_similarity(user_vector, project_vector)

def get_recommendations_unoptimized(skills_string, level, interest, time_availability):
    user_skills = parse_skills(skills_string)
    all_projects = load_all_projects()
    scored_projects = []
    for project in all_projects:
        rule_score = score_single_project(
            project,
            user_skills,
            level,
            interest,
            time_availability,
        )
        similarity_score = ml_similarity_score_unoptimized(
            project,
            user_skills,
            level,
            interest,
            time_availability,
            all_projects,
        )
        final_score = rule_score + similarity_score
        if final_score > 0:
            scored_projects.append({
                "project": project,
                "score": final_score,
            })
    return scored_projects

def run_benchmark():
    # To artificially inflate the dataset size for a meaningful benchmark if needed:
    all_projects = load_all_projects()
    print(f"Number of projects loaded: {len(all_projects)}")
    
    # Let's artificially multiply the data to show the true O(N^2) effect
    # We will mock the load_all_projects behavior to return duplicated data
    
    # We'll just run it on the current dataset first
    skills = "python, react"
    level = "intermediate"
    interest = "web"
    time_avail = "medium"
    
    # Warm up
    _ = get_recommendations_optimized(skills, level, interest, time_avail)
    
    print("\n--- Benchmarking Unoptimized (O(N^2)) ---")
    start = time.time()
    get_recommendations_unoptimized(skills, level, interest, time_avail)
    unoptimized_time = time.time() - start
    print(f"Time taken: {unoptimized_time:.4f} seconds")
    
    print("\n--- Benchmarking Optimized (O(N)) ---")
    start = time.time()
    get_recommendations_optimized(skills, level, interest, time_avail)
    optimized_time = time.time() - start
    print(f"Time taken: {optimized_time:.4f} seconds")
    
    speedup = unoptimized_time / optimized_time if optimized_time > 0 else 0
    print(f"\nSpeedup: {speedup:.2f}x faster")

if __name__ == '__main__':
    import sys
    import os
    # Add src to sys.path so imports work
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    run_benchmark()
