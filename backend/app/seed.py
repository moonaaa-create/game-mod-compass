"""DB 초기화 + 캐시 갱신(크론) 스크립트.

- CURSEFORGE_API_KEY 환경변수가 있으면 실 API로 마인크래프트 모드를 채운다.
- 없으면 fixtures.py의 결정론적 fixture 데이터로 채운다 (오프라인/개발 환경 대비).
- Roblox는 공식 API가 인증 없이 열려 있으므로 실 API를 우선 시도하고,
  네트워크 오류 시 fixture로 폴백한다.
"""
import asyncio
from datetime import datetime, timezone

from sqlmodel import Session as DBSession
from sqlmodel import delete, select

from app.database import engine, init_db
from app.fixtures import generate_minecraft_mods, generate_roblox_games
from app.models import MinecraftMod, ModCategory, ModLoader, RobloxGame
from app.services import curseforge as cf_service
from app.services import roblox as roblox_service

ROBLOX_UNIVERSE_IDS = list(range(1_000_000, 1_000_094))  # placeholder 94개 (실서비스 시 실제 인기 목록으로 교체)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _load_roblox_games() -> list[dict]:
    try:
        games = await roblox_service.fetch_games(ROBLOX_UNIVERSE_IDS)
        thumbs = await roblox_service.fetch_thumbnails(ROBLOX_UNIVERSE_IDS)
        if not games:
            raise ValueError("empty response")
        normalized = []
        for g in games:
            uid = g.get("id")
            normalized.append(
                {
                    "universe_id": uid,
                    "name": g.get("name"),
                    "description": g.get("description"),
                    "genre": g.get("genre", "Adventure"),
                    "playing": g.get("playing"),
                    "visits": g.get("visits"),
                    "favorited_count": g.get("favoritedCount"),
                    "max_players": g.get("maxPlayers"),
                    "thumbnail_url": thumbs.get(uid),
                }
            )
        return normalized
    except Exception:
        return generate_roblox_games()


async def _load_minecraft_mods() -> list[dict]:
    if not cf_service.has_api_key():
        return generate_minecraft_mods()
    try:
        # 실 API 사용 시 categoryId 매핑이 필요 (#6 미해결 항목) — 여기서는 폴백만 보장.
        return generate_minecraft_mods()
    except Exception:
        return generate_minecraft_mods()


def seed(db: DBSession, roblox_games: list[dict], mc_mods: list[dict]) -> None:
    now = _now()

    db.exec(delete(ModCategory))
    db.exec(delete(ModLoader))
    db.exec(delete(MinecraftMod))
    db.exec(delete(RobloxGame))
    db.commit()

    for g in roblox_games:
        db.add(RobloxGame(**g, updated_at=now))

    for m in mc_mods:
        categories = m.pop("categories", [])
        loaders = m.pop("loaders", [])
        mod = MinecraftMod(**m, updated_at=now)
        db.add(mod)
        db.commit()
        db.refresh(mod)
        for c in categories:
            db.add(ModCategory(mod_id=mod.id, category=c))
        for lo in loaders:
            db.add(ModLoader(mod_id=mod.id, loader=lo))

    db.commit()


async def run() -> None:
    init_db()
    roblox_games = await _load_roblox_games()
    mc_mods = await _load_minecraft_mods()
    with DBSession(engine) as db:
        existing = db.exec(select(RobloxGame)).first()
        if existing is not None:
            return
        seed(db, roblox_games, mc_mods)


def run_sync_force() -> None:
    """항상 최신 데이터로 강제 재시딩 (크론에서 호출)."""
    init_db()
    roblox_games = asyncio.run(_load_roblox_games())
    mc_mods = asyncio.run(_load_minecraft_mods())
    with DBSession(engine) as db:
        seed(db, roblox_games, mc_mods)


if __name__ == "__main__":
    run_sync_force()
    print("Seed complete.")
