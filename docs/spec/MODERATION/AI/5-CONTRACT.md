# 5. 계약

<br>

### 5-1 연동 대상과 방식

| 호출자 | 방식 | 응답 |
|---|---|---|
| 백엔드 | `POST /api/v1/moderation/story`<br>JSON 요청과 응답 | 200: 승인, 반려 또는 검수 실패<br>422: 요청 형식 오류<br>500: 예상하지 못한 서버 오류 |

<br>

### 5-2 요청

| 필드명 | 타입 | 필수 여부와 기본값 | 의미 |
|---|---|---|---|
| `submissionId` | `string (UUID)` | 필수 | 검수 제출본 식별자<br>관측 기록 연결용, 판정에서 제외 |
| `storyId` | `string` | 선택, `null`<br>빈 문자열 허용 | 기존 스토리 식별자<br>관측 기록 연결용, 판정에서 제외 |
| `protagonistName` | `string` | 선택, `null`<br>빈 문자열 허용 | 토큰으로 치환하기 전 기본 주인공 이름 |
| `title`, `oneLineIntro`, `description` | `string` | 선택, `null`<br>빈 문자열 허용 | 제목, 한 줄 소개, 상세 소개 |
| `genres` | `string[]` | 선택, `null`<br>빈 배열 허용 | 장르 |
| `storySettings` | `object` | 선택, `null` | 스토리 설정 |
| `storySettings.worldSetting` | `string` | 선택, `null`<br>빈 문자열 허용 | 세계관 |
| `storySettings.characterSetting` | `string` | 선택, `null`<br>빈 문자열 허용 | 주변 인물 설정 |
| `storySettings.userRoleSetting` | `string` | 선택, `null`<br>빈 문자열 허용 | 주인공 설정 |
| `storySettings.ruleSetting` | `string` | 선택, `null`<br>빈 문자열 허용 | 전개 규칙 |
| `startSettings` | `object[]` | 선택, `null`<br>빈 배열 허용 | 시작 설정 |
| `startSettings[].name`, `startSettings[].prologue`, `startSettings[].startSituation` | `string` | 선택, `null`<br>빈 문자열 허용 | 이름, 프롤로그, 시작 상황 |
| `startSettings[].suggestedInputs` | `string[]` | 선택, `null`<br>빈 배열 허용 | 첫 선택지 |
| `startSettings[].endings` | `object[]` | 선택, `null`<br>빈 배열 허용 | 엔딩 |
| `startSettings[].endings[].name`, `startSettings[].endings[].epilogue` | `string` | 선택, `null`<br>빈 문자열 허용 | 엔딩 이름, 에필로그 |
| `startSettings[].endings[].requirement` | `object` | 선택, `null` | 엔딩 조건 |
| `startSettings[].endings[].requirement.achievementCondition` | `string` | 선택, `null`<br>빈 문자열 허용 | 달성 조건 |
| `mainEvents` | `object[]` | 선택, `null`<br>빈 배열 허용 | 주요 사건 |
| `mainEvents[].name`, `mainEvents[].description`, `mainEvents[].keySentence` | `string` | 선택, `null`<br>빈 문자열 허용 | 사건 이름, 설명, 키 문장 |
| `thumbnailUrl` | `string` | 선택, `null`<br>빈 문자열 허용 | 썸네일 이미지 주소 |
| `characters` | `object[]` | 선택, `null`<br>빈 배열 허용 | 주변 인물 |
| `characters[].name`, `characters[].description` | `string` | 선택, `null`<br>빈 문자열 허용 | 인물 이름, 설명 |
| `characters[].images` | `object[]` | 선택, `null`<br>빈 배열 허용 | 인물 이미지 |
| `characters[].images[].imageName`, `characters[].images[].imageUrl` | `string` | 선택, `null`<br>빈 문자열 허용 | 이미지 이름, 주소 |
| 정의하지 않은 필드 | 제한 없음 | 선택 | 무시 |

<br>

**이미지 입력 조건**

| 항목 | 조건 |
|---|---|
| 주소 | 허용된 호스트의 HTTPS 주소, 포트 443, 사용자 인증 정보 없음<br>빈 주소는 이미지 없음으로 처리 |
| 형식 | JPEG, PNG, GIF, WebP |
| 장당 크기 | 기본 상한 32MiB |
| 모델 전송 용량 | base64 이미지, 텍스트와 JSON을 포함해 48MiB 이하 |

<details>
<summary><b>요청 예시</b></summary>

<br>

```json
{
  "submissionId": "00000000-0000-4000-8000-000000000001",
  "title": "별을 찾는 도서관",
  "genres": ["판타지"]
}
```

</details>

<br>

### 5-3 응답

