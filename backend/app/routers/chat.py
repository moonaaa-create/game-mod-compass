import os
from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 메모리 기반 대화 기록 저장소 (세션별)
CHAT_HISTORY = {}

class ChatIn(BaseModel):
    message: str

@router.post("")
async def chat(
    payload: ChatIn,
    request: Request,
    response: Response,
):
    # 쿠키 기반 세션 ID (간단히 구현)
    session_id = request.cookies.get("chat_session")
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        response.set_cookie("chat_session", session_id)
        
    history = CHAT_HISTORY.setdefault(session_id, [
        {"role": "system", "content": "너는 안티그래비티 물리 엔진 웹 인터페이스에 연동된 재미있고 톡톡 튀는 게임 추천 AI 가이드야. 무중력 공간에서 둥둥 떠다니는 말풍선으로 대화하게 될 테니, 짧고 재치있게 답변해줘."}
    ])

    user_msg = payload.message.strip()
    history.append({"role": "user", "content": user_msg})

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"reply": "서버에 OPENAI_API_KEY가 설정되지 않았습니다."}

    client = AsyncOpenAI(api_key=api_key)

    try:
        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history,
            max_tokens=200,
            temperature=0.8
        )
        reply = completion.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"에러가 발생했습니다: {str(e)}"}
