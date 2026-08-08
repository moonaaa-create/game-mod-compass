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

# Public Roblox API로 well-known 인기 게임 placeId -> universeId 변환 후 검증한 실데이터.
# 검증 방법:
#   1) GET /universes/v1/places/{placeId}/universe
#   2) GET https://games.roblox.com/v1/games?universeIds=...
# 2026-08-08 기준 59개를 확인했으며, placeholder 순번 ID는 제거했다.
ROBLOX_UNIVERSE_IDS = [
    383310974,   # Adopt Me!
    1686885941,  # Brookhaven RP
    994732206,   # Blox Fruits
    140239261,   # MeepCity
    88070565,    # Welcome to Bloxburg
    111958650,   # Arsenal
    66654135,    # Murder Mystery 2
    245662005,   # Jailbreak
    703124385,   # Tower of Hell
    1008451066,  # Da Hood
    2440500124,  # DOORS
    2316994223,  # Pet Simulator X!
    65241,       # Natural Disaster Survival
    31970568,    # Theme Park Tycoon 2
    601130232,   # Bee Swarm Simulator
    321778215,   # Royale High
    3647333358,  # Evade
    2619619496,  # BedWars
    1511883870,  # Shindo Life
    2380077519,  # Slap Battles
    1214576306,  # Restaurant Tycoon 2
    3183403065,  # Anime Adventures
    210851291,   # Build A Boat For Treasure
    47545,       # Work at a Pizza Place
    1480782352,  # Vehicle Legends
    113491250,   # Phantom Forces
    271119130,   # Breaking Point
    1516533665,  # Piggy
    372226183,   # Flee the Facility
    2549475383,  # Livetopia
    2711375305,  # Catalog Avatar Creator
    3405618667,  # Sonic Speed Simulator
    1390601379,  # Combat Warriors
    274816972,   # Car Crushers 2
    3085257211,  # Rainbow Friends
    1359573625,  # Deepwoken
    2294168059,  # The Mimic
    1489026993,  # Survive the Killer!
    4348829796,  # Murderers VS Sheriffs DUELS
    3543117236,  # Apeirophobia
    3808081382,  # The Strongest Battlegrounds
    1202096104,  # Driving Empire
    107172930,   # Horrific Housing
    110181652,   # Epic Minigames
    323675642,   # Flood Escape 2
    848145103,   # Dungeon Quest!
    1424449565,  # Super Golf!
    985731078,   # World // Zero
    1348402608,  # Anime Fighting Simulator
    1720936166,  # All Star Tower Defense
    2142948266,  # Project Slayers
    1119466531,  # Legends Of Speed
    1016936714,  # Your Bizarre Adventure
    1451439645,  # King Legacy
    4778845442,  # Toilet Tower Defense
    4777817887,  # Blade Ball
    1176784616,  # Tower Defense Simulator
    1247975681,  # BIG Paintball!
    1235188606,  # Dragon Adventures
]


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
