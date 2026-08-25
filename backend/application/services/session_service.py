from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.db.models.learning import LearningSession
from backend.db.repositories.session_repository import SessionRepository


class SessionService:

    def __init__(self, db: Session):
        self.repository = SessionRepository(db)

    def create(
        self,
        user_id: str,
        title: str,
        goal_id: str | None = None,
    ) -> LearningSession:

        now = datetime.now(UTC).isoformat()

        session = LearningSession(
            user_id=user_id,
            goal_id=goal_id,
            title=title,
            summary=None,
            created_at=now,
            updated_at=now,
        )

        return self.repository.create(session)

    def get(
        self,
        session_id: str,
    ) -> LearningSession | None:

        return self.repository.get(session_id)

    def list_user_sessions(
        self,
        user_id: str,
    ) -> list[LearningSession]:

        return self.repository.list_by_user(user_id)

    def rename(
        self,
        session_id: str,
        title: str,
    ) -> LearningSession | None:

        session = self.repository.get(session_id)

        if session is None:
            return None

        session.title = title
        session.updated_at = datetime.now(UTC).isoformat()

        return self.repository.update(session)

    def update_summary(
        self,
        session_id: str,
        summary: str,
    ) -> LearningSession | None:

        session = self.repository.get(session_id)

        if session is None:
            return None

        session.summary = summary
        session.updated_at = datetime.now(UTC).isoformat()

        return self.repository.update(session)

    def delete(
        self,
        session_id: str,
    ) -> bool:

        session = self.repository.get(session_id)

        if session is None:
            return False

        self.repository.delete(session)

        return True