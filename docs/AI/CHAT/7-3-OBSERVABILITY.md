# 7-3 관측

본 문서는 채팅 요청의 실행과 오류를 추적하고 운영 지표를 집계하는 기준을 정한다.

요청 식별자, 단계별 기록, 오류 조회 위치와 집계 방법, 알림과 데이터 수집 조건을 정의한다.

<br>

### 7-3-1 요청 조회

채팅 턴과 선택지는 별도 요청으로 기록한다. 추적 정보 오류는 채팅 처리를 막지 않으며, 기록은 `request_id`로 연결한다.

| 확인할 내용 | 조회 위치 | 확인 항목 |
|---|---|---|
| 본문과 판정, 선택지의 모델 입력과 출력 | Langfuse 요청 추적과 하위 호출 | 프롬프트, 모델 출력, 사용량과 호출 시간 |
| 본문·판정·선택지 호출 오류 | Sentry | `request_id`, `feature`, `error_code`, 모델과 스택 |
| 저장 이미지 선택 | Langfuse `LLM 판정`, 선택 실패 로그 | 모델, 질문 수, 사용량과 오류 타입 |
| 이미지 생성과 기본 이미지 대체 | Langfuse `child_image` metadata와 이미지 호출 | 작업 상태, 사유, 소요 시간, 기본 이미지 대체 여부 |
| 다운로드·생성·업로드 지연 | 인프라 추적 | HTTP 요청 아래의 `llm.stream`, `llm.complete`, `image.download`, `image.generate`, `image.upload` |
| 요청 간 연결과 내부 경고 | JSON 로그 | `request_id`, 추적 활성 시 `traceId`와 `spanId`, 오류와 대체 결과 경고 |
| 사용자가 받을 결과의 완료 여부 | SSE 수신 결과와 백엔드 저장 결과 | `completed`, `error`, 종료 이벤트 없는 연결 중단을 구분<br>HTTP 200만으로 판단하지 않음 |

<br>

| 식별자 | 기록 위치 | 연결 대상 |
|---|---|---|
| `request_id` | Langfuse 루트 관측 metadata, Sentry 태그, 로그 | 백엔드 요청과 AI 호출 |
| `session_id` | Langfuse 세션, Sentry `identity`, 로그 | 같은 접속 세션 |
| `device_id_hash` | Langfuse 사용자, Sentry `identity`, 로그 | 같은 기기 해시<br>원본 기기 식별자는 수신 안 함 |
| `creation_id`, `story_id`, `start_setting_id` | 채팅 턴과 선택지의 Langfuse metadata | 제작 결과, 스토리와 시작 설정 |
| `chat_id`, `turn_number`, `is_regenerated` | 채팅 턴과 선택지의 Langfuse metadata | 채팅, 턴 번호와 재생성 여부 |
| `traceId`, `spanId` | 인프라 추적과 로그 | 인프라 요청 스팬<br>Langfuse 추적 ID와 구분 |

<br>

### 7-3-2 기록 항목과 구현 위치

