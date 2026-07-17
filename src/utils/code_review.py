"""
Project code review and feedback system.

Enables expert code reviews, quality assessment, and structured feedback
for learner project submissions.
"""

from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
import json


class ReviewStatus(Enum):
    """Status of a code review."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CHANGES_REQUESTED = "changes_requested"


class CodeQualityCategory(Enum):
    """Categories for code quality assessment."""
    FUNCTIONALITY = "functionality"
    CODE_STYLE = "code_style"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TESTING = "testing"
    DOCUMENTATION = "documentation"


FEEDBACK_TEMPLATES = {
    "functionality": {
        "excellent": "Code correctly implements all required functionality",
        "good": "Code implements functionality with minor issues",
        "needs_improvement": "Code is missing key functionality or has logic errors",
    },
    "code_style": {
        "excellent": "Code follows best practices and conventions",
        "good": "Code style is mostly consistent with minor improvements",
        "needs_improvement": "Code style needs significant improvement",
    },
    "performance": {
        "excellent": "Code is optimized and performs efficiently",
        "good": "Code performs adequately with minor optimization opportunities",
        "needs_improvement": "Code has significant performance concerns",
    },
    "security": {
        "excellent": "No security vulnerabilities detected",
        "good": "Code is generally secure with minor hardening suggestions",
        "needs_improvement": "Code has security vulnerabilities that need addressing",
    },
    "testing": {
        "excellent": "Comprehensive test coverage with good test quality",
        "good": "Adequate test coverage with most cases covered",
        "needs_improvement": "Insufficient or low-quality test coverage",
    },
    "documentation": {
        "excellent": "Clear and comprehensive documentation",
        "good": "Adequate documentation with minor gaps",
        "needs_improvement": "Missing or unclear documentation",
    },
}


class CodeReviewManager:
    """Manages code submissions and reviews."""

    def __init__(self):
        self.submissions: Dict[str, Dict] = {}
        self.reviews: Dict[str, Dict] = {}
        self.feedback_comments: Dict[str, List[Dict]] = {}

    def submit_code(
        self,
        submission_id: str,
        user_id: str,
        project_id: int,
        code: str,
        language: str,
        description: Optional[str] = None,
    ) -> Dict:
        """
        Submit project code for review.

        Args:
            submission_id: Unique submission identifier
            user_id: User submitting the code
            project_id: Project ID being worked on
            code: Source code content
            language: Programming language
            description: Optional description of implementation

        Returns:
            Submission metadata
        """
        submission = {
            "submission_id": submission_id,
            "user_id": user_id,
            "project_id": project_id,
            "code": code,
            "language": language,
            "description": description or "",
            "submitted_at": datetime.utcnow().isoformat(),
            "review_status": ReviewStatus.PENDING.value,
            "review_count": 0,
            "metrics": {},
        }

        self.submissions[submission_id] = submission
        return submission

    def start_review(
        self,
        submission_id: str,
        reviewer_id: str,
    ) -> Dict:
        """
        Start a code review session.

        Args:
            submission_id: ID of submission to review
            reviewer_id: ID of person reviewing

        Returns:
            Review session data
        """
        if submission_id not in self.submissions:
            raise ValueError(f"Submission {submission_id} not found")

        submission = self.submissions[submission_id]
        review_id = f"review_{submission_id}_{datetime.utcnow().timestamp()}"

        review = {
            "review_id": review_id,
            "submission_id": submission_id,
            "reviewer_id": reviewer_id,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "status": ReviewStatus.IN_PROGRESS.value,
            "overall_score": None,
            "category_scores": {},
            "issues_found": [],
        }

        self.reviews[review_id] = review
        submission["review_status"] = ReviewStatus.IN_PROGRESS.value
        self.feedback_comments[review_id] = []

        return review

    def add_feedback_comment(
        self,
        review_id: str,
        line_number: int,
        code_snippet: str,
        feedback: str,
        severity: str = "info",
    ) -> Dict:
        """
        Add a feedback comment to a review.

        Args:
            review_id: Review ID
            line_number: Line number with issue
            code_snippet: Code snippet being commented on
            feedback: Feedback message
            severity: "info", "warning", or "error"

        Returns:
            Comment data
        """
        if review_id not in self.reviews:
            raise ValueError(f"Review {review_id} not found")

        comment = {
            "comment_id": f"comment_{review_id}_{len(self.feedback_comments[review_id])}",
            "line_number": line_number,
            "code_snippet": code_snippet,
            "feedback": feedback,
            "severity": severity,
            "created_at": datetime.utcnow().isoformat(),
        }

        self.feedback_comments[review_id].append(comment)

        if review_id in self.reviews:
            if "issues_found" not in self.reviews[review_id]:
                self.reviews[review_id]["issues_found"] = []
            self.reviews[review_id]["issues_found"].append(comment)

        return comment

    def score_category(
        self,
        review_id: str,
        category: str,
        score: float,
        feedback: str = "",
    ) -> Dict:
        """
        Score a code quality category.

        Args:
            review_id: Review ID
            category: Category from CodeQualityCategory
            score: Score 0-100
            feedback: Optional feedback

        Returns:
            Category score data
        """
        if review_id not in self.reviews:
            raise ValueError(f"Review {review_id} not found")

        if not (0 <= score <= 100):
            raise ValueError("Score must be between 0 and 100")

        category_score = {
            "category": category,
            "score": score,
            "feedback": feedback or "",
            "level": self._score_to_level(score),
        }

        self.reviews[review_id]["category_scores"][category] = category_score
        return category_score

    def complete_review(
        self,
        review_id: str,
        summary: str,
        recommend_changes: bool = False,
    ) -> Dict:
        """
        Complete a code review.

        Args:
            review_id: Review ID
            summary: Summary of review findings
            recommend_changes: Whether changes are recommended

        Returns:
            Completed review data
        """
        if review_id not in self.reviews:
            raise ValueError(f"Review {review_id} not found")

        review = self.reviews[review_id]
        scores = [s["score"] for s in review["category_scores"].values()]
        overall_score = sum(scores) / len(scores) if scores else 0

        review["completed_at"] = datetime.utcnow().isoformat()
        review["overall_score"] = round(overall_score, 2)
        review["summary"] = summary
        review["status"] = (
            ReviewStatus.CHANGES_REQUESTED.value
            if recommend_changes
            else ReviewStatus.COMPLETED.value
        )

        submission_id = review["submission_id"]
        if submission_id in self.submissions:
            submission = self.submissions[submission_id]
            submission["review_status"] = review["status"]
            submission["review_count"] += 1
            submission["metrics"] = {
                "overall_score": review["overall_score"],
                "category_scores": review["category_scores"],
            }

        return review

    def get_submission(self, submission_id: str) -> Optional[Dict]:
        """Get a submission by ID."""
        return self.submissions.get(submission_id)

    def get_user_submissions(self, user_id: str) -> List[Dict]:
        """Get all submissions from a user."""
        return [
            s for s in self.submissions.values()
            if s["user_id"] == user_id
        ]

    def get_project_submissions(self, project_id: int) -> List[Dict]:
        """Get all submissions for a project."""
        return [
            s for s in self.submissions.values()
            if s["project_id"] == project_id
        ]

    def get_review(self, review_id: str) -> Optional[Dict]:
        """Get a review by ID."""
        return self.reviews.get(review_id)

    def get_review_comments(self, review_id: str) -> List[Dict]:
        """Get all feedback comments for a review."""
        return self.feedback_comments.get(review_id, [])

    def get_code_quality_score(self, submission_id: str) -> Dict:
        """
        Calculate code quality score for a submission.

        Returns metrics based on completed reviews.
        """
        submission = self.submissions.get(submission_id)
        if not submission or not submission.get("metrics"):
            return {
                "submission_id": submission_id,
                "overall_score": None,
                "categories": {},
                "status": "no_review",
            }

        return {
            "submission_id": submission_id,
            "overall_score": submission["metrics"].get("overall_score"),
            "categories": {
                cat: score.get("score", 0)
                for cat, score in submission["metrics"]
                .get("category_scores", {})
                .items()
            },
            "status": "reviewed",
        }

    def get_improvement_recommendations(self, submission_id: str) -> List[str]:
        """Get improvement recommendations based on reviews."""
        submission = self.submissions.get(submission_id)
        if not submission:
            return []

        recommendations = []

        for review_id in self._get_reviews_for_submission(submission_id):
            review = self.reviews.get(review_id)
            if not review:
                continue

            for category, score_data in review.get(
                "category_scores", {}
            ).items():
                score = score_data.get("score", 0)
                if score < 70:
                    recommendations.append(
                        f"Improve {category}: {score_data.get('feedback', '')}"
                    )

        return recommendations

    @staticmethod
    def _score_to_level(score: float) -> str:
        """Convert numeric score to qualitative level."""
        if score >= 85:
            return "excellent"
        elif score >= 70:
            return "good"
        else:
            return "needs_improvement"

    def _get_reviews_for_submission(self, submission_id: str) -> List[str]:
        """Get all review IDs for a submission."""
        return [
            rid for rid, r in self.reviews.items()
            if r.get("submission_id") == submission_id
        ]
