"""
Tests for AdaptiveLearningManager (adaptive learning paths and personalization system).
"""

import pytest
from src.utils.adaptive_learning import AdaptiveLearningManager


@pytest.fixture
def manager():
    """Create a fresh AdaptiveLearningManager for each test."""
    return AdaptiveLearningManager()


class TestUserProfile:
    """Tests for user profile management."""

    def test_create_user_profile(self, manager):
        """Test creating a user profile with initial skills."""
        profile = manager.create_user_profile(
            user_id="user_123",
            initial_skills=["python", "html"],
            learning_style="visual",
        )
        assert profile["user_id"] == "user_123"
        assert profile["skills"] == ["python", "html"]
        assert profile["learning_style"] == "visual"
        assert profile["preferred_difficulty"] == "Beginner"
        assert profile["learning_pace"] == "Medium"
        assert "created_at" in profile
        assert "updated_at" in profile

    def test_create_profile_stores_in_memory(self, manager):
        """Test that creating a profile stores it in user_profiles."""
        manager.create_user_profile("user_123", ["python"], "auditory")
        assert "user_123" in manager.user_profiles


class TestSkillAssessment:
    """Tests for skill level assessment."""

    def test_assess_skill_level(self, manager):
        """Test assessing a user's skill level."""
        manager.create_user_profile("user_123", ["python"], "visual")
        assessment = manager.assess_skill_level("user_123", "python")
        assert assessment["user_id"] == "user_123"
        assert assessment["skill"] == "python"
        assert "level" in assessment
        assert "confidence" in assessment
        assert "assessed_at" in assessment

    def test_assess_unknown_user_raises(self, manager):
        """Test that assessing an unknown user raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            manager.assess_skill_level("unknown_user", "python")


class TestAdaptivePathGeneration:
    """Tests for adaptive learning path generation."""

    def test_generate_adaptive_path(self, manager):
        """Test generating an adaptive learning path."""
        manager.create_user_profile("user_123", ["python"], "visual")
        path = manager.generate_adaptive_path(
            user_id="user_123",
            goal="Flask",
            available_time_hours=10,
        )
        assert len(path) > 0
        assert path[0]["type"] == "assessment"
        assert "topic" in path[0]
        assert "estimated_hours" in path[0]

    def test_generate_path_stores_path(self, manager):
        """Test that generated path is stored in learning_paths."""
        manager.create_user_profile("user_123", ["python"], "visual")
        manager.generate_adaptive_path("user_123", "Flask", 10)
        assert "user_123" in manager.learning_paths

    def test_generate_path_unknown_user_raises(self, manager):
        """Test that generating a path for an unknown user raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            manager.generate_adaptive_path("unknown_user", "Flask", 10)


class TestProgressRecording:
    """Tests for progress recording."""

    def test_record_progress(self, manager):
        """Test recording learning progress."""
        manager.create_user_profile("user_123", ["python"], "visual")
        record = manager.record_progress(
            user_id="user_123",
            item_id=1,
            score=85.0,
            time_spent=30,
        )
        assert record["item_id"] == 1
        assert record["score"] == 85.0
        assert record["time_spent_minutes"] == 30

    def test_record_progress_appends_to_history(self, manager):
        """Test that recording progress appends to performance history."""
        manager.create_user_profile("user_123", ["python"], "visual")
        manager.record_progress("user_123", 1, 70.0, 20)
        manager.record_progress("user_123", 2, 90.0, 40)
        assert len(manager.performance_history["user_123"]) == 2

    def test_record_progress_adapts_path_on_high_scores(self, manager):
        """Test that high average scores increase difficulty."""
        manager.create_user_profile("user_123", ["python"], "visual")
        manager.record_progress("user_123", 1, 90.0, 20)
        manager.record_progress("user_123", 2, 85.0, 20)
        profile = manager.user_profiles["user_123"]
        assert profile["preferred_difficulty"] == "Advanced"
        assert profile["learning_pace"] == "Fast"

    def test_record_progress_adapts_path_on_low_scores(self, manager):
        """Test that low average scores decrease difficulty."""
        manager.create_user_profile("user_123", ["python"], "visual")
        manager.record_progress("user_123", 1, 40.0, 20)
        manager.record_progress("user_123", 2, 45.0, 20)
        profile = manager.user_profiles["user_123"]
        assert profile["preferred_difficulty"] == "Beginner"
        assert profile["learning_pace"] == "Slow"


class TestNextRecommendation:
    """Tests for next recommended item."""

    def test_get_next_recommendation_with_path(self, manager):
        """Test getting next recommendation from a generated path."""
        manager.create_user_profile("user_123", ["python"], "visual")
        manager.generate_adaptive_path("user_123", "Flask", 10)
        recommendation = manager.get_next_recommendation("user_123")
        assert recommendation is not None
        assert "type" in recommendation

    def test_get_next_recommendation_no_path_returns_none(self, manager):
        """Test that no path means no recommendation."""
        result = manager.get_next_recommendation("user_with_no_path")
        assert result is None

    def test_get_next_recommendation_exhausted_path(self, manager):
        """Test that completing all path items returns None."""
        manager.create_user_profile("user_123", ["python"], "visual")
        manager.generate_adaptive_path("user_123", "Flask", 10)
        path = manager.learning_paths["user_123"]
        for i in range(len(path) + 1):
            manager.record_progress("user_123", i, 80.0, 20)
        result = manager.get_next_recommendation("user_123")
        assert result is None


class TestLearningMetrics:
    """Tests for learning metrics calculation."""

    def test_calculate_learning_metrics_no_history(self, manager):
        """Test metrics return zeros for user with no history."""
        result = manager.calculate_learning_metrics("new_user")
        assert result["user_id"] == "new_user"
        assert result["items_completed"] == 0
        assert result["average_score"] == 0
        assert result["learning_efficiency"] == 0

    def test_calculate_learning_metrics_with_history(self, manager):
        """Test metrics calculate correctly for active users."""
        manager.create_user_profile("user_123", ["python"], "visual")
        manager.record_progress("user_123", 1, 80.0, 20)
        manager.record_progress("user_123", 2, 60.0, 30)
        result = manager.calculate_learning_metrics("user_123")
        assert result["items_completed"] == 2
        assert result["average_score"] == 70.0
        assert result["total_time_spent"] == 50
        assert result["learning_efficiency"] > 0


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_skills_list(self, manager):
        """Test creating a profile with no initial skills."""
        profile = manager.create_user_profile(
            user_id="user_123",
            initial_skills=[],
            learning_style="visual",
        )
        assert profile["skills"] == []

    def test_assess_with_empty_skill_name(self, manager):
        """Test that assessing an empty skill name is handled."""
        manager.create_user_profile("user_123", ["python"], "visual")
        assessment = manager.assess_skill_level("user_123", "")
        assert assessment["skill"] == ""

    def test_generate_path_zero_time_hours(self, manager):
        """Test generating a path with zero available time."""
        manager.create_user_profile("user_123", ["python"], "visual")
        path = manager.generate_adaptive_path("user_123", "Flask", 0)
        assert path is not None
        assert isinstance(path, list)
