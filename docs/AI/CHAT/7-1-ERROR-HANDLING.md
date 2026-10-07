# 7-1 오류 처리

본 문서는 채팅 실행 중 발생하는 오류의 처리와 복구 기준을 정한다.

오류별 처리 위치, 재시도와 시간 한도, 최종 출력과 전달 실패 시 AI 서버와 백엔드의 책임을 구분한다.

<br>

### 7-1-1 오류 분류와 클래스

| 오류 | 예외 클래스 | 정의 위치 (`manyak-ai` 기준) | 역할 |
|---|---|---|---|
| 입력 오류 | `RequestValidationError` | FastAPI, `src/main.py`의 채팅 검증 오류 처리기 | 스키마 위반을 422로 출력<br>입력 원문과 서명 URL을 응답에서 제외 |
| 설정 오류 | `LlmConfigError`, 템플릿 로드의 `RuntimeError` | `src/services/llm/base.py`, 각 템플릿 로더 | 미등록 모델, API 키 누락과 템플릿 오류 구분<br>`LlmConfigError`는 `LlmError`를 상속하지 않음 |
| 텍스트 전송 오류 | `LlmTimeout`, `LlmRateLimited`, `LlmBadRequest`, `LlmUnavailable` | `src/services/llm/base.py` | `LlmError`를 상속하며 오류 메시지, `provider`와 `model` 보관 |
| 선택 API 출력 오류 | `LlmInvalidResponse` | `src/services/llm/base.py`, `typesafe_api.py` | 선택 후보, 확률, 모델 또는 응답 형식 위반 |
| 텍스트 출력 오류 | `json.JSONDecodeError`, `ValueError` | 표준 라이브러리, `chat_judgement.py`, `chat_choices.py` | 빈 응답, JSON 파싱 실패와 출력 형식 위반 구분 |
| 작업 시간 초과 | `TimeoutError` | `asyncio.wait_for`, 이미지 마감 검사 | SDK 재시도를 포함한 판정, 본문 수집과 이미지 작업의 시간 한도 적용 |
| 이미지 생성 오류 | `ImageTimeout`, `ImageRateLimited`, `ImageBadRequest`, `ImageGenerationError` | `src/services/image/base.py` | 다운로드와 생성 실패를 내부 `ChildImageResult.error`로 변환 |
| 이미지 업로드 오류 | `httpx.TimeoutException`, `httpx.HTTPError`, `httpx.InvalidURL`, `ValueError`, `binascii.Error` | HTTPX, 표준 라이브러리, `src/services/image/upload_child.py` | 주소, 데이터와 PUT 실패를 내부 이미지 오류로 변환 |
| 요청 취소 | `asyncio.CancelledError` | 비동기 실행 환경 | 상위 호출로 전파하고 진행 중인 작업과 스트림 정리 |
| 예상하지 못한 오류 | 원래 예외 유지 | 오류가 발생한 코드 | 일반 코드 결함을 모델 출력 오류로 바꾸지 않음<br>이미지 작업 내부의 격리 범위는 7-1-2를 따름 |

<br>

### 7-1-2 오류별 처리

- 공급자 어댑터는 시간 초과를 연결 오류보다 먼저 검사한다. SDK의 시간 초과가 연결 오류의 하위 클래스이기 때문이다.
- OpenAI SDK 어댑터는 400을 `LlmBadRequest`, 429를 `LlmRateLimited`로 분류한다. 인증, 권한, 404, 422와 5xx를 포함한 나머지 SDK 오류는 `LlmUnavailable`로 분류한다.
- 요청 취소는 생성 실패나 대체 결과로 바꾸지 않는다. 연결 종료 시 정리는 7-1-6을 따른다.

**1. 입력과 본문**

