# 6-2 소프트웨어 구현

| 항목 | 값 |
|---|---|
| 적용 태스크 | 간편 제작 스토리 생성(스토리라인 생성, 컴파일, 인물 이미지와 썸네일 생성) |
| 버전 | 0.1 |

이 문서는 AI 실행을 구현하는 코드 구조와 규칙을 정한다. ([6-1 AI 실행](6-1-AI-EXECUTION.md))

실행 순서, 프롬프트 조립과 모델 설정은 AI 실행의 규칙을 따른다. ([6-1 AI 실행](6-1-AI-EXECUTION.md))

모든 경로는 `manyak-ai` 저장소 루트 기준이다.

<br>

### 6-2-1 파일 배치

```text
├── src/
│   ├── main.py                         앱 생성, 시작 검사, 관측 초기화
│   ├── api/
│   │   ├── router.py                   /api/v1 라우터 구성
│   │   └── v1/
│   │       └── story.py                스토리라인과 컴파일 엔드포인트
│   ├── schemas/
│   │   ├── story.py                    인물 입력, 스토리라인 요청과 응답
│   │   ├── story_compile.py            컴파일 요청과 응답, 내부 스토리 명세
│   │   └── response_meta.py            응답 meta
│   ├── services/
│   │   ├── story_llm.py                스토리 서비스
│   │   ├── prompt.py                   텍스트 프롬프트 조립
│   │   ├── prompt_meta.py              템플릿 버전 읽기
│   │   ├── story_compile_render.py     통글 변환
│   │   ├── llm/                       텍스트 모델 통로
│   │   └── image/                     이미지 모델 통로와 이미지 생성
│   └── core/
│       ├── config.py                   환경 변수 설정
│       ├── sentry.py                   오류 보고
│       ├── langfuse.py                 호출 관측
│       ├── json_logging.py             JSON 로그 형식
│       ├── middleware.py               요청 식별자 전달
│       └── request_context.py          요청 식별자 전달
├── prompt/
│   ├── story/                         스토리라인과 컴파일 템플릿
│   └── image/                         인물 이미지와 썸네일 템플릿
└── tests/
    ├── unit/                          단위 테스트
    ├── integration/                   실제 호출 테스트
    ├── test_storylines_api.py
    └── test_story_compile_api.py
```

