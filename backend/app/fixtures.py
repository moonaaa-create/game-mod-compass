"""오프라인 fixture 데이터 생성.

배포/개발 환경에 Roblox·CurseForge API 접근이 없을 때도 앱이 동작하도록,
스펙에서 정한 규모(로블록스 94개, 마인크래프트 100개)의 그럴듯한 fixture를
결정론적으로 생성한다. 실제 API 키가 있으면 backend/app/seed.py가
이 fixture 대신 실 API 데이터를 사용한다.
"""
import random

ROBLOX_GENRES = [
    "Adventure",
    "RPG",
    "Simulation",
    "Horror",
    "Obby and Platformer",
    "Fighting",
    "Sports and Racing",
    "Town and City",
    "Comedy",
    "FPS",
]

ROBLOX_NAME_PARTS = [
    "Tycoon",
    "Simulator",
    "Story",
    "Adventures",
    "Roleplay",
    "Rush",
    "Legends",
    "Blox",
    "Escape",
    "Battle",
    "World",
    "Life",
    "Quest",
    "Arena",
    "Islands",
]

MC_CATEGORIES = ["technology", "magic", "adventure_rpg", "map_information"]
MC_LOADERS = ["forge", "fabric", "quilt", "neoforge"]

MC_NAME_PARTS = {
    "technology": ["Tech", "Industrial", "Mekanism", "Circuit", "Automation", "Machine"],
    "magic": ["Arcane", "Mystic", "Thaumaturgy", "Spellbound", "Enchant", "Wizardry"],
    "adventure_rpg": ["Quest", "Odyssey", "Dungeon", "Chronicles", "Saga", "Realms"],
    "map_information": ["Atlas", "Waystones", "Journeymap", "Compass", "Cartograph", "Minimap"],
}


def generate_roblox_games(count: int = 94, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    games = []
    for i in range(count):
        genre = rng.choice(ROBLOX_GENRES)
        name = f"{rng.choice(MC_NAME_PARTS.get('adventure_rpg', ['Game']))} {rng.choice(ROBLOX_NAME_PARTS)} {i + 1}"
        universe_id = 1_000_000 + i
        playing = rng.randint(50, 250_000)
        visits = playing * rng.randint(50, 500)
        favorited = int(visits * rng.uniform(0.01, 0.08))
        games.append(
            {
                "universe_id": universe_id,
                "name": name,
                "description": f"{genre} 장르의 인기 로블록스 게임입니다.",
                "genre": genre,
                "playing": playing,
                "visits": visits,
                "favorited_count": favorited,
                "max_players": rng.choice([4, 6, 8, 12, 20, 30, 50, 100]),
                "thumbnail_url": f"https://picsum.photos/seed/roblox{universe_id}/150/150",
            }
        )
    return games


def generate_minecraft_mods(count: int = 100, seed: int = 7) -> list[dict]:
    rng = random.Random(seed)
    mods = []
    for i in range(count):
        categories = rng.sample(MC_CATEGORIES, k=rng.choice([1, 1, 2]))
        primary_category = categories[0]
        loaders = rng.sample(MC_LOADERS, k=rng.choice([1, 2, 2, 3]))
        name_part = rng.choice(MC_NAME_PARTS[primary_category])
        curseforge_mod_id = 200_000 + i
        name = f"{name_part} {i + 1}"
        mods.append(
            {
                "curseforge_mod_id": curseforge_mod_id,
                "name": name,
                "slug": name.lower().replace(" ", "-"),
                "summary": f"{primary_category.replace('_', ' ').title()} 카테고리의 인기 마인크래프트 모드입니다.",
                "download_count": rng.randint(10_000, 50_000_000),
                "logo_url": f"https://picsum.photos/seed/mc{curseforge_mod_id}/150/150",
                "categories": categories,
                "loaders": loaders,
            }
        )
    return mods
