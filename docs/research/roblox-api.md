# Roblox 공식 API 조사: 게임 메타데이터 / 인증 / Rate Limit

> **조사 일자**: 2026-08-08
> **대상 티켓**: [#2 Roblox 공식 API 조사](https://github.com/moonaaa-create/game-mod-compass/issues/2)
> **참조 이슈**: [#1 Wayfinder Map](https://github.com/moonaaa-create/game-mod-compass/issues/1)

---

## 요약 (TL;DR)

Roblox 레거시 Web API(`games.roblox.com`)의 `/v1/games?universeIds=...` 엔드포인트를 통해
**인증 없이** 게임 메타데이터(장르, 현재 동접수, 누적 방문수, 즐겨찾기 수, 설명 등)를
배치 조회할 수 있다. 인기 게임 94개의 universe ID를 미리 확보해 두면 해당 엔드포인트
1~2회 호출로 모든 메타데이터를 취득 가능하다. "실시간 인기순" 정렬 전용 엔드포인트
(`/v1/games/list`)는 존재하지만 필수 파라미터(`sortToken`)가 공식 문서화되어 있지
않아 프로덕션 의존이 어렵다. Rate limit은 IP당 약 10 req/s이며, 게임 메타데이터
읽기 전용 조회에는 상업적 사용 제한이 없다.

---

## 1. 인기 게임 목록 조회 가능 여부

### 1-1. 공식 인기 게임 정렬 엔드포인트

```
GET https://games.roblox.com/v1/games/list
```

파라미터: `sortToken`, `gameFilter`, `timeFilter`, `genreFilter`, `maxRows` 등.

- `sortToken`은 Roblox 내부 값으로 **공식 문서에 게시되지 않음**.
  브라우저 DevTools에서 `roblox.com/discover` 페이지의 Network 요청을 캡처해야
  현재 유효한 토큰 값을 알 수 있으며, 수시로 변경될 수 있어 프로덕션 의존 불가.

> 출처: [Roblox DevForum — How to actually use the games/list endpoint](https://devforum.roblox.com/t/how-to-actually-use-the-gamesrobloxapiv1gameslist-endpoint/2839124)

### 1-2. 권장 대안: universe ID 배치 조회

인기 게임 94개의 universe ID를 앱 초기화 시점 또는 별도 수집 로직으로 확보한 뒤,
`/v1/games?universeIds=...` 엔드포인트로 배치 조회하는 방식이 가장 안정적이다.

```
GET https://games.roblox.com/v1/games?universeIds=480700042,1818,2753915549,...
```

- 한 번의 호출로 최대 ~100개의 universe ID 쿼리 가능 (URL 길이 제한 기준).
- 94개 universe ID는 1~2회 호출로 전부 처리 가능.

---

## 2. 제공 메타데이터 필드

`GET https://games.roblox.com/v1/games?universeIds={ids}` 응답 예시:

```json
{
  "data": [
    {
      "id": 3759152694,
      "rootPlaceId": 10269801695,
      "name": "Game Name",
      "description": "게임 설명 텍스트",
      "creator": {
        "id": 123456,
        "name": "CreatorName",
        "type": "User"
      },
      "playing": 15234,
      "visits": 900000000,
      "maxPlayers": 20,
      "created": "2022-07-18T14:21:46.03Z",
      "updated": "2024-01-10T09:00:00.00Z",
      "genre": "Adventure",
      "favoritedCount": 2500000
    }
  ]
}
```

| 필드 | 설명 | 추천 시 활용 |
|------|------|-------------|
| `name` | 게임 이름 | ✅ |
| `description` | 게임 설명 | ✅ LLM 프롬프트용 |
| `genre` | 장르 (Adventure, RPG, Shooter 등) | ✅ 태그 매칭 |
| `playing` | 현재 동시 접속자 수 | ✅ 인기도 지표 |
| `visits` | 누적 방문 횟수 | ✅ 장기 인기도 |
| `favoritedCount` | 즐겨찾기 수 | ✅ 사용자 선호도 |
| `maxPlayers` | 최대 플레이어 수 | ✅ 멀티 여부 판단 |
| `creator` | 제작자 정보 | 참고용 |
| `rootPlaceId` | 메인 플레이스 ID | 썸네일 조회에 사용 |

### 2-1. 태그(Tags)

Roblox 레거시 API의 `/v1/games` 응답에는 `tags` 배열 필드가 **없음**.
장르 분류는 `genre` 단일 값만 제공된다. Roblox 지원 장르 목록:

> Action, Adventure, Educational, Entertainment, Fighting, Horror, Naval, RPG,
> Sci-Fi, Sports, Town and City, Western, All 등
>
> 세부 장르(subgenre)는 Creator Dashboard에서 설정 가능하나 API 응답에는 미포함.
>
> 출처: [Roblox Creator Hub — Experience Genres](https://create.roblox.com/docs/production/publishing/experience-genres)

### 2-2. 썸네일 / 아이콘

```
GET https://thumbnails.roblox.com/v1/games/icons?universeIds={ids}&size=150x150&format=Png
```

인증 불필요, 공개 엔드포인트.

### 2-3. 좋아요 / 싫어요

```
GET https://games.roblox.com/v1/games/{universeId}/votes
```

응답: `{ "upVotes": 12345, "downVotes": 678 }`

---

## 3. 인증 방식

### 3-1. 레거시 Web API (games.roblox.com, thumbnails.roblox.com)

- **인증 불필요** — 게임 메타데이터 읽기 전용 엔드포인트는 모두 공개.
- `.ROBLOSECURITY` 쿠키는 로그인 사용자 전용 기능(투표 여부 확인 등)에만 필요.
- 본 앱에서는 **API 키 / OAuth 설정 불필요**.

### 3-2. Open Cloud API (apis.roblox.com)

- `x-api-key: <KEY>` 헤더 필요.
- [Creator Dashboard — API Keys](https://create.roblox.com/credentials)에서 발급.
- 스코프: `universe:read`, `analytics-query:read` 등.
- **본 앱 유즈케이스에는 불필요** — 자신이 소유한 universe analytics 조회에만 필요.

> 출처: [Roblox Creator Hub — Manage API keys](https://create.roblox.com/docs/cloud/auth/api-keys)

### 3-3. OAuth 2.0

- 사용자 계정 연동 앱(소셜 기능)에 필요. 본 앱(메타데이터 읽기)에는 **불필요**.

---

## 4. Rate Limit

| 항목 | 값 |
|------|----|
| 기본 limit (IP당) | **약 10 req/s** |
| 인증 여부와 무관하게 동일 적용 | ✅ |
| 초과 시 응답 코드 | HTTP 429 Too Many Requests |
| 재시도 지침 | `retry-after` 헤더 참조; 없으면 exponential backoff |
| 응답 헤더 | `x-ratelimit-limit`, `x-ratelimit-remaining`, `x-ratelimit-reset` |

> 참고: DDoS 방지 목적의 **미문서화 추가 제한** 존재 가능 — 항상 429 처리 필요.
>
> 출처: [Roblox Creator Hub — Rate Limits](https://create.roblox.com/docs/cloud/reference/rate-limits),
> [DevForum — Recent changes in API rate limits](https://devforum.roblox.com/t/recent-changes-in-api-rate-limits-cause-higher-costs/3797283)

### 본 앱에서의 영향

- 94개 게임을 `universeIds` 파라미터로 **1~2회 배치 호출** → rate limit 영향 없음.
- 캐싱(TTL 10분~1시간) 적용 시 서버 부하 최소화.

---

## 5. ToS 및 상업적 이용 제한

| 항목 | 허용 여부 |
|------|----------|
| 게임 메타데이터(이름, 장르, 통계) 공개 조회 | ✅ 허용 |
| 게임 추천 서비스 제공 | ✅ 허용 |
| 사용자 개인정보 수집 / 프로파일링 | ❌ 금지 |
| 사용자 행동 추적 / 타사 공유 | ❌ 금지 |
| Roblox 공식 승인 없이 제휴 표방 | ❌ 금지 |

> 출처:
> [Creator Third Party App Policy](https://en.help.roblox.com/hc/en-us/articles/37924211313044-Creator-Third-Party-App-Policy)
> [Roblox Terms of Use](https://www.roblox.com/info/terms)

**⚠️ 주의**: 본 앱은 사용자의 Roblox 계정 연동이나 개인 플레이 기록을 수집하지
않으므로 ToS 위반 소지 없음. 향후 사용자 개인화 기능 추가 시 별도 검토 요망.

---

## 6. 최적 엔드포인트 목록

### [Primary] 게임 메타데이터 배치 조회

```http
GET https://games.roblox.com/v1/games?universeIds=480700042,1818,2753915549
Authorization: 불필요
```

- 응답: `data[]` 배열 — genre, playing, visits, favoritedCount 등 포함
- 94개 universe ID를 한 번에 전달 가능

### [Secondary] 게임 썸네일

```http
GET https://thumbnails.roblox.com/v1/games/icons?universeIds=480700042&size=150x150&format=Png
```

### [Optional] 투표 수

```http
GET https://games.roblox.com/v1/games/{universeId}/votes
```

### [참고 — 사용 비추] 인기 게임 정렬

```http
GET https://games.roblox.com/v1/games/list?sortToken=<OPAQUE>&maxRows=50
```

- `sortToken`이 비공식 내부 값 → 프로덕션 의존 불가

---

## 7. 권장 사항

### 7-1. Universe ID 관리

94개 인기 게임의 universe ID를 **정적 JSON 파일**(`data/roblox-universe-ids.json`)로
관리한다. 초기 목록은 `roblox.com/discover` 인기순 정렬 상태에서 DevTools Network 탭으로
`/v1/games/list` 요청을 캡처해 수집한다. 주기적 갱신(월 1회)은 별도 스크립트나 수동으로 수행.

### 7-2. 메타데이터 캐싱

서비스 시작 시 또는 첫 요청 시 `games.roblox.com/v1/games?universeIds=...`를
1~2회 호출, TTL 30분~1시간으로 캐싱. 실시간 `playing` 수 필요 시 TTL 10분.

### 7-3. 인증 전략

레거시 Web API 사용이므로 **API 키 / OAuth 설정 불필요**. Open Cloud API는 미사용.

### 7-4. Error Handling

- HTTP 429: `retry-after` 헤더 대기 후 재시도 (exponential backoff fallback)
- HTTP 5xx: 캐시된 데이터로 graceful degradation

### 7-5. 태그 보완

`genre` 외의 세부 태그는 Roblox 공개 API에서 제공하지 않으므로:
- 게임별 `description`을 LLM으로 파싱해 자체 태그 생성, 또는
- 수동 큐레이션 방식으로 보완.

---

## 참고 자료

- [games.roblox.com API Reference — Roblox Creator Hub](https://create.roblox.com/docs/cloud/reference/domains/games)
- [Roblox Open Cloud Rate Limits](https://create.roblox.com/docs/cloud/reference/rate-limits)
- [Experience Genres — Roblox Creator Hub](https://create.roblox.com/docs/production/publishing/experience-genres)
- [Manage API Keys — Roblox Creator Hub](https://create.roblox.com/docs/cloud/auth/api-keys)
- [Creator Third Party App Policy — Roblox Help](https://en.help.roblox.com/hc/en-us/articles/37924211313044-Creator-Third-Party-App-Policy)
- [DevForum: Recent changes in API rate limits](https://devforum.roblox.com/t/recent-changes-in-api-rate-limits-cause-higher-costs/3797283)
- [DevForum: How to use games/list endpoint](https://devforum.roblox.com/t/how-to-actually-use-the-gamesrobloxapiv1gameslist-endpoint/2839124)
- [Stack Overflow: Fetching Roblox API game info](https://stackoverflow.com/questions/73087581/fetching-information-from-roblox-api-about-a-game)