| 단위 | 기록 시점과 이름 | 기록 내용 | 구현 위치 (`manyak-ai` 기준) |
|---|---|---|---|
| 채팅 턴 요청 | SSE 생성기 실행부터 종료까지<br>`채팅 턴` | 슬롯을 제외한 요청 입력, 연결 식별자, 프롬프트 버전, `retry_count=0`<br>유효한 `user_source`가 있으면 metadata에도 포함 | `src/api/v1/chat.py`의 `_event_stream` |
| 선택지 요청 | API 실행부터 반환까지<br>`채팅 선택지` | `user_source`와 슬롯을 제외한 입력, 연결 식별자, `NEXT_ACTIONS` 버전<br>반환 전 실제 `retry_count` 반영 | `src/api/v1/chat.py`의 `chat_choices` |
| 텍스트 호출 | 본문, 판정, 선택지 최초 생성과 보완 호출마다 | OpenAI SDK 자동 계측의 프롬프트, 출력, 모델, 사용량과 시간 | `src/core/langfuse.py`의 `init_langfuse`, `src/services/llm/openai_sdk.py` |
| 저장 이미지 선택 호출 | TypeSafe 호출마다<br>`LLM 판정` | 모델, 질문 수, 제한 시간, 재시도 0, 사용량과 응답 수<br>호출 input과 output에 대화·이미지 이름·선택 원문 제외 | `src/services/llm/typesafe_api.py` |
| 이미지 편집 호출 | 모델 호출마다<br>`이미지 생성:자식` | 프롬프트, 모델, 크기, 화질, 형식<br>사용량과 결과 바이트 수 | `src/services/image/openai_api.py`, `src/core/langfuse.py`의 `observe_generation` |
| 이미지 전체 결과 | 이미지 슬롯이 있는 턴의 종료 시 `child_image` 기록<br>슬롯이 없으면 기록 안 함 | 상태, 사유, 작업 시간, 기본 이미지 대체 여부와 이미지 프롬프트 버전 | `src/services/chat_child_image.py`, 라우터의 `finally` |
| 호출 오류 | 실패한 본문·판정·선택지 시도마다 | 기능, 공급자, 모델, 오류 분류, 프롬프트 버전, 보완 횟수와 소요 시간 | `src/core/sentry.py`의 `capture_ai_exception` |
| 인프라 요청과 작업 | HTTP 요청과 각 모델·이미지 작업의 시작과 종료 | 경로 템플릿, HTTP 상태, 공급자, 모델, 작업 종류, 상태와 예외 타입 | `src/core/tracing.py`, 각 공급자 어댑터와 이미지 다운로드·업로드 함수 |
| 로그 | 오류, 판정값 무효화, 저장 이미지 선택 실패, 선택지 대체와 관측 실패 시 | 시각, 서비스, 로그 수준, 메시지, 식별자와 예외 스택 | `src/core/json_logging.py`, 각 서비스 모듈 |

<br>

**실행 정보**

| 정보 | 응답 `meta` | Langfuse | Sentry·로그·인프라 추적 |
|---|---|---|---|
| 환경과 코드 버전 | 없음 | 환경과 `APP_VERSION`을 릴리스로 전달 | Sentry는 환경 설정, 릴리스 명시 없음<br>인프라 resource는 `service.name=manyak-ai` |
| 공급자와 모델 | 본문 또는 선택지의 실제 값 | 하위 호출 모델 | Sentry와 인프라 작업 속성 |
| 프롬프트 버전 | 채팅과 선택지의 계약 키 | 요청 metadata, 이미지 버전은 `child_image.prompt_version` | 명시 캡처의 `ai.prompt_versions` |
| 보완 횟수 | 채팅 0, 선택지 0~2 | 요청 `retry_count` | 명시 캡처의 `ai.retry_count` |
| 토큰 | 채팅은 본문·판정 합계<br>선택지는 최초·보완 합계<br>저장 이미지 선택·이미지 생성 제외 | 호출별 사용량 | Sentry 오류 컨텍스트와 인프라 스팬에는 없음 |
| 시간 | 없음 | 관측 시작·종료, `child_image.duration_ms` | Sentry `ai.latency_ms`, 인프라 스팬 시간 |
| 오류 | 없음 | 호출 오류 수준과 이미지 결과 사유 | Sentry `error_code`, 인프라 `error.type` |
| 입력 출처 | 없음 | 채팅 요청 metadata의 `user_source` | 선택지 metadata에는 없음 |
| 장르 | 없음 | 채팅 요청 input에는 포함, 관측 태그 없음 | 채팅 장르별 구조화 필드 없음 |
| 호출 옵션과 스키마 버전 | 없음 | 이미지는 모델 인자 기록<br>텍스트 옵션·스키마 버전의 별도 공통 metadata 없음 | 코드와 설정을 함께 확인 |

<br>

**이미지 결과 metadata**

