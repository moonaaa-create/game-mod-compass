import json
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

# 카탈로그 캐시 (DB/외부 API 조회 비용 절감용, 5분 TTL)
# text: 프롬프트에 넣을 요약 텍스트, items: 이름 -> 카드 렌더링용 실데이터 매핑
_catalog_cache = {"text": None, "items": {}, "ts": 0}
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


async def build_catalog(db: DBSession):
    """카탈로그를 조회해 (프롬프트용 텍스트, 이름->카드데이터 dict)를 캐시와 함께 반환."""
    now = time.time()
    if _catalog_cache["text"] and now - _catalog_cache["ts"] < CATALOG_TTL_SECONDS:
        return _catalog_cache["text"], _catalog_cache["items"]

    top_mods = db.exec(
        select(MinecraftMod).order_by(MinecraftMod.download_count.desc()).limit(20)
    ).all()
    top_games = db.exec(
        select(RobloxGame).order_by(RobloxGame.playing.desc()).limit(20)
    ).all()

    root_place_ids = await fetch_roblox_root_place_ids([g.universe_id for g in top_games])

    items: dict[str, dict] = {}

    mod_lines = []
    for m in top_mods:
        link = f"https://www.curseforge.com/minecraft/mc-mods?search={quote(m.name)}"
        mod_lines.append(
            f"- {m.name} | 다운로드 {m.download_count:,}회 | 요약: {m.summary or '정보 없음'} | 링크: {link}"
        )
        items[m.name] = {
            "type": "minecraft",
            "name": m.name,
            "image_url": m.logo_url,
            "link": link,
            "stat_label": "다운로드",
            "stat_value": f"{m.download_count:,}회" if m.download_count else "정보 없음",
            "summary": m.summary or "",
        }

    def roblox_link(g: RobloxGame) -> str:
        place_id = root_place_ids.get(g.universe_id)
        if place_id:
            return f"https://www.roblox.com/games/{place_id}/{quote(g.name.replace(' ', '-'))}"
        return f"https://www.roblox.com/discover/?Keyword={quote(g.name)}"

    game_lines = []
    for g in top_games:
        link = roblox_link(g)
        game_lines.append(
            f"- {g.name} | 장르: {g.genre} | 동시 접속 {g.playing:,}명 | 링크: {link}"
        )
        items[g.name] = {
            "type": "roblox",
            "name": g.name,
            "image_url": g.thumbnail_url,
            "link": link,
            "stat_label": "동시 접속",
            "stat_value": f"{g.playing:,}명" if g.playing else "정보 없음",
            "summary": g.genre or "",
        }

    text = (
        "[실시간 인기 마인크래프트 모드 TOP 20]\n" + "\n".join(mod_lines) +
        "\n\n[실시간 인기 로블록스 게임 TOP 20]\n" + "\n".join(game_lines)
    )
    _catalog_cache["text"] = text
    _catalog_cache["items"] = items
    _catalog_cache["ts"] = now
    return text, items


