# utils/recommender.py
# Compatibility shim forwarding to services.project_service
import services.project_service

# Export constants and functions
SCORING_WEIGHTS = services.project_service.SCORING_WEIGHTS
VALID_LEVELS = services.project_service.VALID_LEVELS
VALID_TIME_AVAILABILITY = services.project_service.VALID_TIME_AVAILABILITY
_get_related = services.project_service._get_related
_load_clusters = services.project_service._load_clusters
parse_skills = services.project_service.parse_skills
ml_similarity_score = services.project_service.ml_similarity_score

# Define module-level attribute so it can be monkeypatched by tests
_load_skill_graph = services.project_service._load_skill_graph


def score_single_project(project, user_skills, level, interest, time_availability):
    """Wrapper that forwards to project_service and respects monkeypatched _load_skill_graph."""
    old_load = services.project_service._load_skill_graph
    services.project_service._load_skill_graph = _load_skill_graph
    try:
        return services.project_service.score_single_project(
            project, user_skills, level, interest, time_availability
        )
    finally:
        services.project_service._load_skill_graph = old_load


def get_recommendations(skills_string, level, interest, time_availability):
    """Wrapper that forwards to project_service and respects monkeypatched _load_skill_graph."""
    old_load = services.project_service._load_skill_graph
    services.project_service._load_skill_graph = _load_skill_graph
    try:
        return services.project_service.get_recommendations(
            skills_string, level, interest, time_availability
        )
    finally:
        services.project_service._load_skill_graph = old_load


def validate_recommendation_inputs(skills, level, interest, time_availability):
    return services.project_service.validate_recommendation_inputs(
        skills, level, interest, time_availability
    )