| 필드 | 값과 의미 |
|---|---|
| `status` | `not_started`, `running`, `skipped`, `success`, `failed`, `cancelled` |
| `reason` | 정상 성공은 `null`<br>시작 전 `body_incomplete`<br>생략 사유 `body_timeout`, `body_error`, `no_parent`, `invalid_upload_url`<br>실패 사유 `timeout`, `rate_limited`, `rejected`, `generation_failed`, `unexpected_error`<br>취소 사유 `cancelled` |
| `duration_ms` | 업로드 주소 검사부터 이미지 작업 종료까지의 시간<br>본문 생성과 전송 시간 제외, 작업 미시작이면 `null` 가능 |
| `parent_fallback` | 대상 인물의 이미지 연결 시 기본 이미지로 대체했는지 표시<br>대상 자체가 없는 `no_parent`와 구분 |
| `prompt_version` | 실시간 이미지 템플릿 버전 |

<br>

### 7-3-3 오류 확인

| 기능 | 오류 조회 위치 |
|---|---|
| 본문 | Sentry `feature=chat_response` |
| 판정 | Sentry `feature=chat_response`<br>`prompt_versions`의 `JUDGEMENT`와 스택으로 구분 |
| 선택지 | Sentry `feature=choice_generation` |
| 이미지 | Langfuse `child_image`, 이미지·인프라 호출 기록 |
| 저장 이미지 선택 | Langfuse `LLM 판정`, 예외 타입만 남기는 선택 실패 경고 로그 |

| 오류나 현상 | 기록 | 확인 대상 |
|---|---|---|
| 공급자 또는 판정 대기 시간 초과 | `provider_timeout` | 본문 경과 시간, 판정에 배정된 시간, 공급자 호출 시간<br>자체 대기 초과와 공급자 시간 초과의 대체 결과 차이 |
| 호출량 제한 | `provider_rate_limited` | 공급자 한도와 같은 시간대 호출량 |
| 요청 거부 | `provider_bad_request` | 모델과 호출 인자의 일치 여부, 공급자 거부 사유 |
| 그 밖의 공급자 오류 | `provider_unavailable` | 공급자 연결·응답 상태와 실패한 호출 |
| 판정·선택지 출력 오류 | `invalid_ai_response` | 모델 출력과 JSON 파싱·형식 검증 위치 |
| 판정값 무효화 | 판정 모듈 경고 로그 | 후보 밖 이름, 이미 완결된 사건, 진행 턴 수 검증 |
| 판정 시간 부족으로 호출 생략 | 남은 시간 경고 로그 | 본문 생성 시간과 남은 예산<br>공급자 호출 실패 건수에 포함하지 않음 |
| 선택지 부족분 대체 | 선택지 모듈 경고 로그 | 확보한 개수, 보완 호출 결과<br>`retry_count=2`만으로 대체 여부 판단 안 함 |
| 이미지 실패·대체 | `child_image.status`, `reason`, `parent_fallback` | 다운로드, 모델 호출, 업로드 중 실패한 단계 |
| 예상하지 못한 예외 | 자동 오류 수집과 스택 | 실제 예외 발생 위치<br>수동 캡처가 아니면 `feature`·`error_code` 부착을 보장하지 않음 |

<br>

### 7-3-4 지표

| 지표 | 계산과 구분 | 자료와 한계 |
|---|---|---|
| 요청 수 | 채팅 턴과 선택지 요청을 별도로 집계 | Langfuse 추적 수는 활성화·표본 비율에 영향을 받음<br>전체 요청 수와 동일시하지 않음 |
| 본문 전달 성공률 | 본문을 끝까지 전달한 턴 / 전체 채팅 턴 요청 | SSE 완료 수신 확인 필요<br>HTTP 상태나 모델 호출 성공만으로 집계 불가 |
| 판정 성공률 | 유효한 판정 결과를 얻은 턴 / 판정을 호출한 턴 | 판정 생략 제외<br>형식 보정과 실패 대체의 구조화된 최종 상태가 없어 호출 성공만으로 확정 불가 |
| 선택지 생성 완성률 | 대체 문구 없이 3개를 생성한 요청 / 전체 선택지 요청 | 대체 문구 적용은 로그에만 기록<br>200 응답과 보완 횟수만으로 확정 불가 |
| 실시간 이미지 생성 성공률 | 새 이미지를 전달한 턴 / 실시간 이미지 생성 시도 | 이미지 작업 상태와 최종 전달 결과를 함께 확인<br>대상 없음·생략과 실제 생성 실패 구분 |
| 오류 분포 | `feature`, `error_code`별 보고 수 | Sentry 개별 실패 시도 기준<br>같은 요청의 보완 실패가 여러 건일 수 있음 |
| 보완 분포 | 선택지 `retry_count`별 요청 수 | 응답 메타와 Langfuse<br>SDK 내부 재시도 제외 |
| 처리 시간 | 채팅 턴·선택지 각각의 중앙값과 백분위, 단계별 소요 시간 | Langfuse와 인프라 추적<br>첫 토큰 지연과 사용자 수신 완료 시간은 별도 계측 없음 |
| 본문 재생성률 | 재생성 턴 / 전체 턴 | `is_regenerated`가 있는 채팅 요청<br>선택지 요청을 분모에 중복 포함하지 않음 |
| 선택지 사용률 | `choice` 또는 `edited_choice` 입력 / 전체 사용자 입력 | 채팅 `user_source`<br>누락·무효 값을 직접 입력으로 단정하지 않음 |
| 턴당 생성 비용 | 본문·판정·선택지·저장 이미지 선택·이미지 생성과 재호출 비용 합 | 호출별 사용량과 모델 단가<br>두 요청 추적을 턴 식별자로 연결, 재생성은 별도 건 |