구성 요소별 구현 파일은 다음과 같다. ([4-2-3 구성 요소](4-2-DESIGN-SOFTWARE-ARCHITECTURE.md#4-2-3-구성-요소))

| 구성 요소 | 파일 | 공유 범위 |
|---|---|---|
| 라우터 | `src/api/v1/story.py` | 스토리 전용 |
| 스토리 서비스 | `src/services/story_llm.py` | 스토리 전용 |
| 프롬프트 빌더 | `src/services/prompt.py` <br> `src/services/image/prompt.py` | 스토리 전용 |
| LLM 통로 | `src/services/llm/__init__.py`, `base.py`, `registry.py` <br> 어댑터 `openai_sdk.py`, `anthropic_sdk.py`, `google_sdk.py` | 채팅과 공유 |
| 이미지 통로 | `src/services/image/__init__.py`, `base.py`, `openai_api.py` | 채팅의 자식 이미지와 공유 |
| 인물 이미지, 썸네일 생성 | `src/services/image/generate_characters.py` <br> `src/services/image/generate_thumbnail.py` | 스토리 전용 |
| 통글 렌더러 | `src/services/story_compile_render.py` | 스토리 전용 |
| 관측 계층 | `src/core/sentry.py`, `src/core/langfuse.py` | 채팅과 공유 |

- 위 파일은 모두 구현된 상태다. 평가 CLI는 미구현이며 별도의 평가 구현 문서에서 설계를 정한다. ([6-5 평가 구현](6-5-AI-EVALUATION-IMPLEMENTATION.md))
- 채팅과 공유하는 파일을 바꾸면 채팅 테스트도 함께 실행한다.
- 의존 방향은 `api` → `services` → 통로 → 공급자 SDK다. 모든 계층에서 `schemas`와 `core`를 가져올 수 있다. 통로와 어댑터에서는 `api`와 스토리 서비스를 가져오지 않는다.
- 새 엔드포인트는 `src/api/v1/` 아래 파일에 추가하고 `src/api/router.py`에 등록한다. 라우터 파일 하나에는 라우터 인스턴스를 하나만 둔다.

<br>

### 6-2-2 인터페이스와 모델

<br>

**공개 함수**

| 함수 | 위치 | 입력 | 반환 | 비동기 | 오류 |
|---|---|---|---|---|---|
| `generate_storylines` | `api/v1/story.py` | `StorylinesRequest` | `StorylinesResponse` | 예 | 서비스의 `HTTPException` 전달 |
| `create_story_compile` | `api/v1/story.py` | `StoryCompileRequest` | `StoryCompileResponse` | 예 | 서비스의 `HTTPException` 전달 |
| `generate_storylines` | `services/story_llm.py` | 시스템 프롬프트, 사용자 프롬프트, `required_names` | `(dict, LlmUsage)` | 예 | 502 `HTTPException` <br> 예외의 `retry_count` 속성에 재호출 횟수 |
| `compile_story` | `services/story_llm.py` | `StoryCompileRequest` | `StoryCompileResponse` | 예 | 502 `HTTPException` |
| `build_storylines_prompt` | `services/prompt.py` | 장르 태그, 주인공, 주변 인물 | `(system, user)` | 아니오 | 없음 |
| `build_compile_prompt` | `services/prompt.py` | 컴파일 입력, `provider` | `(system, user, 버전 키)` | 아니오 | 없음 |
| `build_storylines_refill_prompt` <br> `build_refill_prompt` | `services/prompt.py` | 기존 사용자 프롬프트, 직전 결과 JSON, 보완 대상 | `(system, user)` | 아니오 | 없음 |
| `spec_to_response` | `services/story_compile_render.py` | `StorySpec`, `thumbnail_image` | `StoryCompileResponse` | 아니오 | 없음 |
| `llm.complete` | `services/llm/__init__.py` | `LlmRequest` | `LlmResult` | 예 | `LlmError` 계열, `LlmConfigError` |
| `llm.provider_of` | `services/llm/__init__.py` | 모델 이름 | 공급자 이름 | 아니오 | `LlmConfigError` |
| `generate_image` | `services/image/__init__.py` | 프롬프트, `purpose`, `size` | `ImageResult` | 예 | `ImageGenerationError` 계열 |
| `generate_character_images` | `services/image/generate_characters.py` | 인물 카드 목록, 장르 태그 | `list[CharacterImageResult]` | 예 | 공급자 실패는 결과의 `error`로 반환 |
| `generate_thumbnail_image` | `services/image/generate_thumbnail.py` | 인물 카드 목록, 장르 태그 | `ThumbnailImageResult` | 예 | 공급자 실패는 결과의 `error`로 반환 |
| `build_image_prompt` | `services/image/prompt.py` | 인물 카드, 장르 태그 | `str` 또는 `None` | 아니오 | 외형이 비면 `None` |
| `build_thumbnail_prompt` | `services/image/prompt.py` | 인물 카드 목록, 장르 태그 | `str` | 아니오 | 없음 |

스토리 서비스는 본 호출과 보완 호출에 모두 `_complete_json`을 쓴다. 이 함수는 요청 조립, 응답 파싱과 오류 응답의 재호출을 맡는다. 토큰 사용량을 합산하고 호출 실패를 502로 변환하는 일도 맡는다.

<br>

**데이터 모델**

| 구분 | 모델 | 형식 | 위치 |
|---|---|---|---|
| 외부 요청과 응답 | `StorylinesRequest`, `StorylinesResponse`, `StoryCompileRequest`, `StoryCompileResponse`, `StoryResponseMeta` | Pydantic | `src/schemas/` |
| 내부 스토리 명세 | `StorySpec`과 하위 모델 | Pydantic | `src/schemas/story_compile.py` |
| 텍스트 통로 | `LlmRequest`, `LlmResult`, `TokenUsage` | 값을 바꿀 수 없는 dataclass | `src/services/llm/base.py` |
| 이미지 통로 | `ImageRequest`, `ImageResult` | 값을 바꿀 수 없는 dataclass | `src/services/image/base.py` |
| 서비스 내부 결과 | `LlmUsage`, `CharacterImageResult`, `ThumbnailImageResult` | dataclass | 각 서비스 파일 |

| 변환 | 책임 |
|---|---|
| 요청 JSON → 요청 모델, 입력 정규화 | `src/schemas/`의 검증기 |
| 요청 모델 → 프롬프트 문자열 | 프롬프트 빌더 |
| 모델 응답 텍스트 → `dict` | `_complete_json` |
| `dict` → `StorySpec` | `compile_story` |
| `StorySpec` → `StoryCompileResponse` | `spec_to_response` |
| 이미지 바이너리 → Base64 응답 항목 | `_generate_character_images_safe`, `_generate_thumbnail_image_safe` |
| 공급자 SDK 응답과 예외 → 통로 타입 | 각 어댑터 |

<br>

**예외**

| 예외 | 뜻 | 처리 위치 |
|---|---|---|
| `LlmTimeout`, `LlmRateLimited`, `LlmBadRequest`, `LlmUnavailable` | 응답을 받지 못한 전송 오류 | 어댑터에서 예외 발생, `_complete_json`에서 502로 변환 |
| `_InvalidAiResponse`, `json.JSONDecodeError` | 응답 형식이나 내용이 유효하지 않음 | `_complete_json`이 재호출하거나 502로 변환 |
| `LlmConfigError` | 미등록 모델, 키 누락 등 설정 오류 | 서버 시작 검사 <br> `LlmError`를 상속하지 않아 502로 바뀌지 않음 |
| `ImageTimeout`, `ImageRateLimited`, `ImageBadRequest`, `ImageGenerationError` | 이미지 생성 실패 | 이미지 생성 함수가 결과의 `error`로 변환 |

오류 코드와 응답 문구는 실패 계약, 복구 기준은 오류 처리를 따른다. ([5-4 실패 계약](5-CONTRACT.md#5-4-실패-계약), [7-1 오류 처리](7-1-ERROR-HANDLING.md))

<br>

**스토리 서비스의 책임**

스토리라인 생성도 컴파일처럼 서비스가 프롬프트 조립, 모델 호출, 결과 검증·보완과 최종 응답 조립을 맡도록 통일한다. 라우터는 요청을 서비스에 전달하고 완성된 응답을 반환하며, 요청 단위 관측을 맡는다. 이 변경은 별도 티켓에서 구현한다. ([KNK-1336](https://kimandkang.atlassian.net/browse/KNK-1336))

<br>

### 6-2-3 의존성

| 대상 | 생성 위치 | 전달 방식 |
|---|---|---|
| 설정 | `src/core/config.py`의 `settings` | 모듈에서 직접 가져옴 |
| 텍스트 SDK 클라이언트 | 각 어댑터의 `_client` | 첫 호출 때 생성 <br> 공급자·주소·키 지문이 같으면 재사용 |
| 이미지 SDK 클라이언트 | `src/services/image/openai_api.py`의 `_client` | 첫 호출 때 생성 <br> 키 지문·주소가 같으면 재사용 |
| 프롬프트 템플릿과 버전 | `services/prompt.py`, `services/image/prompt.py` | 모듈을 가져올 때 한 번 읽음 |
| 모델 등록부 | `src/services/llm/registry.py` | 통로만 접근 |
| Sentry, Langfuse | `src/main.py`에서 초기화 | 호출부가 `capture_ai_exception`, `observe_request`를 직접 호출 |

- 의존성 주입 도구는 쓰지 않는다. FastAPI의 `Depends`도 스토리 경로에서는 쓰지 않는다.
- 제한 시간은 SDK 클라이언트에 고정하지 않고 호출마다 요청에 넣는다. 전송 재시도 횟수는 클라이언트를 만들 때 지정한다.
- 어댑터는 통로 안에서 필요할 때 가져온다. 통로 모듈의 맨 위에서 가져오면 관측 모듈과 순환 참조가 생긴다.
- 템플릿이 없거나 `version`이 없으면 모듈을 가져올 때 `RuntimeError`가 나고 서버가 시작하지 않는다.
- Sentry DSN과 Langfuse 키가 비어 있으면 관측 기능은 꺼진다. 요청 처리는 계속한다.

`src/main.py`의 실행 순서는 다음과 같다.

1. JSON 로그 설정
2. Sentry와 Langfuse 순서로 초기화
3. 텍스트 모델과 이미지 모델 순서로 시작 검사
4. 앱 생성

앱이 종료되면 아직 보내지 않은 Langfuse 기록을 전송한다.

<br>

**테스트에서 대체하는 경계**

| 경계 | 대체 방법 | 사용처 |
|---|---|---|
| 공급자 SDK 클라이언트 | `tests/conftest.py`의 `install_llm_sdk`가 어댑터의 `_client`를 교체 | 등록부, 인자 조립, 응답 해석과 예외 변환까지 검증하는 단위 테스트 |
| 모델 등록부 | `other_provider_model`이 시험용 모델을 임시 등록 | 공급자를 모델 이름으로 정하는지 검증 |
| 스토리 서비스의 모델 호출 | `story_llm._complete_json` 교체 | API 테스트, 보완과 병합 테스트 |
| 이미지 생성 | `_generate_character_images_safe`, `_generate_thumbnail_image_safe` 교체 | 컴파일 API 테스트 |
| 관측 | `SENTRY_DSN`, Langfuse 키를 비움 <br> 필요하면 `observe_request` 교체 | 모든 테스트 |

모델 호출 경로를 검증할 때는 SDK 클라이언트를 테스트용으로 교체한다. 통로나 호출부를 교체하면 인자 조립과 예외 변환을 검증할 수 없다.

<br>

### 6-2-4 외부 라이브러리

| 라이브러리 | 버전 범위 | 용도 | 사용 위치 |
|---|---|---|---|
| Python | 3.11 이상 | 실행 환경 | 전체 |
| `fastapi` | 0.115.0 이상 | 라우터, HTTP 예외 | `api`, `main`, `story_llm` |
| `uvicorn[standard]` | 0.30.0 이상 | 서버 실행 | 배포 |
| `pydantic-settings` | 2.0.0 이상 | 환경 변수 설정 | `core/config.py` |
| `openai` | 3.3.1 이상 | DeepSeek와 OpenAI 텍스트, OpenAI 이미지 | `llm/openai_sdk.py`, `image/openai_api.py` |
| `google-genai` | 2.0.0 이상 | Google 텍스트 | `llm/google_sdk.py` |
| `anthropic` | 0.120.0 이상 1 미만 | Anthropic 텍스트 | `llm/anthropic_sdk.py` |
| `sentry-sdk[fastapi]` | 2.0.0 이상 | 오류 보고 | `core/sentry.py` |
| `langfuse` | 4.0.0 이상 5 미만 | 호출 관측 | `core/langfuse.py` |
| `pytest`, `pytest-asyncio`, `pytest-cov`, `httpx` | 개발 의존성 | 테스트 | `tests/` |

- 공급자 SDK는 어댑터 파일에서만 가져온다. 스토리 서비스와 프롬프트 빌더는 통로와 통로의 공용 타입만 가져온다.
- 버전 범위는 `pyproject.toml`에서만 바꾼다. 최소 버전은 실제로 확인한 버전으로 정한다. 0.x 라이브러리에는 최대 버전 범위도 지정한다.
- 새 공급자를 추가할 때는 어댑터 파일, 등록부 항목, 설정의 키와 주소를 함께 추가한다. 호출부는 바꾸지 않는다.
- JSON 로그는 표준 라이브러리로 만든다. 로그용 라이브러리를 추가하지 않는다.

<br>

### 6-2-5 구현 규칙

공통 코드 규칙은 `manyak-ai`의 `.agents/STYLEGUIDE.md`를 따른다. 이 절에는 스토리 구현에 적용하는 규칙을 적는다.

| 대상 | 규칙 |
|---|---|
| 이름 | 변수와 함수는 `snake_case`, 클래스는 `PascalCase`, 상수는 `UPPER_SNAKE_CASE` <br> 모듈 밖에서 쓰지 않는 함수와 상수는 `_`로 시작 <br> 요청과 응답 모델은 `Request`, `Response`, 응답 하위 모델은 `Out`으로 끝냄 <br> 예외를 결과로 바꿔 반환하는 함수는 `_safe`로 끝냄 <br> 프롬프트 버전 상수는 `STORYLINES_VERSION`처럼 버전 키에 `_VERSION`을 붙임 |
| 타입 | 모든 함수에 타입 힌트 작성, `Any` 지양 <br> 통로의 요청과 결과는 값을 바꿀 수 없는 dataclass <br> `LlmUsage`의 `provider`는 기본값 없이 키워드 인자로만 전달 |
| 비동기 | 라우터 핸들러와 외부 응답을 기다리는 함수만 `async` <br> 프롬프트 조립, 파싱과 검사 함수는 동기 |
| 예외 | 전송 오류와 내용 오류를 구분해 분류 <br> 502 변환은 스토리 서비스에서만 수행 <br> 502의 `detail`에는 정해진 문구만 넣고 공급자 원문은 넣지 않음 <br> 재호출 여부와 관계없이 실패한 시도는 Sentry에 보고 |
| 시간 | 모든 텍스트 호출에 제한 시간을 넣음 <br> 비우면 OpenAI SDK 기본값인 10분이 적용됨 |
| 토큰 | 실패한 시도와 보완 호출의 토큰까지 합산해 응답 `meta`에 넣음 |
| 설정 접근 | `settings`로만 읽고 `os.environ`을 직접 읽지 않음 <br> 함수의 기본 인자에 설정값을 두지 않고 호출 시점에 읽음 |
| 상수 | 출력 한도, temperature, 보완 횟수, 시간 한도는 스토리 서비스 상단의 상수로 관리 <br> 값은 모델 호출 설정과 일치 [6-1-5 모델 호출](6-1-AI-EXECUTION.md#6-1-5-모델-호출) |
| 로그 | `logging`을 쓰고 JSON 한 줄로 출력 <br> 호출마다 구분 이름, 소요 시간과 토큰 수를 기록 <br> Sentry에는 프롬프트와 응답 원문을 보내지 않음 |
| 템플릿 | LF 줄바꿈으로 저장 <br> 내용을 바꾸면 frontmatter의 `version`과 `updated`를 올림 |

모듈 내부의 함수 분할, 자료 구조와 로그 문구는 구현자가 정한다. 공개 함수의 입력과 반환, 통로 경계, 예외 분류와 상수의 위치는 바꾸지 않는다.

템플릿 치환은 프롬프트 조립, 실행 설정과 공급자별 인자 대응은 모델 호출을 따른다. ([6-1-4 프롬프트 조립](6-1-AI-EXECUTION.md#6-1-4-프롬프트-조립), [6-1-5 모델 호출](6-1-AI-EXECUTION.md#6-1-5-모델-호출))

기록할 필드와 원문 수집 범위는 관측에서 정한다. ([7-3 관측](7-3-OBSERVABILITY.md))

<br>

**서버 시작 검사**

서버 시작 시 다음 설정을 검사한다. 하나라도 조건을 충족하지 못하면 서버를 시작하지 않는다.

- 텍스트 모델이 등록부에 있다.
- 공급자 API 키가 비어 있지 않으며 공백, 개행, 비ASCII 문자가 없다.
- 공급자 주소를 지정했다면 `http` 또는 `https`이고 호스트가 있다.
- 어댑터가 모델의 추론 설정을 인자로 표현할 수 있다.
- 이미지 모델이 등록돼 있고 화질, 크기, 제한 시간 형식이 맞다.

시작 검사는 각 통로의 `validate_startup`이 맡는다.

- 텍스트 모델: `src/services/llm/__init__.py`
- 이미지 모델: `src/services/image/__init__.py`

사용 가능한 모델, 공급자, 추론 설정과 허용 인자는 `src/services/llm/registry.py`에 정의한다.

<br>

### 6-2-6 금지 패턴

| 금지 패턴 | 이유 |
|---|---|
| `src/services/`의 호출부가 공급자 SDK, 어댑터, 등록부를 직접 가져옴 | 모델을 바꿀 때 호출부를 고쳐야 함 |
| 전송 오류를 코드에서 다시 호출 | SDK 재시도와 겹쳐 시간 한도를 넘김 |
| 횟수나 시간 한도가 없는 재호출 | 비용과 대기 시간이 끝없이 늘어남 |
| 호출 인자와 제한 시간 누락 | SDK 기본 제한 시간이 적용됨 |
| 설정 오류를 502로 변환 | 설정 실수가 공급자 장애로 보임 |
| `IndexError`, `AttributeError`를 유효하지 않은 응답으로 분류 | 코드 결함을 응답 오류로 오인해 불필요하게 재호출함 |
| 코드가 필수 내용을 만들어 채움 | 실패한 생성이 정상 결과로 보임 |
| 이미지 실패로 컴파일 전체를 실패 처리 | 부가 결과가 스토리 저장을 막음 |
| 예외를 보고하지 않고 무시 | 이미지가 비어도 원인을 알 수 없음 |
| `LlmUsage`의 `provider`를 위치 인자로 전달 | 다른 값이 공급자 이름으로 기록됨 |
| 비밀값과 주소 하드코딩, `os.environ` 직접 접근, `print`, `global` | 설정과 로그 경로를 우회함 |
| 운영과 평가가 실행 코드를 각각 구현 | 평가한 코드와 배포한 코드가 달라짐 |

`except Exception`은 `_generate_character_images_safe`와 `_generate_thumbnail_image_safe`에서만 쓴다. 두 함수는 예외를 Sentry에 보고한 뒤 빈 결과나 실패 객체를 반환한다.

확인 방법과 테스트 실행 기준은 테스트 케이스를 따른다. ([7-2 테스트 케이스](7-2-TEST-CASES.md))
