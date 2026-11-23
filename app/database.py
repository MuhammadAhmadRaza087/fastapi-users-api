import os
from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.config import DATABASE_URL

_is_sqlite = DATABASE_URL.startswith("sqlite")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
)


def init_db() -> None:
    """Create the SQLite folder (if needed) and all tables."""
    if DATABASE_URL.startswith("sqlite:///"):
        folder = os.path.dirname(DATABASE_URL.removeprefix("sqlite:///"))
        if folder:
            os.makedirs(folder, exist_ok=True)

    from app import models  # noqa: F401  (registers tables on the metadata)

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
