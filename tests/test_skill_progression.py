"""
Tests for skill progression validation and tracking.
"""

import pytest
from src.utils.skill_progression import (
    SkillDifficulty,
    SkillProgressionValidator,
    validate_skill_progression,
    SKILL_PREREQUISITES,
)


@pytest.fixture
def validator():
    """Create a fresh validator instance for each test."""
    return SkillProgressionValidator()


class TestSkillDifficulty:
    """Tests for SkillDifficulty enum."""

    def test_difficulty_ordering(self):
        """Test that difficulty levels are ordered correctly."""
        assert SkillDifficulty.BEGINNER < SkillDifficulty.INTERMEDIATE
        assert SkillDifficulty.INTERMEDIATE < SkillDifficulty.ADVANCED
        assert SkillDifficulty.ADVANCED < SkillDifficulty.EXPERT

    def test_difficulty_values(self):
        """Test that difficulty enum has correct values."""
        assert SkillDifficulty.BEGINNER.value == 1
        assert SkillDifficulty.INTERMEDIATE.value == 2
        assert SkillDifficulty.ADVANCED.value == 3
        assert SkillDifficulty.EXPERT.value == 4


class TestSkillProgressionValidator:
    """Tests for SkillProgressionValidator."""

    def test_can_learn_beginner_without_prerequisites(self, validator):
        """User should be able to learn beginner level without prerequisites."""
        allowed, error = validator.can_learn_skill(
            "user123",
            "Python",
            SkillDifficulty.BEGINNER
        )
        assert allowed is True
        assert error is None

    def test_cannot_learn_intermediate_without_beginner(self, validator):
        """User should not be able to learn intermediate without beginner."""
        allowed, error = validator.can_learn_skill(
            "user123",
            "Python",
            SkillDifficulty.INTERMEDIATE
        )
        assert allowed is False
        assert "prerequisite" in error.lower()

    def test_can_learn_after_meeting_prerequisites(self, validator):
        """User should be able to learn after meeting prerequisites."""
        user_id = "user123"

        validator.record_skill_completion(
            user_id,
            "Python",
            SkillDifficulty.BEGINNER,
            score=85
        )

        allowed, error = validator.can_learn_skill(
            user_id,
            "Python",
            SkillDifficulty.INTERMEDIATE
        )
        assert allowed is True
        assert error is None

    def test_react_requires_javascript_beginner(self, validator):
        """React intermediate requires JavaScript beginner."""
        allowed, error = validator.can_learn_skill(
            "user123",
            "React",
            SkillDifficulty.BEGINNER
        )
        assert allowed is False
        assert "JavaScript" in error

    def test_can_learn_react_after_javascript(self, validator):
        """User can learn React after learning JavaScript."""
        user_id = "user123"

        validator.record_skill_completion(
            user_id,
            "JavaScript",
            SkillDifficulty.BEGINNER,
            score=80
        )

        allowed, error = validator.can_learn_skill(
            user_id,
            "React",
            SkillDifficulty.BEGINNER
        )
        assert allowed is True

    def test_record_skill_completion(self, validator):
        """Test recording skill completion."""
        user_id = "user123"

        skill_data = validator.record_skill_completion(
            user_id,
            "Python",
            SkillDifficulty.BEGINNER,
            assessment_score=88.5
        )

        assert skill_data["difficulty"] == SkillDifficulty.BEGINNER
        assert skill_data["assessment_score"] == 88.5
        assert skill_data["completed_at"] is not None
        assert len(skill_data["progression_history"]) == 1

    def test_get_user_skills(self, validator):
        """Test retrieving user's completed skills."""
        user_id = "user123"

        validator.record_skill_completion(
            user_id,
            "Python",
            SkillDifficulty.BEGINNER
        )
        validator.record_skill_completion(
            user_id,
            "JavaScript",
            SkillDifficulty.BEGINNER
        )

        skills = validator.get_user_skills(user_id)
        assert len(skills) == 2
        assert "Python" in skills
        assert "JavaScript" in skills

    def test_get_recommended_next_skill(self, validator):
        """Test getting recommended next skill level."""
        user_id = "user123"

        validator.record_skill_completion(
            user_id,
            "Python",
            SkillDifficulty.BEGINNER
        )

        next_skill = validator.get_recommended_next_skill(user_id, "Python")
        assert next_skill is not None
        assert next_skill[0] == "Python"
        assert next_skill[1] == SkillDifficulty.INTERMEDIATE

    def test_no_next_skill_at_expert(self, validator):
        """Test that there's no next skill after expert."""
        user_id = "user123"

        validator.record_skill_completion(
            user_id,
            "Python",
            SkillDifficulty.EXPERT
        )

        next_skill = validator.get_recommended_next_skill(user_id, "Python")
        assert next_skill is None

    def test_calculate_overall_proficiency_empty(self, validator):
        """Test proficiency calculation for user with no skills."""
        proficiency = validator.calculate_overall_proficiency("user123")

        assert proficiency["total_skills_completed"] == 0
        assert proficiency["average_score"] == 0
        assert proficiency["proficiency_rating"] == "Novice"

    def test_calculate_overall_proficiency(self, validator):
        """Test proficiency calculation with completed skills."""
        user_id = "user123"

        validator.record_skill_completion(
            user_id,
            "Python",
            SkillDifficulty.BEGINNER,
            assessment_score=95
        )
        validator.record_skill_completion(
            user_id,
            "JavaScript",
            SkillDifficulty.BEGINNER,
            assessment_score=85
        )

        proficiency = validator.calculate_overall_proficiency(user_id)

        assert proficiency["total_skills_completed"] == 2
        assert proficiency["average_score"] == 90.0
        assert proficiency["proficiency_rating"] == "Expert"


class TestValidateSkillProgression:
    """Tests for validate_skill_progression function."""

    def test_valid_difficulty_level(self):
        """Test with valid difficulty level."""
        validator = SkillProgressionValidator()
        result = validate_skill_progression(
            "user123",
            "Python",
            "beginner",
            validator
        )

        assert result["allowed"] is True
        assert result["skill"] == "Python"

    def test_invalid_difficulty_level(self):
        """Test with invalid difficulty level."""
        validator = SkillProgressionValidator()
        result = validate_skill_progression(
            "user123",
            "Python",
            "impossible",
            validator
        )

        assert result["allowed"] is False
        assert "Invalid difficulty" in result["message"]

    def test_missing_prerequisites_listed(self):
        """Test that missing prerequisites are listed in response."""
        validator = SkillProgressionValidator()
        result = validate_skill_progression(
            "user123",
            "React",
            "beginner",
            validator
        )

        assert result["allowed"] is False
        assert len(result["prerequisites"]) > 0
        assert "JavaScript" in result["prerequisites"]


class TestSkillPrerequisites:
    """Tests for prerequisite definitions."""

    def test_prerequisites_are_defined(self):
        """Test that skill prerequisites are properly defined."""
        assert "Python" in SKILL_PREREQUISITES
        assert "JavaScript" in SKILL_PREREQUISITES
        assert "React" in SKILL_PREREQUISITES

    def test_react_has_javascript_requirement(self):
        """Test React prerequisites include JavaScript."""
        react_reqs = SKILL_PREREQUISITES["React"]
        beginner_reqs = react_reqs[SkillDifficulty.BEGINNER]

        javascript_req = any(
            req[0] == "JavaScript" for req in beginner_reqs
        )
        assert javascript_req is True