| 오류 조건 | 처리 위치 | 복구 | 최종 출력 |
|---|---|---|---|
| 서버 시작 시 모델, 키 또는 템플릿 설정 오류 | 시작 검사와 템플릿 로더 | 설정 수정 후 재배포 | 서버 시작 실패 |
| 요청 스키마 위반, 슬롯 개수 또는 URL 형식 위반 | 입력 스키마, `chat_validation_error` | 백엔드가 입력 수정 | 422, 모델 호출 없음 |
| 본문 모델의 시간 초과, 호출량 제한, 요청 거부 또는 연결 실패 | 공급자 어댑터 → `stream_chat_turn` | SDK 정책에 따른 재시도만 허용 | SSE `error`<br>판정과 이미지 생성 안 함 |
| 본문 수집 중 모델 스트림 실패 | `stream_chat_turn` | 본문 재생성이나 이어받기 없음 | SSE `error`, `completed` 없음 |
| 실시간 이미지 요청 턴의 본문 수집 시간 초과 또는 두 이미지 경로의 완료 이벤트 없이 종료 | `stream_with_child_image`, `stream_with_selected_images`, `_collect` | 본문 수집 취소, 후속 작업 생략 | SSE `error` |
| 이미지 처리 후 본문 전송 마감 초과 | `_stream_rendered` | 남은 본문 전송 중단 | SSE `error`, `completed` 없음 |
| 호출 중 설정 오류, 전처리 또는 응답 조립의 내부 예외 | 오류 발생 지점 → 라우터 | 대체 결과로 숨기지 않음 | HTTP 응답 시작 전이면 500<br>SSE 시작 후이면 정상 종료 이벤트 없이 연결 종료 가능 |

<br>

**2. 사건과 엔딩 판정**

| 오류 조건 | 처리 위치 | 복구 | 최종 출력 |
|---|---|---|---|
| 남은 시간 부족으로 판정 시작 불가 | `generate_judgement`, `_frozen` | 모델 호출 생략 | 기존 목표와 진행 턴 수 유지<br>완결 사건과 도달 엔딩은 `null`, 본문 `completed` |
| 판정 전체 대기 시간 초과 | `generate_judgement`의 `asyncio.wait_for` | 진행 중 호출 취소, 추가 호출 없음 | 기존 목표와 진행 턴 수 유지<br>완결 사건과 도달 엔딩은 `null`, 본문 `completed` |
| 공급자 시간 초과 | 공급자 어댑터 → `generate_judgement` | SDK 재시도 후 추가 호출 없음 | `targetMainEvent`, `occurredMainEventName`, `endingName` 모두 `null`, 본문 `completed` |
| 그 밖의 모델 호출 실패, 빈 응답, JSON 파싱 실패 또는 객체가 아닌 응답 | `generate_judgement` | 추가 호출 없음 | `targetMainEvent`, `occurredMainEventName`, `endingName` 모두 `null`, 본문 `completed` |
| 목록 밖 이름, 이미 완결된 사건 또는 유효하지 않은 진행 턴 수 | `_sanitize` | 해당 필드만 `null`로 보정 | 나머지 유효한 판정 유지, 본문 `completed` |
| 목표 사건과 이번 완결 사건이 같음 | `_sanitize` | 목표 사건을 `null`로 보정 | 이번 완결 사건 유지, 본문 `completed` |
| 설정 오류 또는 예상하지 못한 내부 예외 | 판정 모듈 → 라우터의 판정 작업 회수 | 예외 전파 | SSE 시작 후 연결 종료 가능 |

판정 대상인 주요 사건과 엔딩 후보가 모두 없으면 정상 생략이며 오류가 아니다.

<br>

**3. 실시간 이미지**

