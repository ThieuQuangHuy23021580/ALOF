from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import select

from .database import SessionLocal, init_db
from .models import (
    AdaptiveTeachingActionModel,
    ArtifactModel,
    HistoricalEvidenceModel,
    KnowledgeDiagnosisModel,
    KnowledgeStateModel,
    LearningGoalModel,
    LearningInteractionModel,
    LearningPreferenceModel,
    LearningProgressModel,
    LearningProfileModel,
    LearningSessionModel,
    StudentModel,
)


STUDENT_ID = "student-demo"


def seed_demo() -> None:
    init_db()

    db = SessionLocal()

    try:
        existing = db.get(StudentModel, STUDENT_ID)

        if existing is not None:
            print("student-demo already exists.")
            return

        now = datetime.now(timezone.utc)

        student = StudentModel(
            id=STUDENT_ID,
            display_name="Huy",
            created_at=now,
            updated_at=now,
        )

        profile = LearningProfileModel(
            student_id=STUDENT_ID,
            current_level="intermediate",
            target_level="advanced",
            interests=json.dumps(
                ["programming", "computer science"],
                ensure_ascii=False,
            ),
            strengths=json.dumps(
                ["problem solving"],
                ensure_ascii=False,
            ),
            weaknesses=json.dumps(
                ["recursion"],
                ensure_ascii=False,
            ),
            preferred_language="vi",
        )

        preference = LearningPreferenceModel(
            student_id=STUDENT_ID,
            preferred_outputs=json.dumps(
                ["lesson", "summary", "quiz"],
                ensure_ascii=False,
            ),
            preferred_difficulty="adaptive",
            preferred_pace="adaptive",
            session_duration_minutes=30,
            include_examples=True,
            include_quiz=True,
            include_flashcards=True,
            include_summary=True,
        )

        progress = LearningProgressModel(
            student_id=STUDENT_ID,
            completed_topics=0,
            completed_sessions=0,
            mastered_topics=0,
            current_streak=0,
            total_learning_minutes=0,
            overall_mastery=0.42,
        )

        goal = LearningGoalModel(
            id="goal-demo",
            student_id=STUDENT_ID,
            knowledge_node_id="recursion",
            target_level="advanced",
            status="in_progress",
            created_at=now,
        )

        knowledge_state = KnowledgeStateModel(
            learner_id=STUDENT_ID,
            concept_id="recursion",
            mastery=0.42,
            level="intermediate",
            attempts=5,
            correct_attempts=2,
            error_rate=0.60,
            recent_accuracy=0.40,
            last_interaction_at=now,
            metadata_json="{}",
        )

        interaction = LearningInteractionModel(
            id="interaction-demo-1",
            learner_id=STUDENT_ID,
            question_id="question-demo-1",
            question="What is the base case in recursion?",
            answer="The condition that stops recursive calls.",
            correct=True,
            concept_ids=json.dumps(["recursion"]),
            timestamp=now,
            metadata_json="{}",
        )

        diagnosis = KnowledgeDiagnosisModel(
            learner_id=STUDENT_ID,
            current_question="Explain recursion and its base case.",
            primary_concepts=json.dumps(["recursion"]),
            weak_concepts=json.dumps(["recursion"]),
            transfer_deficit_concepts=json.dumps([]),
            metadata_json=json.dumps(
                {"source": "seed"},
                ensure_ascii=False,
            ),
        )

        evidence = HistoricalEvidenceModel(
            learner_id=STUDENT_ID,
            current_question="Explain recursion and its base case.",
            relevant_interactions=json.dumps(
                ["interaction-demo-1"]
            ),
            recent_interactions=json.dumps(
                ["interaction-demo-1"]
            ),
            related_interactions=json.dumps([]),
            related_concept_ids=json.dumps(["recursion"]),
            metadata_json="{}",
            created_at=now,
        )

        teaching_action = AdaptiveTeachingActionModel(
            learner_id=STUDENT_ID,
            action="explain",
            strategy="guided_explanation",
            difficulty="beginner",
            focus_concepts=json.dumps(["recursion"]),
            reason="The learner shows weakness in recursion.",
            metadata_json="{}",
        )

        artifact = ArtifactModel(
            id="artifact-demo-1",
            type="lesson",
            title="Recursion & Frame Invariants",
            content=(
                "A recursive function solves a problem by reducing "
                "it to smaller instances of the same problem."
            ),
            producer="mentor",
            summary="Introduction to recursion and base cases.",
            metadata_json="{}",
            created_at=now,
        )

        session = LearningSessionModel(
            id="session-demo-1",
            student_id=STUDENT_ID,
            request="Explain recursion and its base case.",
            created_at=now,
        )

        db.add_all(
            [
                student,
                profile,
                preference,
                progress,
                goal,
                knowledge_state,
                interaction,
                diagnosis,
                evidence,
                teaching_action,
                artifact,
                session,
            ]
        )

        db.commit()

        print("Seed completed: student-demo")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo()