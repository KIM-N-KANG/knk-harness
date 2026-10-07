# 5. 계약

본 문서는 AI 서버가 백엔드와 외부 모델 API와 통신할 때 지켜야 하는 규약을 정의한다.

채팅 턴과 선택지 API의 요청, 응답, 오류와 메타데이터, 외부 텍스트와 이미지 모델의 호출 형식을 다룬다.

<br>

### 5-1 연동 대상과 방식

| 요청 | 방식 | 성공 | 실패 |
|---|---|---|---|
| 채팅 턴 | `POST /api/v1/chat/turns` | 200, SSE<br>본문과 판정 결과 | 422, 500 또는 SSE `error` |
| 선택지 생성 | `POST /api/v1/chat/choices` | 200, JSON<br>선택지 3개 | 422 또는 500 |

<br>

### 5-2 채팅 턴 요청과 결과

**1. 요청 필드**

| 필드명 | 타입 | 필수 | 뜻과 기본값 |
|---|---|---|---|
| `genre` | `string` | 필수 | 장르 |
| `story_settings` | `object` | 필수 | 스토리 설정 |
| `story_settings.world_setting` | `string` | 필수 | 세계관 마크다운 본문 |
| `story_settings.character_setting` | `string` | 필수 | 주변 인물 마크다운 본문 |
| `story_settings.user_role_setting` | `string` | 필수 | 주인공 마크다운 본문 |
| `story_settings.rule_setting` | `string` | 필수 | 전개 규칙 마크다운 본문 |
| `start_settings` | `object` | 필수 | 선택한 시작 설정 |
| `start_settings.name` | `string` | 필수 | 시작 설정 이름 |
| `start_settings.prologue` | `string` | 필수 | 프롤로그 |
| `start_settings.start_situation` | `string` | 필수 | 시작 상황 |
| `history` | `object[]` | 선택 | 이번 턴 이전 대화와 오프닝, 시간순<br>기본값 `[]` |
| `history[].role` | `string` | 필수 | `USER` 또는 `ASSISTANT`<br>오프닝은 `ASSISTANT` |
| `history[].content` | `string` | 필수 | 메시지 본문 |
| `user_input` | `string` | 필수 | 이번 턴의 사용자 입력 |
| `summary` | `string` | 필수 | 대화 요약<br>없으면 빈 문자열 |
| `user_source` | `string / null` | 선택 | 입력 출처: `choice`, `edited_choice`, `typed`<br>앞뒤 공백 제거, 허용값이 아니면 `null`<br>기본값 `null` |
| `main_events` | `object[]` | 선택 | 주요 사건 최대 10개<br>기본값 `[]` |
| `main_events[].name` | `string` | 필수 | 사건 이름 |
| `main_events[].description` | `string` | 필수 | 사건 설명 |
| `main_events[].key_sentence` | `string` | 필수 | 사용자 입력과 사건의 관련성을 판단하는 문장 |
| `target_main_event` | `object / null` | 선택 | 이전 턴의 목표 사건<br>기본값 `null` |
| `target_main_event.name` | `string` | 필수 | 목표 사건 이름 |
| `target_main_event.progress_turns` | `integer` | 필수 | 진행 턴 수, 0 이상 |
| `occurred_main_event_names` | `string[]` | 선택 | 이전 턴까지 완결된 사건 이름의 누적 목록<br>기본값 `[]` |
| `endings` | `object[]` | 선택 | 최소 턴 수를 충족한 엔딩 후보<br>기본값 `[]`, 이미 엔딩에 도달했으면 `[]` |
| `endings[].name` | `string` | 필수 | 엔딩 이름 |
| `endings[].achievement_condition` | `string` | 필수 | 엔딩 달성 조건 |
| `endings[].epilogue` | `string` | 필수 | 엔딩 연출 방향 |
| `character_images` | `object[]` | 선택 | 저장된 인물 이미지 목록<br>기본값 `[]` |
| `character_images[].name` | `string` | 필수 | 인물의 정식 이름 |
| `character_images[].image_name` | `string / null` | 선택 | 이미지 이름, 기본 이미지는 `인물이름_기본`<br>생략과 `null`은 빈 문자열 |
| `character_images[].image_url` | `string` | 필수 | 이미지 URL |
| `image_slots` | `object[]` | 선택 | 실시간 이미지 업로드 슬롯 최대 1개<br>기본값 `[]`, 비어 있으면 생성하지 않음 |
| `image_slots[].key` | `string` | 필수 | 저장 객체 키<br>빈 문자열과 공백만 있는 값은 허용하지 않음 |
| `image_slots[].upload_url` | `string` | 필수 | WebP 바이너리를 `PUT`할 서명 URL<br>`Content-Type: image/webp`, 허용된 업로드 호스트만 사용 |
| `image_slots[].public_url` | `string` | 필수 | 업로드 성공 후 반환할 이미지 URL |
| `generate_child_image` | `boolean` | 선택 | 이전 요청 호환용, 기본값 `false`<br>생성 여부는 `image_slots`로 결정 |

