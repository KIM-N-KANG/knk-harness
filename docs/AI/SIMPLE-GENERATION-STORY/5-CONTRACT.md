# 5. 계약

| 항목 | 값 |
|---|---|
| 적용 태스크 | 스토리라인 생성, 스토리 컴파일 |
| 버전 | 0.1 |

본 문서는 ([4-2 소프트웨어 설계](4-2-DESIGN-SOFTWARE-ARCHITECTURE.md))에서 정의한 시스템 간 연결을 요청과 응답의 계약으로 구체화한다.

스토리라인과 컴파일 API의 요청 필드, 응답 구조, 필수값과 형식 제약을 명시한다. 정상 결과와 처리 실패의 응답, 요청 식별과 메타데이터, 대기 한도와 복구 책임을 정한다. 모델 호출 인터페이스와 권한 및 호환성 규칙도 다룬다.

<br>

### 5-1 연동 대상과 방식

이 문서의 예시는 구조를 설명하기 위한 가상 값이다. 실제 사용자 입력, 이미지 데이터와 호출 기록이 아니다.

AI 서버가 API를 제공하고 백엔드가 사용한다. 요청, 정상 응답과 422·502 오류 응답은 JSON이며 필드 이름은 `snake_case`를 사용한다. 500 응답은 실패 계약을 따른다. ([5-4 계약](#5-4-실패-계약))

백엔드는 응답을 동기로 기다린다. 대기 한도는 시간 계약을 따른다. ([5-6 계약](#5-6-시간과-복구))

상태 확인은 모델 API의 상태를 확인하지 않는다.

| 요청 | 방식 | 성공 | 실패 |
|---|---|---|---|
| 스토리라인 생성 | `POST /api/v1/story/storylines` | 200<br>후보 3편 | 422, 500 또는 502 |
| 컴파일 | `POST /api/v1/story/compile` | 200<br>스토리 설정과 이미지 | 422, 500 또는 502 |
| 상태 확인 | `GET /api/v1/health` | 200<br>`status`, `version` | 별도 정의 없음 |

<br>

### 5-2 스토리라인 요청과 결과

주변 인물 수와 특징 태그 수는 백엔드가 검사한다. AI 서버는 검사하지 않는다. 이름을 입력한 인물끼리 이름이 같으면 422를 반환한다. 앞뒤 공백과 대소문자는 구분하지 않는다.

AI 서버는 `genre_tags`가 빈 배열인지 검사하지 않는다.

| 요청 필드 | 타입 | 필수 | 뜻과 기본값 |
|---|---|---|---|
| `genre_tags` | `string[]` | 필수 | 장르 태그 |
| `protagonist` | `object` | 필수 | 주인공 |
| `protagonist.name` | `string / null` | 선택 | 이름<br>`null`이면 AI가 결정 |
| `protagonist.gender` | `string / null` | 선택 | `MALE` 또는 `FEMALE`<br>`null`이면 AI가 결정 |
| `protagonist.features` | `string[] / null` | 선택 | 특징 태그<br>생략하거나 `null`이면 빈 배열 |
| `supporting_characters` | `object[] / null` | 선택 | 주변 인물<br>생략하거나 `null`이면 빈 배열 |
| `supporting_characters[].name` | `string / null` | 선택 | 이름<br>`null`이면 AI가 결정 |
| `supporting_characters[].gender` | `string / null` | 선택 | `MALE` 또는 `FEMALE`<br>`null`이면 AI가 결정 |
| `supporting_characters[].features` | `string[] / null` | 선택 | 특징 태그<br>생략하거나 `null`이면 빈 배열 |

<br>

**응답**

200 응답은 후보 3편, 비어 있지 않은 줄거리와 후보별 추천 정보 3개를 보장한다. 추천 정보의 문장이 비었는지는 검사하지 않는다. 이름을 입력한 인물이 빠진 후보가 있어도 200으로 반환하며 응답에는 따로 표시하지 않는다.

백엔드는 사용자가 고른 줄거리와 추천 정보를 컴파일 요청의 `selected_storyline`과 `additional_info`로 보낸다.

| 응답 필드 | 타입 | 뜻 |
|---|---|---|
| `stories` | `object[]` | 후보 3편 |
| `stories[].id` | `integer` | 후보 번호 1, 2, 3 |
| `stories[].storyline` | `string` | 줄거리 |
| `stories[].recommended_infos` | `string[]` | 추천 추가 정보 3개 |
| `meta` | `object` | 호출 기록<br>계약에 정한 집계 기준 적용 ([5-5 계약](#5-5-식별과-전달)) |

<br>

**요청 예시**

```json
{
  "genre_tags": ["판타지", "미스터리"],
  "protagonist": {
    "name": "서린",
    "gender": "FEMALE",
    "features": ["호기심 많음", "꼼꼼함"]
  },
  "supporting_characters": [
    {
      "name": "도윤",
      "gender": "MALE",
      "features": ["침착함", "과묵함"]
    }
  ]
}
```

<br>

**200 응답 예시**

```json
{
  "stories": [
    {
      "id": 1,
      "storyline": "신입 기록관 서린은 마법 도서관에서 다음 날의 기록이 지워지고 있음을 발견한다. 과묵한 사서 도윤과 함께 사라진 기록의 출처를 추적한다.",
      "recommended_infos": [
        "지워진 기록은 지하 보관실에 흔적으로 남는다.",
        "도윤은 과거 기록 소실 사건의 유일한 목격자다.",
        "기록을 복원하려면 누군가의 잊힌 기억이 필요하다."
      ]
    },
    {
      "id": 2,
      "storyline": "서린은 자신의 이름으로 백 년 전에 작성된 편지를 발견한다. 도윤은 편지의 필체를 알아보지만 발신인을 밝히지 않는다.",
      "recommended_infos": [
        "편지는 보름달이 뜨는 밤에만 읽을 수 있다.",
        "도윤의 스승이 같은 편지를 보관하고 있었다.",
        "편지를 읽을 때마다 도서관의 방 하나가 과거 모습으로 바뀐다."
      ]
    },
    {
      "id": 3,
      "storyline": "도서관의 장서들이 사람의 목소리로 오래된 재판을 증언하기 시작한다. 서린과 도윤은 서로 다른 증언 속에서 진실을 찾는다.",
      "recommended_infos": [
        "장서마다 재판 당시 다른 인물의 기억이 담겨 있다.",
        "도윤은 목소리가 난 책들의 대출 기록을 숨겨 두었다.",
        "마지막 증언은 서린이 직접 빈 책에 기록해야 한다."
      ]
    }
  ],
  "meta": {
    "model": "deepseek-flash",
    "provider": "deepseek",
    "prompt_versions": {
      "STORYLINES": 6
    },
    "input_token_count": 900,
    "output_token_count": 1400,
    "retry_count": 0
  }
}
```

<br>

### 5-3 컴파일 요청과 결과

AI 서버는 줄거리·추가 정보·로어북 길이를 검사하지 않는다.

| 요청 필드 | 타입 | 필수 | 뜻과 기본값 |
|---|---|---|---|
| `selected_storyline` | `string` | 필수 | 사용자가 고른 줄거리 |
| `additional_info` | `string` | 선택 | 추가 정보<br>기본값은 빈 문자열 |
| `genre_tags` | `string[]` | 필수 | 스토리라인 요청과 같은 장르 태그 |
| `protagonist` | `object` | 필수 | 스토리라인 요청과 같은 주인공 구조 ([5-2 계약](#5-2-스토리라인-요청과-결과)) |
| `supporting_characters` | `object[] / null` | 선택 | 스토리라인 요청과 같은 주변 인물 구조 ([5-2 계약](#5-2-스토리라인-요청과-결과)) |
| `lorebooks` | `object[] / null` | 선택 | 세계관 참고 자료<br>생략, 빈 배열과 `null` 허용 |
| `lorebooks[].name` | `string` | 필수 | 자료 이름 |
| `lorebooks[].content` | `string` | 필수 | 내용 |

<br>

**응답**

| 응답 필드 | 타입 | 뜻 |
|---|---|---|
| `stories.title` | `string` | 제목 |
| `stories.one_line_intro` | `string` | 한 줄 소개 |
| `stories.description` | `string` | 상세 소개 |
| `story_settings.world_setting` | `string` | 세계관 통글 |
| `story_settings.character_setting` | `string` | 주변 인물 통글 |
| `story_settings.user_role_setting` | `string` | 주인공 통글 |
| `story_settings.rule_setting` | `string` | 전개 규칙 통글 |
| `story_start_settings.name` | `string` | 시작 설정 이름 |
| `story_start_settings.start_situation` | `string` | 시작 상황 |
| `story_start_settings.prologue` | `string` | 프롤로그 |
| `story_suggested_inputs` | `string[]` | 첫 선택지 3개 |
| `story_main_events[]` | `object[]` | 주요 사건 3개에서 5개<br>`name`, `description`, `key_sentence` |
| `story_endings[]` | `object[]` | 엔딩 3개 또는 빈 배열<br>`name`, `min_turns`, `achievement_condition`, `epilogue` |
| `character_appearances[]` | `object[]` | 주변 인물 전원의 외형<br>최대 5명 |
| `character_appearances[].name` | `string` | 인물 이름<br>항상 채움 |
| `character_appearances[].gender` | `string` | 인물 성별<br>항상 채움 |
| `character_appearances[].age` | `string` | 나이대<br>생성하지 못하면 빈 문자열 |
| `character_appearances[].body` | `string` | 체형<br>생성하지 못하면 빈 문자열 |
| `character_appearances[].face` | `string` | 얼굴<br>생성하지 못하면 빈 문자열 |
| `character_appearances[].hair` | `string` | 머리 모양<br>생성하지 못하면 빈 문자열 |
| `character_appearances[].outfit` | `string` | 의상<br>생성하지 못하면 빈 문자열 |
| `character_appearances[].visual_identity` | `string` | 시각적 대표 특징<br>생성하지 못하면 빈 문자열 |
| `character_images[]` | `object[]` | 인물 이미지 결과 최대 5개<br>인물 카드 순서 |
| `character_images[].name` | `string` | 인물 이름 |
| `character_images[].image_name` | `string` | `인물이름_기본` |
| `character_images[].image_base64` | `string / null` | WebP 데이터<br>실패하면 `null` |
| `character_images[].content_type` | `string` | 항상 `image/webp` |
| `character_images[].error` | `string / null` | 실패 사유<br>성공하면 `null` |
| `thumbnail_image` | `object` | 썸네일 결과<br>항상 객체 |
| `thumbnail_image.image_name` | `string` | `썸네일_기본` |
| `thumbnail_image.image_base64` | `string / null` | WebP 데이터<br>실패하면 `null` |
| `thumbnail_image.content_type` | `string` | 항상 `image/webp` |
| `thumbnail_image.error` | `string / null` | 실패 사유<br>성공하면 `null` |
| `meta` | `object` | 호출 기록<br>계약에 정한 집계 기준 적용 ([5-5 계약](#5-5-식별과-전달)) |

200 응답에서 보장하는 값은 다음과 같다.

썸네일에는 이미지 데이터와 `error` 중 하나만 넣는다.

이미지는 백엔드가 저장한다. AI 서버는 저장소에 쓰지 않는다. `min_turns`는 1 이상이다.

| 구분 | 항목 |
|---|---|
| 항상 채워지는 값 | 제목과 소개<br>스토리 설정 4개<br>시작 설정<br>첫 선택지<br>주요 사건<br>입력한 장르 태그<br>입력한 주인공의 이름과 성별<br>입력한 주변 인물의 이름 |
| 비어 있을 수 있는 값 | `story_endings` 빈 배열<br>`character_appearances`의 외형 값 빈 문자열<br>`character_images` 빈 배열 또는 실패 항목 |
| 확인할 값 | 외형 값 6개가 모두 있으면 이미지 생성 대상<br>외형 값이 하나라도 비면 해당 인물 이미지를 생성하지 않음<br>`image_base64`가 문자열이면 성공<br>`null`이면 `error`에 실패 사유 포함 |

<br>

**요청 예시**

```json
{
  "selected_storyline": "신입 기록관 서린은 마법 도서관에서 다음 날의 기록이 지워지고 있음을 발견한다. 과묵한 사서 도윤과 함께 사라진 기록의 출처를 추적한다.",
  "additional_info": "지워진 기록은 지하 보관실에 흔적으로 남는다.",
  "genre_tags": ["판타지", "미스터리"],
  "protagonist": {
    "name": "서린",
    "gender": "FEMALE",
    "features": ["호기심 많음", "꼼꼼함"]
  },
  "supporting_characters": [
    {
      "name": "도윤",
      "gender": "MALE",
      "features": ["침착함", "과묵함"]
    }
  ],
  "lorebooks": [
    {
      "name": "기록의 잔향",
      "content": "마법으로 지워진 문장은 원본이 보관된 장소에 푸른 빛의 흔적을 남긴다."
    }
  ]
}
```

<br>

**200 응답 예시**

이미지 생성이 시간 초과로 실패했지만 스토리 설정은 완성된 부분 완료 예시다.

```json
{
  "stories": {
    "title": "사라지는 내일의 기록",
    "one_line_intro": "마법 도서관에서 지워진 미래를 추적하는 신입 기록관의 이야기",
    "description": "서린과 도윤은 마법 도서관에서 사라진 기록의 출처를 추적한다."
  },
  "story_settings": {
    "world_setting": "# 세계관\n왕립 마법 도서관은 도시의 과거와 미래를 기록한다. 지워진 문장은 원본 가까이에 푸른 잔향을 남긴다.",
    "character_setting": "# 도윤\n과묵한 남성 사서. 기록을 보호하려 하지만 서린의 조사 능력을 인정한다.",
    "user_role_setting": "# 주인공\n서린은 꼼꼼한 여성 신입 기록관이며 기록 소실 사건을 조사한다.",
    "rule_setting": "# 전개 규칙\n사용자의 선택에 따라 단서를 공개한다.\n# 문체\n차분한 미스터리 분위기를 유지한다."
  },
  "story_start_settings": {
    "name": "폐관 뒤의 도서관",
    "start_situation": "폐관 직후 기록 열람실에서 서린과 도윤이 빛나는 기록장을 살핀다.",
    "prologue": "*마지막 종이 울린 뒤, 서린은 빈 기록장 가장자리에서 푸른 빛을 발견한다.*\n도윤: 아직 퇴근하지 않았군요."
  },
  "story_suggested_inputs": [
    "기록장을 빛에 비춰 본다.",
    "도윤에게 푸른 흔적을 가리킨다.",
    "기록장의 보관 위치를 확인한다."
  ],
  "story_main_events": [
    {
      "name": "기록의 잔향 발견",
      "description": "기록장에 남은 푸른 흔적이 지하 보관실로 이어진다는 단서를 찾는다.",
      "key_sentence": "사라진 문장의 흔적을 조사한다."
    },
    {
      "name": "봉인된 원본 확보",
      "description": "지하 보관실에서 사건 이전의 원본 기록을 확보한다.",
      "key_sentence": "보관실의 봉인을 풀고 원본을 확인한다."
    },
    {
      "name": "소실 원인 규명",
      "description": "원본과 현재 기록을 대조해 문장이 지워진 원인을 알아낸다.",
      "key_sentence": "기록이 바뀐 이유와 관련 인물을 밝힌다."
    }
  ],
  "story_endings": [
    {
      "name": "되찾은 기록",
      "min_turns": 8,
      "achievement_condition": "소실 원인을 밝히고 원본을 보존한다.",
      "epilogue": "서린의 선택이 도서관의 기록을 지켜낸 결과를 보여준다."
    },
    {
      "name": "남겨진 빈 페이지",
      "min_turns": 6,
      "achievement_condition": "추가 소실은 막았지만 사라진 기록을 복원하지 못한다.",
      "epilogue": "서린과 도윤이 남은 단서를 정리하며 다음 조사를 준비한다."
    },
    {
      "name": "사라진 도서관의 기억",
      "min_turns": 6,
      "achievement_condition": "원본까지 잃어 기록의 복원이 불가능해진다.",
      "epilogue": "서린과 도윤이 기록을 잃은 도서관을 떠난다."
    }
  ],
  "character_appearances": [
    {
      "name": "도윤",
      "gender": "남성",
      "age": "30대 초반",
      "body": "키가 크고 마른 체형",
      "face": "갸름한 얼굴과 짙은 눈썹",
      "hair": "짧은 검은 머리",
      "outfit": "남색 사서 제복",
      "visual_identity": "은색 책 모양 브로치"
    }
  ],
  "character_images": [
    {
      "name": "도윤",
      "image_name": "도윤_기본",
      "image_base64": null,
      "content_type": "image/webp",
      "error": "timeout"
    }
  ],
  "thumbnail_image": {
    "image_name": "썸네일_기본",
    "image_base64": null,
    "content_type": "image/webp",
    "error": "timeout"
  },
  "meta": {
    "model": "gpt-5.6-terra",
    "provider": "openai",
    "prompt_versions": {
      "COMPILE": 10,
      "CHARACTER_IMAGE": 1,
      "THUMBNAIL_IMAGE": 1
    },
    "input_token_count": 1700,
    "output_token_count": 4300,
    "retry_count": 0
  }
}
```

<br>

### 5-4 실패 계약

| 상태 | 조건 | 본문 | 설명 |
|---|---|---|---|
| 422 | 요청 스키마 위반 또는 인물 이름 중복 | `detail` 배열<br>항목별 `type`, `loc`, `msg` | 백엔드가 요청 수정 후 재호출 |
| 500 | 요청 처리 중 설정 오류 또는 처리하지 않은 내부 예외 | 공통 JSON 형식을 보장하지 않음 | AI 보완 없이 종료, 담당자가 오류 확인<br>백엔드는 본문 파싱·직접 노출 없이 자체 오류 안내 |
| 502 | 모델 호출 실패<br>보완 후에도 형식이나 필수 항목 위반 | `detail` 문자열<br>아래 메시지 중 하나 | 사용자에게 표시 가능한 한국어 문구만 사용<br>공급자 오류 원문 제외 |

| 502 메시지 | 뜻 | 재시도 |
|---|---|---|
| `LLM 응답 시간이 초과되었습니다.` | 모델이 시간 안에 응답하지 않음 | 가능 |
| `LLM 요청이 일시적으로 제한되었습니다.` | 공급자가 호출량을 제한 | 잠시 뒤 가능 |
| `LLM 요청이 거부되었습니다.` | 공급자가 요청을 거부 | 같은 입력은 불필요 |
| `LLM 연동 중 오류가 발생했습니다.` | 공급자 연결 또는 서버 오류 | 가능 |
| `LLM이 올바른 형식의 응답을 반환하지 않았습니다.` | 보완 후에도 형식이나 필수 항목 위반 | 가능 |
| `재호출 후에도 컴파일 결과에 필수 필드가 비어 있습니다.` | 컴파일 보완 후에도 필수 값이 비어 있음 | 가능 |
| `컴파일 결과가 스토리 명세 형식과 맞지 않습니다.` | 컴파일 결과를 응답 형식으로 바꿀 수 없음 | 가능 |

502를 반환한 뒤 AI 서버는 다시 처리하지 않는다. 백엔드와 사용자가 재시도를 결정한다. 이미지 실패는 502가 아니며 200 응답의 `error`로 전달한다. 공급자 오류 원문은 제외하고 아래 값으로 바꾼다.

인물별 생성 실패는 `character_images`의 해당 항목에 `error`로 표시한다. 모든 인물의 생성이 실패해도 인물별 실패 항목을 반환한다. 이미지 생성 로직 전체에서 예상하지 못한 오류가 발생하면 `character_images`는 빈 배열이다. 썸네일이 실패해도 `thumbnail_image` 객체를 반환하고 `error`를 채운다.

| 이미지 `error` | 뜻 |
|---|---|
| `appearance_missing` | 외형 부족으로 호출하지 않음 |
| `timeout` | 이미지 모델 응답 시간 초과 |
| `rate_limited` | 공급자가 호출량을 제한 |
| `rejected` | 공급자가 요청을 거부 |
| `generation_failed` | 그 밖의 생성 실패 |

Sentry 분류는 응답에 넣지 않는다.

| Sentry 분류 | 값 |
|---|---|
| 공급자 오류 | `provider_timeout`<br>`provider_rate_limited`<br>`provider_bad_request`<br>`provider_unavailable` |
| 응답과 실행 오류 | `invalid_ai_response`<br>`schema_validation_failed`<br>`unexpected_error` |

<br>

**422 응답 예시**

`genre_tags`가 없는 요청의 응답이다.

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "genre_tags"],
      "msg": "Field required"
    }
  ]
}
```

<br>

**502 응답 예시**

```json
{
  "detail": "LLM 응답 시간이 초과되었습니다."
}
```

<br>

**500 응답 예시**

```http
HTTP/1.1 500 Internal Server Error
Content-Type: text/plain; charset=utf-8

Internal Server Error
```

디버그 모드가 꺼진 서버의 기본 오류 응답 예시다. 백엔드는 본문의 형식이나 문구에 의존하지 않고 HTTP 상태 코드 500을 기준으로 생성 실패를 처리한다.


<br>

### 5-5 식별과 전달

헤더가 없거나 값이 `unknown`이면 요청을 허용하고 기록만 생략한다. AI 서버는 관측 도구의 `trace` 식별자를 응답하지 않는다. 백엔드는 `X-Manyak-Request-Id`로 기록을 대조한다.

| 요청 헤더 | 필수 | 쓰임 |
|---|---|---|
| `X-Manyak-Request-Id` | 선택 | 백엔드 로그와 AI 관측 기록 연결 |
| `X-Manyak-Session-Id` | 선택 | 클라이언트 접속 세션 식별 |
| `X-Manyak-Device-Id-Hash` | 선택 | 기기 식별자의 해시<br>원문은 받지 않음 |
| `X-Manyak-Creation-Id` | 선택 | 스토리라인 생성부터 컴파일까지 같은 제작 과정으로 연결 |
| `X-Manyak-Parent-Creation-Id` | 선택 | 재생성 전 제작 요청과 연결 |
| `X-Manyak-Storyline-Id` | 선택 | 컴파일에 사용한 스토리라인 식별 |
| `X-Manyak-Storyline-Order` | 선택 | 컴파일에 사용한 후보 번호 식별 |

<br>

**응답 `meta`**

`model`은 본 텍스트 호출의 실제 모델이며 `provider`는 호출 전에 모델 등록부에서 정한다. `prompt_versions`에는 실제 사용한 템플릿 버전을 기록하며, 컴파일은 컴파일·인물 이미지·썸네일 버전을 모두 포함한다.

입출력 토큰 수에는 본 호출, 전체 재생성과 부분 보완을 합산하고 이미지 호출은 제외한다. `retry_count`에는 전체 재생성과 부분 보완만 포함하고 SDK 재시도는 제외한다.

응답을 받지 못한 호출의 토큰 수는 빠질 수 있어 실제 청구액과 다를 수 있다. `retry_count`는 스토리라인 0에서 4, 컴파일 0에서 2다.

| 필드 | 타입 | 뜻 |
|---|---|---|
| `model` | `string` | 실제 호출한 모델 |
| `provider` | `string` | 모델 공급자 |
| `prompt_versions` | `map<string, integer>` | 프롬프트 이름별 버전 |
| `input_token_count` | `integer / null` | 입력 토큰 수<br>알 수 없으면 `null` |
| `output_token_count` | `integer / null` | 출력 토큰 수<br>알 수 없으면 `null` |
| `retry_count` | `integer` | SDK 내부 재시도를 제외한 추가 호출 수 |

<br>

**중복과 순서**

| 상황 | 처리 주체와 기준 |
|---|---|
| 같은 요청을 두 번 수신 | AI 서버가 두 번 처리<br>결과가 다를 수 있음 |
| 중복 방지, 결과 저장과 실패 후 재요청 | 백엔드가 요청 식별자로 관리 |
| 스토리라인 생성과 컴파일 순서 | 백엔드가 선택 상태를 관리<br>AI 서버는 확인하지 않음 |

<br>

### 5-6 시간과 복구

SDK 재시도와 AI 결과 보완은 복구 구분을 따른다. ([7-1-3 오류 처리](7-1-ERROR-HANDLING.md#7-1-3-복구-구분))

| 계층 | 책임 |
|---|---|
| 백엔드 | 전체 대기 한도와 시간 초과 처리 |
| AI 서버 | 생성과 보완 호출별 시간 제한 적용 |
| 모델 SDK | 전송 오류 자동 재시도<br>AI 결과 보완 횟수와 별도 계산 |

스토리라인 생성의 형식 재호출은 최초 생성의 90초 안에 끝낸다. 인물 누락 보완은 호출마다 90초를 적용한다.

컴파일은 최초 생성과 각 보완 호출에 90초를 적용한다. 인물 이미지와 썸네일은 한 장마다 60초를 적용하며 동시에 생성한다.

AI 서버는 스토리라인 생성 전체 90초와 컴파일 전체 180초를 따로 제한하지 않는다. 백엔드 연결이 먼저 끝나도 진행 중인 호출은 바로 취소하지 않는다.

| 항목 | 스토리라인 생성 | 컴파일 |
|---|---|---|
| 백엔드 전체 대기 한도 | 90초 | 180초 |
| 최초 텍스트 생성 한도 | 형식 재호출 포함 90초 | 90초 |
| 텍스트 보완 호출 한도 | 호출마다 90초 | 호출마다 90초 |
| 이미지 모델 한 번의 호출 한도 | 없음 | 60초 |

<br>

### 5-7 권한과 호환성

| 항목 | 규칙 |
|---|---|
| 인증과 권한 | 백엔드가 확인<br>AI 서버는 사용자 권한을 확인하지 않음 |
| 응답과 로그 | 공급자 오류 원문, API 키와 사용자 입력 원문을 넣지 않음 |
| 관측 도구 | 구조화한 입력만 허용<br>수집 범위는 관측 규칙에서 정의 ([7-3 관측](7-3-OBSERVABILITY.md)) |
| 호환 변경 | 필드 추가<br>백엔드는 모르는 필드를 무시 |
| 비호환 변경 | 필드 삭제, 이름과 타입 및 상태 코드 변경<br>백엔드 대응 후 배포 |
| 프롬프트 버전 변경 | 응답 형식을 유지<br>`meta.prompt_versions`에 버전 기록 |

<br>

### 5-8 모델 게이트웨이 계약

호출부는 공급자 SDK를 직접 호출하지 않고 LLM 호출 모듈만 사용한다. LLM 호출 모듈은 모델 이름으로 공급자와 어댑터를 정한다.

- 등록되지 않은 모델은 서버를 시작할 때 오류로 처리한다
- 공급자별 추론 설정과 허용 인자는 모델 등록부가 관리한다

| LLM 호출 모듈 | 내용 |
|---|---|
| 요청 | 시스템 프롬프트, 사용자 프롬프트, 모델 이름, 출력 길이 한도와 시간 제한 |
| 결과 | 본문, 토큰 수, 실제 모델 이름과 공급자 이름 |
| 예외 | 시간 초과, 호출량 제한, 요청 거부와 공급자 불가 |

<br>

**이미지 생성 모듈**

컴파일 호출부는 이미지 생성 예외를 정해진 이미지 `error`로 바꾼다. ([5-4 계약](#5-4-실패-계약))

인물 이미지 로직 전체에서 예상하지 못한 오류가 발생하면 빈 배열로 바꾼다. 모델 이름, 크기와 화질의 기본값은 AI 실행에서 정한다. ([6-1 AI 실행](6-1-AI-EXECUTION.md))

실제 파일과 함수는 소프트웨어 구현에서 정한다. ([6-2 소프트웨어 구현](6-2-SOFTWARE-IMPLEMENTATION.md))

| 방향 | 내용 |
|---|---|
| 요청 | 이미지 프롬프트, 크기, 화질과 시도당 시간 제한 |
| 결과 | WebP 바이너리와 모델 및 공급자 정보 |
| 예외 | 이미지 생성 예외 발생 |
