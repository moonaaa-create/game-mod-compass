"""설문 제출 → 추천 매칭 엔드포인트 (docs/spec.md 섹션 5 로직)."""
import json
from datetime import datetime, timezone
from typing import Literal

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


def match_roblox_recommendations(
    db: DBSession,
    genres: list[str],
    player_size: Literal["large", "small"],
) -> list[dict]:
    candidates = db.exec(select(RobloxGame).where(RobloxGame.genre.in_(genres))).all()
    if not candidates:
        # Fallback if specific genre search yields empty: return top games overall
        candidates = db.exec(select(RobloxGame)).all()

    lo, hi = ROBLOX_PLAYER_SIZE_RANGES.get(player_size, (0, 10_000))

    def sort_key(game: RobloxGame):
        in_range = 0 if (game.max_players and lo <= game.max_players <= hi) else 1
        return (-_roblox_popularity_score(game), in_range)

    ranked = sorted(candidates, key=sort_key)[:5]
    result = []
    for game in ranked:
        item = game.model_dump()
        item["url"] = f"https://www.roblox.com/games/{game.universe_id}"
        playing_fmt = f"{game.playing:,}" if game.playing else "인기"
        size_text = "대규모 멀티" if player_size == "large" else "소규모/캐주얼"
        item["reason"] = f"{game.genre} 장르 대표 게임으로 동시 접속자 {playing_fmt}명 이상이 즐기는 {size_text} 플레이 추천작입니다."
        result.append(item)
    return result


def match_minecraft_recommendations(db: DBSession, categories: list[str]) -> list[dict]:
    from app.models import ModLoader

    mod_ids = db.exec(
        select(ModCategory.mod_id).where(ModCategory.category.in_(categories))
    ).all()
    mod_ids = list(set(mod_ids))

    if not mod_ids:
        candidates: list[MinecraftMod] = db.exec(
            select(MinecraftMod).order_by(MinecraftMod.download_count.desc())
        ).all()
    else:
        candidates = db.exec(
            select(MinecraftMod)
            .where(MinecraftMod.id.in_(mod_ids))
            .order_by(MinecraftMod.download_count.desc())
        ).all()

    ranked = candidates[:5]
    result = []
    for mod in ranked:
        item = mod.model_dump()
        cats = db.exec(
            select(ModCategory.category).where(ModCategory.mod_id == mod.id)
        ).all()
        loaders = db.exec(
            select(ModLoader.loader).where(ModLoader.mod_id == mod.id)
        ).all()
        item["categories"] = cats
        item["loaders"] = loaders if loaders else ["Forge"]
        slug = item.get("slug") or str(item["id"])
        item["url"] = f"https://www.curseforge.com/minecraft/mc-mods/{slug}"
        dl_fmt = f"{mod.download_count:,}" if mod.download_count else "1,000,000+"
        cat_str = ", ".join(cats) if cats else "인기"
        item["reason"] = f"{cat_str} 분야에서 누적 다운로드 {dl_fmt}회를 기록한 필수 모드입니다."
        result.append(item)
    return result


def save_survey_results(
    db: DBSession,
    *,
    session_id: str,
    game_type: Literal["roblox", "minecraft"],
    answers: dict,
    recommendations: list[dict],
) -> int:
    survey = SurveyResponse(
        session_id=session_id,
        game_type=game_type,
        answers=json.dumps(answers, ensure_ascii=False),
        created_at=_now(),
    )
    db.add(survey)
    db.commit()
    db.refresh(survey)

    now = _now()
    for rank, item in enumerate(recommendations, start=1):
        db.add(
            Recommendation(
                survey_response_id=survey.id,
                game_type=game_type,
                item_id=item["id"],
                rank=rank,
                created_at=now,
            )
        )
    db.commit()
    return survey.id


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
    recommendations = match_roblox_recommendations(db, payload.genres, payload.player_size)
    survey_id = save_survey_results(
        db,
        session_id=session_id,
        game_type="roblox",
        answers=payload.model_dump(),
        recommendations=recommendations,
    )
    return {"survey_response_id": survey_id, "recommendations": recommendations}


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
    recommendations = match_minecraft_recommendations(db, payload.categories)
    survey_id = save_survey_results(
        db,
        session_id=session_id,
        game_type="minecraft",
        answers=payload.model_dump(),
        recommendations=recommendations,
    )
    return {"survey_response_id": survey_id, "recommendations": recommendations}
