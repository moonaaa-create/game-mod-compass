"""SQLModel 데이터 모델 정의 (docs/spec.md 섹션 6 기준)."""
from typing import Optional

from sqlmodel import Field, SQLModel


class RobloxGame(SQLModel, table=True):
    __tablename__ = "roblox_games"

    id: Optional[int] = Field(default=None, primary_key=True)
    universe_id: int = Field(unique=True, index=True)
    name: str
    description: Optional[str] = None
    genre: str = Field(index=True)
    playing: Optional[int] = None
    visits: Optional[int] = None
    favorited_count: Optional[int] = None
    max_players: Optional[int] = None
    thumbnail_url: Optional[str] = None
    updated_at: str


class MinecraftMod(SQLModel, table=True):
    __tablename__ = "minecraft_mods"

    id: Optional[int] = Field(default=None, primary_key=True)
    curseforge_mod_id: int = Field(unique=True, index=True)
    name: str
    slug: Optional[str] = None
    summary: Optional[str] = None
    download_count: Optional[int] = None
    logo_url: Optional[str] = None
    updated_at: str


class ModCategory(SQLModel, table=True):
    __tablename__ = "mod_categories"

    mod_id: int = Field(foreign_key="minecraft_mods.id", primary_key=True)
    category: str = Field(primary_key=True)


class ModLoader(SQLModel, table=True):
    __tablename__ = "mod_loaders"

    mod_id: int = Field(foreign_key="minecraft_mods.id", primary_key=True)
    loader: str = Field(primary_key=True)


class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: str = Field(primary_key=True)
    created_at: str
    last_seen_at: str


class SurveyResponse(SQLModel, table=True):
    __tablename__ = "survey_responses"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="sessions.id")
    game_type: str
    answers: str  # JSON text
    created_at: str


class Recommendation(SQLModel, table=True):
    __tablename__ = "recommendations"

    id: Optional[int] = Field(default=None, primary_key=True)
    survey_response_id: int = Field(foreign_key="survey_responses.id")
    game_type: str
    item_id: int
    rank: int
    created_at: str
