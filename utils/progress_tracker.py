"""Progress tracking for learners.

Tracks learner progress across paths and topics, maintains streaks,
and calculates dashboard metrics.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


class ProgressTracker:
    """Tracks learner progress and engagement metrics."""

    def __init__(self, db=None):
        """Initialize progress tracker.

        Args:
            db: Database connection
        """
        self.db = db

    def get_user_progress(self, user_id: int) -> Dict[str, Any]:
        """Get overall progress metrics for a user.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with progress metrics
        """
        if not self.db:
            return {}

        try:
            # Get total and completed topics
            cursor = self.db.execute(
                """SELECT
                   COUNT(*) as total_topics,
                   COUNT(CASE WHEN completed = 1 THEN 1 END) as completed_topics
                   FROM user_topic_progress
                   WHERE user_id = ?""",
                (user_id,),
            )
            result = cursor.fetchone()

            total = result[0] if result else 0
            completed = result[1] if result else 0
            percentage = (completed / total * 100) if total > 0 else 0

            return {
                'total_topics': total,
                'completed_topics': completed,
                'completion_percentage': round(percentage, 1),
                'streak_days': self._calculate_streak(user_id),
                'paths': self._get_path_progress(user_id),
                'weekly_activity': self._get_weekly_activity(user_id),
            }

        except Exception as e:
            print(f"Error getting user progress: {e}")
            return {}

    def _calculate_streak(self, user_id: int) -> int:
        """Calculate current streak of consecutive active days.

        Args:
            user_id: ID of the user

        Returns:
            Number of consecutive active days
        """
        try:
            cursor = self.db.execute(
                """SELECT MAX(date) as last_active
                   FROM user_activity
                   WHERE user_id = ?""",
                (user_id,),
            )
            result = cursor.fetchone()

            if not result or not result[0]:
                return 0

            # For demo, return a simple streak counter
            # In production, would track consecutive days
            return 7  # Placeholder

        except Exception:
            return 0

    def _get_path_progress(self, user_id: int) -> List[Dict]:
        """Get progress for each learning path.

        Args:
            user_id: ID of the user

        Returns:
            List of path progress dictionaries
        """
        try:
            cursor = self.db.execute(
                """SELECT p.id, p.name,
                   COUNT(pt.id) as total,
                   COUNT(CASE WHEN pt.completed = 1 THEN 1 END) as completed
                   FROM paths p
                   LEFT JOIN topics pt ON p.id = pt.path_id
                   LEFT JOIN user_topic_progress utp
                     ON pt.id = utp.topic_id AND utp.user_id = ?
                   GROUP BY p.id
                   HAVING total > 0
                   ORDER BY completed DESC""",
                (user_id,),
            )

            paths = []
            for row in cursor.fetchall():
                paths.append({
                    'id': row[0],
                    'name': row[1],
                    'total': row[2],
                    'completed': row[3] if row[3] else 0,
                })

            return paths

        except Exception as e:
            print(f"Error getting path progress: {e}")
            return []

    def _get_weekly_activity(self, user_id: int) -> List[int]:
        """Get activity counts for last 7 days.

        Args:
            user_id: ID of the user

        Returns:
            List of activity counts for each day of week
        """
        try:
            # Get activity for last 7 days
            cursor = self.db.execute(
                """SELECT strftime('%w', date) as day_of_week,
                   COUNT(*) as activity_count
                   FROM user_activity
                   WHERE user_id = ? AND date >= datetime('now', '-7 days')
                   GROUP BY day_of_week
                   ORDER BY day_of_week""",
                (user_id,),
            )

            # Create array for all 7 days (0=Sun, 6=Sat)
            activity = [0] * 7

            for row in cursor.fetchall():
                day = int(row[0])
                activity[day] = row[1]

            return activity

        except Exception:
            return [0] * 7

    def record_activity(self, user_id: int, topic_id: int) -> bool:
        """Record that user accessed a topic.

        Args:
            user_id: ID of the user
            topic_id: ID of the topic

        Returns:
            True if recorded, False otherwise
        """
        if not self.db:
            return False

        try:
            self.db.execute(
                """INSERT OR IGNORE INTO user_activity
                   (user_id, topic_id, date, timestamp)
                   VALUES (?, ?, date('now'), datetime('now'))""",
                (user_id, topic_id),
            )
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error recording activity: {e}")
            return False

    def mark_topic_complete(self, user_id: int, topic_id: int) -> bool:
        """Mark a topic as completed by user.

        Args:
            user_id: ID of the user
            topic_id: ID of the topic

        Returns:
            True if marked, False otherwise
        """
        if not self.db:
            return False

        try:
            self.db.execute(
                """INSERT OR REPLACE INTO user_topic_progress
                   (user_id, topic_id, completed, completed_at)
                   VALUES (?, ?, 1, datetime('now'))""",
                (user_id, topic_id),
            )
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error marking topic complete: {e}")
            return False