슬롯의 두 URL은 HTTPS만 허용하며 사용자 정보, fragment, 공백과 443 이외의 포트는 허용하지 않는다.

<br>

**2. 응답 이벤트**

`Content-Type`은 `text/event-stream`이다. 각 프레임은 `event: 이름`, `data: JSON`과 빈 줄로 구성한다.

| 이벤트 | 필드명 | 타입 | 뜻 |
|---|---|---|---|
| `token` | `text` | `string` | 본문 조각 |
| `character_image` | `name` | `string` | 인물의 정식 이름 |
| `character_image` | `imageName` | `string` | 이미지 이름 |
| `character_image` | `imageUrl` | `string` | 이미지 URL |
| `ping` | 없음 | `object` | 대기 중 연결 유지, `{}` |
| `completed` | 아래 완료 필드 | `object` | 정상 종료 |
| `error` | `code`, `message` | `string` | 실패 코드와 메시지 ([5-4 실패 계약](#5-4-실패-계약)) |

`character_image`는 해당 인물의 첫 대사 앞에 온다. 실시간 이미지를 요청한 턴은 이미지 처리 후 본문을 전달한다. `started`, `chatId`, `turnId`는 백엔드가 부착한다.

<br>

**3. 완료 필드**

| 필드명 | 타입 | 뜻 |
|---|---|---|
| `aiOutput` | `string` | 최종 본문<br>이미지 위치에 `[[URL]]` 마커와 빈 줄 포함 |
| `choices` | `string[]` | 하위 호환용 빈 배열 고정 |
| `characterImages` | `object[]` | 본문에 연결한 이미지, 표시 순서<br>인물마다 최대 1개, 빈 배열 허용 |
| `characterImages[].name` | `string` | 인물의 정식 이름 |
| `characterImages[].imageName` | `string` | 요청의 이미지 이름<br>실시간 이미지 성공 시 `인물이름_실시간_UUID` |
| `characterImages[].imageUrl` | `string` | 기본 이미지 URL 또는 슬롯의 `public_url` |
| `targetMainEvent` | `object / null` | 다음 턴의 목표 사건<br>없거나 이번 턴에 완결됐으면 `null` |
| `targetMainEvent.name` | `string` | 미완결 주요 사건 이름 |
| `targetMainEvent.progressTurns` | `integer` | 진행 턴 수, 0 이상 |
| `occurredMainEventName` | `string / null` | 이번 턴에 완결된 사건 이름<br>없으면 `null` |
| `endingName` | `string / null` | 도달한 엔딩 후보 이름<br>없으면 `null` |
| `meta` | `object` | 호출 기록 ([5-5 요청 헤더와 메타데이터](#5-5-요청-헤더와-메타데이터)) |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request body**

```json
{
  "genre": "판타지",
  "story_settings": {
    "world_setting": "# 세계관\n마법 도서관에는 지워진 기록의 흔적이 남는다.",
    "character_setting": "# 도윤\n침착한 도서관 사서.",
    "user_role_setting": "# 서린\n기록을 조사하는 신입 기록관.",
    "rule_setting": "# 전개 규칙\n사용자의 행동에 따라 단서를 공개한다."
  },
  "start_settings": {
    "name": "폐관 뒤의 도서관",
    "prologue": "*마지막 종이 울린다.*",
    "start_situation": "기록 열람실에서 조사를 시작한다."
  },
  "history": [],
  "user_input": "기록장에 남은 흔적을 살핀다.",
  "summary": "",
  "user_source": "typed",
  "main_events": [
    {
      "name": "원본 발견",
      "description": "사라진 기록의 원본을 찾는다.",
      "key_sentence": "기록의 흔적을 추적한다."
    }
  ],
  "target_main_event": null,
  "occurred_main_event_names": [],
  "endings": [],
  "character_images": [
    {
      "name": "도윤",
      "image_name": "도윤_기본",
      "image_url": "https://images.example.com/doyun.webp"
    }
  ],
  "image_slots": []
}
```

<br>

**2) 200 Response stream**

```text
event: token
data: {"text":"*기록장 가장자리에 푸른 흔적이 떠오른다.*\n"}

event: character_image
data: {"name":"도윤","imageName":"도윤_기본","imageUrl":"https://images.example.com/doyun.webp"}

event: token
data: {"text":"도윤: 지하 보관실로 이어지는 흔적이군요."}

event: ping
data: {}

```

**3) completed 이벤트의 data**

```json
{
  "aiOutput": "*기록장 가장자리에 푸른 흔적이 떠오른다.*\n[[https://images.example.com/doyun.webp]]\n\n도윤: 지하 보관실로 이어지는 흔적이군요.",
  "choices": [],
  "characterImages": [
    {
      "name": "도윤",
      "imageName": "도윤_기본",
      "imageUrl": "https://images.example.com/doyun.webp"
    }
  ],
  "targetMainEvent": {
    "name": "원본 발견",
    "progressTurns": 1
  },
  "occurredMainEventName": null,
  "endingName": null,
  "meta": {
    "model": "gpt-6-luna",
    "provider": "openai",
    "promptVersions": {
      "CORE": 1,
      "SAFETY": 1,
      "STORY": 1,
      "CHARACTER": 1,
      "USER": 1,
      "MEMORY": 1,
      "JUDGEMENT": 1
    },
    "inputTokenCount": 1200,
    "outputTokenCount": 300,
    "retryCount": 0
  }
}
```

</details>

<br>

### 5-3 선택지 요청과 결과

**1. 요청 필드**

| 필드명 | 타입 | 필수 | 뜻 |
|---|---|---|---|
| 채팅 턴 요청 필드 | 5-2와 같음 | 5-2와 같음 | 같은 설정과 사용자 입력<br>`history`는 이번 턴 제외<br>목표 사건과 누적 완결 사건은 이번 판정 반영 ([5-2 계약](#5-2-채팅-턴-요청과-결과)) |
| `ai_output` | `string` | 필수 | 이번 턴의 `aiOutput` |

<br>

**2. 응답 필드**

| 필드명 | 타입 | 뜻 |
|---|---|---|
| `choices` | `string[]` | 다음 행동 후보 3개 |
| `meta` | `object` | 호출 기록 ([5-5 요청 헤더와 메타데이터](#5-5-요청-헤더와-메타데이터)) |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request body**

```json
{
  "genre": "판타지",
  "story_settings": {
    "world_setting": "# 세계관\n마법 도서관에는 지워진 기록의 흔적이 남는다.",
    "character_setting": "# 도윤\n침착한 도서관 사서.",
    "user_role_setting": "# 서린\n기록을 조사하는 신입 기록관.",
    "rule_setting": "# 전개 규칙\n사용자의 행동에 따라 단서를 공개한다."
  },
  "start_settings": {
    "name": "폐관 뒤의 도서관",
    "prologue": "*마지막 종이 울린다.*",
    "start_situation": "기록 열람실에서 조사를 시작한다."
  },
  "history": [],
  "user_input": "기록장에 남은 흔적을 살핀다.",
  "summary": "",
  "main_events": [
    {
      "name": "원본 발견",
      "description": "사라진 기록의 원본을 찾는다.",
      "key_sentence": "기록의 흔적을 추적한다."
    }
  ],
  "occurred_main_event_names": [],
  "target_main_event": {
    "name": "원본 발견",
    "progress_turns": 1
  },
  "ai_output": "*기록장 가장자리에 푸른 흔적이 떠오른다.*\n[[https://images.example.com/doyun.webp]]\n\n도윤: 지하 보관실로 이어지는 흔적이군요."
}
```

<br>

**2) 200 Response body**

```json
{
  "choices": [
    "지하 보관실로 향한다.",
    "도윤에게 기록장의 출처를 묻는다.",
    "열람실에 다른 흔적이 있는지 살핀다."
  ],
  "meta": {
    "model": "<실제 선택지 모델 이름>",
    "provider": "<모델 공급자>",
    "prompt_versions": {
      "NEXT_ACTIONS": 1
    },
    "input_token_count": 800,
    "output_token_count": 100,
    "retry_count": 0
  }
}
```

</details>

<br>

### 5-4 실패 계약

실패 조건, 오류 응답과 복구 방법은 오류 처리 문서에서 자세히 다룬다. ([7-1 오류 처리](7-1-ERROR-HANDLING.md))

<br>

### 5-5 요청 헤더와 메타데이터

**1. 요청 헤더**

| 요청 헤더 | 값 형식 | 쓰임 | 필수 |
|---|---|---|---|
| `X-Manyak-Request-Id` | 문자열 | 백엔드 로그와 AI 관측 기록 연결 | 선택 |
| `X-Manyak-Session-Id` | 문자열 | 클라이언트 접속 세션 식별 | 선택 |
| `X-Manyak-Device-Id-Hash` | 해시 문자열 | 기기 식별자의 해시 | 선택 |
| `X-Manyak-Creation-Id` | 문자열 | 제작 결과 연결 | 선택 |
| `X-Manyak-Story-Id` | 문자열 | 스토리 연결 | 선택 |
| `X-Manyak-Chat-Id` | 문자열 | 채팅 연결 | 선택 |
| `X-Manyak-Start-Setting-Id` | 문자열 | 시작 설정 연결 | 선택 |
| `X-Manyak-Turn-Number` | 정수 문자열 | 턴 번호, 1~2,147,483,647 | 선택 |
| `X-Manyak-Is-Regenerated` | `true` 또는 `false` | 재생성 여부 | 선택 |

<br>

**2. 응답 `meta`**

| 채팅 턴 필드명 | 선택지 필드명 | 타입 | 뜻 |
|---|---|---|---|
| `model` | `model` | `string` | 실제 본문 또는 선택지 모델 이름 |
| `provider` | `provider` | `string` | 모델 공급자 |
| `promptVersions` | `prompt_versions` | `map<string, integer>` | 템플릿별 버전<br>채팅: `CORE`, `SAFETY`, `STORY`, `CHARACTER`, `USER`, `MEMORY`, `JUDGEMENT`<br>선택지: `NEXT_ACTIONS` |
| `inputTokenCount` | `input_token_count` | `integer / null` | 입력 토큰 합계<br>채팅은 본문과 판정, 선택지는 최초 생성과 보완 호출<br>이미지 제외, 알 수 없으면 `null` |
| `outputTokenCount` | `output_token_count` | `integer / null` | 같은 집계 범위의 출력 토큰 합계<br>알 수 없으면 `null` |
| `retryCount` | `retry_count` | `integer` | 보완 호출 횟수, SDK 재시도 제외<br>채팅은 0, 선택지는 0~2 |

<br>

### 5-6 외부 모델 API 계약

**1. 텍스트 Chat Completions API**

| 요청 항목 | API 인자와 호출 방식 |
|---|---|
| API | `openai` SDK의 `chat.completions.create` |
| 모델 이름 | `model`<br>본문과 판정은 `CHAT_MODEL`, 선택지는 `CHAT_CHOICE_MODEL`<br>프로덕션 `CHAT_MODEL`은 `gpt-6-luna` |
| 메시지 | `messages[]`의 `role`, `content` |
| 본문 스트리밍 | `stream=true`, `stream_options.include_usage=true` |
| 판정과 선택지 JSON 모드 | `response_format.type="json_object"` |
| 출력 토큰 한도 | OpenAI는 `max_completion_tokens`, DeepSeek은 `max_tokens` |
| 추론 설정 | `gpt-6-luna`: `reasoning_effort="none"`<br>`deepseek-flash`: `extra_body.thinking.type="disabled"` |
| 호출 제한 시간 | `timeout`, 초 단위 |

<br>

| 응답 항목 | 출처 |
|---|---|
| 본문 조각 | `choices[0].delta.content` |
| 판정 또는 선택지 JSON 문자열 | `choices[0].message.content` |
| 입력 토큰 | `usage.prompt_tokens` |
| 출력 토큰 | `usage.completion_tokens` |
| 실제 모델 이름 | 응답 `model`, 없으면 요청 모델 이름 |

<details>
<summary><b>텍스트 요청·응답 구조 예시</b></summary>

<br>

```text
본문 요청
  model: gpt-6-luna
  messages:
    - role: system
      content: <조립된 시스템 프롬프트>
    - role: user
      content: <조립된 사용자 프롬프트>
  stream: true
  stream_options:
    include_usage: true
  reasoning_effort: none
  timeout: <호출 제한 시간, 초>

본문 응답 조각
  choices:
    - delta:
        content: <본문 조각>

판정 응답의 message.content
  {"target_main_event":{"name":"원본 발견","progress_turns":1},"occurred_main_event_name":null,"ending_name":null}

선택지 응답의 message.content
  {"choices":["지하 보관실로 향한다.","도윤에게 기록장의 출처를 묻는다.","열람실을 살핀다."]}
```

</details>

<br>

**2. OpenAI Images API**

| 요청 항목 | API 인자와 호출 방식 |
|---|---|
| API | `openai` SDK의 `images.edit` |
| 모델 이름 | `model` |
| 기본 이미지 | `image`: 파일명, 바이너리, MIME 타입 |
| 이미지 프롬프트 | `prompt` |
| 화질 | `quality` |
| 이미지 크기 | `size` (`가로x세로`) |
| 호출 제한 시간 | `timeout` |
| 출력 형식 | `output_format="webp"` |
| 장수 | `n=1` |

<br>

| 응답 항목 | 출처 |
|---|---|
| WebP 이미지 1장 | `data[0].b64_json` (Base64 문자열) |
| 실제 모델 이름 | 요청에 쓴 이름 |

<details>
<summary><b>이미지 요청·응답 구조 예시</b></summary>

<br>

```text
요청
  model: <모델 이름>
  image: <기본 이미지 파일>
  prompt: <조립된 이미지 프롬프트>
  quality: <생성 화질>
  size: <가로x세로>
  timeout: <호출 제한 시간>
  output_format: webp
  n: 1

응답
  data:
    - b64_json: <WebP 이미지의 Base64 문자열>
```

</details>
