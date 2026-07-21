"""Certificate generation utility for completed learning paths.

Generates downloadable PDF certificates with UUID verification codes
when users complete all topics in a learning path.
"""

import uuid
from datetime import datetime
from typing import Dict, Optional, Tuple


class CertificateGenerator:
    """Generates and manages completion certificates."""

    def __init__(self, db=None):
        """Initialize certificate generator with database connection.

        Args:
            db: Database connection for storing verification codes
        """
        self.db = db

    def generate_verification_code(self) -> str:
        """Generate a unique UUID verification code for a certificate.

        Returns:
            UUID string for certificate verification
        """
        return str(uuid.uuid4())

    def create_certificate_metadata(
        self, user_name: str, path_name: str, path_id: int
    ) -> Dict:
        """Create certificate metadata for PDF generation.

        Args:
            user_name: Name of the learner
            path_name: Name of the completed learning path
            path_id: ID of the learning path

        Returns:
            Dictionary with certificate metadata
        """
        verification_code = self.generate_verification_code()
        completion_date = datetime.now().strftime("%B %d, %Y")

        return {
            "learner_name": user_name,
            "path_name": path_name,
            "path_id": path_id,
            "completion_date": completion_date,
            "verification_code": verification_code,
            "generated_at": datetime.now().isoformat(),
        }

    def store_certificate_record(
        self, user_id: int, path_id: int, verification_code: str
    ) -> bool:
        """Store certificate record in database for verification.

        Args:
            user_id: ID of the user who completed the path
            path_id: ID of the learning path
            verification_code: UUID verification code

        Returns:
            True if stored successfully, False otherwise
        """
        if not self.db:
            return False

        try:
            # Insert certificate record
            # Note: Assumes certificates table exists with columns:
            # id, user_id, path_id, verification_code, completion_date, created_at
            self.db.execute(
                """INSERT INTO certificates
                   (user_id, path_id, verification_code, completion_date)
                   VALUES (?, ?, ?, ?)""",
                (user_id, path_id, verification_code, datetime.now()),
            )
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error storing certificate record: {e}")
            return False

    def verify_certificate(self, verification_code: str) -> Optional[Dict]:
        """Verify a certificate using its verification code.

        Args:
            verification_code: UUID code to verify

        Returns:
            Certificate details if valid, None if invalid or not found
        """
        if not self.db:
            return None

        try:
            cursor = self.db.execute(
                """SELECT user_id, path_id, completion_date
                   FROM certificates WHERE verification_code = ?""",
                (verification_code,),
            )
            result = cursor.fetchone()

            if result:
                return {
                    "user_id": result[0],
                    "path_id": result[1],
                    "completion_date": result[2],
                    "valid": True,
                }
            return None
        except Exception as e:
            print(f"Error verifying certificate: {e}")
            return None

    def get_certificate_by_path(
        self, user_id: int, path_id: int
    ) -> Optional[Dict]:
        """Retrieve certificate for a user's completed path.

        Args:
            user_id: ID of the user
            path_id: ID of the learning path

        Returns:
            Certificate metadata if exists, None otherwise
        """
        if not self.db:
            return None

        try:
            cursor = self.db.execute(
                """SELECT verification_code, completion_date
                   FROM certificates
                   WHERE user_id = ? AND path_id = ?""",
                (user_id, path_id),
            )
            result = cursor.fetchone()

            if result:
                return {
                    "verification_code": result[0],
                    "completion_date": result[1],
                }
            return None
        except Exception as e:
            print(f"Error retrieving certificate: {e}")
            return None

    def all_topics_completed(
        self, user_id: int, path_id: int, user_progress: Dict
    ) -> bool:
        """Check if user has completed all topics in a path.

        Args:
            user_id: ID of the user
            path_id: ID of the learning path
            user_progress: Dictionary tracking user progress

        Returns:
            True if all topics are completed, False otherwise
        """
        path_key = f"path_{path_id}"

        if path_key not in user_progress:
            return False

        completed_topics = user_progress[path_key].get("completed_topics", [])

        # This would require knowing total topics in the path
        # Simplified check: if progress indicates completion
        return user_progress[path_key].get("completed", False)
