"""자유 텍스트 기반 추천 챗 엔드포인트."""

import json
import os
import re
from typing import Literal, TypedDict, cast

import httpx
from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel
from sqlmodel import Session as DBSession

from app.database import get_session
from app.routers.survey import (
    match_minecraft_recommendations,
    match_roblox_recommendations,
    save_survey_results,
)
from app.session import get_or_create_session

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 프로세스 메모리에만 저장되므로 서버 재시작/멀티 워커 환경에서는 유지되지 않으며, 운영 환경에서는 DB 테이블로 옮겨야 한다.
CHAT_STATES: dict[str, "ChatState"] = {}

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
MINECRAFT_CATEGORIES = ["technology", "magic", "adventure_rpg", "map_information"]
GAME_KEYWORDS = {
    "roblox": ["로블록스", "roblox", "robux"],
    "minecraft": ["마인크래프트", "minecraft", "마크", "mc"],
}
ROBLOX_GENRE_KEYWORDS = {
    "Adventure": ["adventure", "어드벤처", "모험"],
    "RPG": ["rpg", "롤플레잉", "알피지"],
    "Simulation": ["simulation", "시뮬", "시뮬레이션"],
    "Horror": ["horror", "공포", "호러"],
    "Obby and Platformer": ["obby", "오비", "platform", "platformer", "플랫폼"],
    "Fighting": ["fighting", "격투", "대전"],
    "Sports and Racing": ["sports", "sport", "racing", "레이싱", "스포츠", "경주"],
    "Town and City": ["town", "city", "마을", "도시"],
    "Comedy": ["comedy", "코미디", "웃긴", "유머"],
    "FPS": ["fps", "슈팅", "총싸움", "총질", "사격"],
}
MINECRAFT_CATEGORY_KEYWORDS = {
    "technology": ["technology", "tech", "기술", "테크"],
    "magic": ["magic", "마법"],
    "adventure_rpg": ["adventure", "rpg", "모험", "알피지"],
    "map_information": ["map", "information", "info", "맵", "정보"],
}
PLAYER_SIZE_KEYWORDS = {
    "large": ["large", "많은", "대규모", "멀티", "여럿", "북적", "사람 많은"],
    "small": ["small", "소규모", "혼자", "캐주얼", "casual", "solo", "1인", "가볍게"],
}
PROMPTS = {
    "choose_game": [
        "로블록스와 마인크래프트 중 어떤 쪽을 추천받고 싶으세요?",
        "좋아요! 로블록스인지 마인크래프트인지 알려주시면 바로 이어서 도와드릴게요.",
        "원하시는 쪽을 말씀해 주세요. 로블록스 추천인지, 마인크래프트 모드 추천인지 궁금해요!",
    ],
    "roblox_genres": [
        "로블록스에서는 어떤 장르를 좋아하세요? 예를 들면 모험, 공포, 슈팅, 레이싱 같은 느낌이에요.",
        "취향을 조금만 더 알려주세요! 로블록스에서 선호하는 장르가 있을까요?",
        "좋아요, 그럼 로블록스 장르부터 볼게요. 모험/공포/시뮬레이션/FPS처럼 편하게 말씀해 주세요.",
    ],
    "roblox_player_size": [
        "좋아요! 이번에는 대규모 멀티플레이가 좋은지, 소규모/캐주얼 플레이가 좋은지 알려주세요.",
        "원하는 플레이 규모도 알려주세요. 사람 많은 멀티 쪽일까요, 아니면 소규모/혼자 즐기기 좋은 쪽일까요?",
        "장르는 파악했어요. 대규모로 북적이는 게임과 소규모로 가볍게 즐기는 게임 중 어느 쪽이 더 취향인가요?",
    ],
    "minecraft_categories": [
        "마인크래프트는 어떤 모드가 끌리세요? 기술, 마법, 모험/RPG, 맵/정보 중에서 말씀해 주세요.",
        "좋아요! 관심 있는 모드 성향을 알려주세요. 예를 들면 기술, 마법, 모험/RPG, 맵/정보예요.",
        "조금만 더 알려주시면 바로 추천해 드릴게요. 기술/마법/모험/RPG/맵/정보 중 어떤 쪽이 좋으세요?",
    ],
}


class ChatIn(BaseModel):
    message: str


