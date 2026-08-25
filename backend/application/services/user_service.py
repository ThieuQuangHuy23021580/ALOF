from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.db.models.user import User
from backend.db.repositories.user_repository import UserRepository


class UserService:

    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def get_user(
        self,
        user_id: str,
    ) -> User | None:

        return self.users.get(user_id)

    def get_user_by_email(
        self,
        email: str,
    ) -> User | None:

        return self.users.get_by_email(email)

    def create_user(
        self,
        email: str,
        password_hash: str,
        display_name: str,
    ) -> User:

        if self.users.get_by_email(email) is not None:
            raise ValueError("Email already exists.")

        user = User(
            email=email,
            password_hash=password_hash,
            display_name=display_name,
            role="student",
            created_at=datetime.now(UTC).isoformat(),
        )

        return self.users.create(user)

    def update_display_name(
        self,
        user_id: str,
        display_name: str,
    ) -> User:

        user = self.users.get(user_id)

        if user is None:
            raise ValueError("User not found.")

        user.display_name = display_name
        user.updated_at = datetime.now(UTC).isoformat()

        return self.users.update(user)

    def delete_user(
        self,
        user_id: str,
    ) -> None:

        user = self.users.get(user_id)

        if user is None:
            raise ValueError("User not found.")

        self.users.delete(user)