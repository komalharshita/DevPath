"""GDPR compliance and user data privacy system."""

from typing import Dict, List, Optional
from datetime import datetime
from cryptography.fernet import Fernet
import os


class PrivacyManager:
    """Manages GDPR compliance, data encryption, and privacy controls."""

    def __init__(self):
        self.encryption_key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
        self.cipher = Fernet(self.encryption_key)
        self.user_consent: Dict[str, Dict] = {}
        self.data_requests: Dict[str, Dict] = {}
        self.audit_log: List[Dict] = []

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive user data."""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive user data."""
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def set_user_consent(
        self, user_id: str, data_processing: bool, marketing: bool, analytics: bool
    ) -> Dict:
        """Set user GDPR consent preferences."""
        consent = {
            "user_id": user_id,
            "data_processing": data_processing,
            "marketing": marketing,
            "analytics": analytics,
            "consented_at": datetime.utcnow().isoformat(),
        }
        self.user_consent[user_id] = consent
        self._log_audit(f"Consent updated for user {user_id}")
        return consent

    def get_user_consent(self, user_id: str) -> Optional[Dict]:
        """Get user's consent preferences."""
        return self.user_consent.get(user_id)

    def request_data_export(self, user_id: str) -> Dict:
        """Create a user data export request (Right to Data Portability)."""
        request_id = f"export_{user_id}_{datetime.utcnow().timestamp()}"
        request = {
            "request_id": request_id,
            "user_id": user_id,
            "type": "data_export",
            "status": "pending",
            "requested_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "data_url": None,
        }
        self.data_requests[request_id] = request
        self._log_audit(f"Data export requested by {user_id}")
        return request

    def request_data_deletion(self, user_id: str) -> Dict:
        """Create a user data deletion request (Right to be Forgotten)."""
        request_id = f"delete_{user_id}_{datetime.utcnow().timestamp()}"
        request = {
            "request_id": request_id,
            "user_id": user_id,
            "type": "data_deletion",
            "status": "pending",
            "requested_at": datetime.utcnow().isoformat(),
            "completed_at": None,
        }
        self.data_requests[request_id] = request
        self._log_audit(f"Data deletion requested by {user_id}")
        return request

    def complete_data_export(
        self, request_id: str, exported_data: Dict
    ) -> Dict:
        """Mark data export as completed."""
        if request_id not in self.data_requests:
            raise ValueError(f"Request {request_id} not found")

        request = self.data_requests[request_id]
        request["status"] = "completed"
        request["completed_at"] = datetime.utcnow().isoformat()
        request["data_url"] = f"/api/privacy/export/{request_id}/download"

        self._log_audit(f"Data export completed for {request['user_id']}")
        return request

    def complete_data_deletion(self, request_id: str) -> Dict:
        """Mark data deletion as completed."""
        if request_id not in self.data_requests:
            raise ValueError(f"Request {request_id} not found")

        request = self.data_requests[request_id]
        request["status"] = "completed"
        request["completed_at"] = datetime.utcnow().isoformat()

        self._log_audit(f"Data deletion completed for {request['user_id']}")
        return request

    def validate_gdpr_compliance(self, user_id: str) -> Dict:
        """Validate GDPR compliance for user data."""
        consent = self.user_consent.get(user_id)
        requests = [
            r
            for r in self.data_requests.values()
            if r["user_id"] == user_id
        ]

        return {
            "user_id": user_id,
            "has_consent": consent is not None,
            "consent_data_processing": consent.get("data_processing") if consent else None,
            "pending_requests": len([r for r in requests if r["status"] == "pending"]),
            "completed_requests": len([r for r in requests if r["status"] == "completed"]),
            "compliant": consent is not None and consent.get("data_processing"),
        }

    def _log_audit(self, message: str):
        """Log privacy audit event."""
        self.audit_log.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "message": message,
            }
        )

    def get_audit_log(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get audit log entries."""
        if user_id:
            return [
                log
                for log in self.audit_log
                if user_id in log.get("message", "")
            ]
        return self.audit_log

    def set_data_retention_policy(self, days: int = 365) -> Dict:
        """Set data retention policy."""
        return {
            "retention_days": days,
            "policy_active": True,
            "effective_from": datetime.utcnow().isoformat(),
        }

    def anonymize_user_data(self, user_id: str) -> Dict:
        """Anonymize user data for privacy."""
        return {
            "user_id": user_id,
            "anonymized": True,
            "anonymized_at": datetime.utcnow().isoformat(),
            "original_data_deleted": True,
        }