| 오류 조건 | 처리 위치 | 복구 | 최종 출력 |
|---|---|---|---|
| 생성 대상 화자나 기본 이미지 없음 | `build_child_image_input` | 생성 생략 | 기존 이미지 매핑으로 본문 `completed` |
| 생성 전 업로드 주소 검사 실패 | `_generate_before_deadline` → `validate_upload_url` | 다운로드와 생성 생략 | 기본 이미지 유지, 본문 `completed` |
| 기본 이미지 주소, 크기, 형식 또는 다운로드 실패 | `_download_parent` → `generate_child_image` | 재호출 없음 | 기본 이미지 유지, 본문 `completed` |
| 모델 시간 초과, 호출량 제한, 요청 거부, 빈 데이터 또는 디코딩 실패 | 이미지 어댑터 → `generate_child_image` | 재호출 없음 | 기본 이미지 유지, 본문 `completed` |
| 업로드 시간 초과, 2xx 이외 응답 또는 데이터 검증 실패 | `upload_child_image` | 업로드 재시도 없음 | 기본 이미지 유지, 본문 `completed` |
| 작업 시간 초과 또는 마감 뒤 반환된 결과 | `_generate_before_deadline`, `stream_with_child_image` | 진행 중 작업 취소, 늦은 결과 사용 안 함 | 기본 이미지 유지, 본문 `completed` |
| 다운로드, 생성과 업로드 작업 내부의 예상하지 못한 예외 | `_generate_before_deadline` | `unexpected_error`로 관측, 내부 결과는 `generation_failed` | 기본 이미지 유지, 본문 `completed` |

<br>

**4. 선택지**

| 오류 조건 | 처리 위치 | 복구 | 최종 출력 |
|---|---|---|---|
| 모델 전송 오류, 빈 응답, JSON 파싱 실패 또는 `choices` 배열 누락 | `_call` → `generate_choices` | 확보한 선택지 유지, 최대 2회 추가 호출 | 부족분을 대체 문구로 채워 200 |
| 공백, 비문자열 또는 중복 제외 후 3개 미만 | `_accumulate` → `generate_choices` | 부족분만 최대 2회 추가 생성 | 부족분을 대체 문구로 채워 200 |
| 호출 중 설정 오류 또는 예상하지 못한 내부 예외 | 선택지 모듈 → FastAPI | 대체 문구로 숨기지 않음 | 500, 이미 완료한 채팅 턴에는 영향 없음 |

<br>

**5. 저장 이미지 선택**

| 오류 조건 | 처리 위치 | 복구 | 최종 출력 |
|---|---|---|---|
| 선택 API 키 누락, 호출 실패, 10초 초과 또는 응답 형식 오류 | `select_images` → `stream_with_selected_images` | 해당 호출의 선택 결과 전체 폐기, 재호출 없음<br>호출 없이 정한 단일 후보 유지 | 나머지 인물은 기본 이미지, 없으면 URL이 있는 첫 이미지로 본문 `completed` |

<br>

실시간 이미지 실패 시 본문을 유지하는 처리는 본문 전송 시간이 남아 있을 때 적용한다. 이미지 작업을 포기했더라도 본문 전송이 마감을 넘으면 SSE `error`로 종료한다.

본문, 판정과 선택지의 호출 오류는 `capture_ai_exception`으로 기록한다. 이미지 결과는 요청별 `ChildImageObservation`에 고정된 상태와 사유를 남기며 URL, 이미지 데이터와 인물 이름을 넣지 않는다. 관측 실패 때문에 원래 오류나 취소가 바뀌어서는 안 된다.

오류별 검증 항목과 테스트 범위는 테스트 케이스 문서를 따른다. 테스트 파일의 존재는 실행해 통과했다는 뜻이 아니다. ([7-2 테스트 케이스](7-2-TEST-CASES.md))

기록 항목과 수집 범위는 관측 문서를 따른다. ([7-3 관측](7-3-OBSERVABILITY.md))

| 검증 대상 | 기존 테스트 (`manyak-ai` 기준) |
|---|---|
| 422 정제, SSE 오류, 판정 대기와 연결 종료 | [test_chat_api.py](../../../../manyak-ai/tests/test_chat_api.py) |
| 본문 전송 실패 | [test_chat_llm.py](../../../../manyak-ai/tests/unit/test_chat_llm.py) |
| 판정 실패, 형식 보정과 시간 한도 | [test_chat_judgement.py](../../../../manyak-ai/tests/unit/test_chat_judgement.py) |
| 선택지 보완, 대체 문구와 내부 예외 | [test_chat_choices.py](../../../../manyak-ai/tests/unit/test_chat_choices.py) |
| 이미지 실패, 늦은 결과와 취소 | [test_chat_child_image.py](../../../../manyak-ai/tests/unit/test_chat_child_image.py), [test_child_image_generation.py](../../../../manyak-ai/tests/unit/test_child_image_generation.py), [test_child_image_upload.py](../../../../manyak-ai/tests/unit/test_child_image_upload.py) |

<br>

### 7-1-3 재시도와 시간 한도

**1. 재시도와 보완 횟수**

- 다른 모델로 바꿔 호출하는 폴백은 없다. 기본 이미지 유지와 고정 선택지 추가는 모델 교체가 아니다.
- 본문과 판정은 서비스에서 다시 호출하지 않는다. 선택지는 호출 실패도 부족분으로 처리해 같은 보완 한도 안에서 추가 호출한다.
- 서비스의 추가 호출 사이에는 별도 대기 시간이 없다. SDK의 재시도 대기는 SDK 정책을 따른다.
- 큐에서 요청을 다시 꺼내는 메시지 재처리는 없다.

| 복구 방식 | 대상 | 한도 | 응답의 재호출 횟수 포함 여부 |
|---|---|---|---|
| OpenAI SDK 자동 재시도 | OpenAI와 DeepSeek 텍스트 호출의 전송 오류 | 최대 2회, 최초 시도 포함 최대 3회 | 포함하지 않음 |
| 본문 재생성 또는 판정 보완 | 본문, 판정 | 없음 | 채팅 `retryCount=0` |
| 선택지 추가 생성 | 부족한 선택지, 호출 또는 파싱 실패 | 최초 호출 이후 최대 2회 | 선택지 `retry_count=0~2` |
| 저장 이미지 선택 | TypeSafe 선택 API | 재시도 없음 | 포함하지 않음 |
| 실시간 이미지 편집 | 이미지 모델 호출 | SDK와 서비스 재시도 없음 | 포함하지 않음 |
| 기본 이미지 다운로드와 결과 업로드 | 이미지 HTTP 요청 | 재시도 없음 | 포함하지 않음 |
| 고정 선택지 추가 | 추가 생성 후에도 부족한 선택지 | 모델 호출 없음 | 포함하지 않음 |

SDK 재시도는 스트림 일부를 전달한 뒤 본문을 다시 생성하거나 이어받는 기능이 아니다. 스트리밍 도중 실패하면 해당 턴을 종료한다.

<br>

**2. 시간과 호출 한도**

제한 시간과 대기 방식은 실행 문서를 따른다. SDK의 시도별 제한과 `asyncio.wait_for`의 전체 제한을 구분한다. ([6-1 AI 실행](6-1-AI-EXECUTION.md))

| 단계 | 제한 시간 | 적용 범위 |
|---|---|---|
| 채팅 턴 | 120초 | 백엔드 `SseEmitter`의 연결 제한<br>초과 시 백엔드가 SSE 종료 |
| 본문 모델 | SDK 호출 90초 | SDK 재시도로 전체 대기가 더 길어질 수 있음 |
| 판정 | `min(60초, 120초 - 턴 경과 시간 - 15초)` | SDK 재시도를 포함한 전체 호출<br>0 이하이면 생략 |
| 이미지 요청 턴의 본문과 이미지 전달 | AI 처리 시작부터 105초 | 턴 상한에서 완료 여유 15초 제외 |
| 이미지 요청 턴의 본문 수집 | 위 마감까지 남은 시간에서 `min(8초, 남은 시간 / 4)` 제외 | 본문을 보낼 시간 확보 |
| 저장 이미지 선택 | 최대 10초 | 여러 인물의 선택 질문을 한 호출로 처리 |
| 실시간 이미지 작업 | 최대 30초 | 다운로드, 생성과 업로드 합계<br>본문 전송 여유를 뺀 작업 마감이 더 가까우면 단축 |
| 이미지 SDK 호출 | 기본 60초, 연결 10초 | `IMAGE_TIMEOUT`과 연결 제한<br>바깥의 이미지 작업 한도가 먼저 적용될 수 있음 |
| 선택지 | SDK 호출마다 60초 | 최초 생성과 추가 생성 각각 적용 |

판정과 이미지 대기 중에는 10초 간격으로 `ping`을 보낸다. `ping`은 연결을 유지하는 이벤트이며 턴 전체 한도를 연장하지 않는다.

백엔드가 전체 연결 시간을 제한하고, AI 서버는 판정의 남은 시간과 실시간 이미지 작업 마감을 계산한다.

<br>

| 요청 | 텍스트 모델 호출 | 저장 이미지 선택 | 이미지 생성 |
|---|---|---|---|
| 채팅 턴 | 본문 1회, 판정 최대 1회 | 슬롯이 없고 복수 후보가 있으면 최대 1회 | 슬롯과 대상이 있으면 최대 1회 |
| 선택지 | 최초 1회, 추가 생성 최대 2회 | 없음 | 없음 |

호출 수는 SDK 재시도를 제외한다. 두 API를 합치면 턴당 텍스트 생성 호출은 최대 5회이며 저장 이미지 선택 또는 이미지 생성이 최대 1회 추가된다. 비용에는 재시도와 실패한 호출도 포함한다. ([2-2-4 비용](2-2-OPERATION-REQUIREMENTS.md#2-2-4-비용))

<br>

### 7-1-4 최종 실패와 부분 완료

- 판정 실패와 정상적인 미도달은 완료 필드만으로 구분할 수 없으므로 실패 기록을 확인한다.
- 선택지 대체 문구는 `chat_choices.py`의 `_FALLBACK`에서 관리한다. ([chat_choices.py](../../../../manyak-ai/src/services/chat_choices.py))

| 주체 | 하는 일 |
|---|---|
| AI 서버 | 본문 실패 시 SSE `error` 출력<br>판정과 이미지의 허용된 실패는 대체 결과를 반영해 본문 전달<br>선택지 부족분은 대체 문구로 채움 |
| 백엔드 | 완료 본문, 대화 기록과 판정 상태 저장<br>실시간 이미지 생성 실패 시 해당 이미지 결제 취소 |
| 사용자 | 정상 응답이 마음에 들지 않으면 같은 턴의 본문 재생성 가능 |

선택지 생성에 실패해도 이미 생성된 본문은 유지한다.

<br>

### 7-1-5 실패 출력

| 상태 | 조건 | 본문 | 설명 |
|---|---|---|---|
| 422 | 채팅 턴 또는 선택지 요청 스키마 위반 | `detail` 배열<br>항목별 `type`, `loc`, `msg` | `input`, `ctx` 제외<br>백엔드가 입력 수정 |
| 500 | HTTP 응답 시작 전 처리하지 않은 설정 오류 또는 내부 예외 | 공통 JSON 형식 보장 안 함 | 외부 모델의 오류 원문을 사용자 안내로 쓰지 않음 |
| 200, SSE `error` | 본문 호출 실패, 이미지 요청 턴의 본문 수집 또는 전송 시간 초과 | `code`, `message` | `completed` 없이 종료<br>HTTP 200만으로 성공 판단 안 함 |
| 200, SSE 중단 | SSE 시작 후 처리하지 않은 내부 예외 또는 연결 종료 | 종료 이벤트 보장 안 함 | 완료 본문을 수신한 것으로 판단하지 않음 |

<br>

| SSE `code` | `message` | 조건 |
|---|---|---|
| `LLM_ERROR` | `채팅 연동 중 오류가 발생했습니다.` | 본문 모델 호출 실패 또는 두 이미지 경로에서 본문 완료 없이 스트림 종료 |
| `LLM_ERROR` | `채팅 응답 대기 시간이 초과됐습니다.` | 이미지 요청 경로의 본문 수집 또는 본문 전송 시간 초과 |

공급자 오류 원문은 SSE 메시지에 포함하지 않는다. 판정 실패와 이미지 실패는 별도 `error` 이벤트를 내지 않으며, 선택지의 예상한 호출 실패도 200 대체 응답으로 처리한다.

<br>

이미지 `error`는 AI 서버 내부 결과이며 채팅의 외부 응답 필드가 아니다. 외부 응답에는 기존 이미지 매핑을 유지한다.

| 내부 이미지 `error` | 뜻 |
|---|---|
| `timeout` | 다운로드, 생성, 업로드 또는 전체 작업 시간 초과 |
| `rate_limited` | 이미지 공급자의 호출량 제한 |
| `rejected` | 이미지 공급자의 요청 거부 |
| `generation_failed` | 주소 검증, 다운로드, 형식, 빈 데이터, 디코딩, 업로드 또는 그 밖의 생성 실패 |

<details>
<summary><b>실패 출력 예시</b></summary>

<br>

**1) 422 출력**

`genre`가 없는 요청의 응답이다. 요청 원문과 슬롯 URL은 포함하지 않는다.

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "genre"],
      "msg": "Field required"
    }
  ]
}
```

<br>

**2) SSE 오류**

```text
event: error
data: {"code":"LLM_ERROR","message":"채팅 연동 중 오류가 발생했습니다."}

