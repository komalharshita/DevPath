"""Community and peer support system."""

from typing import Dict, List, Optional
from datetime import datetime


class CommunityManager:
    """Manages discussion forums, Q&A, and peer support."""

    def __init__(self):
        self.discussions: Dict[str, Dict] = {}
        self.questions: Dict[str, Dict] = {}
        self.study_groups: Dict[str, Dict] = {}
        self.user_reputation: Dict[str, int] = {}

    def create_discussion(
        self, discussion_id: str, user_id: str, course_id: int, title: str, content: str
    ) -> Dict:
        """Create a discussion thread."""
        discussion = {
            "discussion_id": discussion_id,
            "user_id": user_id,
            "course_id": course_id,
            "title": title,
            "content": content,
            "created_at": datetime.utcnow().isoformat(),
            "replies": [],
            "likes": 0,
        }
        self.discussions[discussion_id] = discussion
        self._add_reputation(user_id, 5)
        return discussion

    def reply_to_discussion(
        self, discussion_id: str, user_id: str, reply_content: str
    ) -> Dict:
        """Reply to a discussion thread."""
        if discussion_id not in self.discussions:
            raise ValueError(f"Discussion {discussion_id} not found")

        reply = {
            "reply_id": f"reply_{len(self.discussions[discussion_id]['replies'])}",
            "user_id": user_id,
            "content": reply_content,
            "created_at": datetime.utcnow().isoformat(),
            "likes": 0,
        }
        self.discussions[discussion_id]["replies"].append(reply)
        self._add_reputation(user_id, 3)
        return reply

    def ask_question(
        self,
        question_id: str,
        user_id: str,
        course_id: int,
        title: str,
        content: str,
        tags: List[str],
    ) -> Dict:
        """Post a Q&A question."""
        question = {
            "question_id": question_id,
            "user_id": user_id,
            "course_id": course_id,
            "title": title,
            "content": content,
            "tags": tags,
            "created_at": datetime.utcnow().isoformat(),
            "answers": [],
            "views": 0,
            "upvotes": 0,
        }
        self.questions[question_id] = question
        self._add_reputation(user_id, 10)
        return question

    def answer_question(
        self, question_id: str, user_id: str, answer_content: str
    ) -> Dict:
        """Answer a Q&A question."""
        if question_id not in self.questions:
            raise ValueError(f"Question {question_id} not found")

        answer = {
            "answer_id": f"answer_{len(self.questions[question_id]['answers'])}",
            "user_id": user_id,
            "content": answer_content,
            "created_at": datetime.utcnow().isoformat(),
            "upvotes": 0,
            "is_accepted": False,
        }
        self.questions[question_id]["answers"].append(answer)
        self._add_reputation(user_id, 15)
        return answer

    def create_study_group(
        self, group_id: str, creator_id: str, name: str, course_id: int
    ) -> Dict:
        """Create a study group."""
        group = {
            "group_id": group_id,
            "creator_id": creator_id,
            "name": name,
            "course_id": course_id,
            "members": [creator_id],
            "created_at": datetime.utcnow().isoformat(),
            "description": "",
            "schedule": None,
        }
        self.study_groups[group_id] = group
        self._add_reputation(creator_id, 20)
        return group

    def join_study_group(self, group_id: str, user_id: str) -> Dict:
        """Join a study group."""
        if group_id not in self.study_groups:
            raise ValueError(f"Group {group_id} not found")

        group = self.study_groups[group_id]
        if user_id not in group["members"]:
            group["members"].append(user_id)
            self._add_reputation(user_id, 5)

        return group

    def get_user_reputation(self, user_id: str) -> int:
        """Get user reputation score."""
        return self.user_reputation.get(user_id, 0)

    def get_user_contributions(self, user_id: str) -> Dict:
        """Get user's community contributions."""
        discussions = len([d for d in self.discussions.values() if d["user_id"] == user_id])
        questions = len([q for q in self.questions.values() if q["user_id"] == user_id])
        answers = 0
        for q in self.questions.values():
            answers += len([a for a in q["answers"] if a["user_id"] == user_id])

        return {
            "user_id": user_id,
            "reputation": self.get_user_reputation(user_id),
            "discussions_started": discussions,
            "questions_asked": questions,
            "answers_provided": answers,
            "total_contributions": discussions + questions + answers,
        }

    def _add_reputation(self, user_id: str, points: int):
        """Add reputation points to user."""
        self.user_reputation[user_id] = self.user_reputation.get(user_id, 0) + points

    def get_top_contributors(self, limit: int = 10) -> List[Dict]:
        """Get top community contributors."""
        sorted_users = sorted(
            self.user_reputation.items(), key=lambda x: x[1], reverse=True
        )
        return [
            {"user_id": uid, "reputation": rep} for uid, rep in sorted_users[:limit]
        ]
