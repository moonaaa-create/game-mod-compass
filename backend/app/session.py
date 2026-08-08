"""세션 쿠키 처리 유틸 (비회원, 쿠키 기반 UUID)."""
import uuid
from datetime import datetime, timezone

from fastapi import Request, Response
from sqlmodel import Session as DBSession

from app.models import Session as SessionModel

SESSION_COOKIE_NAME = "session_id"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_or_create_session(request: Request, response: Response, db: DBSession) -> str:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    now = _now()

    if session_id:
        existing = db.get(SessionModel, session_id)
        if existing:
            existing.last_seen_at = now
            db.add(existing)
            db.commit()
            return session_id

    session_id = str(uuid.uuid4())
    db.add(SessionModel(id=session_id, created_at=now, last_seen_at=now))
    db.commit()
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 365,
    )
    return session_id
