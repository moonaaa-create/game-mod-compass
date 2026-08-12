import os
import time
from urllib.parse import quote
import httpx
from fastapi import APIRouter, Request, Response, Depends
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_session
from app.models import MinecraftMod, RobloxGame

load_dotenv()

# APIM Foundry 프록시 설정 (사내 발급 키, 우선순위 높음)
APIM_BASE_URL = os.environ.get("APIM_BASE_URL", "").rstrip("/")
APIM_KEY = os.environ.get("APIM_KEY")
CHAT_MODEL = os.environ.get("CHAT_MODEL", "gpt-3.5-turbo")

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 메모리 기반 대화 기록 저장소 (세션별)
CHAT_HISTORY = {}
MAX_HISTORY_TURNS = 12  # system 제외, 최근 N개 메시지만 유지 (컨텍스트 폭주 방지)

# 카탈로그 요약 캐시 (DB 조회 비용 절감용, 5분 TTL)
_catalog_cache = {"text": None, "ts": 0}
CATALOG_TTL_SECONDS = 300


async def fetch_roblox_root_place_ids(universe_ids: list[int]) -> dict[int, int]:
    """Roblox 공개 API로 universe_id -> rootPlaceId 매핑을 조회.
    (실패해도 전체 요청이 죽지 않도록 예외를 삼키고 빈 dict를 반환)"""
    if not universe_ids:
        return {}
    try:
        ids_param = ",".join(str(u) for u in universe_ids)
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://games.roblox.com/v1/games",
                params={"universeIds": ids_param},
            )
            resp.raise_for_status()
            data = resp.json().get("data", [])
            return {
                item["id"]: item["rootPlaceId"]
                for item in data
                if item.get("id") and item.get("rootPlaceId")
            }
    except Exception:
        return {}


async def build_catalog_context(db: DBSession) -> str:
    now = time.time()
    if _catalog_cache["text"] and now - _catalog_cache["ts"] < CATALOG_TTL_SECONDS:
        return _catalog_cache["text"]

    top_mods = db.exec(
        select(MinecraftMod).order_by(MinecraftMod.download_count.desc()).limit(20)
    ).all()
    top_games = db.exec(
        select(RobloxGame).order_by(RobloxGame.playing.desc()).limit(20)
    ).all()

    root_place_ids = await fetch_roblox_root_place_ids([g.universe_id for g in top_games])

    mod_lines = [
        f"- {m.name} | 다운로드 {m.download_count:,}회 | 요약: {m.summary or '정보 없음'} "
        f"| 링크: https://www.curseforge.com/minecraft/mc-mods?search={quote(m.name)}"
        for m in top_mods
    ]

    def roblox_link(g: RobloxGame) -> str:
        place_id = root_place_ids.get(g.universe_id)
        if place_id:
            # 실제 게임 상세 페이지로 바로 이동하는 정확한 링크
            return f"https://www.roblox.com/games/{place_id}/{quote(g.name.replace(' ', '-'))}"
        # rootPlaceId를 못 찾은 경우에만 검색 결과 페이지로 폴백
        return f"https://www.roblox.com/discover/?Keyword={quote(g.name)}"

    game_lines = [
        f"- {g.name} | 장르: {g.genre} | 동시 접속 {g.playing:,}명 "
        f"| 링크: {roblox_link(g)}"
        for g in top_games
    ]

    text = (
        "[실시간 인기 마인크래프트 모드 TOP 20]\n" + "\n".join(mod_lines) +
        "\n\n[실시간 인기 로블록스 게임 TOP 20]\n" + "\n".join(game_lines)
    )
    _catalog_cache["text"] = text
    _catalog_cache["ts"] = now
    return text


