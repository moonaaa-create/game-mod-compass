# CurseForge API 조사: 모드 메타데이터 / 인증 / Rate Limit

> **조사일:** 2026-08-08
> **대상 이슈:** [#3 CurseForge API 조사](https://github.com/moonaaa-create/game-mod-compass/issues/3)
> **참고 문서:** <https://docs.curseforge.com/rest-api/>

---

## 요약 (Summary)

CurseForge API(CFCore)는 `https://api.curseforge.com` 기반의 REST API로,
`x-api-key` 헤더 방식의 API 키 인증을 사용한다.
Minecraft (gameId = **432**) 모드를 `GET /v1/mods/search` 엔드포인트 하나로 검색할 수 있으며,
카테고리(`classId=6`), 게임 버전(`gameVersion`), 모드로더(`modLoaderType`) 필터를 모두 지원한다.
응답에는 모드명·요약·카테고리·다운로드 수·로고·지원 게임 버전·모드로더·최신 파일·제작자 정보가 포함된다.
API 키는 무료이나 Overwolf 팀의 심사·승인 절차가 필요하다.
공개된 rate limit 수치는 없으나 초과 시 `429/403` 에러가 반환되며, 재시도 전 최대 1~2시간 대기가 권장된다.

---

## 1. API 키 발급 방법

- **발급 창구:** <https://console.curseforge.com/> (계정 생성 후 키 발급 신청)
- **비용:** 무료 (단, Overwolf 팀의 심사·승인 필요)
- **절차:**
  1. 신청 폼([monday.com 폼](https://forms.monday.com/forms/dce5ccb7afda9a1c21dab1a1aa1d84eb?r=use1))에서 연락처, 프로젝트 설명, 예상 API 사용 목적 등을 작성.
  2. [3rd Party Developers API Terms of Service](https://support.curseforge.com/en/support/solutions/articles/9000207405-curse-forge-3rd-party-api-terms-and-conditions) 동의.
  3. Overwolf 팀 검토 후 이메일로 키 발급.
- **심사 기준:** 모드 작가의 수익 영향, 서버/CDN 부하, 제3자 배포 시 작가 동의 여부.
- **출처:** [About the CurseForge API and How to Apply for a Key](https://support.curseforge.com/en/support/solutions/articles/9000208346-about-the-curseforge-api-and-how-to-apply-for-a-key)

---

## 2. 모드 검색 엔드포인트 및 필터

### Base URL

```
https://api.curseforge.com
```

페이지당 최대 50건, 총 결과 최대 10,000건 (`index + pageSize ≤ 10,000`).

### 핵심 엔드포인트: `GET /v1/mods/search`

| 파라미터 | 필수 | 설명 |
|---|---|---|
| `gameId` | ✅ | Minecraft = **432** |
| `classId` | - | 섹션 분류. Minecraft 모드 = **6** |
| `categoryId` | - | 세부 카테고리 ID |
| `categoryIds` | - | 복수 카테고리 (최대 10개) |
| `gameVersion` | - | 게임 버전 문자열 (예: `"1.20.1"`) |
| `gameVersions` | - | 복수 버전 (최대 4개) |
| `modLoaderType` | - | 모드로더 타입 (아래 열거값 참고) |
| `modLoaderTypes` | - | 복수 모드로더 (최대 5개) |
| `sortField` | - | 정렬 기준 (1~12) |
| `sortOrder` | - | `asc` / `desc` |
| `searchFilter` | - | 모드명·작가 자유 텍스트 검색 |
| `slug` | - | 슬러그로 특정 모드 조회 |
| `index` | - | 페이지네이션 오프셋 (0부터) |
| `pageSize` | - | 페이지 크기 (기본/최대 50) |

#### modLoaderType 열거값

| 값 | 의미 |
|---|---|
| 0 | Any |
| 1 | Forge |
| 2 | Cauldron |
| 3 | LiteLoader |
| 4 | Fabric |
| 5 | Quilt |
| 6 | NeoForge |

#### sortField 열거값 (주요)

| 값 | 의미 |
|---|---|
| 1 | Featured |
| 2 | Popularity |
| 3 | LastUpdated |
| 4 | Name |
| 5 | Author |
| 6 | TotalDownloads |
| 11 | Rating |

**출처:** <https://docs.curseforge.com/rest-api/>

---

## 3. 응답 메타데이터 필드

`GET /v1/mods/search` 응답의 `data[]` 배열 각 모드 객체에 포함되는 주요 필드:

| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | int | 모드 고유 ID |
| `gameId` | int | 게임 ID (Minecraft = 432) |
| `name` | string | 모드명 |
| `slug` | string | URL용 슬러그 |
| `summary` | string | 짧은 설명 |
| `status` | int | 모드 상태 |
| `downloadCount` | int | 누적 다운로드 수 |
| `isFeatured` | bool | 피처드 여부 |
| `primaryCategoryId` | int | 주 카테고리 ID |
| `categories` | array | 카테고리 목록 (id, name, slug, iconUrl) |
| `classId` | int | 섹션 분류 ID |
| `authors` | array | 제작자 목록 (id, name, url) |
| `logo` | object | 로고 (thumbnailUrl, url) |
| `screenshots` | array | 스크린샷 목록 |
| `latestFiles` | array | 최신 파일 목록 |
| `latestFilesIndexes` | array | 게임버전×모드로더별 최신 파일 인덱스 |
| `dateCreated` / `dateModified` / `dateReleased` | datetime | 날짜 정보 |
| `allowModDistribution` | bool | 제3자 배포 허용 여부 |
| `gamePopularityRank` | int | 인기 순위 |
| `thumbsUpCount` | int | 좋아요 수 |
| `rating` | float | 평점 |
| `links` | object | websiteUrl, wikiUrl, issuesUrl, sourceUrl |

#### `latestFilesIndexes[]` — 모드로더 필터링에 가장 유용

```json
{
  "gameVersion": "1.20.1",
  "fileId": 12345678,
  "filename": "mymod-1.0.0-1.20.1.jar",
  "releaseType": 1,
  "gameVersionTypeId": 517,
  "modLoader": 1
}
```

`modLoader` 값은 `modLoaderType`과 동일한 열거값 (1=Forge, 4=Fabric 등).

---

## 4. 인증 방식

- **방식:** HTTP 헤더 기반 API 키
- **헤더명:** `x-api-key`
- **예시:**

```http
GET https://api.curseforge.com/v1/mods/search?gameId=432&classId=6
x-api-key: YOUR_API_KEY
Accept: application/json
```

- 2026년 7월 16일부터 직접 파일 다운로드(CDN)에도 `x-api-key` 인증이 필수화되었으며, 키 없이 요청 시 `401 Unauthorized` 반환.
- **출처:** [Introducing API Key Authentication for CurseForge File Downloads](https://blog.curseforge.com/introducing-api-key-authentication-for-curseforge-file-downloads/)

---

## 5. Rate Limit 및 이용 제한

### Rate Limit

- **공개된 수치 없음.** 공식 문서에 구체적 한도는 명시되지 않음.
- 한도 초과 시 `403 Forbidden` 또는 `429 Too Many Requests` 에러.
- 재시도 전 대기 시간: 비공식적으로 최대 **1~2시간** 권장.
- 자동화된 대량 요청 시 쉽게 한도에 도달할 수 있다는 사용자 보고 다수.

### 이용 제한 (ToS)

- **모드 파일 재배포 금지:** API를 통해 얻은 모드 파일을 별도 서버에서 재호스팅하는 것은 ToS 위반.
- **저작권 표시 의무:** API 제공 데이터 사용 시 CurseForge 출처 표시 필요.
- **서비스 복제 금지:** CurseForge 앱을 단순 복제하거나 모드 다운로더로만 동작하는 앱은 허용되지 않음.
- **키 공유 금지:** API 키는 등록된 앱에만 사용하며, 타인과 공유 불가.
- **`allowModDistribution` 필드 준수:** `false`인 모드의 직접 다운로드 URL 노출 금지.
- **출처:** [CurseForge 3rd Party API Terms and Conditions](https://support.curseforge.com/en/support/solutions/articles/9000207405-curse-forge-3rd-party-api-terms-and-conditions)

---

## 6. 엔드포인트 예시

### 예시 1: 인기 Forge 모드 50개 조회 (Minecraft 1.20.1)

```http
GET https://api.curseforge.com/v1/mods/search?gameId=432&classId=6&gameVersion=1.20.1&modLoaderType=1&sortField=2&sortOrder=desc&pageSize=50&index=0
x-api-key: YOUR_API_KEY
```

### 예시 2: Fabric 모드, 다음 50개 (페이지네이션)

```http
GET https://api.curseforge.com/v1/mods/search?gameId=432&classId=6&gameVersion=1.20.1&modLoaderType=4&sortField=2&sortOrder=desc&pageSize=50&index=50
x-api-key: YOUR_API_KEY
```

### 예시 3: 특정 모드 ID 배치 조회

100개의 모드 ID를 미리 선정한 경우:

```http
POST https://api.curseforge.com/v1/mods
Content-Type: application/json
x-api-key: YOUR_API_KEY

{
  "modIds": [32274, 238222, 306612],
  "filterPcOnly": true
}
```

### 응답 구조 요약

```json
{
  "data": [
    {
      "id": 32274,
      "name": "JEI (Just Enough Items)",
      "slug": "jei",
      "summary": "View Items and Recipes",
      "downloadCount": 350000000,
      "categories": [{ "id": 421, "name": "Map and Information" }],
      "latestFilesIndexes": [
        { "gameVersion": "1.20.1", "modLoader": 1, "fileId": 1234567 },
        { "gameVersion": "1.20.1", "modLoader": 4, "fileId": 1234568 }
      ],
      "logo": { "thumbnailUrl": "https://..." },
      "authors": [{ "name": "mezz" }],
      "allowModDistribution": true,
      "gamePopularityRank": 1
    }
  ],
  "pagination": {
    "index": 0,
    "pageSize": 50,
    "resultCount": 50,
    "totalCount": 8423
  }
}
```

### 기타 유용한 엔드포인트

| 엔드포인트 | 설명 |
|---|---|
| `GET /v1/categories?gameId=432` | Minecraft 전체 카테고리 목록 |
| `GET /v1/categories?gameId=432&classId=6` | 모드(class 6) 하위 카테고리만 |
| `GET /v1/mods/{modId}` | 특정 모드 단건 조회 |
| `GET /v1/games/432/versions` | Minecraft 지원 버전 목록 |

---

## 권장 사항

1. **사전 데이터 수집 (빌드 타임 캐시) 권장**
   Rate limit이 낮고 실시간 조회가 불필요하므로, 서버 배포 시 또는 주기적 크론잡으로 인기 모드 100개의 메타데이터를 미리 수집하여 로컬 JSON/DB에 캐싱한다. 사용자 설문 응답 시에는 캐시된 데이터만 조회하여 API 호출을 최소화한다.

2. **수집 쿼리 전략**
   `sortField=2`(Popularity) + `sortOrder=desc` + `pageSize=50`으로 2회 호출(index=0, index=50)하면 인기 모드 100개 수집 완료. Forge/Fabric 각각 50개씩 또는 모드로더 무관 상위 100개 — 요구사항에 따라 선택.

3. **모드로더 & 버전 정보 활용**
   `latestFilesIndexes[]`의 `modLoader` + `gameVersion` 조합으로 Forge/Fabric/Quilt/NeoForge 지원 여부를 태깅하여 설문 필터로 사용.

4. **`allowModDistribution` 필드 준수**
   `allowModDistribution: false`인 모드의 직접 다운로드 URL 노출 금지. 모드 상세 페이지 CurseForge 링크 제공은 항상 가능.

5. **출처 표시 (ToS 준수)**
   UI에 "모드 데이터 제공: CurseForge" 문구 및 CurseForge 링크 포함.

6. **API 키 관리**
   키를 환경변수(`CURSEFORGE_API_KEY`)로 관리하고, 클라이언트 코드에 하드코딩 금지. 프론트엔드에서 직접 호출하지 말고 서버사이드(백엔드 API)에서만 호출.

---

*출처 목록*

- CurseForge API 공식 문서: <https://docs.curseforge.com/rest-api/>
- API 키 신청 안내: <https://support.curseforge.com/en/support/solutions/articles/9000208346-about-the-curseforge-api-and-how-to-apply-for-a-key>
- 3rd Party API ToS: <https://support.curseforge.com/en/support/solutions/articles/9000207405-curse-forge-3rd-party-api-terms-and-conditions>
- 파일 다운로드 API 키 인증 도입 공지: <https://blog.curseforge.com/introducing-api-key-authentication-for-curseforge-file-downloads/>
