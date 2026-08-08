"""SQLite 엔진 및 세션 설정."""
import os
from pathlib import Path
from typing import Iterator

from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine

DATA_DIR = Path(os.getenv("DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "app.db"

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[DBSession]:
    # expire_on_commit=False: 커밋 후에도 이미 조회한 ORM 객체를 그대로 직렬화할 수 있게 유지.
    with DBSession(engine, expire_on_commit=False) as session:
        yield session
