"""
Tests for CertificationManager (skill assessment and certificate issuance system).
"""

import pytest
from src.utils.certification import CertificationManager


@pytest.fixture
def manager():
    """Create a fresh CertificationManager for each test."""
    return CertificationManager()


class TestAssessmentCreation:
    """Tests for assessment creation."""

    def test_create_assessment(self, manager):
        """Test creating an assessment with questions."""
        questions = [
            {"id": "q1", "question": "What is Flask?", "correct_answer": "A web framework"},
            {"id": "q2", "question": "Is Flask Python?", "correct_answer": "Yes"},
        ]
        assessment = manager.create_assessment(
            assessment_id="assess_001",
            user_id="user_123",
            skill="Flask",
            difficulty="Intermediate",
            questions=questions,
        )
        assert assessment["assessment_id"] == "assess_001"
        assert assessment["user_id"] == "user_123"
        assert assessment["skill"] == "Flask"
        assert assessment["difficulty"] == "Intermediate"
        assert len(assessment["questions"]) == 2
        assert assessment["score"] is None
        assert assessment["passed"] is False
        assert assessment["completed_at"] is None

    def test_assessment_stored_in_memory(self, manager):
        """Test that created assessments are stored."""
        questions = [{"id": "q1", "question": "Test?", "correct_answer": "Answer"}]
        manager.create_assessment(
            "assess_001", "user_123", "Flask", "Beginner", questions
        )
        assert "assess_001" in manager.assessments


class TestScoreCalculation:
    """Tests for score calculation logic."""

    def test_calculate_score_empty_questions(self, manager):
        """Test that _calculate_score returns 0 for empty question list."""
        score = manager._calculate_score([], {})
        assert score == 0

    def test_calculate_score_all_correct(self, manager):
        """Test score is 100 when all answers are correct."""
        questions = [
            {"id": "q1", "correct_answer": "A"},
            {"id": "q2", "correct_answer": "B"},
        ]
        answers = {"q1": "A", "q2": "B"}
        score = manager._calculate_score(questions, answers)
        assert score == 100.0

    def test_calculate_score_all_wrong(self, manager):
        """Test score is 0 when all answers are wrong."""
        questions = [
            {"id": "q1", "correct_answer": "A"},
            {"id": "q2", "correct_answer": "B"},
        ]
        answers = {"q1": "Wrong", "q2": "Also Wrong"}
        score = manager._calculate_score(questions, answers)
        assert score == 0.0

    def test_calculate_score_partial(self, manager):
        """Test score is 50 when half the answers are correct."""
        questions = [
            {"id": "q1", "correct_answer": "A"},
            {"id": "q2", "correct_answer": "B"},
        ]
        answers = {"q1": "A"}
        score = manager._calculate_score(questions, answers)
        assert score == 50.0

    def test_calculate_score_unanswered_questions(self, manager):
        """Test that unanswered questions count as wrong."""
        questions = [
            {"id": "q1", "correct_answer": "A"},
            {"id": "q2", "correct_answer": "B"},
            {"id": "q3", "correct_answer": "C"},
        ]
        answers = {"q1": "A"}
        score = manager._calculate_score(questions, answers)
        assert score == pytest.approx(33.33, abs=0.01)