def build_system_prompt(catalog_context: str) -> str:
    return f"""너는 '유스AI프로젝트 2기 2조'가 만든 'Mod Compass' 웹사이트에 내장된 게임/모드 추천 AI 가이드야.

역할과 대화 방식:
1. 사용자가 평소 하는 게임, 관심사, 취미 등을 말하면 그 내용을 바탕으로 마인크래프트 모드나 로블록스 게임을
   맞춤 추천해줘. 아직 정보가 부족하면 짧게 되물어서 취향(장르, 난이도, 혼자/같이, PC 사양 등)을 파악해.
2. 정해진 틀에 박힌 답을 반복하지 말고, 사용자의 이전 발언과 취향을 기억해서 자연스럽게 이어지는 대화를 해.
3. 추천할 때는 아래 실시간 카탈로그 데이터를 우선 참고해서 실제로 사이트에 있는 항목 위주로 추천해.
   카탈로그의 정확한 이름(대소문자, 이모지, 띄어쓰기까지 원문 그대로)을 사용해야 카드가 정상 표시돼.
4. 말투는 사용자를 그대로 따라가: 사용자가 반말로 물으면 편하고 친근한 반말로, 존댓말로 물으면 정중한
   존댓말로 답해. 첫 메시지처럼 아직 말투를 모를 땐 존댓말로 시작해.
5. 답변은 최대한 짧고 간결하게 핵심만 전달해. 장황한 설명은 피하고, 문장은 항상 완결되게 마무리해.
6. 너는 마인크래프트 모드와 로블록스 게임 추천을 위한 챗봇이야. 이 주제와 관련 없는 질문
   (예: 숙제/코딩/일반 상식/시사/개인 고민 등)이 들어오면 답을 바로 해주지 말고,
   "그건 제 담당 주제는 아닌데, 그래도 답변해드릴까요?" 같은 식으로 먼저 되물어봐.
   사용자가 "응/네/그래/알려줘" 등 긍정으로 답할 때만 그 다음 답변부터 원래 질문에 대해 답해주고,
   답한 뒤에는 다시 마인크래프트/로블록스 이야기로 자연스럽게 돌아오도록 유도해.
   사용자가 부정하거나 다른 말을 하면 원래 주제(게임/모드 추천)로 바로 돌아가.

출력 형식 (반드시 지켜야 함):
아래 JSON 스키마 형태로만 응답해. 마크다운 코드블록(```) 없이 순수 JSON 텍스트만 출력해.
{{
  "message": "사용자에게 보여줄 짧은 대화체 문장 (1~2줄). 별표(*)나 마크다운 문법 쓰지 말 것.",
  "recommendations": [
    {{
      "name": "카탈로그에 있는 정확한 이름 (마인크래프트 모드 또는 로블록스 게임)",
      "reason": "이 항목을 추천하는 이유를 1문장으로, 사용자 취향과 연결해서 설명"
    }}
  ]
}}
- 실제로 모드/게임을 추천하는 답변일 때만 recommendations 배열을 채우고, 취향을 되묻거나 잡담/가드레일
  답변일 때는 recommendations를 빈 배열 []로 둬.
- recommendations는 0~3개까지만. 카탈로그에 없는 이름은 절대 넣지 마.

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

    catalog_context, catalog_items = await build_catalog(db)
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
            return {"reply": "서버에 APIM_KEY 또는 OPENAI_API_KEY가 설정되지 않았습니다.", "cards": []}
        client = AsyncOpenAI(api_key=api_key)
        model = "gpt-3.5-turbo"

    try:
        completion = await client.chat.completions.create(
            model=model,
            messages=history,
            max_completion_tokens=400,
            temperature=0.9,
            response_format={"type": "json_object"},
        )
        raw = completion.choices[0].message.content or "{}"

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # 혹시 모델이 JSON을 못 지켰을 때를 대비한 폴백: 원문을 그대로 메시지로 사용
            parsed = {"message": raw, "recommendations": []}

        reply_text = (parsed.get("message") or "").strip()
        # 안전장치: 혹시 남아있는 마크다운 굵게 표시 제거
        reply_text = reply_text.replace("**", "")

        cards = []
        for rec in parsed.get("recommendations", [])[:3]:
            name = (rec.get("name") or "").strip()
            item = catalog_items.get(name)
            if not item:
                continue  # 카탈로그에 없는(모델이 지어낸) 이름은 카드로 만들지 않음
            cards.append({
                "type": item["type"],
                "name": item["name"],
                "reason": (rec.get("reason") or "").strip(),
                "image_url": item["image_url"],
                "link": item["link"],
                "stat_label": item["stat_label"],
                "stat_value": item["stat_value"],
                "summary": item["summary"],
            })

        # 히스토리에는 원래 JSON 대신 사람이 읽기 쉬운 텍스트로 요약해 저장 (다음 턴 컨텍스트 절약)
        history_summary = reply_text
        if cards:
            history_summary += " (추천: " + ", ".join(c["name"] for c in cards) + ")"
        history.append({"role": "assistant", "content": history_summary})

        return {"reply": reply_text, "cards": cards}
    except Exception as e:
        return {"reply": f"에러가 발생했습니다: {str(e)}", "cards": []}


@router.post("/reset")
async def reset_chat(request: Request, response: Response):
    """세션의 대화 기록을 서버 메모리에서 초기화."""
    session_id = request.cookies.get("chat_session")
    if session_id and session_id in CHAT_HISTORY:
        del CHAT_HISTORY[session_id]
    return {"status": "reset"}
