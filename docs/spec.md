# 게임모드/게임 추천 웹앱 — 상세 스펙

> 이 문서는 Wayfinder 맵 [#1 게임모드/게임 추천 웹앱 스펙 작성](https://github.com/moonaaa-create/game-mod-compass/issues/1)에서
> 확정된 모든 결정 사항을 개발팀/에이전트가 바로 구현에 착수할 수 있는 수준으로 정리한 것이다.
> 각 결정의 상세 근거는 링크된 이슈를 참고한다.

## 1. 개요 (Destination)

로블록스(공식 API로 동적 조회되는 인기 게임 94개 중 추천) + 마인크래프트(CurseForge API로 조회되는 모드 100개 중 추천)를
사용자 취향/설문 기반으로 개인화 추천하는 **반응형 웹앱**.

- 대상 사용자: 비회원 포함 누구나 (회원가입 불필요)
- 핵심 흐름: 게임 선택(로블록스/마인크래프트) → 맞춤 설문 → 상위 5개 추천 결과
- 지원 언어: 한국어만 (MVP, [#12](https://github.com/moonaaa-create/game-mod-compass/issues/12))
- 수익 모델: 없음, 완전 무료 ([#13](https://github.com/moonaaa-create/game-mod-compass/issues/13))

## 2. 기술 스택

| 영역 | 선택 | 근거 |
|---|---|---|
| 프론트엔드 | **Vue 3 + Vite** (SPA) | 가벼운 프레임워크, 컴포넌트/상태관리 용이 ([#4](https://github.com/moonaaa-create/game-mod-compass/issues/4)) |
| 백엔드 | **Python + FastAPI** | 자동 OpenAPI 문서, Pydantic 타입 검증, 비동기 지원 ([#10](https://github.com/moonaaa-create/game-mod-compass/issues/10)) |
| ORM | **SQLModel** | FastAPI 제작자가 만든 경량 ORM, Pydantic과 자연스럽게 통합 ([#10](https://github.com/moonaaa-create/game-mod-compass/issues/10)) |
| DB | **SQLite** | 가벼운 구성 지향 |
| 아키텍처 | 프론트(SPA)와 백엔드(REST API) **완전 분리** — 백엔드는 정적 파일을 서빙하지 않음 | ([#4](https://github.com/moonaaa-create/game-mod-compass/issues/4)) |
| 인증 | 없음 — 비회원, 세션/쿠키 기반으로 취향 저장 | |
| 배포 | **Render** 단일 PaaS — Vue 빌드 결과물은 Static Site, FastAPI는 Web Service, SQLite는 Persistent Disk에 마운트 | ([#5](https://github.com/moonaaa-create/game-mod-compass/issues/5)) |
| CORS | Static Site와 Web Service가 다른 도메인이므로 FastAPI `CORSMiddleware` 설정 필요 | ([#10](https://github.com/moonaaa-create/game-mod-compass/issues/10)) |

## 3. 외부 API 연동

### 3-1. Roblox 공식 API ([#2](https://github.com/moonaaa-create/game-mod-compass/issues/2))

- **엔드포인트**: `GET https://games.roblox.com/v1/games?universeIds={ids}` — 인증 불필요.
- 94개 인기 게임의 universe ID를 정적으로 관리(수집 방법: `roblox.com/discover` 인기순에서 DevTools Network 탭으로 캡처), 1~2회 배치 호출로 메타데이터 취득.
- **제공 필드**: `name`, `description`, `genre`(단일값), `playing`(동접), `visits`(누적 방문), `favoritedCount`, `maxPlayers`. `tags` 배열은 없음.
- 썸네일: `GET https://thumbnails.roblox.com/v1/games/icons?universeIds={ids}&size=150x150&format=Png`
- **Rate limit**: IP당 약 10 req/s, 429 시 `retry-after` 헤더 준수.
- 상세: [`docs/research/roblox-api.md`](https://github.com/moonaaa-create/game-mod-compass/blob/research/roblox-api/docs/research/roblox-api.md) (research 브랜치)

### 3-2. CurseForge API ([#3](https://github.com/moonaaa-create/game-mod-compass/issues/3))

- **엔드포인트**: `GET https://api.curseforge.com/v1/mods/search` — `x-api-key` 헤더 인증 (console.curseforge.com에서 발급, Overwolf 팀 심사 필요).
- 파라미터: `gameId=432`(Minecraft), `classId=6`(모드), `categoryIds`, `sortField`, `sortOrder`, `pageSize`, `index`.
- **제공 필드**: `name`, `summary`, `categories[]`, `downloadCount`, `logo`, `latestFilesIndexes[]`(게임버전×모드로더), `allowModDistribution`.
- **Rate limit**: 공개 수치 없음 — 사전 수집 + 캐싱 전략 필수.
- **ToS 준수**: 모드 파일 재배포 금지, "모드 데이터 제공: CurseForge" 출처 표시, `allowModDistribution: false`인 모드는 다운로드 URL 노출 금지.
- 상세: [`docs/research/curseforge-api.md`](https://github.com/moonaaa-create/game-mod-compass/blob/research/curseforge-api/docs/research/curseforge-api.md) (research 브랜치)

## 4. 콘텐츠 선정 기준

### 4-1. 로블록스 (94개)

동적 조회, 별도 카테고리/장르 제한 없음 — 인기순 상위 94개.

### 4-2. 마인크래프트 모드 (100개) — [#6](https://github.com/moonaaa-create/game-mod-compass/issues/6)

- 게임 버전: 특정 버전 고정 없음 (전체 버전 통합 인기순).
- 모드로더: Forge/Fabric/Quilt/NeoForge 구분 없이 통합 인기순 (추천 결과 카드에는 로더 태그만 표시).
- **카테고리 제한**: 기술(Technology), 마법(Magic), 모험/RPG(Adventure and RPG), 맵/정보(Map and Information) 4개.
- 4개 카테고리를 통합해(균등 배분 없이) 인기 지표(`downloadCount` 등) 기준 상위 100개 선정.

### 4-3. 데이터 갱신 — [#11](https://github.com/moonaaa-create/game-mod-compass/issues/11)

- **완전 자동화**: 크론 잡이 사람 개입 없이 매일 1회 각 API에서 상위 항목을 그대로 가져와 DB 갱신.

## 5. 설문 및 추천 매칭 로직 — [#7](https://github.com/moonaaa-create/game-mod-compass/issues/7)

### 5-1. 흐름

사용자가 먼저 **로블록스** 또는 **마인크래프트**를 선택 → 전용 설문 → **상위 5개** 추천 결과.

### 5-2. 로블록스 설문 (2문항)

1. **장르 선호** — 복수 선택 (Roblox 공식 genre 값: Adventure, RPG, Horror 등)
2. **인원수/강도 선호** — 단일 선택: 대규모(멀티플레이 지향) vs 소규모(캐주얼)

**매칭 로직**:
1. `genre`가 선택한 장르 중 하나와 일치하는 게임만 필터링 (AND 매칭)
2. 인기도(`playing` + `visits` + `favoritedCount` 종합 정규화 스코어) 내림차순 정렬
3. 인원수/강도 선호는 **동점 시 tie-breaker**로만 사용 (`maxPlayers`가 선택 구간에 가까울수록 우선)
4. 상위 5개 반환

### 5-3. 마인크래프트 설문 (1문항)

1. **카테고리 선호** — 복수 선택 (기술/마법/모험·RPG/맵·정보)

**매칭 로직**:
1. 모드의 `categories` 중 하나가 선택한 카테고리와 일치하는 모드만 필터링
2. `downloadCount` 내림차순 정렬
3. 상위 5개 반환, 모드로더는 결과 카드에 **태그로만 표시** (필터링에는 사용하지 않음)

## 6. 데이터 모델 (SQLite) — [#8](https://github.com/moonaaa-create/game-mod-compass/issues/8)

```sql
-- 로블록스 게임 캐시
CREATE TABLE roblox_games (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  universe_id INTEGER UNIQUE NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  genre TEXT NOT NULL,
  playing INTEGER,
  visits INTEGER,
  favorited_count INTEGER,
  max_players INTEGER,
  thumbnail_url TEXT,
  updated_at TEXT NOT NULL
);

-- 마인크래프트 모드 캐시
CREATE TABLE minecraft_mods (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  curseforge_mod_id INTEGER UNIQUE NOT NULL,
  name TEXT NOT NULL,
  slug TEXT,
  summary TEXT,
  download_count INTEGER,
  logo_url TEXT,
  updated_at TEXT NOT NULL
);

-- 모드 ↔ 카테고리 (다대다)
CREATE TABLE mod_categories (
  mod_id INTEGER NOT NULL REFERENCES minecraft_mods(id),
  category TEXT NOT NULL CHECK (category IN ('technology','magic','adventure_rpg','map_information')),
  PRIMARY KEY (mod_id, category)
);

-- 모드 ↔ 모드로더 (다대다, 결과 태그 표시용)
CREATE TABLE mod_loaders (
  mod_id INTEGER NOT NULL REFERENCES minecraft_mods(id),
  loader TEXT NOT NULL CHECK (loader IN ('forge','fabric','quilt','neoforge')),
  PRIMARY KEY (mod_id, loader)
);

-- 비회원 세션 (쿠키 기반)
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,           -- 쿠키에 저장되는 UUID
  created_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL
);

-- 취향 설문 응답
CREATE TABLE survey_responses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL REFERENCES sessions(id),
  game_type TEXT NOT NULL CHECK (game_type IN ('roblox','minecraft')),
  answers TEXT NOT NULL,         -- JSON: 예) {"genres": ["Adventure","RPG"], "player_size": "large"}
  created_at TEXT NOT NULL
);

-- 추천 결과 이력
CREATE TABLE recommendations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  survey_response_id INTEGER NOT NULL REFERENCES survey_responses(id),
  game_type TEXT NOT NULL CHECK (game_type IN ('roblox','minecraft')),
  item_id INTEGER NOT NULL,      -- roblox_games.id 또는 minecraft_mods.id
  rank INTEGER NOT NULL CHECK (rank BETWEEN 1 AND 5),
  created_at TEXT NOT NULL
);
```

- 게임/모드 메타데이터는 크론이 미리 캐싱 (요청 시 실시간 API 호출 없음).
- 설문 응답 → 추천 결과는 세션별로 이력 저장 (조회/분석용).
- `answers`는 JSON 텍스트 컬럼 (SQLite 네이티브 JSON 타입 없음, `json_extract`로 조회 가능).

## 7. UI/UX — [#9](https://github.com/moonaaa-create/game-mod-compass/issues/9)

**채택안: 대화형 챗봇 스타일**

- 질문이 말풍선(bot)으로 하나씩 표시되고, 사용자는 칩(chip) 버튼으로 응답 → 사용자 말풍선으로 누적.
- 복수 선택 문항(장르/카테고리)은 여러 칩을 선택한 뒤 "선택 완료 →" 버튼으로 확정.
- 추천 결과도 채팅 리스트 형태(순위 배지 + 썸네일 + 이름/메타/태그)로 표시.
- 실제 Vue 3 구현 시, 대화 흐름은 상태 머신(질문 인덱스 → 답변 수집 → 결과)으로 모델링.
- 프로토타입(3개 변형 전체, 참고용): [`prototype/survey-ui` 브랜치](https://github.com/moonaaa-create/game-mod-compass/tree/prototype/survey-ui/prototype/survey-ui)

## 8. 범위 외 (MVP 제외)

- 다국어 지원 ([#12](https://github.com/moonaaa-create/game-mod-compass/issues/12)) — 한국어만.
- 수익화(광고/제휴/프리미엄) ([#13](https://github.com/moonaaa-create/game-mod-compass/issues/13)) — 완전 무료.

## 9. 참고

- Wayfinder 맵(전체 의사결정 이력): [#1](https://github.com/moonaaa-create/game-mod-compass/issues/1)
- Roblox API 조사 원본: `research/roblox-api` 브랜치
- CurseForge API 조사 원본: `research/curseforge-api` 브랜치
- UI 프로토타입 원본: `prototype/survey-ui` 브랜치
