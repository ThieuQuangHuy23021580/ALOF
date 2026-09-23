from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.domain.artifact.artifact import Artifact
from backend.domain.artifact.artifact_type import ArtifactType
from backend.domain.goal.learning_goal import LearningGoal
from backend.domain.learning.adaptive_teaching_action import (
    AdaptiveTeachingAction,
    TeachingActionType,
    TeachingStrategy,
)
from backend.domain.knowledge.knowledge_level import KnowledgeLevel
from backend.domain.knowledge.knowledge_state import KnowledgeState
from backend.domain.learning.historical_evidence import HistoricalEvidence
from backend.domain.learning.knowledge_diagnosis import KnowledgeDiagnosis
from backend.domain.learning.learning_interaction import LearningInteraction
from backend.domain.student.learning_preference import LearningPreference
from backend.domain.student.learning_progress import LearningProgress
from backend.domain.student.profile import LearningProfile
from backend.domain.student.student import Student


DEFAULT_STUDENT_ID = "student-demo"


class ApiStore:
    """
    Temporary API data source.

    Later this class can be replaced by repositories/database
    without changing the Flutter API contract.
    """

    def __init__(self) -> None:
        self.students: dict[str, Student] = {}
        self.goals: dict[str, LearningGoal] = {}
        self.knowledge_states: dict[str, list[KnowledgeState]] = {}
        self.interactions: dict[str, list[LearningInteraction]] = {}
        self.artifacts: dict[str, list[Artifact]] = {}
        self.sessions: dict[str, list[dict]] = {}

        self._seed()

    def _seed(self) -> None:
        student = Student(
            id=DEFAULT_STUDENT_ID,
            display_name="Huy",
            learning_profile=LearningProfile(
                current_level="intermediate",
                target_level="advanced",
                interests=["Programming", "Software Architecture"],
                strengths=["Problem solving"],
                weaknesses=["Recursion"],
                preferred_language="vi",
            ),
            learning_preference=LearningPreference(
                preferred_outputs=["lesson", "summary"],
                preferred_difficulty="adaptive",
                preferred_pace="adaptive",
            ),
            learning_progress=LearningProgress(
                completed_topics=4,
                completed_sessions=7,
                mastered_topics=3,
                current_streak=4,
                total_learning_minutes=185,
                overall_mastery=0.68,
            ),
        )

        self.students[student.id] = student

        goal = LearningGoal(
            id="goal-demo",
            student_id=student.id,
            knowledge_node_id="recursion",
            target_level="advanced",
        )

        self.goals[goal.id] = goal

        state = KnowledgeState(
            concept_id="recursion",
            mastery=0.42,
            level=KnowledgeLevel.INTERMEDIATE,
            attempts=8,
            correct_attempts=4,
            error_rate=0.5,
            recent_accuracy=0.5,
        )

        self.knowledge_states[student.id] = [state]

        interaction = LearningInteraction(
            id=str(uuid4()),
            learner_id=student.id,
            question_id="q-recursion-001",
            question="What is the base case in recursion?",
            answer="It stops the recursive calls.",
            correct=True,
            concept_ids=["recursion"],
            timestamp=datetime.now(UTC),
        )

        self.interactions[student.id] = [interaction]

        evidence = HistoricalEvidence(
            learner_id=student.id,
            current_question="Explain recursion and its base case.",
            relevant_interactions=[interaction],
            recent_interactions=[interaction],
            related_interactions=[],
            related_concept_ids=["recursion"],
        )

        diagnosis = KnowledgeDiagnosis(
            learner_id=student.id,
            current_question=evidence.current_question,
            primary_concepts=["recursion"],
            weak_concepts=["recursion"],
            concepts={
                "recursion": {
                    "concept_id": "recursion",
                    "mastery": 0.42,
                    "level": KnowledgeLevel.INTERMEDIATE,
                    "attempts": 8,
                    "correct_attempts": 4,
                    "accuracy": 0.5,
                    "error_rate": 0.5,
                    "evidence_count": 1,
                    "has_recent_evidence": True,
                    "has_relevant_evidence": True,
                    "weakness_signal": True,
                    "transfer_deficit_signal": False,
                }
            },
        )

        action = AdaptiveTeachingAction(
            action=TeachingActionType.EXPLAIN,
            strategy=TeachingStrategy.GUIDED_EXPLANATION,
            difficulty="beginner",
            focus_concepts=["recursion"],
            reason="The learner shows a weakness signal on recursion.",
        )

        artifact = Artifact(
            id="artifact-demo",
            type=ArtifactType.LESSON,
            title="Recursion & Frame Invariants",
            content=(
                "A recursive function solves a problem by reducing it "
                "to smaller instances of the same problem."
            ),
            producer="mentor",
            summary="Introduction to recursion and base cases.",
        )

        self.artifacts[student.id] = [artifact]

        self.sessions[student.id] = [
            {
                "id": "session-demo",
                "topic": "Recursion & Frame Invariants",
                "focus": "Base Case Anatomy",
                "activity": "Guided Explanation",
                "status": "in_progress",
            }
        ]

        self._diagnosis = {student.id: diagnosis}
        self._evidence = {student.id: evidence}
        self._actions = {student.id: action}

    def get_student(self, student_id: str) -> Student | None:
        return self.students.get(student_id)

    def get_goal(self, student_id: str) -> LearningGoal | None:
        return next(
            (
                goal
                for goal in self.goals.values()
                if goal.student_id == student_id
            ),
            None,
        )

    def get_diagnosis(
        self,
        student_id: str,
    ) -> KnowledgeDiagnosis | None:
        return self._diagnosis.get(student_id)

    def get_evidence(
        self,
        student_id: str,
    ) -> HistoricalEvidence | None:
        return self._evidence.get(student_id)

    def get_action(
        self,
        student_id: str,
    ) -> AdaptiveTeachingAction | None:
        return self._actions.get(student_id)

    def get_artifacts(
        self,
        student_id: str,
    ) -> list[Artifact]:
        return self.artifacts.get(student_id, [])

    def get_sessions(
        self,
        student_id: str,
    ) -> list[dict]:
        return self.sessions.get(student_id, [])