"""CurseForge API 연동 (docs/research/curseforge-api.md 참고).

인증: `x-api-key` 헤더 (console.curseforge.com 발급).
gameId=432 (Minecraft), classId=6 (Mods).
API 키가 없으면 호출하지 않고 상위 호출부에서 fixture 데이터로 대체한다.
"""
import os
from typing import Any

import httpx

SEARCH_ENDPOINT = "https://api.curseforge.com/v1/mods/search"
MINECRAFT_GAME_ID = 432
MODS_CLASS_ID = 6

# 4개 채택 카테고리 (docs/spec.md 섹션 4-2). 실제 categoryId는 배포 전
# `GET /v1/categories?gameId=432&classId=6`로 조회해 채워야 한다 (#6 결정사항).
TARGET_CATEGORIES = ["technology", "magic", "adventure_rpg", "map_information"]


def has_api_key() -> bool:
    return bool(os.getenv("CURSEFORGE_API_KEY"))


async def fetch_mods_by_category(category_id: int, page_size: int = 50) -> list[dict[str, Any]]:
    """카테고리 하나에 대해 다운로드 수 기준 상위 모드를 조회한다."""
    api_key = os.getenv("CURSEFORGE_API_KEY")
    if not api_key:
        return []
    headers = {"x-api-key": api_key, "Accept": "application/json"}
    params = {
        "gameId": MINECRAFT_GAME_ID,
        "classId": MODS_CLASS_ID,
        "categoryId": category_id,
        "sortField": 6,  # totalDownloads
        "sortOrder": "desc",
        "pageSize": page_size,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(SEARCH_ENDPOINT, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json().get("data", [])
