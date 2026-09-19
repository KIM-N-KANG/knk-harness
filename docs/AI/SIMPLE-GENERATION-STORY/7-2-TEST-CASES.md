# 7-2 테스트 케이스

| 항목 | 값 |
|---|---|
| 적용 태스크 | 간편 제작 스토리 생성(스토리라인 생성, 컴파일, 인물 이미지와 썸네일 생성) |
| 버전 | 0.1 |

이 문서는 코드와 외부 연동이 명세대로 동작하는지 확인하는 테스트를 정한다. 정상 동작과 오류 처리를 단위·API·통합 테스트로 확인한다. 각 테스트가 확인할 범위는 별도로 구분한다. ([7-2-1 범위](#7-2-1-범위))

AI 결과의 품질은 별도의 AI 평가로 확인한다. ([6-4 AI 평가 방법](6-4-AI-EVALUATION-METHOD.md))

이 문서의 테스트를 통과해도 품질 평가에 합격한 것은 아니다.

모든 코드 경로는 `manyak-ai` 저장소 루트 기준이다. 각 케이스에는 이 문서에서 붙인 식별자와 해당 테스트의 코드 위치를 적는다.

<br>

### 7-2-1 범위

| 종류 | 위치 | 확인 대상 | 외부 의존성 | 실행 시점 |
|---|---|---|---|---|
| 단위 테스트 | `tests/unit/` | 스키마, 프롬프트 조립, 설정, 응답 검증, 보완, 결과 조립, 어댑터의 오류 변환 | 모두 대체 | 일반 테스트 실행 시, CI 포함 |
| API 테스트 | `tests/` 바로 아래 | HTTP 요청부터 응답까지의 계약. 상태 코드, 응답 형식, `meta`, 추적 기록 | 모델 호출만 대체 | 일반 테스트 실행 시, CI 포함 |
| 통합 테스트 | `tests/integration/` | 실제 모델을 연결한 파이프라인의 동작, 컴파일 결과와 채팅 입력의 연결 | 대체하지 않음 | 실제 모델 호출은 수동 실행만 허용 |

외부 의존성은 소프트웨어 구현에서 정한 범위에서 대체한다. ([6-2-3 의존성](6-2-SOFTWARE-IMPLEMENTATION.md#6-2-3-의존성))

| 대체 대상 | 방법 |
|---|---|
| 텍스트 모델 SDK | `install_llm_sdk`로 가짜 SDK를 설치하거나 `_complete_json`을 교체 |
| 이미지 모델 | 이미지 생성 함수와 `_safe` 함수를 교체 |
| Sentry | 보고 함수를 교체해 전달받은 인자를 기록 |
| Langfuse | 비활성화한 상태로 실행 <br> 기록 실패가 요청에 영향을 주지 않는지는 `tests/unit/test_langfuse.py`에서 가짜 SDK로 확인 |
| API 키 | 더미 키. 일반 테스트는 실제 공급자 키를 쓰지 않음 |

- 백엔드, 저장소와 CDN은 테스트 범위에 포함하지 않는다. 백엔드에 반환할 응답 형식은 API 테스트로 확인한다.
- 모델이 생성한 문장 자체는 비교하지 않는다. 단위 테스트는 미리 정한 가짜 응답으로 코드의 분기를 확인한다. 통합 테스트는 형식과 개수를 확인한다.

<br>

**금지 패턴 확인 방법**

금지 패턴의 준수 여부는 다음과 같이 확인한다. ([6-2-6 금지 패턴](6-2-SOFTWARE-IMPLEMENTATION.md#6-2-6-금지-패턴))

| 확인 대상 | 확인 방법 |
|---|---|
| `src/services/`의 호출부가 공급자 SDK, 어댑터, 등록부를 직접 가져옴 | `tests/unit/test_llm_gateway_boundary.py` <br> `openai`와 `anthropic`만 검사하며 Google SDK는 대상에 없음 |
| 전송 오류가 난 요청을 코드에서 다시 호출 | `tests/unit/test_story_llm_faults.py`의 `test_provider_error_is_not_retried` |
| 횟수나 시간 한도가 없는 재호출 | `tests/unit/test_story_llm_faults.py`의 재호출 한도 도달과 제한 시간 테스트 <br> `tests/unit/test_storylines_refill.py` |
| 호출 인자와 제한 시간 누락 | `tests/unit/test_story_llm_faults.py`의 호출 계약과 남은 시간 테스트 |
| 설정 오류를 502로 변환 | `tests/unit/test_story_llm_faults.py`의 `test_unregistered_model_is_not_disguised_as_502` |
| `IndexError`, `AttributeError`를 유효하지 않은 응답으로 분류 | 자동 검사 없음, 리뷰로 확인 |
| 코드가 필수 내용을 만들어 채움 | `tests/unit/test_story_compile.py`의 `test_compile_story_502_after_max_refill` |
| 이미지 실패로 컴파일 전체를 실패 처리 | `tests/unit/test_compile_images.py`, `tests/unit/test_compile_thumbnail.py` |
| 예외를 보고하지 않고 무시 | `tests/unit/test_compile_images.py`, `tests/unit/test_compile_thumbnail.py`의 Sentry 보고 테스트 |
| `LlmUsage`의 `provider`를 위치 인자로 전달 | `tests/unit/test_story_llm_faults.py`의 `LlmUsage` 테스트 |
| 비밀값과 주소 하드코딩, `os.environ` 직접 접근, `print`, `global` | 자동 검사 없음, 리뷰로 확인 |
| 운영용 실행 코드와 평가용 실행 코드를 따로 구현 | 평가 CLI 미구현, 검사 없음 |

<br>

### 7-2-2 스토리라인 케이스

스토리라인의 검증과 복구 규칙, 요청과 응답 계약을 기준으로 검사한다. ([6-1-6 검증과 복구](6-1-AI-EXECUTION.md#6-1-6-검증과-복구), [5-2 스토리라인 요청과 결과](5-CONTRACT.md#5-2-스토리라인-요청과-결과))

| 식별자 | 확인 대상 | 입력과 조건 | 기대 결과 | 코드 위치 |
|---|---|---|---|---|
| ST-01 | 입력 스키마 | 인물 필드를 모두 비움, 명시적 `null`, 공백 이름, 빈 특징 태그 | 요청을 허용하고 빈 값으로 정리 | `tests/unit/test_story_schemas.py` |
| ST-02 | 입력 거부 | 허용하지 않는 성별, 문자열이 아닌 특징, 이름 중복(대소문자와 정규화 포함) | 검증 오류 | `tests/unit/test_story_schemas.py` <br> `tests/test_request_validation.py` |
| ST-03 | 프롬프트 조립 | 인물 필드가 있음, 일부 비움, 주변 인물 없음, 자리표시자처럼 보이는 이름 | 인물 블록을 채우고 빈 값은 미정으로 표시. 이름 안의 자리표시자는 치환하지 않음 | `tests/unit/test_storylines_characters.py` |
| ST-04 | 형식 검증과 전체 재생성 | 후보 수나 추천 정보 수가 맞지 않거나, 줄거리가 비었거나, 스키마에 맞지 않는 가짜 응답 | 재생성에 성공하면 200, 2회 뒤에도 실패하면 502 | `tests/unit/test_story_llm_faults.py`의 `test_storylines_schema_mismatch_retries_then_succeeds`, `test_storylines_contract_violation_exhausts_to_502` |
| ST-05 | 후보 번호 | `id`가 없거나 순서가 틀린 응답 | 재생성하지 않고 1, 2, 3으로 덮어씀 | `test_story_llm_faults.py`의 `test_storylines_missing_id_passes`, `test_storylines_ids_normalized_to_sequence` |
| ST-06 | 인물 누락 탐지 | 이름을 입력한 인물이 일부 후보에서 빠짐, 정규화가 다른 이름, 이름 입력 없음 | 빠진 후보만 고름. 이름 입력이 없으면 보완하지 않음 | `tests/unit/test_storylines_characters.py` |
| ST-07 | 인물 보완 | 한 후보에서만 인물이 빠진 응답 | 해당 후보만 보완하고 다른 후보는 그대로 | `tests/unit/test_storylines_refill.py`의 `test_refills_only_missing_story` |
| ST-08 | 보완 결과 병합 | 요청하지 않은 번호, 범위를 벗어난 번호, 깨진 보완 응답, 빈 본문 | 요청한 후보만 반영하고 나머지는 원본 유지 | `test_storylines_characters.py`의 병합 테스트 <br> `test_storylines_refill.py`의 `test_refill_breaking_contract_falls_back_to_original`, `test_empty_body_refill_restores_original` |
| ST-09 | 보완 한도 도달 | 보완 2회 뒤에도 인물이 빠짐 | 200으로 반환하고 경고 보고 | `test_storylines_refill.py`의 `test_returns_result_with_warning_after_two_refills` |
| ST-10 | 응답 `meta`와 추적 | 토큰 없음, 재호출 발생, 이전 제작 요청 식별자 없음 | 토큰은 `null`, `retry_count`는 실제 값, 없는 식별자는 기록하지 않음 | `tests/test_storylines_api.py` |
| ST-11 | 서비스와 HTTP의 일치 | 같은 입력을 서비스 함수와 HTTP로 실행 | 프롬프트와 응답이 같음 | `test_storylines_api.py`의 `test_storylines_service_and_http_share_prompt_and_response` |

<br>

### 7-2-3 컴파일 케이스

컴파일의 검증과 복구 규칙, 요청과 응답 계약을 기준으로 검사한다. ([6-1-6 검증과 복구](6-1-AI-EXECUTION.md#6-1-6-검증과-복구), [5-3 컴파일 요청과 결과](5-CONTRACT.md#5-3-컴파일-요청과-결과))

| 식별자 | 확인 대상 | 입력과 조건 | 기대 결과 | 코드 위치 |
|---|---|---|---|---|
| CP-01 | 내부 명세 스키마 | 인물 5명·6명, 주요 사건 수, 엔딩 0개·3개·그 외 개수, `min_turns` 하한 | 허용 범위 안이면 통과, 벗어나면 거부 | `tests/unit/test_story_compile.py` |
| CP-02 | 프롬프트 조립 | 추가 정보 없음, 로어북이 없거나 `null`이거나 여러 개인 입력, 인물 블록 | 모든 자리를 채우고 빈 입력은 정해진 문구로 대체 | `test_story_compile.py`의 `test_build_compile_prompt_` 계열 <br> `tests/unit/test_compile_characters.py` |
| CP-03 | 공급자별 템플릿 | 컴파일 모델이 Gemini | Gemini용 템플릿과 버전을 최초 생성과 보완에 모두 사용 | `test_story_compile.py`, `test_compile_characters.py`의 `gemini` 테스트 |
| CP-04 | 입력값 덮어쓰기 | 모델이 장르, 주인공 이름과 성별, 입력 인물 이름을 바꿔 답함 | 입력값으로 되돌림. 비운 값은 모델 값을 유지. 보완 뒤에도 다시 적용 | `tests/unit/test_compile_protagonist.py` <br> `test_compile_characters.py`의 `test_compile_story_overwrites_changed_input_character_name` |
| CP-05 | 필수 블록 검사 | 빈 필수값, 첫 선택지가 3개가 아님, 객체 자리에 다른 타입 | 누락 블록을 찾음. 선택 항목은 비어도 통과 | `test_story_compile.py`의 `test_find_missing_keys_` 계열 |
| CP-06 | 입력 인물 검사 | 입력 인물의 식별자가 없음, 이름이 빠짐, 인물 수가 맞지 않음 | 인물 카드 블록 전체를 보완 대상으로 지정. 이미지 생성 전에 보완 | `test_compile_characters.py` <br> `tests/unit/test_compile_character_count.py` |
| CP-07 | 인물 필드 검사와 병합 | 빈 이름, 겹치는 이름, 공백뿐인 외형 | 입력 인물의 카드는 두고 생성된 카드의 이름을 고침. 요청한 필드만 반영 | `test_compile_characters.py`의 `test_character_field_repairs_` 계열, `test_merge_character_field_repairs_changes_only_requested_fields` |
| CP-08 | 부분 보완 | 블록, 이름과 외형이 함께 빠짐 | 한 번의 호출로 함께 요청. 카드 블록 전체를 요청할 때는 개별 필드 수정을 요청하지 않음 | `test_compile_characters.py`의 `test_compile_story_repairs_blocks_names_and_appearance_in_one_call`, `test_compile_story_refills_whole_character_block_before_field_repairs` |
| CP-09 | 엔딩 폴백 | 불완전한 엔딩, `min_turns`가 숫자 문자열이거나 숫자로 변환할 수 없거나 하한 미만인 값 | 고칠 수 있으면 엔딩 유지, 고칠 수 없으면 빈 배열로 대체하고 200 반환 | `test_story_compile.py`의 `test_compile_story_falls_back_` 계열, `test_compile_story_keeps_` 계열 |
| CP-10 | 외형 누락 허용 | 보완 뒤에도 외형이 비어 있음 | 빈 문자열로 두고 200 | `test_compile_characters.py`의 `test_compile_story_keeps_success_when_appearance_remains_blank` |
| CP-11 | 결과 조립 | 유효한 내부 명세 | 설정 문서와 주요 사건, 엔딩을 응답 형식으로 변환. 외형은 설정 문서에 넣지 않음 | `test_story_compile.py`의 `test_spec_to_response_` 계열 <br> `test_compile_characters.py`의 `test_appearance_not_in_togul` |
| CP-12 | 응답 계약 | HTTP 컴파일 요청 | 중첩 응답 형식과 `meta`가 계약에 맞음. 모델 오류는 502 | `tests/test_story_compile_api.py` |
| CP-13 | 두 단계의 연결 | 스토리라인 입력의 인물 명단을 컴파일에 전달 | 인물 명단을 유지. 보완 한도를 넘으면 이미지를 만들지 않고 502 | `tests/test_story_character_count_flow.py` |

<br>

### 7-2-4 이미지 케이스

인물 이미지와 썸네일의 생성 규칙을 기준으로 검사한다. ([3-3 인물 이미지 생성](3-TASK-DEFINITION.md#3-3-인물-이미지-생성), [3-4 썸네일 생성](3-TASK-DEFINITION.md#3-4-썸네일-생성))

이미지 실패는 실패 계약의 `error` 값과 비교한다. ([5-4 실패 계약](5-CONTRACT.md#5-4-실패-계약))

| 식별자 | 확인 대상 | 입력과 조건 | 기대 결과 | 코드 위치 |
|---|---|---|---|---|
| IM-01 | 인물 이미지 프롬프트 | 외형을 갖춘 인물, 장르 여러 개, 외형이 없거나 공백 | 인물 블록을 채움. 외형이 부족하면 프롬프트를 만들지 않음 | `tests/unit/test_image_characters.py` |
| IM-02 | 템플릿 읽기 | 파일 없음, 프롬프트 블록 없음 | 예외 발생 | `test_image_characters.py`의 `test_load_template_` 계열 |
| IM-03 | 인물별 생성 | 전원 성공, 일부 실패, 전원 실패, 외형 부족, 빈 목록, 깨진 공급자 응답 | 인물별 결과 반환. 한 인물의 이미지 생성 실패가 다른 인물의 결과에 영향을 주지 않음 | `test_image_characters.py`의 `test_generate_` 계열 |
| IM-04 | 이미지 어댑터의 오류 변환 | 시간 초과, 호출량 제한, 요청 거부, 빈 데이터, 깨진 Base64 | 공급자와 관계없이 쓰는 공통 예외로 변환 | `tests/unit/test_image_generation.py`의 `test_openai_generate_` 계열 |
| IM-05 | 실패 코드 | 공급자 오류 문구 | 정해진 `error` 값으로 변환. 단어 일부가 겹치는 문구를 호출량 제한으로 오인하지 않음 | `tests/unit/test_compile_images.py`의 `test_classify_image_error_` 계열 <br> `tests/unit/test_compile_thumbnail.py`의 `test_thumbnail_safe_maps_failure_to_stable_code` |
| IM-06 | 컴파일과의 결합 | 인물 이미지 실패, 썸네일 실패, 이미지 로직의 예상하지 못한 오류 | 컴파일은 200. 한쪽 실패가 다른 쪽 결과를 지우지 않음 | `test_compile_thumbnail.py`의 `test_compile_story_thumbnail_failure_keeps_200_and_character_images`, `test_compile_story_character_failure_keeps_thumbnail` <br> `test_compile_images.py` |
| IM-07 | 동시 실행 | 인물 이미지와 썸네일 | 두 생성을 동시에 실행 | `test_compile_thumbnail.py`의 `test_compile_story_runs_images_and_thumbnail_concurrently` |
| IM-08 | 썸네일 인물 선정 | 외형을 모두 갖춘 인물이 0명, 1명, 3명 이상. 인물 없음 | 외형을 모두 갖춘 인물 중 앞에서 최대 2명 사용 <br> 해당 인물이 없으면 첫 인물의 채워진 정보 사용 <br> 인물이 없으면 장르만 사용. 인물 이름은 프롬프트에서 제외 | `tests/unit/test_image_thumbnail.py` |
| IM-09 | 크기와 형식 | 썸네일 생성 호출 | 세로 3:4 크기로 호출. 응답에 내용 형식과 이미지 이름 포함 | `test_compile_thumbnail.py`, `test_image_generation.py`의 크기 테스트 <br> `test_compile_images.py`의 `test_character_image_out_` 계열 |
| IM-10 | Sentry 보고 | 공급자 실패, 전체 실패, 외형 부족 | 실패는 보고하고 외형 부족은 보고하지 않음 | `test_image_characters.py`, `test_compile_images.py`, `test_compile_thumbnail.py`의 Sentry 테스트 |
| IM-11 | 호출 기록 | 사용량 있음, 일부만 있음, 없음, 실패, 응답 해석 실패 | 받은 사용량만 기록. 해석에 실패해도 사용량은 남김. 이미지 데이터는 기록하지 않음 | `test_image_generation.py`의 `test_openai_generate_records_` 계열 |
| IM-12 | 서버 시작 검사 | 등록되지 않은 이미지 모델, 잘못된 키와 인자 | 시작 검사에서 거부 | `test_image_generation.py`의 `test_image_startup_validation_` 계열 |

<br>

### 7-2-5 실패와 반복

오류 처리 규칙을 기준으로 검사한다. ([7-1 오류 처리](7-1-ERROR-HANDLING.md))

모든 케이스에 가짜 응답과 예외를 사용하며 실제 모델은 호출하지 않는다.

| 식별자 | 상황 | 기대 결과 | 코드 위치 |
|---|---|---|---|
| FL-01 | 시간 초과, 호출량 제한, 요청 거부, 연결 실패 | 502와 분류별 메시지. Sentry 분류가 일치 | `tests/unit/test_story_llm_faults.py`의 `test_provider_error_returns_502` <br> `tests/unit/test_sentry.py`의 `test_classify_` 계열 |
| FL-02 | 전송 오류 | 코드는 다시 호출하지 않음 | `test_story_llm_faults.py`의 `test_provider_error_is_not_retried` |
| FL-03 | 빈 본문, 깨진 JSON, 객체가 아닌 응답, 깨진 SDK 응답 형태 | 유효하지 않은 응답으로 분류하고 502 | `test_bad_content_returns_502_invalid`, `test_malformed_sdk_shape_returns_502_invalid` |
| FL-04 | 코드 펜스로 감싼 JSON | 통과 | `test_code_fenced_json_passes` |
| FL-05 | 유효하지 않은 응답 뒤 성공 | 재호출해 200. `retry_count`에 반영 | `test_invalid_json_retries_then_succeeds`, `test_generate_storylines_retries_twice_on_invalid` |
| FL-06 | 재호출 한도 도달 | 502 | `test_invalid_json_exhausts_retries_returns_502` <br> `tests/unit/test_story_compile.py`의 `test_compile_story_502_after_max_refill`, `test_compile_story_refill_boundary_retry_two` |
| FL-07 | 60초가 지난 뒤의 유효하지 않은 응답 | 새 재호출을 시작하지 않음 | `test_retry_gives_up_after_deadline` |
| FL-08 | 재호출의 제한 시간 | 남은 시간에 맞춰 줄이되 최소 1초로 지정 | `test_retry_attempt_timeout_shrinks_to_remaining_budget`, `test_retry_attempt_timeout_never_goes_below_one_second` |
| FL-09 | 등록되지 않은 모델 | 502로 바꾸지 않음 | `test_unregistered_model_is_not_disguised_as_502` |
| FL-10 | 사용량이나 모델 이름이 없는 응답 | 토큰은 `null`, 모델은 요청한 이름으로 통과 | `test_missing_usage_passes_with_null_tokens`, `test_missing_model_falls_back_to_requested_model` |
| FL-11 | 엔딩이 불완전하고 다른 필수 항목도 비어 있음 | 엔딩을 빈 배열로 대체해 성공 처리하지 않고 502 반환 | `test_story_compile.py`의 `test_compile_story_502_when_endings_incomplete_and_other_field_missing` |
| FL-12 | 보완 뒤에도 인물 이름이 겹침 | 502 | `tests/unit/test_compile_characters.py`의 `test_compile_story_502_when_duplicate_name_remains_after_refills` |
| FL-13 | 성공한 컴파일, 형식 변환 실패 | 성공은 보고하지 않고 실패만 보고 | `test_story_compile.py`의 `test_compile_story_success_does_not_capture`, `test_compile_story_schema_failure_captures` |
| FL-14 | 관측 도구의 초기화, 추적 시작, 종료 실패 | 요청 처리에 영향 없음 | `tests/unit/test_langfuse.py` |

테스트가 없는 상황은 다음과 같다.

| 상황 | 상태 |
|---|---|
| 백엔드가 먼저 연결을 끊었을 때 진행 중인 호출이 이어지는 동작 | 테스트 없음. 계약에 동작만 적혀 있음 ([5-6 시간과 복구](5-CONTRACT.md#5-6-시간과-복구)) |
| 같은 요청을 두 번 받음 | 테스트 없음. AI 서버는 중복을 막지 않으며 백엔드가 맡음 |
| SDK 재시도의 실제 횟수와 시간 | 어댑터 단위 테스트가 설정값 전달만 확인. 실제 재시도는 실행하지 않음 |
| 결과 전송 실패 | 해당 없음. 같은 HTTP 연결로 응답함 |

<br>

### 7-2-6 통합 테스트

IT-01부터 IT-04는 실제 모델을 호출하므로 비용이 든다. `RUN_LIVE_TESTS=1`일 때만 실행하며 CI에서는 건너뛴다. IT-05는 모델을 호출하지 않으므로 CI에서도 실행한다.

| 식별자 | 실행 범위 | 입력 | 확인하는 것 | 코드 위치 |
|---|---|---|---|---|
| IT-01 | HTTP 스토리라인 요청부터 응답까지 | 테스트 코드에 적힌 고정 입력 한 건 | 200, 후보 3편, 후보별 추천 정보 3개, 빈 값 없음, `meta`의 토큰 수 | `tests/integration/test_storylines_live.py` |
| IT-02 | 컴파일 서비스 함수 | 고정 입력 한 건 | 설정 문서의 제목과 구분, 첫 선택지 3개, 주요 사건 3개에서 5개, 엔딩 0개 또는 3개, `meta`의 토큰 수 | `tests/integration/test_story_compile_live.py`의 `test_compile_story_live` |
| IT-03 | 컴파일 부분 보완 | 블록과 인물 필드가 빠진 명세 | 보완 호출 한 번으로 요청한 부분만 채움 | `test_story_compile_live.py`의 `test_compile_refill_repairs_mixed_issues_in_one_live_call` |
| IT-04 | 이미지 생성 | 고정 프롬프트 | WebP 형식, 썸네일은 요청한 세로 크기 | `tests/integration/test_image_generation_live.py` |
| IT-05 | 컴파일 결과를 채팅 입력으로 연결 | 저장된 유효 명세. 모델을 호출하지 않아 매번 실행됨 | 설정, 주요 사건과 엔딩이 채팅 프롬프트의 자리에 들어감 | `tests/integration/test_compile_chat_chaining.py` |

- 통합 테스트는 문장을 비교하지 않는다. 상태 코드, 형식과 개수만 본다.
- 현재는 테스트 코드에 직접 적은 고정 입력을 사용한다. 벤치마크와는 연결하지 않았다. 벤치마크가 아직 확정되지 않았기 때문이다. ([6-4-2 벤치마크](6-4-AI-EVALUATION-METHOD.md#6-4-2-벤치마크))
- 벤치마크가 확정되면 합격 판정의 선정 기준에 따라 사례 5건 안팎을 고른다. ([6-4-8 합격 판정](6-4-AI-EVALUATION-METHOD.md#6-4-8-합격-판정))

  테스트에는 사례 ID와 세트 버전을 기록한다.
- 선정 기준 중 인물 정보를 모두 비운 입력, 주변 인물 5명의 입력, 로어북이 있는 입력은 현재 통합 테스트에 없다.
- HTTP 컴파일 요청을 실제 모델로 끝까지 실행하는 통합 테스트는 없다. IT-02는 서비스 함수를 직접 호출한다.

<br>

### 7-2-7 실행 증거

테스트는 도커 환경에서 `scripts/test.sh`로 실행한다. CI에서는 `pytest`를 실행하며 분기 커버리지 90% 이상을 요구한다. 린트와 타입 검사는 실행하지 않는다.

이번 문서 정리에서는 테스트를 실행하지 않았다.

| 실행 | 명령 | 환경 |
|---|---|---|
| 일반 테스트 | `./scripts/test.sh` | 도커 `python:3.11-slim`, 더미 키, 통합 테스트는 건너뜀 |
| 일부만 실행 | `./scripts/test.sh tests/unit` | 위와 같음 |
| 통합 테스트 포함 | `./scripts/test.sh --live` | `RUN_LIVE_TESTS=1`, `.env`의 실제 키 필요, 비용 발생 |
| CI | `pytest --cov --cov-report=term-missing --cov-fail-under=90` | GitHub Actions의 `docker-image.yml` |

결과를 남길 때 다음을 지킨다.

- 대상 커밋, 실행 명령, 통과·실패·건너뛴 테스트 수를 PR에 적는다. 결과를 모아 두는 별도 위치는 정하지 않았다.
- 건너뛴 테스트를 통과로 적지 않는다. 통합 테스트를 실행하지 않았으면 실행하지 않았다고 적는다.
- 테스트 코드의 존재와 실행 결과를 구분한다. 이 문서의 표는 코드가 있다는 뜻이며 통과를 보장하지 않는다.
- 실패한 통합 테스트를 통과할 때까지 반복 실행하지 않는다. 모델 출력 때문에 가끔 실패하면 실패 비율을 적고 AI 정렬의 개선 항목으로 기록한다. ([6-3 AI 정렬](6-3-AI-ALIGNMENT.md))
- 통과시키려고 검사 기준을 낮추지 않는다. 기준을 바꿔야 하면 해당 명세를 먼저 고친다.
- 커버리지 90%는 분기 기준이며 `src/`만 측정한다.
