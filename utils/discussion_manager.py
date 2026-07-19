"""Discussion threads management for learning paths.

Manages community discussion threads where learners can ask questions,
share tips, and support each other while following a learning path.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any


class DiscussionManager:
    """Manages discussion threads and comments for learning paths."""

    def __init__(self, db=None):
        """Initialize discussion manager with database connection.

        Args:
            db: Database connection
        """
        self.db = db

    def create_thread(
        self, path_id: int, user_id: int, title: str, body: str
    ) -> Optional[int]:
        """Create a new discussion thread.

        Args:
            path_id: ID of the learning path
            user_id: ID of thread creator
            title: Thread title
            body: Thread content (markdown supported)

        Returns:
            Thread ID if created, None if failed
        """
        if not self.db:
            return None

        try:
            cursor = self.db.execute(
                """INSERT INTO discussion_threads
                   (path_id, user_id, title, body, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (path_id, user_id, title, body, datetime.now(), datetime.now()),
            )
            self.db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating thread: {e}")
            return None

    def get_thread(self, thread_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a discussion thread with all comments.

        Args:
            thread_id: ID of the thread

        Returns:
            Thread data with comments, or None if not found
        """
        if not self.db:
            return None

        try:
            cursor = self.db.execute(
                """SELECT id, path_id, user_id, title, body, created_at,
                   updated_at FROM discussion_threads WHERE id = ?""",
                (thread_id,),
            )
            thread_row = cursor.fetchone()

            if not thread_row:
                return None

            thread = {
                "id": thread_row[0],
                "path_id": thread_row[1],
                "user_id": thread_row[2],
                "title": thread_row[3],
                "body": thread_row[4],
                "created_at": thread_row[5],
                "updated_at": thread_row[6],
                "comments": self._get_thread_comments(thread_id),
            }

            return thread
        except Exception as e:
            print(f"Error retrieving thread: {e}")
            return None

    def _get_thread_comments(self, thread_id: int) -> List[Dict[str, Any]]:
        """Get all comments for a thread.

        Args:
            thread_id: ID of the thread

        Returns:
            List of comment dictionaries
        """
        try:
            cursor = self.db.execute(
                """SELECT id, user_id, body, created_at
                   FROM thread_comments
                   WHERE thread_id = ?
                   ORDER BY created_at ASC""",
                (thread_id,),
            )

            comments = []
            for row in cursor.fetchall():
                comments.append(
                    {
                        "id": row[0],
                        "user_id": row[1],
                        "body": row[2],
                        "created_at": row[3],
                    }
                )

            return comments
        except Exception as e:
            print(f"Error retrieving comments: {e}")
            return []

    def add_comment(
        self, thread_id: int, user_id: int, body: str
    ) -> Optional[int]:
        """Add a comment to a discussion thread.

        Args:
            thread_id: ID of the thread
            user_id: ID of comment author
            body: Comment content

        Returns:
            Comment ID if created, None if failed
        """
        if not self.db:
            return None

        try:
            cursor = self.db.execute(
                """INSERT INTO thread_comments
                   (thread_id, user_id, body, created_at)
                   VALUES (?, ?, ?, ?)""",
                (thread_id, user_id, body, datetime.now()),
            )
            self.db.commit()

            # Update thread updated_at timestamp
            self.db.execute(
                "UPDATE discussion_threads SET updated_at = ? WHERE id = ?",
                (datetime.now(), thread_id),
            )
            self.db.commit()

            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding comment: {e}")
            return None

    def get_path_threads(
        self, path_id: int, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all discussion threads for a learning path.

        Args:
            path_id: ID of the learning path
            limit: Maximum number of threads to return
            offset: Number of threads to skip (for pagination)

        Returns:
            List of thread summaries (without full comments)
        """
        if not self.db:
            return []

        try:
            cursor = self.db.execute(
                """SELECT id, path_id, user_id, title, body, created_at,
                   updated_at
                   FROM discussion_threads
                   WHERE path_id = ?
                   ORDER BY updated_at DESC
                   LIMIT ? OFFSET ?""",
                (path_id, limit, offset),
            )

            threads = []
            for row in cursor.fetchall():
                # Count comments for this thread
                comment_count = self._count_thread_comments(row[0])

                threads.append(
                    {
                        "id": row[0],
                        "path_id": row[1],
                        "user_id": row[2],
                        "title": row[3],
                        "preview": row[4][:150] + "..." if len(row[4]) > 150 else row[4],
                        "created_at": row[5],
                        "updated_at": row[6],
                        "comment_count": comment_count,
                    }
                )

            return threads
        except Exception as e:
            print(f"Error retrieving path threads: {e}")
            return []

    def _count_thread_comments(self, thread_id: int) -> int:
        """Count comments on a thread.

        Args:
            thread_id: ID of the thread

        Returns:
            Number of comments
        """
        try:
            cursor = self.db.execute(
                "SELECT COUNT(*) FROM thread_comments WHERE thread_id = ?",
                (thread_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception:
            return 0

    def delete_thread(self, thread_id: int, user_id: int) -> bool:
        """Delete a discussion thread (only by creator or admin).

        Args:
            thread_id: ID of the thread
            user_id: ID of user attempting deletion

        Returns:
            True if deleted, False otherwise
        """
        if not self.db:
            return False

        try:
            # Verify user is thread creator
            cursor = self.db.execute(
                "SELECT user_id FROM discussion_threads WHERE id = ?",
                (thread_id,),
            )
            thread = cursor.fetchone()

            if not thread or thread[0] != user_id:
                return False

            # Delete comments first
            self.db.execute(
                "DELETE FROM thread_comments WHERE thread_id = ?", (thread_id,)
            )

            # Delete thread
            self.db.execute(
                "DELETE FROM discussion_threads WHERE id = ?", (thread_id,)
            )

            self.db.commit()
            return True
        except Exception as e:
            print(f"Error deleting thread: {e}")
            return False

    def search_threads(self, path_id: int, query: str) -> List[Dict[str, Any]]:
        """Search discussion threads by title or content.

        Args:
            path_id: ID of the learning path
            query: Search query

        Returns:
            List of matching threads
        """
        if not self.db:
            return []

        try:
            search_query = f"%{query}%"
            cursor = self.db.execute(
                """SELECT id, path_id, user_id, title, body, created_at,
                   updated_at
                   FROM discussion_threads
                   WHERE path_id = ? AND (title LIKE ? OR body LIKE ?)
                   ORDER BY updated_at DESC""",
                (path_id, search_query, search_query),
            )

            threads = []
            for row in cursor.fetchall():
                comment_count = self._count_thread_comments(row[0])
                threads.append(
                    {
                        "id": row[0],
                        "path_id": row[1],
                        "user_id": row[2],
                        "title": row[3],
                        "preview": row[4][:150] + "..." if len(row[4]) > 150 else row[4],
                        "created_at": row[5],
                        "updated_at": row[6],
                        "comment_count": comment_count,
                    }
                )

            return threads
        except Exception as e:
            print(f"Error searching threads: {e}")
            return []
