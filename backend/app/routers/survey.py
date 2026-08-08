"""설문 제출 → 추천 매칭 엔드포인트 (docs/spec.md 섹션 5 로직)."""
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_session
from app.models import (
    MinecraftMod,
    ModCategory,
    Recommendation,
    RobloxGame,
    SurveyResponse,
)
from app.session import get_or_create_session

router = APIRouter(prefix="/api/survey", tags=["survey"])

ROBLOX_PLAYER_SIZE_RANGES = {
    "large": (20, 10_000),  # 대규모/멀티플레이 지향
    "small": (1, 8),  # 소규모/캐주얼
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RobloxSurveyIn(BaseModel):
    genres: list[str]
    player_size: str  # "large" | "small"


class MinecraftSurveyIn(BaseModel):
    categories: list[str]


def _roblox_popularity_score(game: RobloxGame) -> float:
    return (game.playing or 0) * 3 + (game.visits or 0) * 0.001 + (game.favorited_count or 0) * 0.5


@router.post("/roblox")
def submit_roblox_survey(
    payload: RobloxSurveyIn,
    request: Request,
    response: Response,
    db: DBSession = Depends(get_session),
):
    if not payload.genres:
        raise HTTPException(400, "최소 1개 이상의 장르를 선택해야 합니다.")

    session_id = get_or_create_session(request, response, db)

    candidates = db.exec(
        select(RobloxGame).where(RobloxGame.genre.in_(payload.genres))
    ).all()

    lo, hi = ROBLOX_PLAYER_SIZE_RANGES.get(payload.player_size, (0, 10_000))

    def sort_key(g: RobloxGame):
        in_range = 0 if (g.max_players and lo <= g.max_players <= hi) else 1
        return (-_roblox_popularity_score(g), in_range)

    ranked = sorted(candidates, key=sort_key)[:5]

    survey = SurveyResponse(
        session_id=session_id,
        game_type="roblox",
        answers=json.dumps(payload.model_dump(), ensure_ascii=False),
        created_at=_now(),
    )
    db.add(survey)
    db.commit()
    db.refresh(survey)

    now = _now()
    result = [g.model_dump() for g in ranked]  # commit 전에 직렬화 (expire_on_commit 대비)
    for rank, game in enumerate(ranked, start=1):
        db.add(
            Recommendation(
                survey_response_id=survey.id,
                game_type="roblox",
                item_id=game.id,
                rank=rank,
                created_at=now,
            )
        )
    db.commit()

    return {"survey_response_id": survey.id, "recommendations": result}


@router.post("/minecraft")
def submit_minecraft_survey(
    payload: MinecraftSurveyIn,
    request: Request,
    response: Response,
    db: DBSession = Depends(get_session),
):
    if not payload.categories:
        raise HTTPException(400, "최소 1개 이상의 카테고리를 선택해야 합니다.")

    session_id = get_or_create_session(request, response, db)

    mod_ids = db.exec(
        select(ModCategory.mod_id).where(ModCategory.category.in_(payload.categories))
    ).all()
    mod_ids = list(set(mod_ids))

    if not mod_ids:
        candidates: list[MinecraftMod] = []
    else:
        candidates = db.exec(
            select(MinecraftMod)
            .where(MinecraftMod.id.in_(mod_ids))
            .order_by(MinecraftMod.download_count.desc())
        ).all()

    ranked = candidates[:5]

    survey = SurveyResponse(
        session_id=session_id,
        game_type="minecraft",
        answers=json.dumps(payload.model_dump(), ensure_ascii=False),
        created_at=_now(),
    )
    db.add(survey)
    db.commit()
    db.refresh(survey)

    now = _now()
    result = []
    for rank, mod in enumerate(ranked, start=1):
        db.add(
            Recommendation(
                survey_response_id=survey.id,
                game_type="minecraft",
                item_id=mod.id,
                rank=rank,
                created_at=now,
            )
        )
        item = mod.model_dump()
        item["categories"] = db.exec(
            select(ModCategory.category).where(ModCategory.mod_id == mod.id)
        ).all()
        result.append(item)
    db.commit()

    return {"survey_response_id": survey.id, "recommendations": result}
