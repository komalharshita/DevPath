"""Adaptive learning paths and personalization system."""

from typing import Dict, List, Optional
from datetime import datetime


class AdaptiveLearningManager:
    """Manages personalized learning paths and adaptive recommendations."""

    def __init__(self):
        self.user_profiles: Dict[str, Dict] = {}
        self.learning_paths: Dict[str, List[Dict]] = {}
        self.performance_history: Dict[str, List[Dict]] = {}

    def create_user_profile(
        self, user_id: str, initial_skills: List[str], learning_style: str
    ) -> Dict:
        """Create personalized user learning profile."""
        profile = {
            "user_id": user_id,
            "skills": initial_skills,
            "learning_style": learning_style,
            "preferred_difficulty": "Beginner",
            "learning_pace": "Medium",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        self.user_profiles[user_id] = profile
        return profile

    def assess_skill_level(self, user_id: str, skill: str) -> Dict:
        """Assess user's current skill level."""
        if user_id not in self.user_profiles:
            raise ValueError(f"User {user_id} not found")

        assessment = {
            "user_id": user_id,
            "skill": skill,
            "level": "Beginner",
            "confidence": 0.0,
            "assessed_at": datetime.utcnow().isoformat(),
        }
        return assessment

    def generate_adaptive_path(
        self, user_id: str, goal: str, available_time_hours: int
    ) -> List[Dict]:
        """Generate personalized learning path."""
        if user_id not in self.user_profiles:
            raise ValueError(f"User {user_id} not found")

        path = [
            {"step": 1, "type": "assessment", "topic": goal, "estimated_hours": 1},
            {"step": 2, "type": "lesson", "topic": f"{goal} Basics", "estimated_hours": 2},
            {
                "step": 3,
                "type": "project",
                "topic": f"{goal} Project",
                "estimated_hours": 3,
            },
            {
                "step": 4,
                "type": "assessment",
                "topic": f"{goal} Mastery",
                "estimated_hours": 1,
            },
        ]

        self.learning_paths[user_id] = path
        return path

    def record_progress(
        self, user_id: str, item_id: int, score: float, time_spent: int
    ) -> Dict:
        """Record learning progress and update path."""
        if user_id not in self.performance_history:
            self.performance_history[user_id] = []

        record = {
            "item_id": item_id,
            "score": score,
            "time_spent_minutes": time_spent,
            "recorded_at": datetime.utcnow().isoformat(),
        }
        self.performance_history[user_id].append(record)

        self._adapt_path(user_id)
        return record

    def _adapt_path(self, user_id: str):
        """Adapt learning path based on performance."""
        if user_id not in self.performance_history:
            return

        history = self.performance_history[user_id]
        if not history:
            return

        avg_score = sum(r["score"] for r in history) / len(history)
        profile = self.user_profiles[user_id]

        if avg_score >= 80:
            profile["preferred_difficulty"] = "Advanced"
            profile["learning_pace"] = "Fast"
        elif avg_score >= 60:
            profile["preferred_difficulty"] = "Intermediate"
            profile["learning_pace"] = "Medium"
        else:
            profile["preferred_difficulty"] = "Beginner"
            profile["learning_pace"] = "Slow"

        profile["updated_at"] = datetime.utcnow().isoformat()

    def get_next_recommendation(self, user_id: str) -> Optional[Dict]:
        """Get next recommended item in adaptive path."""
        if user_id not in self.learning_paths:
            return None

        path = self.learning_paths[user_id]
        completed = len(self.performance_history.get(user_id, []))

        if completed < len(path):
            return path[completed]
        return None

    def calculate_learning_metrics(self, user_id: str) -> Dict:
        """Calculate adaptive learning metrics."""
        history = self.performance_history.get(user_id, [])

        if not history:
            return {
                "user_id": user_id,
                "items_completed": 0,
                "average_score": 0,
                "learning_efficiency": 0,
            }

        avg_score = sum(r["score"] for r in history) / len(history)
        total_time = sum(r["time_spent_minutes"] for r in history)
        efficiency = (avg_score / max(total_time, 1)) * 100

        return {
            "user_id": user_id,
            "items_completed": len(history),
            "average_score": round(avg_score, 2),
            "total_time_spent": total_time,
            "learning_efficiency": round(efficiency, 2),
        }
