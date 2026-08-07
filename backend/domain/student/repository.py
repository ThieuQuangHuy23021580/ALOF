from __future__ import annotations

from abc import ABC, abstractmethod

from backend.domain.student.student import Student


class StudentRepository(ABC):
    """
    Domain repository for Student Aggregate.

    Infrastructure implementations (SQLite, PostgreSQL,
    MongoDB, etc.) must implement this contract.
    """

    @abstractmethod
    def add(
        self,
        student: Student,
    ) -> None:
        """
        Persist a new student.
        """
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        student_id: str,
    ) -> Student | None:
        """
        Retrieve a student by id.
        """
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
    ) -> list[Student]:
        """
        Retrieve all students.
        """
        raise NotImplementedError

    @abstractmethod
    def remove(
        self,
        student_id: str,
    ) -> None:
        """
        Remove a student.
        """
        raise NotImplementedError