응답은 아래 필드를 항상 포함하며 `meta`는 반환하지 않는다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `decision` | `string` | `APPROVED` 또는 `REJECTED` |
| `issues` | `object[]` | 확인한 내용 위반 |
| `issues[].path` | `string` | 입력의 필드 경로<br>배열 인덱스는 0부터 시작 |
| `issues[].type` | `string` | `TEXT` 또는 `IMAGE` |
| `issues[].rule` | `string` | 위반 기준 코드 |
| `issues[].reason` | `string` | 한국어 위반 이유 |
| `error_code` | `string / null` | 검수 실행 오류의 대표 코드 |
| `image_errors` | `object[]` | 이미지별 실행 오류 |
| `image_errors[].path` | `string` | 오류가 발생한 이미지의 입력 경로 |
| `image_errors[].error_code` | `string` | 이미지 오류 코드 |

| 결과 | `decision` | `issues` | `error_code` | `image_errors` |
|---|---|---|---|---|
| 승인 | `APPROVED` | `[]` | `null` | `[]` |
| 내용 위반 | `REJECTED` | 위반 항목 | `null` | `[]` |
| 검수 실패 | `REJECTED` | 확인한 위반이 있으면 보존 | 오류 코드 | 이미지 오류가 있으면 포함 |

<br>

**위반 기준 코드**

| 코드 | 의미 |
|---|---|
| `EXPLICIT_SEXUAL_CONTENT` | 노골적인 성적 표현 |
| `DRUGS` | 마약 |
| `EXTREME_GORE` | 극단적인 잔혹 표현 |
| `SELF_HARM_PROMOTION` | 자살과 자해 조장 |
| `HATE_VIOLENCE_INCITEMENT` | 혐오 폭력 선동 |
| `GAMBLING_PROMOTION` | 불법 도박 사이트 이용 안내 |

<details>
<summary><b>응답 예시</b></summary>

<br>

**1) 승인**

```json
{
  "decision": "APPROVED",
  "issues": [],
  "error_code": null,
  "image_errors": []
}
```

**2) 내용 위반**

```json
{
  "decision": "REJECTED",
  "issues": [
    {
      "path": "description",
      "type": "TEXT",
      "rule": "DRUGS",
      "reason": "마약 관련 금지 내용이 포함되어 있음."
    }
  ],
  "error_code": null,
  "image_errors": []
}
```

**3) 이미지 실패**

```json
{
  "decision": "REJECTED",
  "issues": [],
  "error_code": "IMAGE_DOWNLOAD_FAILED",
  "image_errors": [
    {
      "path": "thumbnailUrl",
      "error_code": "IMAGE_DOWNLOAD_FAILED"
    }
  ]
}
```

</details>

<br>

### 5-4 실패 계약

오류 코드와 처리 기준은 오류 처리 문서에서 정의한다. ([7-1 오류 처리](7-1-ERROR-HANDLING.md))

<br>

### 5-5 외부 모델 API 계약

**1. OpenAI 호환 Chat Completions API**

| 요청 항목 | API 인자와 호출 방식 |
|---|---|
| API | `openai` SDK의 `chat.completions.create` |
| 모델 이름 | `model`<br>기본: `MODERATION_MODEL`, 대체: `MODERATION_FALLBACK_MODEL` |
| 메시지 | `messages[]`의 `role`, `content`<br>시스템 검수 기준과 사용자 게시물 |
| 이미지 | `content[]`의 `image_url.url`에 base64 data URL |
| JSON 출력 | OpenAI: `response_format.type="json_schema"`, `strict=true`<br>DeepSeek: `response_format.type="json_object"` |
| 추론 설정 | OpenAI: `reasoning_effort="high"`<br>DeepSeek: `extra_body.thinking.type="disabled"` |
| 호출 제한 시간 | `timeout`, 초 단위 |

| 응답 항목 | 출처 |
|---|---|
| 판정 JSON 문자열 | `choices[0].message.content`<br>`decision`, `issues[]`의 `path`, `rule`, `reason`<br>이미지 판독 불가이면 `rule=null` |
| 종료 사유 | `choices[0].finish_reason` |
| 입력 토큰 | `usage.prompt_tokens` |
| 출력 토큰 | `usage.completion_tokens` |
| 실제 모델 이름 | 응답 `model`, 없으면 요청 모델 이름 |

<details>
<summary><b>요청과 응답 구조 예시</b></summary>

<br>

**1) OpenAI 요청**

```text
model: <모델 이름>
messages:
  - role: system
    content: <검수 기준>
  - role: user
    content:
      - type: text
        text: <게시물 JSON과 이미지 경로>
      - type: image_url
        image_url:
          url: data:image/webp;base64,<이미지 데이터>
response_format:
  type: json_schema
  json_schema:
    name: response
    strict: true
    schema: <판정 JSON 스키마>
reasoning_effort: high
timeout: <호출 제한 시간, 초>
```

<br>

**2) 응답의 `choices[0].message.content`**

```json
{
  "decision": "APPROVED",
  "issues": []
}
```

</details>
