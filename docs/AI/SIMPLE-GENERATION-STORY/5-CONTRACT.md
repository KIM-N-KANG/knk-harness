# 5. 계약

본 문서는 AI 서버가 백엔드·외부 모델 API와 통신할 때 지켜야 하는 규약을 정의한다.

백엔드와의 스토리라인·컴파일 API 계약, 외부 모델과의 텍스트·이미지 생성 API 계약을 다룬다.

<br>

### 5-1 연동 대상과 방식

| 요청 | 방식 | 성공 | 실패 |
|---|---|---|---|
| 스토리라인 생성 | `POST /api/v1/story/storylines` | 200<br>후보 3편 | 422, 500 또는 502 |
| 컴파일 | `POST /api/v1/story/compile` | 200<br>스토리 설정과 이미지 | 422, 500 또는 502 |
| 상태 확인 | `GET /api/v1/health` | 200<br>`status`, `version` | 별도 정의 없음 |

<br>

### 5-2 스토리라인 요청과 결과

**1. 요청 필드**

| 필드명 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `genre_tags` | `string[]` | 필수 | 장르 태그 |
| `protagonist` | `object` | 필수 | 주인공 |
| `protagonist.name` | `string / null` | 선택 | 이름<br>생략·`null`·공백만 있는 값은 AI가 결정 |
| `protagonist.gender` | `string / null` | 선택 | `MALE` 또는 `FEMALE`<br>생략하거나 `null`이면 AI가 결정 |
| `protagonist.features` | `string[] / null` | 선택 | 특징 태그 최대 3개 (백엔드 검증)<br>생략하거나 `null`이면 빈 배열 |
| `supporting_characters` | `object[] / null` | 선택 | 주변 인물 0~5명 (백엔드 검증)<br>생략하거나 `null`이면 빈 배열<br>빈 객체 `{}`도 한 명으로 취급 |
| `supporting_characters[].name` | `string / null` | 선택 | 이름<br>생략·`null`·공백만 있는 값은 AI가 결정 |
| `supporting_characters[].gender` | `string / null` | 선택 | `MALE` 또는 `FEMALE`<br>생략하거나 `null`이면 AI가 결정 |
| `supporting_characters[].features` | `string[] / null` | 선택 | 특징 태그 최대 3개 (백엔드 검증)<br>생략하거나 `null`이면 빈 배열 |

<br>

**2. 응답 필드**