class ChatState(TypedDict):
    stage: str
    game_type: Literal["roblox", "minecraft"] | None
    genres: list[str]
    categories: list[str]
    player_size: Literal["large", "small"] | None
    history: list[dict[str, str]]
    recommendations: list[dict] | None


class ExtractedIntent(TypedDict, total=False):
    game_type: Literal["roblox", "minecraft"] | None
    genres: list[str]
    categories: list[str]
    player_size: Literal["large", "small"] | None
    reply: str


def _default_state() -> ChatState:
    return {
        "stage": "chatting",
        "game_type": None,
        "genres": [],
        "categories": [],
        "player_size": None,
        "history": [],
        "recommendations": None,
    }


def _pick_prompt(kind: str, state: ChatState) -> str:
    prompts = PROMPTS[kind]
    assistant_turns = sum(1 for item in state["history"] if item["role"] == "assistant")
    return prompts[assistant_turns % len(prompts)]


def _contains_keyword(text: str, keyword: str) -> bool:
    if keyword == "mc":
        return re.search(r"(?<![a-z])mc(?![a-z])", text) is not None
    return keyword in text


def _merge_unique(existing: list[str], values: list[str]) -> list[str]:
    merged = list(existing)
    for value in values:
        if value not in merged:
            merged.append(value)
    return merged


def _detect_game_type(message: str) -> Literal["roblox", "minecraft"] | None:
    lowered = message.lower()
    hits = []
    for game_type, keywords in GAME_KEYWORDS.items():
        if any(_contains_keyword(lowered, keyword.lower()) for keyword in keywords):
            hits.append(game_type)
    if len(hits) == 1:
        return cast(Literal["roblox", "minecraft"], hits[0])
    return None


def _detect_many(message: str, mapping: dict[str, list[str]]) -> list[str]:
    lowered = message.lower()
    found = []
    for canonical, keywords in mapping.items():
        if any(_contains_keyword(lowered, keyword.lower()) for keyword in keywords):
            found.append(canonical)
    return found


def _detect_player_size(message: str) -> Literal["large", "small"] | None:
    lowered = message.lower()
    large = any(_contains_keyword(lowered, keyword.lower()) for keyword in PLAYER_SIZE_KEYWORDS["large"])
    small = any(_contains_keyword(lowered, keyword.lower()) for keyword in PLAYER_SIZE_KEYWORDS["small"])
    if large and not small:
        return "large"
    if small and not large:
        return "small"
    return None


def _rule_extract_intent(message: str) -> ExtractedIntent:
    return {
        "game_type": _detect_game_type(message),
        "genres": _detect_many(message, ROBLOX_GENRE_KEYWORDS),
        "categories": _detect_many(message, MINECRAFT_CATEGORY_KEYWORDS),
        "player_size": _detect_player_size(message),
    }


def _normalize_llm_intent(data: dict) -> ExtractedIntent:
    game_type = data.get("game_type")
    if game_type not in {"roblox", "minecraft"}:
        game_type = None
    genres = [genre for genre in data.get("genres", []) if genre in ROBLOX_GENRES]
    categories = [category for category in data.get("categories", []) if category in MINECRAFT_CATEGORIES]
    player_size = data.get("player_size")
    if player_size not in {"large", "small"}:
        player_size = None
    intent: ExtractedIntent = {
        "game_type": game_type,
        "genres": genres,
        "categories": categories,
        "player_size": player_size,
    }
    reply = data.get("reply")
    if isinstance(reply, str) and reply.strip():
        intent["reply"] = reply.strip()
    return intent


def _llm_endpoint_config() -> tuple[str, dict[str, str], str] | None:
    """LLM 호출용 (url, headers, model) 설정을 반환. 사용 가능한 provider가 없으면 None.

    사내 APIM Foundry 프록시(APIM_BASE_URL/APIM_KEY)가 설정돼 있으면 우선 사용하고,
    없으면 OpenAI 직접 호출(OPENAI_API_KEY)로 대체한다.
    """
    apim_base_url = os.getenv("APIM_BASE_URL")
    apim_key = os.getenv("APIM_KEY")
    if apim_base_url and apim_key:
        model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
        url = apim_base_url.rstrip("/") + "/" + model + "/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "api-key": apim_key,
        }
        return url, headers, model

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        auth_value = "Bearer" + " " + openai_key
        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_value,
        }
        return "https://api.openai.com/v1/chat/completions", headers, "gpt-4o-mini"

    return None


