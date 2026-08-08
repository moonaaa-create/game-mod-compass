# Game Mod Compass (게임모드 나침반)

로블록스(인기 게임)와 마인크래프트(모드)를 취향 설문 기반으로 추천하는 반응형 웹앱입니다.

> 상세 스펙: [`docs/spec.md`](docs/spec.md) — 기술 스택, API 연동, 데이터 모델, 매칭 로직 등
> 모든 설계 결정은 [Wayfinder 맵 #1](https://github.com/moonaaa-create/game-mod-compass/issues/1)에서 이슈 단위로 확정되었습니다.

## 핵심 흐름

게임 선택(로블록스/마인크래프트) → 대화형(챗봇 스타일) 설문 → 상위 5개 추천 결과

- 로블록스: 장르(복수 선택) + 인원 규모 선호 → 인기도 기준 상위 5개
- 마인크래프트: 모드 카테고리(복수 선택) → 다운로드 수 기준 상위 5개
- 회원가입 없이 쿠키 기반 세션으로 이용 가능

## 기술 스택

| 영역 | 선택 |
|---|---|
| 프론트엔드 | Vue 3 + Vite (SPA) |
| 백엔드 | FastAPI + SQLModel |
| DB | SQLite |
| 배포 | Render (Static Site + Web Service + Persistent Disk) |

## 프로젝트 구조

```
backend/    FastAPI + SQLModel REST API
frontend/   Vue 3 + Vite SPA (챗봇 스타일 설문 UI)
docs/       스펙, 리서치 문서
```

## 로컬 실행

### 백엔드

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # CURSEFORGE_API_KEY 등 설정 (없어도 fixture 데이터로 동작)
uvicorn app.main:app --reload --port 8000
```

- 최초 실행 시 DB가 비어있으면 로블록스 94개 / 마인크래프트 100개 fixture 데이터를 자동으로 시딩합니다.
- `CURSEFORGE_API_KEY`가 없으면 CurseForge 실 API 대신 결정론적 fixture 데이터를 사용합니다 (오프라인 개발 대비).
- AI 자유 대화(`/api/chat`)는 `APIM_BASE_URL`/`APIM_KEY`/`CHAT_MODEL` (사내 APIM Foundry 프록시) 또는 `OPENAI_API_KEY`가 있으면 사용하고, 둘 다 없으면 규칙 기반 한국어 파서로 자동 대체됩니다. 값은 `.env`에만 설정하고 절대 커밋하지 마세요.
- API 문서: http://localhost:8000/docs

### 프론트엔드

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE=http://localhost:8000
npm run dev
```

## Render 배포

- 이 저장소에는 Render Blueprint용 `render.yaml`이 포함되어 있습니다.
- Render Dashboard에서 **New + → Blueprint**로 이 리포지토리와 `main` 브랜치를 연결해 배포하세요.
- `game-mod-compass-api`는 FastAPI Web Service + Persistent Disk(`/var/data`), `game-mod-compass-web`는 Vue Static Site로 생성됩니다.
- 첫 배포 후 `CURSEFORGE_API_KEY`는 대시보드에서 수동으로 입력하세요.
- `ALLOWED_ORIGINS`와 `VITE_API_BASE`는 Blueprint에서 서비스 URL을 참조하도록 설정했으니 실제 URL로 올바르게 연결됐는지 한 번 확인하세요.
- 필요하면 두 값을 대시보드에서 직접 수정한 뒤 재배포하면 됩니다.

## 데이터 갱신 (크론)

`backend/app/seed.py`의 `run_sync_force()`가 매일 1회(APScheduler, 새벽 3시) 자동 실행되어
Roblox/CurseForge 최신 데이터로 캐시를 갱신합니다 (사람 개입 없음).

## 남은 구현 과제

- 실제 로블록스 인기 게임 94개의 `universe_id` 목록 수집 (현재는 placeholder ID 사용, `app/seed.py` 참고)
- CurseForge 4개 카테고리(Technology/Magic/Adventure&RPG/Map&Information)의 실제 `categoryId` 조회 및 매핑
- CurseForge API 키 발급 (console.curseforge.com, Overwolf 팀 심사)
