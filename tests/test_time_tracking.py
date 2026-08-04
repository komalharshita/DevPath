"""
Tests for TimeTrackingManager (learning time tracking and analytics system).
"""

import pytest
from datetime import datetime, timedelta
from src.utils.time_tracking import TimeTrackingManager, TimeSession


@pytest.fixture
def manager():
    """Create a fresh TimeTrackingManager for each test."""
    return TimeTrackingManager()


class TestSessionLifecycle:
    """Tests for session start and end."""

    def test_start_session(self, manager):
        """Test starting a learning session."""
        session = manager.start_session(
            session_id="sess_001",
            user_id="user_123",
            item_type="lesson",
            item_id=1,
        )
        assert session.session_id == "sess_001"
        assert session.user_id == "user_123"
        assert session.item_type == "lesson"
        assert session.item_id == 1
        assert session.end_time is None
        assert session.duration_minutes is None

    def test_end_session(self, manager):
        """Test ending a session calculates duration."""
        session = manager.start_session(
            session_id="sess_001",
            user_id="user_123",
            item_type="lesson",
            item_id=1,
        )
        ended = manager.end_session("sess_001")
        assert ended is not None
        assert ended.end_time is not None
        assert ended.duration_minutes is not None
        assert ended.duration_minutes >= 0

    def test_end_nonexistent_session_returns_none(self, manager):
        """Test that ending a non-existent session returns None."""
        result = manager.end_session("nonexistent")
        assert result is None

    def test_session_saved_after_ending(self, manager):
        """Test that ended sessions are stored in the sessions dict."""
        manager.start_session(
            session_id="sess_001",
            user_id="user_123",
            item_type="lesson",
            item_id=1,
        )
        manager.end_session("sess_001")
        assert "sess_001" in manager.sessions
        assert "sess_001" not in manager.active_sessions

    def test_to_dict(self, manager):
        """Test TimeSession.to_dict() returns correct fields."""
        session = manager.start_session(
            session_id="sess_001",
            user_id="user_123",
            item_type="project",
            item_id=2,
        )
        d = session.to_dict()
        assert d["session_id"] == "sess_001"
        assert d["user_id"] == "user_123"
        assert d["item_type"] == "project"
        assert d["item_id"] == 2
        assert d["start_time"] is not None
        assert d["end_time"] is None
        assert d["duration_minutes"] is None


class TestTimeCalculations:
    """Tests for time calculation methods."""

    def test_get_time_spent_on_item_no_sessions(self, manager):
        """Test that time spent is 0 when there are no sessions."""
        result = manager.get_time_spent_on_item("user_123", "lesson", 1)
        assert result == 0

    def test_get_user_total_time_no_sessions(self, manager):
        """Test total time is 0 for a user with no sessions."""
        result = manager.get_user_total_time("user_123")
        assert result == 0

    def test_get_user_time_by_type_no_sessions(self, manager):
        """Test time breakdown returns zeros for a user with no sessions."""
        result = manager.get_user_time_by_type("user_123")
        assert result["lesson"] == 0
        assert result["project"] == 0


class TestTimeEstimates:
    """Tests for time estimation methods."""

    def test_estimate_time_for_item_lesson(self, manager):
        """Test lesson time estimate returns the default."""
        result = manager.estimate_time_for_item("lesson")
        assert result == manager.default_lesson_time

    def test_estimate_time_for_item_project(self, manager):
        """Test project time estimate returns the default."""
        result = manager.estimate_time_for_item("project")
        assert result == manager.default_project_time

    def test_estimate_time_for_item_unknown(self, manager):
        """Test unknown item type returns the generic default."""
        result = manager.estimate_time_for_item("unknown")
        assert result == 60


class TestLearningVelocity:
    """Tests for learning velocity calculations."""

    def test_calculate_learning_velocity_no_sessions(self, manager):
        """Test velocity returns zeros when there are no sessions."""
        result = manager.calculate_learning_velocity("user_123", days=7)
        assert result["days_active"] == 0
        assert result["total_time"] == 0
        assert result["average_daily_time"] == 0
        assert result["sessions_count"] == 0


class TestCompletionEstimates:
    """Tests for completion time estimation."""

    def test_estimate_completion_time_no_history(self, manager):
        """Test estimate uses default velocity for users with no history."""
        result = manager.estimate_completion_time("new_user", [])
        assert result["total_estimated_minutes"] == 0
        assert result["total_estimated_hours"] == 0
        assert "days_to_complete" in result

    def test_estimate_completion_time_with_items(self, manager):
        """Test estimate calculates for remaining items."""
        items = [{"type": "lesson"}, {"type": "project"}]
        result = manager.estimate_completion_time("new_user", items)
        expected_minutes = manager.default_lesson_time + manager.default_project_time
        assert result["total_estimated_minutes"] == expected_minutes


class TestTimeAnalytics:
    """Tests for comprehensive time analytics."""

    def test_get_time_analytics_no_sessions(self, manager):
        """Test analytics returns zero values for users with no sessions."""
        result = manager.get_time_analytics("new_user")
        assert result["user_id"] == "new_user"
        assert result["total_time"] == 0
        assert result["sessions_count"] == 0
        assert result["average_session_duration"] == 0

    def test_get_time_analytics_with_sessions(self, manager):
        """Test analytics calculates correct stats for active users."""
        session1 = manager.start_session("s1", "user_123", "lesson", 1)
        session1.duration_minutes = 30.0
        manager.sessions["s1"] = session1
        session2 = manager.start_session("s2", "user_123", "project", 1)
        session2.duration_minutes = 60.0
        manager.sessions["s2"] = session2
        result = manager.get_time_analytics("user_123")
        assert result["sessions_count"] == 2
        assert result["average_session_duration"] == 45.0
        assert result["time_by_type"]["lesson"] == 30.0
        assert result["time_by_type"]["project"] == 60.0


class TestSkillProficiencyPrediction:
    """Tests for skill proficiency prediction."""

    def test_predict_skill_proficiency_target_reached(self, manager):
        """Test that target_reached status is returned when goal is met."""
        session = manager.start_session("s1", "user_123", "lesson", 1)
        session.duration_minutes = 100 * 60  # 100 hours
        manager.sessions["s1"] = session
        result = manager.predict_skill_proficiency("user_123", target_hours=50)
        assert result["status"] == "target_reached"
        assert result["hours_remaining"] == 0

    def test_predict_skill_proficiency_no_history(self, manager):
        """Test that prediction uses default velocity for users with no history."""
        result = manager.predict_skill_proficiency("new_user", target_hours=100)
        assert result["target_hours"] == 100
        assert result["current_hours"] == 0
        assert result["hours_remaining"] == 100
        assert result["days_to_target"] > 0
        assert "target_date" in result
