"""
Learning time tracking and analytics system.

Tracks time spent on lessons/projects and provides analytics on learning pace,
estimated completion times, and time management recommendations.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import statistics


class TimeSession:
    """Represents a learning session."""

    def __init__(
        self,
        session_id: str,
        user_id: str,
        item_type: str,
        item_id: int,
        start_time: datetime,
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.item_type = item_type
        self.item_id = item_id
        self.start_time = start_time
        self.end_time: Optional[datetime] = None
        self.duration_minutes: Optional[float] = None

    def end_session(self):
        """End the session and calculate duration."""
        self.end_time = datetime.utcnow()
        duration = self.end_time - self.start_time
        self.duration_minutes = duration.total_seconds() / 60

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "item_type": self.item_type,
            "item_id": self.item_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_minutes": self.duration_minutes,
        }


class TimeTrackingManager:
    """Manages learning time tracking and analytics."""

    def __init__(self):
        self.sessions: Dict[str, TimeSession] = {}
        self.active_sessions: Dict[str, TimeSession] = {}
        self.default_lesson_time = 60
        self.default_project_time = 180

    def start_session(
        self,
        session_id: str,
        user_id: str,
        item_type: str,
        item_id: int,
    ) -> TimeSession:
        """
        Start a learning session.

        Args:
            session_id: Unique session identifier
            user_id: User ID
            item_type: Type of item ("lesson" or "project")
            item_id: ID of the lesson/project

        Returns:
            TimeSession object
        """
        session = TimeSession(session_id, user_id, item_type, item_id, datetime.utcnow())
        self.active_sessions[session_id] = session
        return session

    def end_session(self, session_id: str) -> Optional[TimeSession]:
        """End a learning session and save it."""
        if session_id not in self.active_sessions:
            return None

        session = self.active_sessions.pop(session_id)
        session.end_session()
        self.sessions[session_id] = session
        return session

    def get_time_spent_on_item(self, user_id: str, item_type: str, item_id: int) -> float:
        """Get total time spent on a specific item (in minutes)."""
        total_minutes = 0
        for session in self.sessions.values():
            if (
                session.user_id == user_id
                and session.item_type == item_type
                and session.item_id == item_id
                and session.duration_minutes
            ):
                total_minutes += session.duration_minutes
        return round(total_minutes, 2)

    def get_user_total_time(self, user_id: str) -> float:
        """Get total time spent learning by a user (in minutes)."""
        total_minutes = 0
        for session in self.sessions.values():
            if session.user_id == user_id and session.duration_minutes:
                total_minutes += session.duration_minutes
        return round(total_minutes, 2)

    def get_user_time_by_type(self, user_id: str) -> Dict[str, float]:
        """Get time breakdown by item type."""
        breakdown = {"lesson": 0, "project": 0}
        for session in self.sessions.values():
            if session.user_id == user_id and session.duration_minutes:
                breakdown[session.item_type] = (
                    breakdown.get(session.item_type, 0) + session.duration_minutes
                )
        return {k: round(v, 2) for k, v in breakdown.items()}

    def estimate_time_for_item(self, item_type: str) -> int:
        """
        Estimate time needed for an item based on type.

        Returns time in minutes.
        """
        if item_type == "lesson":
            return self.default_lesson_time
        elif item_type == "project":
            return self.default_project_time
        return 60

    def calculate_learning_velocity(self, user_id: str, days: int = 7) -> Dict:
        """
        Calculate learning velocity (time spent per day).

        Args:
            user_id: User ID
            days: Number of days to calculate for (default 7)

        Returns:
            Velocity metrics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_sessions = [
            s
            for s in self.sessions.values()
            if s.user_id == user_id
            and s.start_time >= cutoff_date
            and s.duration_minutes
        ]

        if not recent_sessions:
            return {
                "days_active": 0,
                "total_time": 0,
                "average_daily_time": 0,
                "sessions_count": 0,
            }

        total_time = sum(s.duration_minutes for s in recent_sessions)
        unique_days = len(set(s.start_time.date() for s in recent_sessions))
        avg_daily = total_time / unique_days if unique_days > 0 else 0

        return {
            "days_active": unique_days,
            "total_time": round(total_time, 2),
            "average_daily_time": round(avg_daily, 2),
            "sessions_count": len(recent_sessions),
        }

    def estimate_completion_time(
        self,
        user_id: str,
        remaining_items: List[Dict],
    ) -> Dict:
        """
        Estimate time to complete remaining items.

        Args:
            user_id: User ID
            remaining_items: List of items with their types

        Returns:
            Completion time estimate
        """
        velocity = self.calculate_learning_velocity(user_id, days=30)
        avg_daily_time = velocity.get("average_daily_time", 30)

        if avg_daily_time == 0:
            avg_daily_time = 45

        total_estimated = sum(
            self.estimate_time_for_item(item["type"]) for item in remaining_items
        )

        days_to_complete = total_estimated / avg_daily_time if avg_daily_time > 0 else 0
        completion_date = datetime.utcnow() + timedelta(days=days_to_complete)

        return {
            "total_estimated_minutes": total_estimated,
            "total_estimated_hours": round(total_estimated / 60, 2),
            "days_to_complete": round(days_to_complete, 1),
            "estimated_completion_date": completion_date.isoformat(),
            "based_on_average_daily_time": avg_daily_time,
        }

    def get_time_analytics(self, user_id: str) -> Dict:
        """Get comprehensive time analytics for a user."""
        user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]

        if not user_sessions:
            return {
                "user_id": user_id,
                "total_time": 0,
                "sessions_count": 0,
                "average_session_duration": 0,
                "time_by_type": {"lesson": 0, "project": 0},
                "learning_velocity": {},
            }

        durations = [s.duration_minutes for s in user_sessions if s.duration_minutes]

        return {
            "user_id": user_id,
            "total_time": round(self.get_user_total_time(user_id), 2),
            "sessions_count": len(user_sessions),
            "average_session_duration": (
                round(statistics.mean(durations), 2) if durations else 0
            ),
            "median_session_duration": (
                round(statistics.median(durations), 2) if durations else 0
            ),
            "time_by_type": self.get_user_time_by_type(user_id),
            "learning_velocity": self.calculate_learning_velocity(user_id, days=7),
        }

    def predict_skill_proficiency(self, user_id: str, target_hours: int = 100) -> Dict:
        """
        Predict time needed to reach target proficiency.

        Args:
            user_id: User ID
            target_hours: Target hours of study

        Returns:
            Proficiency prediction
        """
        total_time = self.get_user_total_time(user_id)
        target_minutes = target_hours * 60

        if total_time >= target_minutes:
            return {
                "target_hours": target_hours,
                "current_hours": round(total_time / 60, 2),
                "status": "target_reached",
                "hours_remaining": 0,
            }

        velocity = self.calculate_learning_velocity(user_id, days=30)
        avg_daily_time = velocity.get("average_daily_time", 45)

        if avg_daily_time == 0:
            avg_daily_time = 45

        remaining_minutes = target_minutes - total_time
        days_needed = remaining_minutes / avg_daily_time

        return {
            "target_hours": target_hours,
            "current_hours": round(total_time / 60, 2),
            "hours_remaining": round(remaining_minutes / 60, 2),
            "days_to_target": round(days_needed, 1),
            "target_date": (
                datetime.utcnow() + timedelta(days=days_needed)
            ).isoformat(),
        }
