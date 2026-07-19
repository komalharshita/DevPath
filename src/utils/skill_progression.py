"""
Skill progression validation and tracking system.

Implements skill difficulty tiers, prerequisites validation, and progression
recommendations to ensure users develop foundational knowledge before advancing.
"""

from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
from datetime import datetime


class SkillDifficulty(Enum):
    """Skill difficulty levels in progression order."""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4

    def __lt__(self, other):
        if not isinstance(other, SkillDifficulty):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other):
        if not isinstance(other, SkillDifficulty):
            return NotImplemented
        return self.value <= other.value

    def __gt__(self, other):
        if not isinstance(other, SkillDifficulty):
            return NotImplemented
        return self.value > other.value

    def __ge__(self, other):
        if not isinstance(other, SkillDifficulty):
            return NotImplemented
        return self.value >= other.value


SKILL_PREREQUISITES = {
    "JavaScript": {
        SkillDifficulty.BEGINNER: [],
        SkillDifficulty.INTERMEDIATE: [
            ("JavaScript", SkillDifficulty.BEGINNER),
        ],
        SkillDifficulty.ADVANCED: [
            ("JavaScript", SkillDifficulty.INTERMEDIATE),
        ],
        SkillDifficulty.EXPERT: [
            ("JavaScript", SkillDifficulty.ADVANCED),
        ],
    },
    "Python": {
        SkillDifficulty.BEGINNER: [],
        SkillDifficulty.INTERMEDIATE: [
            ("Python", SkillDifficulty.BEGINNER),
        ],
        SkillDifficulty.ADVANCED: [
            ("Python", SkillDifficulty.INTERMEDIATE),
        ],
        SkillDifficulty.EXPERT: [
            ("Python", SkillDifficulty.ADVANCED),
        ],
    },
    "React": {
        SkillDifficulty.BEGINNER: [
            ("JavaScript", SkillDifficulty.BEGINNER),
        ],
        SkillDifficulty.INTERMEDIATE: [
            ("React", SkillDifficulty.BEGINNER),
            ("JavaScript", SkillDifficulty.INTERMEDIATE),
        ],
        SkillDifficulty.ADVANCED: [
            ("React", SkillDifficulty.INTERMEDIATE),
            ("JavaScript", SkillDifficulty.ADVANCED),
        ],
        SkillDifficulty.EXPERT: [
            ("React", SkillDifficulty.ADVANCED),
            ("JavaScript", SkillDifficulty.EXPERT),
        ],
    },
    "Node.js": {
        SkillDifficulty.BEGINNER: [
            ("JavaScript", SkillDifficulty.BEGINNER),
        ],
        SkillDifficulty.INTERMEDIATE: [
            ("Node.js", SkillDifficulty.BEGINNER),
            ("JavaScript", SkillDifficulty.INTERMEDIATE),
        ],
        SkillDifficulty.ADVANCED: [
            ("Node.js", SkillDifficulty.INTERMEDIATE),
            ("JavaScript", SkillDifficulty.ADVANCED),
        ],
        SkillDifficulty.EXPERT: [
            ("Node.js", SkillDifficulty.ADVANCED),
            ("JavaScript", SkillDifficulty.EXPERT),
        ],
    },
    "SQL": {
        SkillDifficulty.BEGINNER: [],
        SkillDifficulty.INTERMEDIATE: [
            ("SQL", SkillDifficulty.BEGINNER),
        ],
        SkillDifficulty.ADVANCED: [
            ("SQL", SkillDifficulty.INTERMEDIATE),
        ],
        SkillDifficulty.EXPERT: [
            ("SQL", SkillDifficulty.ADVANCED),
        ],
    },
}


