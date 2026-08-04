"""
Tests for CommunityManager (discussion forums, Q&A, and peer support system).
"""

import pytest
from src.utils.community import CommunityManager


@pytest.fixture
def manager():
    """Create a fresh CommunityManager for each test."""
    return CommunityManager()


class TestDiscussion:
    """Tests for discussion-related methods."""

    def test_create_discussion(self, manager):
        """Test creating a discussion thread."""
        discussion = manager.create_discussion(
            discussion_id="disc_001",
            user_id="user_123",
            course_id=1,
            title="How to learn Flask?",
            content="I need guidance on getting started with Flask.",
        )
        assert discussion["discussion_id"] == "disc_001"
        assert discussion["user_id"] == "user_123"
        assert discussion["course_id"] == 1
        assert discussion["title"] == "How to learn Flask?"
        assert discussion["content"] == "I need guidance on getting started with Flask."
        assert discussion["replies"] == []
        assert discussion["likes"] == 0
        assert "created_at" in discussion

    def test_reply_to_discussion(self, manager):
        """Test adding a reply to a discussion."""
        manager.create_discussion(
            discussion_id="disc_001",
            user_id="user_123",
            course_id=1,
            title="Test",
            content="Test content",
        )
        reply = manager.reply_to_discussion(
            discussion_id="disc_001",
            user_id="user_456",
            reply_content="Here is my answer.",
        )
        assert reply["user_id"] == "user_456"
        assert reply["content"] == "Here is my answer."
        assert "reply_id" in reply
        assert "created_at" in reply

    def test_reply_to_nonexistent_discussion_raises(self, manager):
        """Test that replying to a non-existent discussion raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            manager.reply_to_discussion(
                discussion_id="nonexistent",
                user_id="user_123",
                reply_content="Reply",
            )

    def test_discussion_reply_count_increments(self, manager):
        """Test that multiple replies are appended correctly."""
        manager.create_discussion(
            discussion_id="disc_001",
            user_id="user_123",
            course_id=1,
            title="Test",
            content="Test content",
        )
        manager.reply_to_discussion("disc_001", "user_456", "First reply")
        manager.reply_to_discussion("disc_001", "user_789", "Second reply")
        discussion = manager.discussions["disc_001"]
        assert len(discussion["replies"]) == 2


class TestQuestions:
    """Tests for Q&A methods."""

    def test_ask_question(self, manager):
        """Test posting a Q&A question."""
        question = manager.ask_question(
            question_id="q_001",
            user_id="user_123",
            course_id=1,
            title="What is a decorator in Python?",
            content="Can someone explain decorators?",
            tags=["python", "decorators"],
        )
        assert question["question_id"] == "q_001"
        assert question["user_id"] == "user_123"
        assert question["tags"] == ["python", "decorators"]
        assert question["views"] == 0
        assert question["upvotes"] == 0
        assert question["answers"] == []

    def test_answer_question(self, manager):
        """Test answering a question."""
        manager.ask_question(
            question_id="q_001",
            user_id="user_123",
            course_id=1,
            title="Test",
            content="Test content",
            tags=["test"],
        )
        answer = manager.answer_question(
            question_id="q_001",
            user_id="user_456",
            answer_content="Decorators wrap a function to add behavior.",
        )
        assert answer["user_id"] == "user_456"
        assert answer["content"] == "Decorators wrap a function to add behavior."
        assert answer["is_accepted"] is False
        assert answer["upvotes"] == 0

    def test_answer_nonexistent_question_raises(self, manager):
        """Test that answering a non-existent question raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            manager.answer_question(
                question_id="nonexistent",
                user_id="user_123",
                answer_content="Answer",
            )