<br>

**집계 조건**

| 항목 | 기준과 제한 |
|---|---|
| 기간과 표본 | 같은 환경·기간·모델·프롬프트 버전을 비교<br>표본 비율이 다르면 원시 건수 직접 비교 안 함 |
| 부분 사용량 | 알려진 토큰만 합산하며 누락값을 실제 0 사용으로 해석하지 않음<br>응답 메타는 한 호출의 사용량이 빠져도 다른 호출의 합계가 남을 수 있음 |
| 파싱 실패 | 공급자가 응답해도 판정·선택지의 파싱 실패 사용량은 서비스 응답 합계에서 빠질 수 있음<br>하위 호출 기록과 대조 |
| 이미지 비용 | 입력 텍스트·입력 이미지·출력 이미지 사용량별 단가 확인<br>전체 토큰과 세부 토큰에 비용 중복 적용 안 함 |
| 생성 뒤 실패 | 업로드나 본문 전달이 실패해도 이미지 생성 비용은 발생할 수 있음 |
| 비용 누락 | 사용량 없는 실패·취소, 미수집 요청과 전송 유실 구분<br>관측 비용 합계가 실제 청구액과 같다고 보장하지 않음 |
| 단가 | Langfuse 프로젝트의 모델 단가 설정 확인 필요<br>DeepSeek은 계측 활성 시 `pricing_window` metadata 전달 |
| 중복과 재생성 | 요청 식별자와 턴 연결값을 함께 확인<br>`chat_id`와 `turn_number`만으로 재생성 호출을 한 건으로 합치지 않음 |

<br>

### 7-3-5 사용자 반응

AI 서버는 채팅 요청의 `user_source`와 `is_regenerated`를 기록한다.

| 반응 | 현재 확인 가능한 자료 | 해석 범위 |
|---|---|---|
| 직접 입력과 선택지 사용 | `user_source`: `typed`, `choice`, `edited_choice` | 입력 방식 구분<br>선택지 노출 여부와 미선택 이유는 알 수 없음 |
| 본문 재생성 | `is_regenerated` | 재생성 호출 구분<br>이전 결과의 평가 점수나 불만 사유를 뜻하지 않음 |

<br>

### 7-3-6 알림

Sentry 일일 보고는 `daily-sentry-report` 스킬에 정의되어 있다. ([daily-sentry-report](../../../../manyak-ai/.agents/skills/daily-sentry-report/SKILL.md))

| 항목 | 확인한 기준 |
|---|---|
| 정기 보고 | 매일 오전 10시(KST), 지난 24시간의 운영 Sentry 오류 요약 |
| 범위 | AI 서버, 백엔드와 웹 프로젝트 |
| 오류 없음과 조회 실패 | 오류가 없다는 결과와 조회 실패를 구분해 전달 |
| 채팅 부분 실패 | Sentry에 캡처된 판정·선택지 오류 포함 가능<br>이미지 metadata와 선택지 부족 경고는 이 보고만으로 집계 안 됨 |

