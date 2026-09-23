from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    AdaptiveTeachingActionModel,
    ArtifactModel,
    ConceptDiagnosisModel,
    HistoricalEvidenceModel,
    KnowledgeDiagnosisModel,
    KnowledgeStateModel,
    LearningGoalModel,
    LearningInteractionModel,
    LearningMessageModel,
    LearningPreferenceModel,
    LearningProgressModel,
    LearningProfileModel,
    LearningSessionModel,
    StudentModel,
)


def _json_load(value: str | None, default):
    if not value:
        return default

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default


def _json_dump(value) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
    )


class ALOFRepository:

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Student
    # ------------------------------------------------------------------

    def get_student(self, student_id: str) -> StudentModel | None:
        return self.db.get(StudentModel, student_id)

    def get_profile(self, student_id: str):
        return self.db.scalar(
            select(LearningProfileModel).where(
                LearningProfileModel.student_id == student_id
            )
        )

    def get_preference(self, student_id: str):
        return self.db.scalar(
            select(LearningPreferenceModel).where(
                LearningPreferenceModel.student_id == student_id
            )
        )

    def get_progress(self, student_id: str):
        return self.db.scalar(
            select(LearningProgressModel).where(
                LearningProgressModel.student_id == student_id
            )
        )

    # ------------------------------------------------------------------
    # Goal
    # ------------------------------------------------------------------

    def get_goal(self, student_id: str):
        return self.db.scalar(
            select(LearningGoalModel)
            .where(
                LearningGoalModel.student_id == student_id
            )
            .order_by(
                LearningGoalModel.created_at.desc()
            )
        )

    # ------------------------------------------------------------------
    # Knowledge
    # ------------------------------------------------------------------

    def get_knowledge_states(self, student_id: str):
        return list(
            self.db.scalars(
                select(KnowledgeStateModel)
                .where(
                    KnowledgeStateModel.learner_id == student_id
                )
                .order_by(
                    KnowledgeStateModel.concept_id
                )
            )
        )

    def get_concept_diagnoses(self, student_id: str):
        return list(
            self.db.scalars(
                select(ConceptDiagnosisModel)
                .where(
                    ConceptDiagnosisModel.learner_id == student_id
                )
                .order_by(
                    ConceptDiagnosisModel.concept_id
                )
            )
        )

    def get_diagnosis(self, student_id: str):
        return self.db.scalar(
            select(KnowledgeDiagnosisModel)
            .where(
                KnowledgeDiagnosisModel.learner_id == student_id
            )
            .order_by(
                KnowledgeDiagnosisModel.id.desc()
            )
        )

    # ------------------------------------------------------------------
    # Learning evidence
    # ------------------------------------------------------------------

    def get_evidence(self, student_id: str):
        return self.db.scalar(
            select(HistoricalEvidenceModel)
            .where(
                HistoricalEvidenceModel.learner_id == student_id
            )
            .order_by(
                HistoricalEvidenceModel.id.desc()
            )
        )

    def get_interactions(self, student_id: str):
        return list(
            self.db.scalars(
                select(LearningInteractionModel)
                .where(
                    LearningInteractionModel.learner_id == student_id
                )
                .order_by(
                    LearningInteractionModel.timestamp.desc()
                )
            )
        )

    # ------------------------------------------------------------------
    # Adaptive teaching
    # ------------------------------------------------------------------

    def get_teaching_action(self, student_id: str):
        return self.db.scalar(
            select(AdaptiveTeachingActionModel)
            .where(
                AdaptiveTeachingActionModel.learner_id == student_id
            )
            .order_by(
                AdaptiveTeachingActionModel.id.desc()
            )
        )

    # ------------------------------------------------------------------
    # Artifacts
    # ------------------------------------------------------------------

    def get_artifacts(self, student_id: str):
        """
        Current schema does not yet contain an explicit student_id/session_id
        relation on ArtifactModel.

        For the current demo database, artifacts are therefore returned
        separately. The explicit Artifact -> LearningSession relation will
        be added when session persistence is wired into the runtime.
        """
        return list(
            self.db.scalars(
                select(ArtifactModel)
                .order_by(
                    ArtifactModel.created_at.desc()
                )
            )
        )

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    def get_sessions(self, student_id: str):
        return list(
            self.db.scalars(
                select(LearningSessionModel)
                .where(
                    LearningSessionModel.student_id == student_id
                )
                .order_by(
                    LearningSessionModel.created_at.desc()
                )
            )
        )

    def get_latest_session(self, student_id: str):
        return self.db.scalar(
            select(LearningSessionModel)
            .where(
                LearningSessionModel.student_id == student_id
            )
            .order_by(
                LearningSessionModel.created_at.desc()
            )
        )

    def get_session(
        self,
        student_id: str,
        session_id: str,
    ):
        return self.db.scalar(
            select(LearningSessionModel)
            .where(
                LearningSessionModel.id == session_id,
                LearningSessionModel.student_id == student_id,
            )
        )

    # ------------------------------------------------------------------
    # Session messages
    # ------------------------------------------------------------------

    def get_session_messages(self, session_id: str):
        return list(
            self.db.scalars(
                select(LearningMessageModel)
                .where(
                    LearningMessageModel.session_id == session_id
                )
                .order_by(
                    LearningMessageModel.created_at.asc()
                )
            )
        )

    def create_message(
        self,
        session_id: str,
        message_id: str,
        role: str,
        content: str,
        created_at: datetime,
    ):
        message = LearningMessageModel(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            created_at=created_at,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    # ------------------------------------------------------------------
    # Preferences
    # ------------------------------------------------------------------

    def update_preference(
        self,
        student_id: str,
        data: dict,
    ):
        preference = self.get_preference(student_id)

        if preference is None:
            preference = LearningPreferenceModel(
                student_id=student_id,
            )
            self.db.add(preference)

        preference.preferred_outputs = _json_dump(
            data.get("preferred_outputs", [])
        )

        preference.preferred_difficulty = data.get(
            "preferred_difficulty",
            "adaptive",
        )

        preference.preferred_pace = data.get(
            "preferred_pace",
            "adaptive",
        )

        preference.session_duration_minutes = data.get(
            "session_duration_minutes",
            30,
        )

        preference.include_examples = data.get(
            "include_examples",
            True,
        )

        preference.include_quiz = data.get(
            "include_quiz",
            True,
        )

        preference.include_flashcards = data.get(
            "include_flashcards",
            True,
        )

        preference.include_summary = data.get(
            "include_summary",
            True,
        )

        self.db.commit()
        self.db.refresh(preference)

        return preference

    # ------------------------------------------------------------------
    # Create session
    # ------------------------------------------------------------------


    def create_session(
        self,
        student_id: str,
        session_id: str,
        request: str,
        created_at: datetime,
    ):
        session = LearningSessionModel(
            id=session_id,
            student_id=student_id,
            request=request,
            created_at=created_at,
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

