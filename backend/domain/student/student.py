from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.domain.student.learning_preference import LearningPreference
from backend.domain.student.learning_progress import LearningProgress
from backend.domain.student.profile import LearningProfile
from pydantic import BaseModel, Field


class Student(BaseModel):
    """
    Aggregate Root representing a learner.

    Student contains only learning-related information.
    Authentication and authorization belong to the
    Infrastructure layer.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
    )

    display_name: str

    learning_profile: LearningProfile = Field(
        default_factory=LearningProfile,
        )

    learning_preference: LearningPreference = Field(
         default_factory=LearningPreference,
        )

    learning_progress: LearningProgress = Field(
        default_factory=LearningProgress,
        )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    def touch(
        self,
    ) -> None:
        """
        Update the modification timestamp.
        """

        self.updated_at = datetime.now(
            UTC,
        )