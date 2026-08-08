"""Roblox 공식 API 연동 (docs/research/roblox-api.md 참고).

인증 불필요. 94개 인기 게임의 universe ID 목록을 정적으로 관리하고,
배치로 games/thumbnails 엔드포인트를 호출해 메타데이터를 채운다.
"""
from typing import Any

import httpx

GAMES_ENDPOINT = "https://games.roblox.com/v1/games"
THUMBNAILS_ENDPOINT = "https://thumbnails.roblox.com/v1/games/icons"


async def fetch_games(universe_ids: list[int]) -> list[dict[str, Any]]:
    """주어진 universe_id 목록에 대한 게임 메타데이터를 조회한다."""
    results: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=10) as client:
        for i in range(0, len(universe_ids), 100):
            chunk = universe_ids[i : i + 100]
            ids_param = ",".join(str(x) for x in chunk)
            resp = await client.get(GAMES_ENDPOINT, params={"universeIds": ids_param})
            resp.raise_for_status()
            results.extend(resp.json().get("data", []))
    return results


async def fetch_thumbnails(universe_ids: list[int]) -> dict[int, str]:
    """universe_id -> 썸네일 URL 매핑을 조회한다."""
    thumbs: dict[int, str] = {}
    async with httpx.AsyncClient(timeout=10) as client:
        for i in range(0, len(universe_ids), 100):
            chunk = universe_ids[i : i + 100]
            ids_param = ",".join(str(x) for x in chunk)
            resp = await client.get(
                THUMBNAILS_ENDPOINT,
                params={"universeIds": ids_param, "size": "150x150", "format": "Png"},
            )
            resp.raise_for_status()
            for item in resp.json().get("data", []):
                if item.get("imageUrl"):
                    thumbs[item["targetId"]] = item["imageUrl"]
    return thumbs