class TestAssessmentSubmission:
    """Tests for assessment submission and scoring."""

    def test_submit_assessment_passing(self, manager):
        """Test submitting an assessment with a passing score."""
        questions = [{"id": "q1", "correct_answer": "Flask"}]
        manager.create_assessment(
            "assess_001", "user_123", "Flask", "Beginner", questions
        )
        result = manager.submit_assessment("assess_001", {"q1": "Flask"})
        assert result["score"] == 100.0
        assert result["passed"] is True
        assert result["completed_at"] is not None

    def test_submit_assessment_failing(self, manager):
        """Test submitting an assessment with a failing score."""
        questions = [{"id": "q1", "correct_answer": "Flask"}]
        manager.create_assessment(
            "assess_001", "user_123", "Flask", "Beginner", questions
        )
        result = manager.submit_assessment("assess_001", {"q1": "Django"})
        assert result["score"] == 0.0
        assert result["passed"] is False
        assert result["completed_at"] is not None

    def test_submit_assessment_issues_certificate_on_pass(self, manager):
        """Test that a certificate is issued when assessment is passed."""
        questions = [{"id": "q1", "correct_answer": "Flask"}]
        manager.create_assessment(
            "assess_001", "user_123", "Flask", "Beginner", questions
        )
        manager.submit_assessment("assess_001", {"q1": "Flask"})
        cert_id = "cert_assess_001"
        assert cert_id in manager.certificates
        cert = manager.certificates[cert_id]
        assert cert["user_id"] == "user_123"
        assert cert["skill"] == "Flask"
        assert "verification_code" in cert

    def test_submit_assessment_no_certificate_on_fail(self, manager):
        """Test that no certificate is issued when assessment fails."""
        questions = [{"id": "q1", "correct_answer": "Flask"}]
        manager.create_assessment(
            "assess_001", "user_123", "Flask", "Beginner", questions
        )
        manager.submit_assessment("assess_001", {"q1": "Wrong"})
        assert "cert_assess_001" not in manager.certificates

    def test_submit_nonexistent_assessment_raises(self, manager):
        """Test that submitting a non-existent assessment raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            manager.submit_assessment("nonexistent", {})

    def test_submit_assessment_score_updates_on_resubmit(self, manager):
        """Test that submitting twice updates the score to the latest."""
        questions = [{"id": "q1", "correct_answer": "Flask"}]
        manager.create_assessment(
            "assess_001", "user_123", "Flask", "Beginner", questions
        )
        manager.submit_assessment("assess_001", {"q1": "Flask"})
        manager.submit_assessment("assess_001", {"q1": "Wrong"})
        assessment = manager.assessments["assess_001"]
        assert assessment["score"] == 0.0


class TestCertificateManagement:
    """Tests for certificate retrieval and verification."""

    def test_issue_certificate_directly(self, manager):
        """Test that _issue_certificate creates a certificate entry."""
        assessment = {
            "assessment_id": "assess_001",
            "user_id": "user_123",
            "skill": "Flask",
            "difficulty": "Beginner",
            "score": 100.0,
        }
        cert = manager._issue_certificate(assessment)
        assert cert["certificate_id"] == "cert_assess_001"
        assert cert["user_id"] == "user_123"
        assert cert["skill"] == "Flask"
        assert "verification_code" in cert
        assert "issued_at" in cert

    def test_get_user_certificates(self, manager):
        """Test retrieving all certificates for a user."""
        manager._issue_certificate({
            "assessment_id": "a1", "user_id": "user_123",
            "skill": "Flask", "difficulty": "Beginner", "score": 100.0,
        })
        manager._issue_certificate({
            "assessment_id": "a2", "user_id": "user_123",
            "skill": "Django", "difficulty": "Intermediate", "score": 85.0,
        })
        certs = manager.get_user_certificates("user_123")
        assert len(certs) == 2
        assert {c["skill"] for c in certs} == {"Flask", "Django"}

    def test_get_user_certificates_none_exist(self, manager):
        """Test that get_user_certificates returns empty list for users with none."""
        certs = manager.get_user_certificates("user_with_no_certs")
        assert certs == []

    def test_verify_certificate_valid(self, manager):
        """Test verifying a valid certificate."""
        cert = manager._issue_certificate({
            "assessment_id": "a1", "user_id": "user_123",
            "skill": "Flask", "difficulty": "Beginner", "score": 100.0,
        })
        result = manager.verify_certificate("cert_a1", cert["verification_code"])
        assert result is True

    def test_verify_certificate_invalid_code(self, manager):
        """Test verifying a certificate with wrong code returns False."""
        manager._issue_certificate({
            "assessment_id": "a1", "user_id": "user_123",
            "skill": "Flask", "difficulty": "Beginner", "score": 100.0,
        })
        result = manager.verify_certificate("cert_a1", "wrong_code")
        assert result is False

    def test_verify_certificate_not_found(self, manager):
        """Test verifying a non-existent certificate returns False."""
        result = manager.verify_certificate("cert_nonexistent", "any_code")
        assert result is False


class TestBadgeManagement:
    """Tests for digital badge issuance and retrieval."""

    def test_issue_digital_badge(self, manager):
        """Test issuing a digital badge."""
        badge = manager.issue_digital_badge("user_123", "Python", "Beginner")
        assert badge["user_id"] == "user_123"
        assert badge["skill"] == "Python"
        assert badge["level"] == "Beginner"
        assert "badge_id" in badge
        assert "issued_at" in badge

    def test_get_user_badges(self, manager):
        """Test retrieving all badges for a user."""
        manager.issue_digital_badge("user_123", "Python", "Beginner")
        manager.issue_digital_badge("user_123", "Flask", "Intermediate")
        badges = manager.get_user_badges("user_123")
        assert len(badges) == 2

    def test_get_user_badges_none_exist(self, manager):
        """Test that get_user_badges returns empty list for users with none."""
        badges = manager.get_user_badges("user_with_no_badges")
        assert badges == []


class TestCertificationStatus:
    """Tests for overall certification status."""

    def test_get_certification_status_empty(self, manager):
        """Test certification status for a user with no credentials."""
        status = manager.get_certification_status("new_user")
        assert status["user_id"] == "new_user"
        assert status["total_certificates"] == 0
        assert status["total_badges"] == 0
        assert status["certified_skills"] == []
        assert status["badges_earned"] == []

    def test_get_certification_status_with_credentials(self, manager):
        """Test certification status aggregates certificates and badges."""
        manager._issue_certificate({
            "assessment_id": "a1", "user_id": "user_123",
            "skill": "Flask", "difficulty": "Beginner", "score": 100.0,
        })
        manager.issue_digital_badge("user_123", "Python", "Beginner")
        status = manager.get_certification_status("user_123")
        assert status["total_certificates"] == 1
        assert status["total_badges"] == 1
        assert "Flask" in status["certified_skills"]
        assert "Python" in status["badges_earned"]


class TestCredentialPDF:
    """Tests for credential PDF generation."""

    def test_generate_credential_pdf(self, manager):
        """Test generating a credential PDF for a valid certificate."""
        manager._issue_certificate({
            "assessment_id": "a1", "user_id": "user_123",
            "skill": "Flask", "difficulty": "Beginner", "score": 100.0,
        })
        pdf = manager.generate_credential_pdf("cert_a1")
        assert pdf["certificate_id"] == "cert_a1"
        assert pdf["user_id"] == "user_123"
        assert pdf["skill"] == "Flask"
        assert "pdf_url" in pdf

    def test_generate_credential_pdf_not_found(self, manager):
        """Test that generating PDF for non-existent certificate raises."""
        with pytest.raises(ValueError, match="not found"):
            manager.generate_credential_pdf("cert_nonexistent")


class TestEdgeCases:
    """Tests for edge cases in certification logic."""

    def test_score_at_boundary_70_percent(self, manager):
        """Test that exactly 70% is a passing score."""
        questions = [
            {"id": f"q{i}", "correct_answer": chr(64 + i)}
            for i in range(1, 11)
        ]
        manager.create_assessment(
            "assess_001", "user_123", "Skill", "Beginner", questions
        )
        answers = {f"q{i}": chr(64 + i) for i in range(1, 8)}
        result = manager.submit_assessment("assess_001", answers)
        assert result["passed"] is True

    def test_score_below_boundary_69_percent(self, manager):
        """Test that 69% is a failing score."""
        questions = [
            {"id": f"q{i}", "correct_answer": chr(64 + i)}
            for i in range(1, 11)
        ]
        manager.create_assessment(
            "assess_001", "user_123", "Skill", "Beginner", questions
        )
        answers = {f"q{i}": chr(64 + i) for i in range(1, 7)}
        result = manager.submit_assessment("assess_001", answers)
        assert result["passed"] is False
