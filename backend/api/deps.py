from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.application.orchestration.orchestrator_factory import (
    create_learning_orchestrator,
)
from backend.application.services.learning_service import (
    LearningService,
)
from backend.application.services.session_service import (
    SessionService,
)
from backend.application.services.user_service import (
    UserService,
)
from backend.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_learning_service() -> LearningService:
    return LearningService(
        orchestrator=create_learning_orchestrator(),
    )


def get_user_service(
    db: Session = Depends(get_db),
) -> UserService:
    return UserService(db)


def get_session_service(
    db: Session = Depends(get_db),
) -> SessionService:
    return SessionService(db)