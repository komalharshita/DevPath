# utils/recommender.py
# Contains all recommendation logic: scoring and filtering projects.
# Upgraded to use vector similarity-based scoring via TF-IDF and cosine similarity.
# Kept separate from routing so it can be tested and extended independently.

from utils.data_loader import load_all_projects
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Maximum number of recommendations returned to the user
MAX_RESULTS = 3

# Scale factor to convert cosine similarity (0.0–1.0) to 0–10 range
# so skill match weight is comparable to bonus_score (max 5 points)
SIMILARITY_SCALE = 10

# Scoring weights — kept for backward compatibility and reference
# These are used as bonus points for non-skill criteria
SCORING_WEIGHTS = {
    "skill":    3,
    "level":    2,
    "interest": 2,
    "time":     1,
}

# Individual weight constants for clarity inside scoring function
WEIGHT_LEVEL    = SCORING_WEIGHTS["level"]
WEIGHT_INTEREST = SCORING_WEIGHTS["interest"]
WEIGHT_TIME     = SCORING_WEIGHTS["time"]

# Common aliases and abbreviations for skills
# This improves recommendation accuracy by normalizing user input
SKILL_ALIASES = {
    "js": "javascript",
    "py": "python",
    "html5": "html",
    "css3": "css",
    "c++": "cpp",
    "web dev": "javascript"
}


def parse_skills(skills_string):
    """
    Convert a raw comma-separated skills string into
    a normalized lowercase list.

    Example:
    "JS, HTML5, CSS3" -> ["javascript", "html", "css"]
    """
    raw_skills = [
        s.strip().lower()
        for s in skills_string.split(",")
        if s.strip()
    ]

    normalized_skills = [
        SKILL_ALIASES.get(skill, skill)
        for skill in raw_skills
    ]

    return normalized_skills


def compute_skill_similarity(user_skills, project_skills):
    """
    Compute cosine similarity between user skills and project skills
    using TF-IDF vectorization.

    Steps:
      1. Convert skill lists to single strings
      2. Fit TF-IDF vectorizer on both
      3. Compute cosine similarity between vectors
      4. Return similarity score between 0.0 and 1.0

    Example:
      user_skills    = ["python", "html"]
      project_skills = ["python", "css", "html"]
      returns ~0.82 (high similarity)
    """
    if not user_skills or not project_skills:
        return 0.0

    user_text    = " ".join(user_skills)
    project_text = " ".join([s.lower() for s in project_skills])

    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([user_text, project_text])
    except ValueError:
        return 0.0

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    return float(similarity[0][0])


def score_single_project(
        project, user_skills,
        level, interest, time_availability):
    """
    Calculate a relevance score for one project using:
      - TF-IDF cosine similarity for skill matching (0.0 to 1.0)
      - Fixed points for level, interest, time match

    Final score combines both for a balanced ranking.
    SIMILARITY_SCALE converts cosine score to 0-10 range
    so it is comparable to bonus_score (max 5 points).
    """
    # Compare time availability — only recommend projects within user's time budget
    TIME_AVAILABILITY = ['low', 'medium', 'high']
    time_availability_index = TIME_AVAILABILITY.index(time_availability.strip().lower())
    valid_time = TIME_AVAILABILITY[:time_availability_index + 1]

    if project.get("time", "").lower() not in valid_time:
        return 0

    # Vector similarity-based skill score (between 0.0 and 1.0)
    project_skills = [SKILL_ALIASES.get(s.strip().lower(), s.strip().lower()) 
                  for s in project.get("skills", [])]
    skill_score = compute_skill_similarity(user_skills, project_skills)

    # Fixed bonus points for level, interest, time match
    bonus_score = 0

    if project.get("level", "").lower() == level.lower():
        bonus_score += WEIGHT_LEVEL

    if project.get("interest", "").lower() == interest.lower():
        bonus_score += WEIGHT_INTEREST

    if project.get("time", "").lower() == time_availability.lower():
        bonus_score += WEIGHT_TIME

    # Combine: skill similarity (scaled to 0–10) + bonus points (max 5)
    final_score = (skill_score * SIMILARITY_SCALE) + bonus_score

    return final_score


def get_recommendations(skills_string, level, interest, time_availability):
    """
    Return the top N recommended projects for the given user inputs.

    Steps:
      1. Parse the raw skills input into a list.
      2. Compute cosine similarity score for every project.
      3. Drop projects with a score of zero (no overlap at all).
      4. Sort by score descending.
      5. Return the top MAX_RESULTS projects.
    """
    user_skills = parse_skills(skills_string)
    all_projects = load_all_projects()

    scored_projects = []

    for project in all_projects:
        score = score_single_project(
            project, user_skills, level, interest, time_availability
        )
        if score > 0:
            scored_projects.append({"project": project, "score": score})

    scored_projects.sort(key=lambda item: item["score"], reverse=True)

    return [item["project"] for item in scored_projects[:MAX_RESULTS]]


def validate_recommendation_inputs(skills, level, interest, time_availability):
    """
    Validate all four required fields.
    Returns a list of error strings. An empty list means all inputs are valid.
    """
    errors = []

    if not skills or not skills.strip():
        errors.append("Please enter at least one skill.")

    if not level or not level.strip():
        errors.append("Please select an experience level.")

    if not interest or not interest.strip():
        errors.append("Please select an area of interest.")

    if not time_availability or not time_availability.strip():
        errors.append("Please select your time availability.")

    return errors