| 필드명 | 타입 | 뜻 |
|---|---|---|
| `stories` | `object[]` | 후보 3편 |
| `stories[].id` | `integer` | 후보 번호 1, 2, 3 |
| `stories[].storyline` | `string` | 줄거리 |
| `stories[].recommended_infos` | `string[]` | 추천 추가 정보 3개 |
| `meta` | `object` | 호출 기록<br>계약에 정한 집계 기준 적용 ([5-5 계약](#5-5-요청-헤더와-메타데이터)) |

<details>
<summary><strong>요청·응답 예시</strong></summary>

<br>

**1) Request body**

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

**2) 200 Response body**

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
    "model": "<실제 사용한 모델 이름>",
    "provider": "google",
    "prompt_versions": {
      "STORYLINES": 7
    },
    "input_token_count": 900,
    "output_token_count": 1400,
    "retry_count": 0
  }
}
```

</details>

<br>

### 5-3 컴파일 요청과 결과

**1. 요청 필드**

| 필드명 | 타입 | 필수 | 뜻과 기본값 |
|---|---|---|---|
| `selected_storyline` | `string` | 필수 | 사용자가 고른 줄거리 |
| `additional_info` | `string` | 선택 | 항목당 최대 100자, 최대 13개를 백엔드가 검사한 뒤 줄바꿈으로 합쳐 전달<br>기본값은 빈 문자열 |
| `genre_tags` | `string[]` | 필수 | 스토리라인 요청과 같은 장르 태그 |
| `protagonist` | `object` | 필수 | 스토리라인 요청과 같은 주인공 구조 ([5-2 계약](#5-2-스토리라인-요청과-결과)) |
| `supporting_characters` | `object[] / null` | 선택 | 스토리라인 요청과 같은 주변 인물 구조 ([5-2 계약](#5-2-스토리라인-요청과-결과)) |
| `lorebooks` | `object[] / null` | 선택 | 세계관 참고 자료<br>생략, 빈 배열과 `null` 허용 |
| `lorebooks[].name` | `string` | 필수 | 자료 이름 |
| `lorebooks[].content` | `string` | 필수 | 내용 |

<br>

**2. 응답 필드**

| 필드명 | 타입 | 값 필수 여부 | 뜻 |
|---|---|---|---|
| `stories.title` | `string` | 필수 | 제목 |
| `stories.one_line_intro` | `string` | 필수 | 한 줄 소개 |
| `stories.description` | `string` | 필수 | 상세 소개 |
| `story_settings.world_setting` | `string` | 필수 | 세계관 마크다운 본문 |
| `story_settings.character_setting` | `string` | 필수 | 주변 인물 마크다운 본문 |
| `story_settings.user_role_setting` | `string` | 필수 | 주인공 마크다운 본문 |
| `story_settings.rule_setting` | `string` | 필수 | 전개 규칙 마크다운 본문 |
| `story_start_settings.name` | `string` | 필수 | 시작 설정 이름 |
| `story_start_settings.start_situation` | `string` | 필수 | 시작 상황 |
| `story_start_settings.prologue` | `string` | 필수 | 프롤로그 |
| `story_suggested_inputs` | `string[]` | 필수 | 첫 선택지 3개 |
| `story_main_events` | `object[]` | 필수 | 주요 사건 3개에서 5개 |
| `story_main_events[].name` | `string` | 필수 | 사건 이름 |
| `story_main_events[].description` | `string` | 필수 | 사건 설명 |
| `story_main_events[].key_sentence` | `string` | 필수 | 사용자 입력과 사건의 관련성을 판단하는 문장 |
| `story_endings` | `object[]` | 선택 | 엔딩 3개 또는 빈 배열 |
| `story_endings[].name` | `string` | 필수 | 엔딩 이름 |
| `story_endings[].min_turns` | `integer` | 필수 | 최소 턴 수<br>1 이상 |
| `story_endings[].achievement_condition` | `string` | 필수 | 엔딩 달성 조건 |
| `story_endings[].epilogue` | `string` | 필수 | 에필로그 연출 방향 |
| `character_appearances[]` | `object[]` | 필수 | 주변 인물 전원의 외형<br>최대 5명 |
| `character_appearances[].name` | `string` | 필수 | 인물 이름 |
| `character_appearances[].gender` | `string` | 필수 | 인물 성별 |
| `character_appearances[].age` | `string` | 이미지 필수 | 나이대<br>생성하지 못하면 빈 문자열 |
| `character_appearances[].body` | `string` | 이미지 필수 | 체형<br>생성하지 못하면 빈 문자열 |
| `character_appearances[].face` | `string` | 이미지 필수 | 얼굴<br>생성하지 못하면 빈 문자열 |
| `character_appearances[].hair` | `string` | 이미지 필수 | 머리 모양<br>생성하지 못하면 빈 문자열 |
| `character_appearances[].outfit` | `string` | 이미지 필수 | 의상<br>생성하지 못하면 빈 문자열 |
| `character_appearances[].visual_identity` | `string` | 이미지 필수 | 시각적 대표 특징<br>생성하지 못하면 빈 문자열 |
| `character_images[]` | `object[]` | 선택 | 인물 이미지 결과 최대 5개<br>인물 카드 순서<br>빈 배열 허용 |
| `character_images[].name` | `string` | 필수 | 인물 이름 |
| `character_images[].image_name` | `string` | 필수 | `인물이름_기본` |
| `character_images[].image_base64` | `string / null` | 이미지 성공 시 필수 | WebP 데이터<br>실패하면 `null` |
| `character_images[].content_type` | `string` | 필수 | 항상 `image/webp` |
| `character_images[].error` | `string / null` | 이미지 실패 시 필수 | 실패 사유<br>성공하면 `null` |
| `thumbnail_image` | `object` | 필수 | 썸네일 결과 객체 |
| `thumbnail_image.image_name` | `string` | 필수 | `썸네일_기본` |
| `thumbnail_image.image_base64` | `string / null` | 이미지 성공 시 필수 | WebP 데이터<br>실패하면 `null` |
| `thumbnail_image.content_type` | `string` | 필수 | 항상 `image/webp` |
| `thumbnail_image.error` | `string / null` | 이미지 실패 시 필수 | 실패 사유<br>성공하면 `null` |
| `meta` | `object` | 필수 | 호출 기록<br>계약에 정한 집계 기준 적용 ([5-5 계약](#5-5-요청-헤더와-메타데이터)) |

<details>
<summary><strong>요청·응답 예시</strong></summary>

<br>

**1) Request body**

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

**2) 200 Response body — 전체 완료**

스토리 설정, 인물 이미지와 썸네일이 모두 생성된 예시다. 이미지의 Base64 문자열은 생략했다.

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
      "image_base64": "<WebP 이미지의 Base64 문자열>",
      "content_type": "image/webp",
      "error": null
    }
  ],
  "thumbnail_image": {
    "image_name": "썸네일_기본",
    "image_base64": "<WebP 이미지의 Base64 문자열>",
    "content_type": "image/webp",
    "error": null
  },
  "meta": {
    "model": "<실제 사용한 모델 이름>",
    "provider": "google",
    "prompt_versions": {
      "COMPILE": 11,
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

**3) 200 Response body — 부분 완료**

인물 이미지와 썸네일 생성이 시간 초과로 실패한 경우다. 전체 완료 예시와 달라지는 필드만 표시했다.

```json
{
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
  }
}
```

</details>

<br>

### 5-4 실패 계약

422·500·502의 조건, 본문 형식, 502 메시지와 이미지 `error` 값은 오류 처리에서 정한다. ([7-1-5 실패 출력](7-1-ERROR-HANDLING.md#7-1-5-실패-출력))

<br>

### 5-5 요청 헤더와 메타데이터

**1. 요청 헤더**

| 요청 헤더 | 값 형식 | 쓰임 | 필수 |
| --- | --- | --- | --- |
| `X-Manyak-Request-Id` | 문자열 | 백엔드 로그와 AI 관측 기록 연결 | 선택 |
| `X-Manyak-Session-Id` | 문자열 | 클라이언트 접속 세션 식별 | 선택 |
| `X-Manyak-Device-Id-Hash` | 해시 문자열 | 기기 식별자의 해시 | 선택 |
| `X-Manyak-Creation-Id` | UUID 문자열 | `trace_creation_id`로 스토리라인 생성과 컴파일 연결 | 선택 |
| `X-Manyak-Parent-Creation-Id` | UUID 문자열 | 스토리라인 재생성 시 검증된 직전 `trace_creation_id` 전달 | 선택 |
| `X-Manyak-Storyline-Id` | 양의 정수 문자열 | 컴파일에 사용한 스토리라인 ID | 선택 |
| `X-Manyak-Storyline-Order` | 정수 문자열 (1~3) | 컴파일에 사용한 후보 번호 | 선택 |

<br>

**2. 응답 `meta`**

| 필드명 | 타입 | 뜻 |
|---|---|---|
| `model` | `string` | 본 텍스트 호출의 실제 모델 이름 |
| `provider` | `string` | 모델 공급자 |
| `prompt_versions` | `map<string, integer>` | 실제 사용한 템플릿의 이름별 버전<br>컴파일 요청은 컴파일·인물 이미지·썸네일 템플릿 버전 포함 |
| `input_token_count` | `integer / null` | 본 호출·전체 재생성·부분 보완의 입력 토큰 합계<br>이미지 호출 제외, 알 수 없으면 `null`<br>응답 없는 호출은 누락될 수 있어 실제 청구량과 다를 수 있음 |
| `output_token_count` | `integer / null` | 본 호출·전체 재생성·부분 보완의 출력 토큰 합계<br>이미지 호출 제외, 알 수 없으면 `null`<br>응답 없는 호출은 누락될 수 있어 실제 청구량과 다를 수 있음 |
| `retry_count` | `integer` | 전체 재생성과 부분 보완의 호출 횟수<br>SDK 재시도 제외<br>스토리라인 0~4회, 컴파일 0~2회 |

<br>

### 5-6 외부 모델 API 계약

#### 1. Google Gemini API

**1. 요청**

| 항목 | API 인자·호출 방식 |
|---|---|
| API | `google-genai` SDK의 `generate_content` |
| 모델 이름 | `model` |
| 작성 규칙 (시스템 프롬프트) | `config.system_instruction` |
| 입력을 채운 프롬프트 | `contents[0]` (`role="user"`) |
| 출력 토큰 한도 | `config.max_output_tokens` |
| 생성 온도 | `config.temperature` |
| 추론 강도 | `config.thinking_config.thinking_level` |
| 호출 제한 시간 | `config.http_options.timeout` (ms) |
| JSON 모드 | `config.response_mime_type="application/json"` |

<br>

**2. 응답**

| 결과 | 출처 |
|---|---|
| 본문 | `response.text`. 비어 있어도 예외를 내지 않고 호출부가 판정 |
| 입력 토큰 | `usage_metadata.prompt_token_count` |
| 출력 토큰 | `usage_metadata.candidates_token_count`와 `thoughts_token_count`의 합 |
| 실제 모델 이름 | 응답의 모델 이름. 비어 있으면 요청에 쓴 이름 |

<details>
<summary><strong>텍스트 요청·응답 구조 예시</strong></summary>

<br>

```text
요청
  model: <모델 이름>
  config.max_output_tokens: <출력 토큰 한도>
  config.temperature: <생성 온도>
  config.thinking_config.thinking_level: <추론 강도>
  config.http_options.timeout: <호출 제한 시간, 밀리초>
  config.system_instruction: <조립된 시스템 프롬프트>
  contents:
    - role: user
      parts:
        - text: <조립된 사용자 프롬프트>
  config.response_mime_type: application/json

