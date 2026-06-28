"""Learning outcome assessment and certification system."""

from typing import Dict, List, Optional
from datetime import datetime
import hashlib


class CertificationManager:
    """Manages skill assessments and certificate issuance."""

    def __init__(self):
        self.assessments: Dict[str, Dict] = {}
        self.certificates: Dict[str, Dict] = {}
        self.digital_badges: Dict[str, Dict] = {}

    def create_assessment(
        self,
        assessment_id: str,
        user_id: str,
        skill: str,
        difficulty: str,
        questions: List[Dict],
    ) -> Dict:
        """Create a skill assessment."""
        assessment = {
            "assessment_id": assessment_id,
            "user_id": user_id,
            "skill": skill,
            "difficulty": difficulty,
            "questions": questions,
            "created_at": datetime.utcnow().isoformat(),
            "score": None,
            "passed": False,
            "completed_at": None,
        }
        self.assessments[assessment_id] = assessment
        return assessment

    def submit_assessment(
        self, assessment_id: str, answers: Dict[str, str]
    ) -> Dict:
        """Submit assessment answers and calculate score."""
        if assessment_id not in self.assessments:
            raise ValueError(f"Assessment {assessment_id} not found")

        assessment = self.assessments[assessment_id]
        score = self._calculate_score(assessment["questions"], answers)

        assessment["score"] = score
        assessment["passed"] = score >= 70
        assessment["completed_at"] = datetime.utcnow().isoformat()

        if assessment["passed"]:
            self._issue_certificate(assessment)

        return assessment

    def _calculate_score(self, questions: List[Dict], answers: Dict) -> float:
        """Calculate assessment score."""
        if not questions:
            return 0

        correct = 0
        for question in questions:
            qid = question.get("id")
            if qid in answers and answers[qid] == question.get("correct_answer"):
                correct += 1

        return (correct / len(questions)) * 100

    def _issue_certificate(self, assessment: Dict):
        """Issue certificate upon passing assessment."""
        cert_id = f"cert_{assessment['assessment_id']}"
        cert = {
            "certificate_id": cert_id,
            "user_id": assessment["user_id"],
            "skill": assessment["skill"],
            "difficulty": assessment["difficulty"],
            "score": assessment["score"],
            "issued_at": datetime.utcnow().isoformat(),
            "valid_until": None,
            "verification_code": self._generate_verification_code(cert_id),
        }
        self.certificates[cert_id] = cert
        return cert

    def _generate_verification_code(self, cert_id: str) -> str:
        """Generate unique verification code."""
        data = f"{cert_id}{datetime.utcnow().isoformat()}".encode()
        return hashlib.sha256(data).hexdigest()[:16]

    def issue_digital_badge(self, user_id: str, skill: str, level: str) -> Dict:
        """Issue digital badge for skill completion."""
        badge_id = f"badge_{user_id}_{skill}_{level}"
        badge = {
            "badge_id": badge_id,
            "user_id": user_id,
            "skill": skill,
            "level": level,
            "issued_at": datetime.utcnow().isoformat(),
            "icon_url": f"/badges/{skill.lower()}_{level.lower()}.png",
            "description": f"{level} {skill} Badge",
        }
        self.digital_badges[badge_id] = badge
        return badge

    def get_user_certificates(self, user_id: str) -> List[Dict]:
        """Get all certificates for a user."""
        return [c for c in self.certificates.values() if c["user_id"] == user_id]

    def get_user_badges(self, user_id: str) -> List[Dict]:
        """Get all badges earned by user."""
        return [b for b in self.digital_badges.values() if b["user_id"] == user_id]

    def verify_certificate(self, cert_id: str, verification_code: str) -> bool:
        """Verify certificate authenticity."""
        if cert_id not in self.certificates:
            return False
        return self.certificates[cert_id]["verification_code"] == verification_code

    def get_certification_status(self, user_id: str) -> Dict:
        """Get user's overall certification status."""
        certs = self.get_user_certificates(user_id)
        badges = self.get_user_badges(user_id)

        return {
            "user_id": user_id,
            "total_certificates": len(certs),
            "total_badges": len(badges),
            "certified_skills": [c["skill"] for c in certs],
            "badges_earned": [b["skill"] for b in badges],
        }

    def generate_credential_pdf(self, cert_id: str) -> Dict:
        """Generate downloadable credential PDF."""
        if cert_id not in self.certificates:
            raise ValueError(f"Certificate {cert_id} not found")

        cert = self.certificates[cert_id]
        return {
            "certificate_id": cert_id,
            "user_id": cert["user_id"],
            "skill": cert["skill"],
            "difficulty": cert["difficulty"],
            "issued_at": cert["issued_at"],
            "verification_code": cert["verification_code"],
            "pdf_url": f"/certificates/{cert_id}.pdf",
        }
