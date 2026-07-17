"""
Tests for code review and feedback system.
"""

import pytest
from src.utils.code_review import (
    CodeReviewManager,
    ReviewStatus,
    CodeQualityCategory,
    FEEDBACK_TEMPLATES,
)


@pytest.fixture
def review_manager():
    """Create a fresh review manager for each test."""
    return CodeReviewManager()


class TestCodeReviewManager:
    """Tests for CodeReviewManager."""

    def test_submit_code(self, review_manager):
        """Test submitting code for review."""
        submission = review_manager.submit_code(
            submission_id="sub_001",
            user_id="user_123",
            project_id=1,
            code="print('hello')",
            language="python",
            description="Simple hello world",
        )

        assert submission["submission_id"] == "sub_001"
        assert submission["user_id"] == "user_123"
        assert submission["project_id"] == 1
        assert submission["review_status"] == ReviewStatus.PENDING.value
        assert submission["submitted_at"] is not None

    def test_get_submission(self, review_manager):
        """Test retrieving a submission."""
        review_manager.submit_code(
            submission_id="sub_001",
            user_id="user_123",
            project_id=1,
            code="test code",
            language="python",
        )

        submission = review_manager.get_submission("sub_001")
        assert submission is not None
        assert submission["code"] == "test code"

    def test_get_user_submissions(self, review_manager):
        """Test getting all submissions from a user."""
        review_manager.submit_code(
            submission_id="sub_001",
            user_id="user_123",
            project_id=1,
            code="test 1",
            language="python",
        )
        review_manager.submit_code(
            submission_id="sub_002",
            user_id="user_123",
            project_id=2,
            code="test 2",
            language="javascript",
        )

        submissions = review_manager.get_user_submissions("user_123")
        assert len(submissions) == 2

    def test_get_project_submissions(self, review_manager):
        """Test getting all submissions for a project."""
        review_manager.submit_code(
            submission_id="sub_001",
            user_id="user_123",
            project_id=1,
            code="test 1",
            language="python",
        )
        review_manager.submit_code(
            submission_id="sub_002",
            user_id="user_456",
            project_id=1,
            code="test 2",
            language="python",
        )

        submissions = review_manager.get_project_submissions(1)
        assert len(submissions) == 2

    def test_start_review(self, review_manager):
        """Test starting a code review."""
        review_manager.submit_code(
            submission_id="sub_001",
            user_id="user_123",
            project_id=1,
            code="test code",
            language="python",
        )

        review = review_manager.start_review(
            submission_id="sub_001",
            reviewer_id="reviewer_001",
        )

        assert review["submission_id"] == "sub_001"
        assert review["reviewer_id"] == "reviewer_001"
        assert review["status"] == ReviewStatus.IN_PROGRESS.value

    def test_start_review_invalid_submission(self, review_manager):
        """Test starting a review for non-existent submission."""
        with pytest.raises(ValueError):
            review_manager.start_review(
                submission_id="invalid",
                reviewer_id="reviewer_001",
            )

    def test_add_feedback_comment(self, review_manager):
        """Test adding feedback comments to a review."""
        review_manager.submit_code(
            submission_id="sub_001",
            user_id="user_123",
            project_id=1,
            code="test code",
            language="python",
        )
        review = review_manager.start_review(
            submission_id="sub_001",
            reviewer_id="reviewer_001",
        )

        comment = review_manager.add_feedback_comment(
            review_id=review["review_id"],
            line_number=5,
            code_snippet="x = 1",
            feedback="Variable naming could be more descriptive",
            severity="warning",
        )

        assert comment["line_number"] == 5
        assert comment["severity"] == "warning"

    def test_score_category(self, review_manager):
        """Test scoring a code quality category."""
        review_manager.submit_code(
            submission_id="sub_001",
            user_id="user_123",
            project_id=1,
            code="test code",
            language="python",
        )
        review = review_manager.start_review(
            submission_id="sub_001",
            reviewer_id="reviewer_001",
        )

        score_data = review_manager.score_category(
            review_id=review["review_id"],
            category="functionality",
            score=85,
            feedback="Works correctly",
        )

        assert score_data["score"] == 85
        assert score_data["level"] == "excellent"

    def test_score_category_invalid_score(self, review_manager):
        """Test scoring with invalid score range."""
        review_manager.submit_code(
            submission_id="sub_001",
            user_id="user_123",
            project_id=1,
            code="test code",
            language="python",
        )
        review = review_manager.start_review(
            submission_id="sub_001",
            reviewer_id="reviewer_001",
        )

        with pytest.raises(ValueError):
            review_manager.score_category(
                review_id=review["review_id"],
                category="functionality",
                score=150,
            )

    def test_complete_review(self, review_manager):
        """Test completing a code review."""
        review_manager.submit_code(
            submission_id="sub_001",
            user_id="user_123",
            project_id=1,
            code="test code",
            language="python",
        )
        review = review_manager.start_review(
            submission_id="sub_001",
            reviewer_id="reviewer_001",
        )

        review_manager.score_category(
            review_id=review["review_id"],
            category="functionality",
            score=80,
        )
        review_manager.score_category(
            review_id=review["review_id"],
            category="code_style",
            score=75,
        )

        completed = review_manager.complete_review(
            review_id=review["review_id"],
            summary="Good work, with some style improvements needed",
            recommend_changes=True,
        )

        assert completed["overall_score"] == 77.5
        assert completed["status"] == ReviewStatus.CHANGES_REQUESTED.value

    def test_get_review_comments(self, review_manager):
        """Test retrieving all comments for a review."""
        review_manager.submit_code(
            submission_id="sub_001",
            user_id="user_123",
            project_id=1,
            code="test code",
            language="python",
        )
        review = review_manager.start_review(
            submission_id="sub_001",
            reviewer_id="reviewer_001",
        )

        review_manager.add_feedback_comment(
            review_id=review["review_id"],
            line_number=1,
            code_snippet="code 1",
            feedback="Comment 1",
        )
        review_manager.add_feedback_comment(
            review_id=review["review_id"],
            line_number=5,
            code_snippet="code 5",
            feedback="Comment 5",
        )

        comments = review_manager.get_review_comments(review["review_id"])
        assert len(comments) == 2

    def test_get_code_quality_score(self, review_manager):
        """Test getting code quality score."""
        review_manager.submit_code(
            submission_id="sub_001",
            user_id="user_123",
            project_id=1,
            code="test code",
            language="python",
        )
        review = review_manager.start_review(
            submission_id="sub_001",
            reviewer_id="reviewer_001",
        )

        review_manager.score_category(
            review_id=review["review_id"],
            category="functionality",
            score=90,
        )

        review_manager.complete_review(
            review_id=review["review_id"],
            summary="Good work",
        )

        score_data = review_manager.get_code_quality_score("sub_001")
        assert score_data["status"] == "reviewed"
        assert score_data["overall_score"] == 90.0

    def test_get_improvement_recommendations(self, review_manager):
        """Test getting improvement recommendations."""
        review_manager.submit_code(
            submission_id="sub_001",
            user_id="user_123",
            project_id=1,
            code="test code",
            language="python",
        )
        review = review_manager.start_review(
            submission_id="sub_001",
            reviewer_id="reviewer_001",
        )

        review_manager.score_category(
            review_id=review["review_id"],
            category="code_style",
            score=50,
            feedback="Code style needs improvement",
        )

        review_manager.complete_review(
            review_id=review["review_id"],
            summary="Needs work",
        )

        recommendations = review_manager.get_improvement_recommendations("sub_001")
        assert len(recommendations) > 0
        assert "code_style" in recommendations[0].lower()


class TestReviewStatus:
    """Tests for ReviewStatus enum."""

    def test_review_status_values(self):
        """Test review status values."""
        assert ReviewStatus.PENDING.value == "pending"
        assert ReviewStatus.IN_PROGRESS.value == "in_progress"
        assert ReviewStatus.COMPLETED.value == "completed"
        assert ReviewStatus.CHANGES_REQUESTED.value == "changes_requested"


class TestFeedbackTemplates:
    """Tests for feedback templates."""

    def test_templates_exist_for_categories(self):
        """Test that templates exist for all categories."""
        assert "functionality" in FEEDBACK_TEMPLATES
        assert "code_style" in FEEDBACK_TEMPLATES
        assert "performance" in FEEDBACK_TEMPLATES
        assert "security" in FEEDBACK_TEMPLATES
        assert "testing" in FEEDBACK_TEMPLATES
        assert "documentation" in FEEDBACK_TEMPLATES

    def test_templates_have_levels(self):
        """Test that templates have all quality levels."""
        for category, templates in FEEDBACK_TEMPLATES.items():
            assert "excellent" in templates
            assert "good" in templates
            assert "needs_improvement" in templates