응답
  text: <생성 결과를 담은 JSON 문자열>
  usage_metadata:
    prompt_token_count: 900
    candidates_token_count: 1200
    thoughts_token_count: 200
```

</details>

<br>

#### 2. OpenAI Images API

**1. 요청**

| 항목 | API 인자·호출 방식 |
|---|---|
| API | `openai` SDK의 `images.generate` |
| 모델 이름 | `model` |
| 화질 | `quality` |
| 이미지 크기 | `size` (`가로x세로`) |
| 호출·연결 제한 시간 | `timeout` |
| 이미지 프롬프트 | `prompt` |
| 출력 형식 | `output_format="webp"` |
| 장수 | `n=1` |

<br>

**2. 응답**

| 결과 | 출처 |
|---|---|
| WebP 이미지 1장 | `data[0].b64_json` (Base64 문자열) |
| 실제 모델 이름 | 요청에 쓴 이름 |

<details>
<summary><strong>이미지 요청·응답 구조 예시</strong></summary>

<br>

```text
요청
  model: <모델 이름>
  quality: <생성 화질>
  size: <가로x세로>
  timeout: <호출·연결 제한 시간>
  prompt: <조립된 이미지 프롬프트>
  output_format: webp
  n: 1

응답
  data:
    - b64_json: <WebP 이미지의 Base64 문자열>
```

</details>
