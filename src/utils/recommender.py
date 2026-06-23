# src/utils/recommender.py

# Grouped scoring weights structure expected by tests/test_basic.py
SCORING_WEIGHTS = {
    'skill_match': 3,
    'level_match': 2,
    'interest_match': 2,
    'time_match': 1
}

# Validation constants expected by tests/test_basic.py
VALID_LEVELS = ["beginner", "intermediate", "advanced"]
VALID_INTERESTS = ["web", "data", "automation", "ml", "security"]
VALID_TIMES = ["low", "medium", "high"]

def validate_recommendation_inputs(user_input):
    """
    Validates incoming user input dictionary maps to prevent runtime type crashes.
    Required by tests/test_basic.py
    """
    if not user_input or not isinstance(user_input, dict):
        return False
    return True

def parse_skills(skills_input):
    """
    Cleans and normalizes skill inputs into a list of lowercase strings.
    Handles both list inputs and raw string splitting.
    Required by tests/test_basic.py
    """
    if not skills_input:
        return []
         
    if isinstance(skills_input, list):
        return [skill.strip().lower() for skill in skills_input if skill.strip()]
         
    if isinstance(skills_input, str):
        return [skill.strip().lower() for skill in skills_input.split(',') if skill.strip()]
         
    return []

def score_single_project(project, user_skills, user_level, user_interest, user_time):
    """
    Calculates the matching score for a single project case-insensitively.
    Required by tests/test_basic.py
    """
    score = 0
    
    project_skills_lower = [s.lower() for s in project.get('skills', [])]
    
    for skill in user_skills:
        if skill in project_skills_lower:
            score += SCORING_WEIGHTS['skill_match']
             
    if project.get('level', '').lower() == user_level:
        score += SCORING_WEIGHTS['level_match']
         
    if project.get('interest', '').lower() == user_interest:
        score += SCORING_WEIGHTS['interest_match']
         
    if project.get('time', '').lower() == user_time:
        score += SCORING_WEIGHTS['time_match']
         
    return score

def get_recommendations(user_input, projects_dataset):
    """
    Scores and filters projects based on user input parameters.
    Handles matching case-insensitively to prevent false zero-match returns.
    """
    if not validate_recommendation_inputs(user_input):
        return []

    recommended_projects = []
     
    user_skills = parse_skills(user_input.get('skills', []))
     
    user_level = user_input.get('level', '').strip().lower()
    user_interest = user_input.get('interest', '').strip().lower()
    user_time = user_input.get('time', '').strip().lower()

    for project in projects_dataset:
        score = score_single_project(project, user_skills, user_level, user_interest, user_time)
             
        if score > 0:
            project_copy = project.copy()
            project_copy['match_score'] = score
            recommended_projects.append(project_copy)
             
    recommended_projects.sort(key=lambda x: x['match_score'], reverse=True)
     
    return recommended_projects[:3]
