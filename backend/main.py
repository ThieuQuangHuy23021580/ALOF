from backend.infrastructure.api.app import app
from backend.infrastructure.database import init_db


init_db()


__all__ = ["app"]