def build_system_prompt(catalog_context: str) -> str:
    return f"""너는 '유스AI프로젝트 2기 2조'가 만든 'Mod Compass' 웹사이트에 내장된 게임/모드 추천 AI 가이드야.

역할과 대화 방식:
1. 사용자가 평소 하는 게임, 관심사, 취미 등을 말하면 그 내용을 바탕으로 마인크래프트 모드나 로블록스 게임을
   맞춤 추천해줘. 아직 정보가 부족하면 짧게 되물어서 취향(장르, 난이도, 혼자/같이, PC 사양 등)을 파악해.
2. 정해진 틀에 박힌 답을 반복하지 말고, 사용자의 이전 발언과 취향을 기억해서 자연스럽게 이어지는 대화를 해.
3. 추천할 때는 아래 실시간 카탈로그 데이터를 우선 참고해서 실제로 사이트에 있는 항목 위주로 추천하고,
   카탈로그에 없는 유명한 것도 필요하면 보조적으로 언급해도 돼.
4. 추천하는 모드/게임에는 카탈로그에 있는 "링크:" 뒤의 URL을 그대로 함께 걸어줘.
   마크다운 링크 문법 [이름](URL) 형태로 자연스럽게 문장 안에 넣어. 없는 URL은 절대 지어내지 마.
5. 매번 같은 형식/같은 목록을 복붙하지 말고, 직전 대화 맥락에 맞춰 답변 내용과 추천 항목을 다르게 구성해.
6. 말투는 사용자를 그대로 따라가: 사용자가 반말로 물으면 편하고 친근한 반말로, 존댓말로 물으면 정중한
   존댓말로 답해. 첫 메시지처럼 아직 말투를 모를 땐 존댓말로 시작해.
7. **텍스트** 같은 마크다운 굵게 표시는 절대 쓰지 마. 별표(*) 없이 순수 텍스트로만 답해.
8. 답변은 최대한 짧고 간결하게, 2~4줄 이내로 핵심만 전달해. 추천은 보통 1~3개만 콕 집어서 제시하고,
   장황한 설명이나 긴 목록은 피해. 답변이 중간에 끊기지 않도록 항상 완결된 문장으로 마무리해.

{catalog_context}
"""

class ChatIn(BaseModel):
    message: str

@router.post("")
async def chat(
    payload: ChatIn,
    request: Request,
    response: Response,
    db: DBSession = Depends(get_session),
):
    # 쿠키 기반 세션 ID (간단히 구현)
    session_id = request.cookies.get("chat_session")
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        response.set_cookie(
            "chat_session",
            session_id,
            samesite="none",
            secure=True,
        )

    catalog_context = await build_catalog_context(db)
    system_prompt = {"role": "system", "content": build_system_prompt(catalog_context)}

    history = CHAT_HISTORY.setdefault(session_id, [system_prompt])
    # 카탈로그가 갱신됐을 수 있으니 system 프롬프트는 항상 최신으로 갱신
    history[0] = system_prompt

    user_msg = payload.message.strip()
    history.append({"role": "user", "content": user_msg})

    # 컨텍스트 폭주 방지: system + 최근 N개 메시지만 유지
    if len(history) > MAX_HISTORY_TURNS + 1:
        history[:] = [history[0]] + history[-MAX_HISTORY_TURNS:]

    # APIM Foundry 프록시가 설정돼 있으면 우선 사용, 없으면 일반 OpenAI API로 폴백
    if APIM_BASE_URL and APIM_KEY:
        client = AsyncOpenAI(
            api_key="placeholder",
            base_url=f"{APIM_BASE_URL}/{CHAT_MODEL}/",
            default_headers={"api-key": APIM_KEY},
        )
        model = CHAT_MODEL
    else:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {"reply": "서버에 APIM_KEY 또는 OPENAI_API_KEY가 설정되지 않았습니다."}
        client = AsyncOpenAI(api_key=api_key)
        model = "gpt-3.5-turbo"

    try:
        completion = await client.chat.completions.create(
            model=model,
            messages=history,
            max_completion_tokens=320,
            temperature=0.9
        )
        reply = completion.choices[0].message.content
        # 모델이 지시를 무시하고 마크다운 굵게 표시(**)를 붙이는 경우를 대비한 안전장치
        reply = reply.replace("**", "")
        finish_reason = completion.choices[0].finish_reason
        # 토큰 제한으로 문장이 중간에 끊긴 경우, 어색하게 잘리지 않도록 자연스럽게 마무리
        if finish_reason == "length" and reply and reply[-1] not in ".!?…\n":
            reply = reply.rstrip() + "…"
        history.append({"role": "assistant", "content": reply})

        return {"reply": reply}
    except Exception as e:
        return {"reply": f"에러가 발생했습니다: {str(e)}"}


@router.post("/reset")
async def reset_chat(request: Request, response: Response):
    """세션의 대화 기록을 서버 메모리에서 초기화."""
    session_id = request.cookies.get("chat_session")
    if session_id and session_id in CHAT_HISTORY:
        del CHAT_HISTORY[session_id]
    return {"status": "reset"}