```

<br>

**3) 500 출력**

```http
HTTP/1.1 500 Internal Server Error
Content-Type: text/plain; charset=utf-8

Internal Server Error
```

</details>

<br>

### 7-1-6 전달 실패 처리

AI 서버는 채팅 상태와 완료 결과를 저장하지 않는다. 요청 헤더의 식별자는 관측 연결에 사용하며 수신 확인, 중복 제거와 이벤트 재전송을 수행하지 않는다. ([5-5 요청 헤더와 메타데이터](5-CONTRACT.md#5-5-요청-헤더와-메타데이터))

| 상황 | AI 서버 | 백엔드와의 경계 |
|---|---|---|
| 본문 생성 중 연결 종료 | 모델 스트림과 이벤트 생성기 닫음 | 이미 받은 본문 조각만으로 정상 완료 판단 안 함 |
| 판정이나 이미지 대기 중 연결 종료 | 진행 중 작업 취소 후 회수<br>정리 작업은 `shield`로 보호 | 취소 이전 모델 호출 비용이 남을 수 있음 |
| 이미지 처리 후 본문 전송 중 연결 종료 | 남은 본문 전송 중단, 미완료 판정 작업 정리 | `completed` 수신과 저장 여부를 구분함 |
| 이미지 업로드 성공 후 시간 초과 또는 연결 종료 | 마감 뒤 결과를 본문에 반영하지 않음<br>업로드 객체 삭제 경로 없음 |  |
| 동일 요청 중복 수신 | 요청마다 별도 생성, 결과가 다를 수 있음 | 중복 방지는 AI 서버에서 보장하지 않음 |
| 생성 완료 후 응답 전달 실패 | 완료 결과 보관과 재전송 없음 | 결과 저장과 사용자 복구는 백엔드 책임 |

연결 종료로 로컬 작업을 취소해도 공급자가 이미 수행한 생성과 이미지 저장이 되돌아가는 것은 아니다. 전달 실패를 모델 생성 실패와 구분한다.