class SkillProgressionValidator:
    """Validates skill progression and manages skill proficiency tracking."""

    def __init__(self):
        self.user_skills: Dict[str, Dict] = {}

    def can_learn_skill(
        self,
        user_id: str,
        skill_name: str,
        target_difficulty: SkillDifficulty,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a user can learn a skill at the given difficulty level.

        Returns:
            (is_allowed, error_message)
        """
        if skill_name not in SKILL_PREREQUISITES:
            return True, None

        prerequisites = SKILL_PREREQUISITES[skill_name].get(target_difficulty, [])

        if not prerequisites:
            return True, None

        user_skills = self.get_user_skills(user_id)

        for prereq_skill, prereq_difficulty in prerequisites:
            if prereq_skill not in user_skills:
                return (
                    False,
                    f"Missing prerequisite: {prereq_skill} at {prereq_difficulty.name} level",
                )

            user_level = user_skills[prereq_skill].get("difficulty")
            if user_level is None or user_level < prereq_difficulty:
                return (
                    False,
                    f"Incomplete prerequisite: {prereq_skill} requires {prereq_difficulty.name} level, "
                    f"but you have {user_level.name if user_level else 'no'} level",
                )

        return True, None

    def record_skill_completion(
        self,
        user_id: str,
        skill_name: str,
        difficulty: SkillDifficulty,
        assessment_score: Optional[float] = None,
        score: Optional[float] = None,
    ) -> Dict:
        """
        Record user completion of a skill at given difficulty level.

        Args:
            user_id: Unique user identifier
            skill_name: Name of the skill
            difficulty: Difficulty level completed
            assessment_score: Optional assessment score (0-100)
            score: Optional assessment score (0-100) — backward compatibility

        Returns:
            Updated skill profile
        """
        if assessment_score is None:
            assessment_score = score

        if user_id not in self.user_skills:
            self.user_skills[user_id] = {}

        if skill_name not in self.user_skills[user_id]:
            self.user_skills[user_id][skill_name] = {
                "difficulty": None,
                "completed_at": None,
                "assessment_score": None,
                "progression_history": [],
            }

        skill_data = self.user_skills[user_id][skill_name]
        skill_data["difficulty"] = difficulty
        skill_data["completed_at"] = datetime.utcnow().isoformat()
        skill_data["assessment_score"] = assessment_score
        skill_data["progression_history"].append(
            {
                "difficulty": difficulty.name,
                "completed_at": skill_data["completed_at"],
                "assessment_score": assessment_score,
            }
        )

        return skill_data

    def get_user_skills(self, user_id: str) -> Dict:
        """Get all skills completed by a user."""
        return self.user_skills.get(user_id, {})

    def get_recommended_next_skill(
        self,
        user_id: str,
        skill_name: str,
    ) -> Optional[Tuple[str, SkillDifficulty]]:
        """
        Get the recommended next skill level for a user to pursue.

        Returns:
            (skill_name, next_difficulty) or None if at expert level
        """
        user_skills = self.get_user_skills(user_id)

        if skill_name not in user_skills:
            return None

        current_difficulty = user_skills[skill_name].get("difficulty")
        if current_difficulty is None:
            return None

        next_difficulty_value = current_difficulty.value + 1
        if next_difficulty_value > SkillDifficulty.EXPERT.value:
            return None

        try:
            next_difficulty = SkillDifficulty(next_difficulty_value)
            return (skill_name, next_difficulty)
        except ValueError:
            return None

    def get_skill_proficiency(self, user_id: str, skill_name: str) -> Optional[Dict]:
        """Get proficiency data for a specific skill."""
        user_skills = self.get_user_skills(user_id)
        return user_skills.get(skill_name)

    def calculate_overall_proficiency(self, user_id: str) -> Dict:
        """Calculate overall proficiency metrics for a user."""
        user_skills = self.get_user_skills(user_id)

        if not user_skills:
            return {
                "total_skills_completed": 0,
                "average_score": 0,
                "levels_distribution": {},
                "proficiency_rating": "Novice",
            }

        completed_skills = len(user_skills)
        scores = [
            s.get("assessment_score")
            for s in user_skills.values()
            if s.get("assessment_score") is not None
        ]
        average_score = sum(scores) / len(scores) if scores else 0

        levels_distribution = {}
        for skill, data in user_skills.items():
            difficulty = data.get("difficulty")
            if difficulty:
                level_name = difficulty.name
                levels_distribution[level_name] = (
                    levels_distribution.get(level_name, 0) + 1
                )

        if average_score >= 90:
            rating = "Expert"
        elif average_score >= 75:
            rating = "Advanced"
        elif average_score >= 60:
            rating = "Intermediate"
        else:
            rating = "Beginner"

        return {
            "total_skills_completed": completed_skills,
            "average_score": round(average_score, 2),
            "levels_distribution": levels_distribution,
            "proficiency_rating": rating,
        }


def validate_skill_progression(
    user_id: str,
    skill_name: str,
    target_difficulty: str,
    validator: SkillProgressionValidator,
) -> Dict:
    """
    Validate if user can progress to a skill level.

    Returns:
        {
            "allowed": bool,
            "skill": str,
            "target_difficulty": str,
            "message": str (error or success message),
            "prerequisites": List[str] (missing prerequisites if any)
        }
    """
    try:
        difficulty = SkillDifficulty[target_difficulty.upper()]
    except KeyError:
        return {
            "allowed": False,
            "skill": skill_name,
            "target_difficulty": target_difficulty,
            "message": f"Invalid difficulty level: {target_difficulty}",
            "prerequisites": [],
        }

    is_allowed, error_msg = validator.can_learn_skill(user_id, skill_name, difficulty)

    return {
        "allowed": is_allowed,
        "skill": skill_name,
        "target_difficulty": target_difficulty,
        "message": error_msg or "Skill progression allowed",
        "prerequisites": (
            [p[0] for p in SKILL_PREREQUISITES.get(skill_name, {}).get(difficulty, [])]
            if not is_allowed
            else []
        ),
    }