<br>

### 7-3-7 수집 조건과 실패 처리

**1. 데이터 범위**

요청 본문을 기록에서 제거해도 로그와 Sentry의 오류 메시지에는 모델 출력이나 공급자 응답 일부가 남을 수 있다.

| 데이터 | 현재 기록 방식 |
|---|---|
| 채팅 요청, 프롬프트와 모델 출력 | 활성화된 Langfuse 요청 input과 하위 호출에 포함<br>태그·metadata에 사용자 자유입력을 추가하지 않음 |
| 이미지 슬롯과 서명 URL | Langfuse 요청 입력과 422 오류 응답에서 제외<br>업로드는 서명 URL을 로그로 남기는 HTTP 클라이언트 경로를 피함 |
| 기본 이미지 URL | 요청의 `character_images`에 포함되므로 Langfuse input에는 남음<br>모든 URL이 제거되는 것은 아님 |
| 이미지 프롬프트 | Langfuse 이미지 generation input에 기록<br>부모 이미지 바이너리는 전달하지 않음 |
| 생성 이미지 바이너리 | 관측 제외<br>Langfuse 출력은 형식과 바이트 수만 기록 |
| 이미지 결과 `child_image` | URL, 이미지 데이터와 인물 이름 제외 |
| Sentry 요청·지역변수 | `before_send`에서 요청 제거, `include_local_variables=False`, `send_default_pii=False` |
| 인프라 추적 | 등록 경로 템플릿과 허용된 기술 속성만 전송<br>본문, URL, 헤더, 예외 메시지, 이벤트와 링크 제외 |
| 로그 | 구조화된 식별자와 메시지·스택 기록<br>JSON 포매터 자체에는 원문을 제거하는 공통 정제 기능 없음 |

<br>

**2. 활성화와 표본 수집**

| 항목 | 코드 기준 |
|---|---|
| Langfuse 활성화 | 공개 키·비밀 키 설정, `LANGFUSE_HOST=https://jp.cloud.langfuse.com`, `SENTRY_ENVIRONMENT=prod`를 모두 충족 |
| Langfuse 표본 비율 | `LANGFUSE_SAMPLE_RATE`, 기본값 `1.0`, 허용 범위 0~1<br>추적 ID 기반으로 요청과 하위 호출의 선택을 맞춤 |
| 인프라 추적 활성화 | `MANYAK_TRACING_ENABLED=true`와 유효한 `MANYAK_OTLP_TRACES_ENDPOINT`<br>기본값은 비활성 |
| 인프라 표본 정책 | 부모 표본 결정을 따름, 부모 없으면 수집<br>Langfuse 표본 결정과 분리 |
| Sentry 활성화 | `SENTRY_DSN` 설정<br>코드에는 `prod` 전용 활성화 가드 없음 |
| Sentry 성능 추적 | `SENTRY_TRACES_SAMPLE_RATE`, 기본값 `0.0`<br>오류 이벤트 수집 비율과 다른 설정 |
| 테스트 | `tests/conftest.py`에서 외부 관측 비활성화<br>가짜 관측 객체와 exporter로 검사 |

<br>

**3. 수집 실패**

| 상황 | 처리 |
|---|---|
| 초기화 조건 불충족 또는 관측 초기화 실패 | 해당 관측을 비활성화하고 서버 기동 계속 |
| 추적 시작·metadata·결과 기록 실패 | 경고 기록, 생성 결과 유지 |
| 인프라 스팬 정제 실패 | 해당 스팬 전송 생략, 요청 처리 유지 |
| 관측 종료 실패 | 원래 생성 실패나 요청 취소를 바꾸지 않음 |
| 서버 종료 | 인프라 종료와 Langfuse flush를 각각 기본 3초 한도로 대기<br>시간 초과와 전송 실패 시 마지막 기록 유실 가능 |
| 재전송 | SDK 배치 전송 사용<br>애플리케이션의 영구 저장·별도 재전송 큐 없음 |
| 미수집과 누락 | 비활성화, 표본 제외, 기록 실패와 전송 유실을 구분<br>추적이 없다는 이유만으로 요청이 없었다고 판단하지 않음 |
