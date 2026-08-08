"""게임/모드 목록 조회 엔드포인트."""
from fastapi import APIRouter, Depends
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_session
from app.models import MinecraftMod, ModCategory, ModLoader, RobloxGame

router = APIRouter(prefix="/api/games", tags=["games"])


@router.get("/roblox")
def list_roblox_games(db: DBSession = Depends(get_session)):
    games = db.exec(select(RobloxGame).order_by(RobloxGame.playing.desc())).all()
    return games


@router.get("/minecraft")
def list_minecraft_mods(db: DBSession = Depends(get_session)):
    mods = db.exec(select(MinecraftMod).order_by(MinecraftMod.download_count.desc())).all()
    result = []
    for mod in mods:
        categories = db.exec(
            select(ModCategory.category).where(ModCategory.mod_id == mod.id)
        ).all()
        loaders = db.exec(select(ModLoader.loader).where(ModLoader.mod_id == mod.id)).all()
        item = mod.model_dump()
        item["categories"] = categories
        item["loaders"] = loaders
        result.append(item)
    return result