def _llm_extract_intent(state: ChatState, message: str) -> ExtractedIntent | None:
    endpoint_config = _llm_endpoint_config()
    if not endpoint_config:
        return None
    url, headers, model = endpoint_config

    history_lines = []
    for item in state["history"][-8:]:
        prefix = "user" if item["role"] == "user" else "assistant"
        history_lines.append(f"{prefix}: {item['text']}")
    history_lines.append(f"user: {message}")

    tool_schema = {
        "type": "function",
        "function": {
            "name": "extract_chat_intent",
            "description": "Extract canonical game recommendation intent and draft a short Korean reply.",
            "parameters": {
                "type": "object",
                "properties": {
                    "game_type": {"type": ["string", "null"], "enum": ["roblox", "minecraft", None]},
                    "genres": {"type": "array", "items": {"type": "string", "enum": ROBLOX_GENRES}},
                    "categories": {"type": "array", "items": {"type": "string", "enum": MINECRAFT_CATEGORIES}},
                    "player_size": {"type": ["string", "null"], "enum": ["large", "small", None]},
                    "reply": {"type": "string"},
                },
                "required": ["game_type", "genres", "categories", "player_size", "reply"],
                "additionalProperties": False,
            },
        },
    }
    conversation = "\n".join(history_lines)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You extract intent for a Korean game recommendation chatbot. "
                    "Never invent recommendations. Only map the user's words to canonical values. "
                    "Draft the reply in Korean, short and friendly."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Known Roblox genres: {', '.join(ROBLOX_GENRES)}\n"
                    f"Known Minecraft categories: {', '.join(MINECRAFT_CATEGORIES)}\n"
                    f"Conversation so far:\n{conversation}"
                ),
            },
        ],
        "tools": [tool_schema],
        "tool_choice": {"type": "function", "function": {"name": "extract_chat_intent"}},
        "temperature": 0.2,
    }

    try:
        with httpx.Client(timeout=8.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        data = response.json()
        tool_calls = data["choices"][0]["message"].get("tool_calls") or []
        if not tool_calls:
            return None
        args = json.loads(tool_calls[0]["function"]["arguments"])
        return _normalize_llm_intent(args)
    except Exception:
        return None


def _combine_intents(rule_intent: ExtractedIntent, llm_intent: ExtractedIntent | None) -> ExtractedIntent:
    if not llm_intent:
        return rule_intent
    combined: ExtractedIntent = {
        "game_type": llm_intent.get("game_type") or rule_intent.get("game_type"),
        "genres": _merge_unique(rule_intent.get("genres", []), llm_intent.get("genres", [])),
        "categories": _merge_unique(rule_intent.get("categories", []), llm_intent.get("categories", [])),
        "player_size": llm_intent.get("player_size") or rule_intent.get("player_size"),
    }
    if llm_intent.get("reply"):
        combined["reply"] = llm_intent["reply"]
    return combined


def _done_reply_for_roblox(state: ChatState, recommendations: list[dict], llm_reply: str | None) -> str:
    if llm_reply:
        return llm_reply
    genre_text = ", ".join(state["genres"])
    size_text = "대규모 멀티" if state["player_size"] == "large" else "소규모/캐주얼"
    if recommendations:
        return f"좋아요! {genre_text} 취향과 {size_text} 선호를 바탕으로 로블록스 추천 5개를 골라봤어요."
    return f"{genre_text} 장르와 {size_text} 조건으로 찾아봤는데, 지금은 딱 맞는 로블록스 추천을 찾지 못했어요."


def _done_reply_for_minecraft(state: ChatState, recommendations: list[dict], llm_reply: str | None) -> str:
    if llm_reply:
        return llm_reply
    category_text = ", ".join(state["categories"])
    if recommendations:
        return f"좋아요! {category_text} 성향에 맞춰 마인크래프트 모드 추천 5개를 준비했어요."
    return f"{category_text} 쪽으로 찾아봤는데, 지금은 딱 맞는 마인크래프트 모드를 찾지 못했어요."


def _record_and_finish(
    *,
    db: DBSession,
    session_id: str,
    state: ChatState,
    answers: dict,
    recommendations: list[dict],
    reply: str,
) -> dict:
    save_survey_results(
        db,
        session_id=session_id,
        game_type=cast(Literal["roblox", "minecraft"], state["game_type"]),
        answers=answers,
        recommendations=recommendations,
    )
    state["stage"] = "done"
    state["recommendations"] = recommendations
    return {
        "reply": reply,
        "stage": "done",
        "game_type": state["game_type"],
        "recommendations": recommendations,
    }


@router.post("")
def chat(
    payload: ChatIn,
    request: Request,
    response: Response,
    db: DBSession = Depends(get_session),
):
    session_id = get_or_create_session(request, response, db)
    state = CHAT_STATES.setdefault(session_id, _default_state())
    message = payload.message.strip()

    if state["stage"] == "done":
        reply = "이미 추천을 완료했어요. 새로운 추천을 원하시면 다시 시작해 주세요!"
        state["history"].append({"role": "user", "text": message})
        state["history"].append({"role": "assistant", "text": reply})
        return {
            "reply": reply,
            "stage": "done",
            "game_type": state["game_type"],
            "recommendations": state["recommendations"],
        }

    rule_intent = _rule_extract_intent(message)
    llm_intent = _llm_extract_intent(state, message)
    extracted = _combine_intents(rule_intent, llm_intent)

    previous_game_type = state["game_type"]
    previous_genres = list(state["genres"])
    previous_categories = list(state["categories"])
    previous_player_size = state["player_size"]

    if state["game_type"] is None and extracted.get("game_type"):
        state["game_type"] = extracted["game_type"]

    if state["game_type"] == "roblox":
        state["genres"] = _merge_unique(state["genres"], extracted.get("genres", []))
        if state["player_size"] is None and extracted.get("player_size"):
            state["player_size"] = extracted["player_size"]
    elif state["game_type"] == "minecraft":
        state["categories"] = _merge_unique(state["categories"], extracted.get("categories", []))

    state["history"].append({"role": "user", "text": message})

    added_info = (
        previous_game_type != state["game_type"]
        or previous_genres != state["genres"]
        or previous_categories != state["categories"]
        or previous_player_size != state["player_size"]
    )
    llm_reply = extracted.get("reply")

    if state["game_type"] is None:
        reply = _pick_prompt("choose_game", state)
        state["history"].append({"role": "assistant", "text": reply})
        return {"reply": reply, "stage": "chatting", "game_type": None, "recommendations": None}

    if state["game_type"] == "roblox":
        if not state["genres"]:
            reply = llm_reply if (llm_reply and added_info) else _pick_prompt("roblox_genres", state)
            state["history"].append({"role": "assistant", "text": reply})
            return {
                "reply": reply,
                "stage": "chatting",
                "game_type": "roblox",
                "recommendations": None,
            }

        if state["player_size"] is None:
            reply = _pick_prompt("roblox_player_size", state)
            state["history"].append({"role": "assistant", "text": reply})
            return {
                "reply": reply,
                "stage": "chatting",
                "game_type": "roblox",
                "recommendations": None,
            }

        recommendations = match_roblox_recommendations(db, state["genres"], state["player_size"])
        reply = _done_reply_for_roblox(state, recommendations, llm_reply)
        result = _record_and_finish(
            db=db,
            session_id=session_id,
            state=state,
            answers={"genres": state["genres"], "player_size": state["player_size"]},
            recommendations=recommendations,
            reply=reply,
        )
        state["history"].append({"role": "assistant", "text": reply})
        return result

    if not state["categories"]:
        reply = llm_reply if (llm_reply and added_info) else _pick_prompt("minecraft_categories", state)
        state["history"].append({"role": "assistant", "text": reply})
        return {
            "reply": reply,
            "stage": "chatting",
            "game_type": "minecraft",
            "recommendations": None,
        }

    recommendations = match_minecraft_recommendations(db, state["categories"])
    reply = _done_reply_for_minecraft(state, recommendations, llm_reply)
    result = _record_and_finish(
        db=db,
        session_id=session_id,
        state=state,
        answers={"categories": state["categories"]},
        recommendations=recommendations,
        reply=reply,
    )
    state["history"].append({"role": "assistant", "text": reply})
    return result


@router.get("/reset")
@router.post("/reset")
def reset_chat(
    request: Request,
    response: Response,
    db: DBSession = Depends(get_session),
):
    session_id = get_or_create_session(request, response, db)
    CHAT_STATES.pop(session_id, None)
    return {"ok": True}
