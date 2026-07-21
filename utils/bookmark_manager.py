"""Bookmark management for resources and learning paths.

Manages bookmarks for authenticated and non-authenticated users.
Non-authenticated users use localStorage, authenticated users use database.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any


class BookmarkManager:
    """Manages bookmarks for resources and topics."""

    def __init__(self, db=None):
        """Initialize bookmark manager.

        Args:
            db: Database connection for authenticated users
        """
        self.db = db

    def add_bookmark(
        self,
        user_id: int,
        resource_type: str,
        resource_id: int,
        resource_name: str,
    ) -> Optional[int]:
        """Add a bookmark for an authenticated user.

        Args:
            user_id: ID of the user
            resource_type: Type of resource (path, topic, project)
            resource_id: ID of the resource
            resource_name: Name of the resource for display

        Returns:
            Bookmark ID if created, None if failed
        """
        if not self.db:
            return None

        try:
            cursor = self.db.execute(
                """INSERT INTO bookmarks
                   (user_id, resource_type, resource_id, resource_name, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, resource_type, resource_id, resource_name, datetime.now()),
            )
            self.db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding bookmark: {e}")
            return None

    def remove_bookmark(
        self, user_id: int, resource_type: str, resource_id: int
    ) -> bool:
        """Remove a bookmark for a user.

        Args:
            user_id: ID of the user
            resource_type: Type of resource
            resource_id: ID of the resource

        Returns:
            True if removed, False if not found or error
        """
        if not self.db:
            return False

        try:
            self.db.execute(
                """DELETE FROM bookmarks
                   WHERE user_id = ? AND resource_type = ? AND resource_id = ?""",
                (user_id, resource_type, resource_id),
            )
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error removing bookmark: {e}")
            return False

    def get_user_bookmarks(
        self, user_id: int, resource_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all bookmarks for a user.

        Args:
            user_id: ID of the user
            resource_type: Optional filter by resource type

        Returns:
            List of bookmark dictionaries
        """
        if not self.db:
            return []

        try:
            if resource_type:
                cursor = self.db.execute(
                    """SELECT id, user_id, resource_type, resource_id,
                       resource_name, created_at
                       FROM bookmarks
                       WHERE user_id = ? AND resource_type = ?
                       ORDER BY created_at DESC""",
                    (user_id, resource_type),
                )
            else:
                cursor = self.db.execute(
                    """SELECT id, user_id, resource_type, resource_id,
                       resource_name, created_at
                       FROM bookmarks
                       WHERE user_id = ?
                       ORDER BY created_at DESC""",
                    (user_id,),
                )

            bookmarks = []
            for row in cursor.fetchall():
                bookmarks.append(
                    {
                        "id": row[0],
                        "user_id": row[1],
                        "resource_type": row[2],
                        "resource_id": row[3],
                        "resource_name": row[4],
                        "created_at": row[5],
                    }
                )

            return bookmarks
        except Exception as e:
            print(f"Error retrieving bookmarks: {e}")
            return []

    def is_bookmarked(
        self, user_id: int, resource_type: str, resource_id: int
    ) -> bool:
        """Check if a resource is bookmarked by user.

        Args:
            user_id: ID of the user
            resource_type: Type of resource
            resource_id: ID of the resource

        Returns:
            True if bookmarked, False otherwise
        """
        if not self.db:
            return False

        try:
            cursor = self.db.execute(
                """SELECT id FROM bookmarks
                   WHERE user_id = ? AND resource_type = ? AND resource_id = ?""",
                (user_id, resource_type, resource_id),
            )
            result = cursor.fetchone()
            return result is not None
        except Exception:
            return False

    def get_bookmark_count(self, user_id: int) -> int:
        """Get total bookmark count for user.

        Args:
            user_id: ID of the user

        Returns:
            Number of bookmarks
        """
        if not self.db:
            return 0

        try:
            cursor = self.db.execute(
                "SELECT COUNT(*) FROM bookmarks WHERE user_id = ?", (user_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception:
            return 0

    def get_popular_bookmarks(self, resource_type: str, limit: int = 10) -> List[Dict]:
        """Get most bookmarked resources of a type.

        Args:
            resource_type: Type of resource
            limit: Number to return

        Returns:
            List of popular bookmarked resources
        """
        if not self.db:
            return []

        try:
            cursor = self.db.execute(
                """SELECT resource_id, resource_name, COUNT(*) as bookmark_count
                   FROM bookmarks
                   WHERE resource_type = ?
                   GROUP BY resource_id
                   ORDER BY bookmark_count DESC
                   LIMIT ?""",
                (resource_type, limit),
            )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "resource_id": row[0],
                        "resource_name": row[1],
                        "bookmark_count": row[2],
                    }
                )

            return results
        except Exception:
            return []