class TestStudyGroups:
    """Tests for study group methods."""

    def test_create_study_group(self, manager):
        """Test creating a study group."""
        group = manager.create_study_group(
            group_id="group_001",
            creator_id="user_123",
            name="Flask Learners",
            course_id=1,
        )
        assert group["group_id"] == "group_001"
        assert group["creator_id"] == "user_123"
        assert group["name"] == "Flask Learners"
        assert "user_123" in group["members"]
        assert group["description"] == ""
        assert group["schedule"] is None

    def test_join_study_group(self, manager):
        """Test joining a study group."""
        manager.create_study_group(
            group_id="group_001",
            creator_id="user_123",
            name="Flask Learners",
            course_id=1,
        )
        group = manager.join_study_group("group_001", "user_456")
        assert "user_456" in group["members"]

    def test_join_study_group_idempotent(self, manager):
        """Test that joining a group twice does not duplicate the member."""
        manager.create_study_group(
            group_id="group_001",
            creator_id="user_123",
            name="Flask Learners",
            course_id=1,
        )
        manager.join_study_group("group_001", "user_456")
        group = manager.join_study_group("group_001", "user_456")
        assert group["members"].count("user_456") == 1

    def test_join_nonexistent_study_group_raises(self, manager):
        """Test that joining a non-existent group raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            manager.join_study_group("nonexistent", "user_123")


class TestReputation:
    """Tests for reputation tracking."""

    def test_get_user_reputation_new_user(self, manager):
        """Test that new users have zero reputation."""
        assert manager.get_user_reputation("new_user") == 0

    def test_create_discussion_increases_reputation(self, manager):
        """Test that creating a discussion awards reputation points."""
        manager.create_discussion(
            discussion_id="disc_001",
            user_id="user_123",
            course_id=1,
            title="Test",
            content="Test content",
        )
        assert manager.get_user_reputation("user_123") == 5

    def test_reply_increases_reputation(self, manager):
        """Test that replying awards reputation points."""
        manager.create_discussion(
            discussion_id="disc_001",
            user_id="user_123",
            course_id=1,
            title="Test",
            content="Test content",
        )
        manager.reply_to_discussion("disc_001", "user_456", "Reply content")
        assert manager.get_user_reputation("user_456") == 3

    def test_ask_question_increases_reputation(self, manager):
        """Test that asking a question awards reputation points."""
        manager.ask_question(
            question_id="q_001",
            user_id="user_123",
            course_id=1,
            title="Test",
            content="Test content",
            tags=["test"],
        )
        assert manager.get_user_reputation("user_123") == 10

    def test_answer_question_increases_reputation(self, manager):
        """Test that answering a question awards reputation points."""
        manager.ask_question(
            question_id="q_001",
            user_id="user_123",
            course_id=1,
            title="Test",
            content="Test content",
            tags=["test"],
        )
        manager.answer_question("q_001", "user_456", "Answer content")
        assert manager.get_user_reputation("user_456") == 15

    def test_create_study_group_increases_reputation(self, manager):
        """Test that creating a study group awards reputation points."""
        manager.create_study_group(
            group_id="group_001",
            creator_id="user_123",
            name="Test Group",
            course_id=1,
        )
        assert manager.get_user_reputation("user_123") == 20


class TestUserContributions:
    """Tests for user contribution tracking."""

    def test_get_user_contributions(self, manager):
        """Test that contributions are tracked correctly."""
        manager.create_discussion(
            discussion_id="disc_001",
            user_id="user_123",
            course_id=1,
            title="Test",
            content="Test content",
        )
        manager.ask_question(
            question_id="q_001",
            user_id="user_123",
            course_id=1,
            title="Test",
            content="Test content",
            tags=["test"],
        )
        contributions = manager.get_user_contributions("user_123")
        assert contributions["user_id"] == "user_123"
        assert contributions["discussions_started"] == 1
        assert contributions["questions_asked"] == 1
        assert contributions["answers_provided"] == 0
        assert contributions["total_contributions"] == 2

    def test_get_user_contributions_new_user(self, manager):
        """Test contributions for a user with no activity."""
        contributions = manager.get_user_contributions("new_user")
        assert contributions["total_contributions"] == 0
        assert contributions["reputation"] == 0


class TestTopContributors:
    """Tests for top contributors listing."""

    def test_get_top_contributors(self, manager):
        """Test that top contributors are returned sorted by reputation."""
        manager.create_discussion(
            discussion_id="disc_001",
            user_id="user_123",
            course_id=1,
            title="Test",
            content="Test content",
        )
        manager.ask_question(
            question_id="q_001",
            user_id="user_456",
            course_id=1,
            title="Test",
            content="Test content",
            tags=["test"],
        )
        manager.answer_question("q_001", "user_789", "Answer")
        top = manager.get_top_contributors(limit=3)
        assert len(top) == 3
        assert top[0]["user_id"] == "user_789"
        assert top[1]["user_id"] == "user_456"
        assert top[2]["user_id"] == "user_123"

    def test_get_top_contributors_limit(self, manager):
        """Test that the limit parameter is respected."""
        manager.create_discussion(
            discussion_id="disc_001",
            user_id="user_1",
            course_id=1,
            title="Test",
            content="Test",
        )
        manager.ask_question(
            question_id="q_001",
            user_id="user_2",
            course_id=1,
            title="Test",
            content="Test",
            tags=["test"],
        )
        top = manager.get_top_contributors(limit=1)
        assert len(top) == 1
