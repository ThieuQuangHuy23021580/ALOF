
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class StudentModel(Base):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    profile: Mapped["LearningProfileModel | None"] = relationship(
        back_populates="student",
        uselist=False,
        cascade="all, delete-orphan",
    )

    preference: Mapped["LearningPreferenceModel | None"] = relationship(
        back_populates="student",
        uselist=False,
        cascade="all, delete-orphan",
    )

    progress: Mapped["LearningProgressModel | None"] = relationship(
        back_populates="student",
        uselist=False,
        cascade="all, delete-orphan",
    )

    goals: Mapped[list["LearningGoalModel"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )


class LearningProfileModel(Base):
    __tablename__ = "learning_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    student_id: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
        unique=True,
    )

    current_level: Mapped[str] = mapped_column(
        String(50),
        default="",
        nullable=False,
    )

    target_level: Mapped[str] = mapped_column(
        String(50),
        default="",
        nullable=False,
    )

    interests: Mapped[str] = mapped_column(
        Text,
        default="[]",
        nullable=False,
    )

    strengths: Mapped[str] = mapped_column(
        Text,
        default="[]",
        nullable=False,
    )

    weaknesses: Mapped[str] = mapped_column(
        Text,
        default="[]",
        nullable=False,
    )

    preferred_language: Mapped[str] = mapped_column(
        String(20),
        default="vi",
        nullable=False,
    )

    student: Mapped["StudentModel"] = relationship(
        back_populates="profile",
    )


class LearningPreferenceModel(Base):
    __tablename__ = "learning_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    student_id: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
        unique=True,
    )

    preferred_outputs: Mapped[str] = mapped_column(
        Text,
        default="[]",
        nullable=False,
    )

    preferred_difficulty: Mapped[str] = mapped_column(
        String(50),
        default="adaptive",
        nullable=False,
    )

    preferred_pace: Mapped[str] = mapped_column(
        String(50),
        default="adaptive",
        nullable=False,
    )

    session_duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
    )

    include_examples: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    include_quiz: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    include_flashcards: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    include_summary: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    student: Mapped["StudentModel"] = relationship(
        back_populates="preference",
    )


class LearningProgressModel(Base):
    __tablename__ = "learning_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    student_id: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
        unique=True,
    )

    completed_topics: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    completed_sessions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    mastered_topics: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    total_learning_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    overall_mastery: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    student: Mapped["StudentModel"] = relationship(
        back_populates="progress",
    )


class LearningGoalModel(Base):
    __tablename__ = "learning_goals"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)

    student_id: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
    )

    knowledge_node_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    target_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="not_started",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    student: Mapped["StudentModel"] = relationship(
        back_populates="goals",
    )


class KnowledgeStateModel(Base):
    __tablename__ = "knowledge_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    learner_id: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
    )

    concept_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    mastery: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    level: Mapped[str] = mapped_column(
        String(50),
        default="beginner",
        nullable=False,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    correct_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    error_rate: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    recent_accuracy: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    last_interaction_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    metadata_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "learner_id",
            "concept_id",
            name="uq_knowledge_state_learner_concept",
        ),
    )


class LearningInteractionModel(Base):
    __tablename__ = "learning_interactions"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    learner_id: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
    )

    question_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    question: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )

    answer: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )

    correct: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    concept_ids: Mapped[str] = mapped_column(
        Text,
        default="[]",
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    metadata_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
        nullable=False,
    )


class ArtifactModel(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        default="",
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    producer: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )

    metadata_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )


class LearningSessionModel(Base):
    __tablename__ = "learning_sessions"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    student_id: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
    )

    request: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    messages: Mapped[list["LearningMessageModel"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="LearningMessageModel.created_at",
    )


class LearningMessageModel(Base):
    __tablename__ = "learning_messages"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey("learning_sessions.id"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    session: Mapped["LearningSessionModel"] = relationship(
        back_populates="messages",
    )


class ConceptDiagnosisModel(Base):
    __tablename__ = "concept_diagnoses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    learner_id: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
    )

    concept_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    mastery: Mapped[float] = mapped_column(Float, default=0.0)
    level: Mapped[str] = mapped_column(String(50), default="beginner")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct_attempts: Mapped[int] = mapped_column(Integer, default=0)
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    error_rate: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)

    has_recent_evidence: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    has_relevant_evidence: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    weakness_signal: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    transfer_deficit_signal: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "learner_id",
            "concept_id",
            name="uq_concept_diagnosis_learner_concept",
        ),
    )


class KnowledgeDiagnosisModel(Base):
    __tablename__ = "knowledge_diagnoses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    learner_id: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
    )

    current_question: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    primary_concepts: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )

    weak_concepts: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )

    transfer_deficit_concepts: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )

    metadata_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
    )


class HistoricalEvidenceModel(Base):
    __tablename__ = "historical_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    learner_id: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
    )

    current_question: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    relevant_interactions: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )

    recent_interactions: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )

    related_interactions: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )

    related_concept_ids: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )

    metadata_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )


class AdaptiveTeachingActionModel(Base):
    __tablename__ = "adaptive_teaching_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    learner_id: Mapped[str] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    strategy: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(50),
        default="medium",
    )

    focus_concepts: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )

    reason: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    metadata_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
    )

