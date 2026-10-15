# 7-2 테스트 케이스

본 문서는 채팅의 정상 동작과 오류 처리가 명세를 따르는지 검증할 테스트를 정의한다.

테스트별 입력과 상황, 기대 결과, 코드 위치와 실행 방법, 외부 시스템과의 통합 범위를 정리한다.

<br>

### 7-2-1 테스트 범위

| 종류 | 확인 범위 | 외부 호출 | 실행 |
|---|---|---|---|
| 단위 | 입력 검증, 프롬프트 조립, 본문 변환, 판정 보정, 이미지 처리와 선택지 보완 | 가짜 SDK 출력과 예외, HTTP 응답으로 대체 | 로컬, CI |
| API | HTTP 상태, SSE 순서와 필드, 메타, 대기와 취소 | 서비스 함수나 SDK 대체, ASGI 클라이언트 사용 | 로컬, CI |
| 저장 이미지 선택 | 후보 구성, TypeSafe 요청과 응답 검사, 대체 이미지와 순차 전송 | 가짜 HTTP 응답 또는 선택 함수로 대체 | 로컬, CI |
| 이미지 경로 통합 | 본문 수신부터 기본 이미지 선택, 편집, 업로드와 SSE 연결 | SDK 또는 HTTP 전송 대체 | 로컬, CI |
| 실제 모델 통합 | 본문 서비스와 채팅 턴 HTTP, 선택지 HTTP | 실제 텍스트 공급자 호출 | 수동 실행<br>`RUN_LIVE_TESTS=1` 필요 |
| 컴파일과 채팅 연결 | 컴파일 출력의 채팅 프롬프트 반영 | 저장된 명세 사용, 외부 호출 없음 | 로컬, CI |

<br>

**외부 의존성과 테스트 데이터**

| 대상 | 방법 |
|---|---|
| 텍스트 모델 | `install_llm_sdk`로 가짜 클라이언트 설치<br>`FakeStream`으로 조각, 종료, 중간 예외와 닫힘 재현 |
| API | `client`의 `ASGITransport`로 요청<br>일반 API 테스트는 본문이나 선택지 서비스 결과 대체 |
| 이미지 다운로드, 편집과 업로드 | `httpx.MockTransport`, `AsyncMock` 사용<br>일부 케이스는 실제 OpenAI SDK에 가짜 HTTP 전송을 연결해 요청 형식과 호출 횟수 검사 |
| 시간과 취소 | 짧은 시험용 시간 한도, 단조 시계와 `asyncio.Event`로 지연·종료 재현<br>운영 시간값 전달 검사와 실제 대기 종료 검사를 구분 |
| 관측 | `tests/conftest.py`에서 실제 Sentry, Langfuse와 추적 전송 비활성화<br>기록 함수 대체 후 전달 인자 검사 |
| 요청과 결과 | 각 테스트의 고정 요청, 가짜 모델 응답과 시험용 이미지 바이트 사용<br>실제 사용자 대화와 비밀값 사용 안 함 |
| 컴파일 연결 | `tests/unit/fixtures/spec_valid.json`을 출력 모델로 변환해 사용 |
| 인증 정보 | 일반 실행은 더미 키 사용<br>라이브 실행은 선택한 모델에 필요한 실제 키 사용 |

<details>
<summary><b>실행 명령</b></summary>

<br>

명령은 `manyak-ai` 저장소에서 실행한다.

| 실행 | 명령 | 조건 |
|---|---|---|
| 일반 테스트 | `./scripts/test.sh` | Docker `python:3.11-slim`, 개발 의존성 설치<br>실제 모델 테스트는 건너뜀 |
| 단위 테스트 | `./scripts/test.sh tests/unit` | 위와 같음 |
| 채팅 API | `./scripts/test.sh tests/test_chat_api.py tests/test_chat_choices_api.py` | 공급자 호출 대체 |
| 컴파일과 채팅 연결 | `./scripts/test.sh tests/integration/test_compile_chat_chaining.py` | 실제 모델 호출 없음 |
| 실제 채팅 모델 통합 | `./scripts/test.sh --live tests/integration/test_chat_live.py` | `.env`의 실제 키 필요<br>호출 비용 발생 |
| CI | `pytest --cov --cov-report=term-missing --cov-fail-under=90` | Python 3.11<br>`src/` 전체 분기 커버리지 90% 이상 |

로컬 검증은 Docker 실행 스크립트를 사용한다. CI의 커버리지 기준은 전체 테스트에 적용하며 채팅 파일만 실행한 결과와 구분한다. 실제 모델 테스트는 예상 호출 규모를 확인하고 승인 후 실행한다.

PR에 대상 커밋, 실행 명령, 모델과 설정, 통과·실패·건너뜀 건수와 로그 위치를 남긴다.

</details>

<br>

### 7-2-2 채팅 응답 생성

| 확인 항목 | 입력과 상황 | 기대 결과 | 테스트 코드 |
|---|---|---|---|
| 요청 기본값과 경계 | 사건과 이미지 필드 생략, 음수 진행 턴 수, 주요 사건 11개<br>이미지 이름 생략 또는 `null`, 알 수 없는 입력 출처 | 선택 필드 기본값 적용<br>음수 진행 턴 수와 사건 상한 초과 거부<br>이미지 이름은 빈 문자열, 알 수 없는 출처는 `null` | [test_chat_turn_schema](../../../../manyak-ai/tests/unit/test_chat_turn_schema.py) |
| 프롬프트 순서와 입력 반영 | 설정, 이력, 요약, 사건과 엔딩을 포함한 요청 | 메시지 역할과 레이어 순서 유지<br>정해진 슬롯에 입력 반영, 미치환 슬롯 없음<br>핵심 규칙 재배치 순서 유지 | [test_chat_assembler](../../../../manyak-ai/tests/unit/test_chat_assembler.py) |
| 이미지 마커와 원본 보존 | 시작 설정과 이전 본문에 저장 마커 포함 | 모델 입력에서 마커 제거<br>원래 요청과 이력은 유지<br>인물 이미지 목록은 본문 프롬프트에서 제외 | [test_chat_assembler](../../../../manyak-ai/tests/unit/test_chat_assembler.py) |
| 스트림과 화자 변환 | 빈 조각, 여러 조각으로 나뉜 화자명, 굵은 화자 표기 | 빈 조각 제외<br>본문과 완료 결과 모두 같은 평문 화자 표기 사용<br>화자 밖의 강조는 유지 | [test_chat_llm](../../../../manyak-ai/tests/unit/test_chat_llm.py) |
| 인물 이미지 연결 | 반복 대사, 정식 이름과 별칭, 충돌하는 별칭, 긴 이름 | 인물별 첫 대사 앞에 이미지 한 번 표시<br>정식 이름 우선, 모호한 별칭 제외<br>이벤트와 저장 마커의 인물·순서 일치 | [test_chat_llm](../../../../manyak-ai/tests/unit/test_chat_llm.py) |
| 턴별 상태 분리 | 다음 턴에서 다른 화자 등장 | 이전 턴의 이미지 표시 상태를 이어받지 않음 | [test_chat_llm](../../../../manyak-ai/tests/unit/test_chat_llm.py) |
| 본문 실패 | 호출 시작 실패, 일부 토큰 전달 뒤 연결 오류 | `LLM_ERROR`와 정제 메시지 출력<br>공급자 원문 제외, `completed` 없음 | [test_chat_llm](../../../../manyak-ai/tests/unit/test_chat_llm.py), [test_chat_api](../../../../manyak-ai/tests/test_chat_api.py) |
| 완료 응답과 메타 | 가짜 본문과 판정 결과, 사용량 누락 | SSE 필드는 camelCase<br>`choices=[]`, 본문과 판정 사용량 합산<br>알 수 없는 사용량은 `null`, `retryCount=0` | [test_chat_api](../../../../manyak-ai/tests/test_chat_api.py), [test_chat_llm](../../../../manyak-ai/tests/unit/test_chat_llm.py) |
| 요청 문맥 격리 | 서로 다른 식별자로 동시 요청 | 각 요청의 관측 식별자가 섞이지 않음 | [test_chat_api](../../../../manyak-ai/tests/test_chat_api.py) |

<br>

### 7-2-3 사건과 엔딩 판정

| 확인 항목 | 입력과 상황 | 기대 결과 | 테스트 코드 |
|---|---|---|---|
| 대상 없음 | 주요 사건과 엔딩 후보 모두 없음 | 모델 호출 없이 `targetMainEvent`, `occurredMainEventName`, `endingName` 모두 `null` | [test_chat_judgement](../../../../manyak-ai/tests/unit/test_chat_judgement.py) |
| 입력과 호출 인자 | 사건과 엔딩 후보, 이미지 마커가 있는 본문 | 판정 입력에서 마커 제거<br>본문 모델 사용, JSON 모드, 출력 256토큰과 제한 시간 전달 | [test_chat_judgement](../../../../manyak-ai/tests/unit/test_chat_judgement.py) |
| 정상 결과와 이름 보정 | 유효한 판정, 목록 밖 이름, 음수 진행 턴 수 | 유효한 값 유지<br>유효하지 않은 필드만 `null` | [test_chat_judgement](../../../../manyak-ai/tests/unit/test_chat_judgement.py) |
| 사건 상태 일관성 | 이전에 완결된 사건을 재보고, 목표와 이번 완결 사건이 같음 | 이미 완결된 사건을 목표나 완결 사건으로 다시 반환하지 않음<br>이번에 완결된 목표는 해제 | [test_chat_judgement](../../../../manyak-ai/tests/unit/test_chat_judgement.py) |
| 판정 내부 예외 | 서비스 내부 코드 오류 | 예외 전파, 빈 판정으로 변환하지 않음 | [test_chat_judgement](../../../../manyak-ai/tests/unit/test_chat_judgement.py) |
| 호출과 출력 실패 | 공급자 시간 초과를 포함한 모델 오류, 빈 응답, 잘못된 JSON, 객체가 아닌 출력 | 예상한 실패를 기록하고 `targetMainEvent`, `occurredMainEventName`, `endingName` 모두 `null`<br>내부 코드 결함은 빈 판정으로 숨기지 않음 | [test_chat_judgement](../../../../manyak-ai/tests/unit/test_chat_judgement.py) |
| 남은 시간 소진 | 기존 목표가 있는 요청, 남은 시간 0 | 모델 호출 안 함<br>목표와 진행 턴 수 유지, 완결 사건과 엔딩은 `null`<br>완료 이벤트에도 같은 상태 반영 | [test_chat_judgement](../../../../manyak-ai/tests/unit/test_chat_judgement.py), [test_chat_api](../../../../manyak-ai/tests/test_chat_api.py) |
| 자체 대기 시간 초과 | 판정 호출을 한도보다 오래 지연 | 진행 중 호출 취소<br>기존 목표와 진행 턴 수 유지<br>시간 초과 기록 한 번 | [test_chat_judgement](../../../../manyak-ai/tests/unit/test_chat_judgement.py) |
| 시간 배정과 ping | 본문 생성 지연, 느린 판정과 즉시 끝나는 판정 | 본문 경과 시간과 완료 여유를 빼서 판정 시간 배정<br>최대 60초<br>대기 중 ping, 즉시 완료 시 불필요한 ping 없음 | [test_chat_api](../../../../manyak-ai/tests/test_chat_api.py) |

<br>

### 7-2-4 실시간 이미지

| 확인 항목 | 입력과 상황 | 기대 결과 | 테스트 코드 |
|---|---|---|---|
| 슬롯 검증과 생성 조건 | 슬롯 생략, 2개 슬롯, 빈 키, 허용하지 않는 URL 형식<br>호환용 플래그만 전달 | 슬롯 없으면 생성 안 함<br>개수와 형식 위반은 422<br>검증 오류 응답에서 입력 원문과 서명 URL 제외 | [test_chat_turn_schema](../../../../manyak-ai/tests/unit/test_chat_turn_schema.py), [test_chat_api](../../../../manyak-ai/tests/test_chat_api.py) |
| 기본 이미지와 대상 선정 | 이미지 목록 순서 변경, 기본 이미지 없는 첫 화자, 별칭 충돌 | 기본 이미지가 있는 첫 화자 선택<br>모호한 별칭 제외, 대상 없으면 생성 생략 | [test_child_image_input](../../../../manyak-ai/tests/unit/test_child_image_input.py) |
| 대화 입력 구성 | 오프닝, 짝 없는 메시지, 이전 대화 여러 턴과 이미지 마커 | 최근 완전한 대화 최대 2턴을 시간순 반영<br>현재 본문은 대상 인물의 첫 대사 줄 끝까지 사용<br>현재 입력 한 번 포함, 이미지 마커 제거<br>원본 이력 유지 | [test_child_image_input](../../../../manyak-ai/tests/unit/test_child_image_input.py) |
| 프롬프트 조립 | 짧은 이력과 템플릿 자리표시자가 포함된 시험 입력 | 대화 순서와 인용 형식 유지<br>삽입된 입력을 다시 템플릿으로 해석하지 않음 | [test_child_image_generation](../../../../manyak-ai/tests/unit/test_child_image_generation.py) |
| 다운로드 검증 | 허용하지 않는 호스트, HTTP, 사용자 정보나 다른 포트<br>리다이렉트, 404, 지원하지 않는 형식과 크기 초과 | 허용되지 않은 주소는 연결 전 거부<br>리다이렉트 따르지 않음<br>다운로드 실패 후 모델 호출 없음 | [test_child_image_generation](../../../../manyak-ai/tests/unit/test_child_image_generation.py) |
| 편집 호출과 결과 | PNG, JPEG, WebP 기본 이미지<br>성공, 400, 429, 500, 시간 초과, 깨진 Base64와 빈 데이터 | 참조 이미지를 `images.edit`에 전달<br>WebP 결과 또는 고정 오류 코드<br>SDK 재시도 없이 1회, 공급자 원문 제외 | [test_child_image_generation](../../../../manyak-ai/tests/unit/test_child_image_generation.py) |
| 업로드 | 생성 성공과 실패, 200·204·302·403·500, 연결 실패와 시간 초과 | WebP 바이너리를 한 번 PUT<br>2xx만 공개 URL 사용<br>생성 실패 시 업로드 생략<br>실패 데이터 제거, 서명 URL 로그 제외 | [test_child_image_upload](../../../../manyak-ai/tests/unit/test_child_image_upload.py) |
| 본문과 이미지 연결 | 업로드 성공, 생성·업로드 실패, 같은 기본 URL을 쓰는 다른 인물 | 대상 인물의 이벤트와 저장 마커만 교체<br>실패 시 기본 이미지와 본문 유지<br>외부 응답에 이미지 바이너리 없음 | [test_chat_child_image](../../../../manyak-ai/tests/unit/test_chat_child_image.py), [test_chat_api](../../../../manyak-ai/tests/test_chat_api.py) |
| 본문 실패와 시간 초과 | 본문 `error`, 본문 수집 마감 초과 | 이미지와 판정 시작 안 함<br>원본 스트림 닫고 SSE `error` | [test_chat_child_image](../../../../manyak-ai/tests/unit/test_chat_child_image.py) |
| 이미지 마감 | 다운로드·생성·업로드 지연, 취소 뒤 늦은 반환 | 전체 작업 시간으로 제한<br>늦은 결과 제외, 기본 이미지 유지<br>본문 전송 시간 확보 | [test_chat_child_image](../../../../manyak-ai/tests/unit/test_chat_child_image.py), [test_child_image_upload](../../../../manyak-ai/tests/unit/test_child_image_upload.py) |
| 전송 순서와 마감 | 이미지 처리 지연, 긴 본문, 본문 전송 중 마감 | 이미지 처리가 끝난 뒤 본문과 이미지를 순서대로 전달<br>전송 간격을 남은 시간에 맞춤<br>마감 후 남은 본문을 보내지 않고 `error` | [test_chat_child_image](../../../../manyak-ai/tests/unit/test_chat_child_image.py) |
| 병렬 실행과 요청 분리 | 판정과 이미지가 서로 다른 순서로 완료, 동시 요청과 재생성 | 판정과 이미지 병렬 실행<br>인물 선택과 이미지 이름의 요청별 상태 분리 | [test_chat_api](../../../../manyak-ai/tests/test_chat_api.py), [test_chat_child_image](../../../../manyak-ai/tests/unit/test_chat_child_image.py), [test_child_image_input](../../../../manyak-ai/tests/unit/test_child_image_input.py) |

<br>

### 7-2-5 선택지 생성

| 확인 항목 | 입력과 상황 | 기대 결과 | 테스트 코드 |
|---|---|---|---|
| 입력과 프롬프트 | 사건과 목표, 완결 사건, 이미지 마커가 있는 이력과 이번 본문 | 사건 재료 반영, 미치환 슬롯과 이미지 마커 제외 | [test_chat_choices](../../../../manyak-ai/tests/unit/test_chat_choices.py) |
| 호출 모델과 설정 | 본문과 다른 선택지 모델 설정 | `CHAT_CHOICE_MODEL` 사용<br>JSON 모드, 출력 512토큰과 60초 전달<br>성공·실패 기록의 공급자와 모델 일치 | [test_chat_choices](../../../../manyak-ai/tests/unit/test_chat_choices.py) |
| 최초 성공과 초과 | 첫 응답에 선택지 3개 또는 5개 | 앞의 유효한 3개 반환, 보완 횟수 0 | [test_chat_choices](../../../../manyak-ai/tests/unit/test_chat_choices.py) |
| 누적과 중복 | 최초 2개 뒤 새 항목 1개, 같은 문구 반복 | 기존 선택지를 유지하고 새 선택지 누적<br>완전히 같은 문구 중복 제외<br>추가 호출 횟수와 사용량 합산 | [test_chat_choices](../../../../manyak-ai/tests/unit/test_chat_choices.py) |
| 보완 소진 | 매 호출 같은 선택지 1개만 반환 | 추가 호출 최대 2회<br>확보한 선택지 유지, 대체 문구로 3개 구성 | [test_chat_choices](../../../../manyak-ai/tests/unit/test_chat_choices.py) |
| 호출과 출력 실패 | 모든 호출 실패, 빈 응답, 잘못된 JSON, 객체·배열 형식 위반 | 한도 내 추가 호출 후 대체 문구 3개<br>성공한 호출이 없으면 토큰 `null`<br>코드 펜스 안의 정상 JSON은 허용 | [test_chat_choices](../../../../manyak-ai/tests/unit/test_chat_choices.py) |
| 내부 예외 | 코드 결함으로 `AttributeError` 발생 | 대체 선택지로 숨기지 않고 예외 전파 | [test_chat_choices](../../../../manyak-ai/tests/unit/test_chat_choices.py) |
| API와 메타 | 정상 결과와 대체 결과, `ai_output` 누락 | 정상·대체 모두 200, 선택지 3개와 snake_case 메타<br>`NEXT_ACTIONS` 버전과 `retry_count` 반영<br>필수 입력 누락은 422 | [test_chat_choices_api](../../../../manyak-ai/tests/test_chat_choices_api.py) |
| 출력 스키마 | 선택지 2개 또는 4개로 응답 모델 구성 | 검증 오류 | [test_chat_choices_api](../../../../manyak-ai/tests/test_chat_choices_api.py) |

<br>

### 7-2-6 저장 이미지 선택

| 확인 항목 | 입력과 상황 | 기대 결과 | 테스트 코드 |
|---|---|---|---|
| 저장 이미지 후보 | 대사하지 않은 인물, 빈 필드, 인물별 후보 0·1·2·256개 | 화자와 유효 후보만 사용<br>단일 후보는 바로 선택, 2~255개 후보의 질문만 한 번에 호출 | [test_chat_image_selection](../../../../manyak-ai/tests/unit/test_chat_image_selection.py) |
| 저장 이미지 입력과 선택 | 여러 화자, 최근 대화와 이미지 마커 | 최근 완전한 2턴과 이번 본문 전체 전달<br>후보의 URL 필드와 바이너리 제외, 선택 ID를 원본 이미지에 연결 | [test_chat_image_selection](../../../../manyak-ai/tests/unit/test_chat_image_selection.py) |
| 저장 이미지 선택 실패 | 키 누락, HTTP 실패, 잘못된 응답, 시간 초과 | 재호출 없이 단일 후보 유지<br>나머지는 기본 이미지, 없으면 첫 이미지 | [test_chat_image_selection](../../../../manyak-ai/tests/unit/test_chat_image_selection.py), [test_chat_selected_images](../../../../manyak-ai/tests/unit/test_chat_selected_images.py) |
| 저장 이미지 순차 전송 | 여러 인물과 반복 대사, 선택 지연, 본문 오류와 연결 종료 | 선택 후 인물별 첫 대사 앞에 이미지 표시<br>본문 최대 5자·0.06초 간격, 저장 결과와 일치<br>대기 중 ping, 본문 오류 시 선택 생략, 취소 시 스트림 정리 | [test_chat_selected_images](../../../../manyak-ai/tests/unit/test_chat_selected_images.py), [test_chat_api](../../../../manyak-ai/tests/test_chat_api.py) |

<br>

### 7-2-7 공통 오류 처리

| 확인 항목 | 입력과 상황 | 기대 결과 | 테스트 코드 |
|---|---|---|---|
| TypeSafe 어댑터 | 요청 형식, 모델·질문·후보·확률 오류, 1MB 초과 응답, 취소 | 단발 HTTP 호출, 응답 검증<br>답변 하나가 잘못돼도 호출 결과 전체 거부<br>공통 오류 변환, 원문 기록 제외, 취소 전파 | [test_llm_typesafe_api](../../../../manyak-ai/tests/unit/test_llm_typesafe_api.py) |
| 공급자 오류 분류 | 시간 초과, 호출량 제한, 요청 거부와 연결 실패 | 공통 `LlmError` 하위 예외로 변환<br>시간 초과를 연결 오류보다 먼저 구분 | [test_llm_openai_sdk](../../../../manyak-ai/tests/unit/test_llm_openai_sdk.py) |
| 설정 오류 | 미등록 모델, 누락된 키와 잘못된 호출 설정 | 시작 검사 또는 호출 전 오류<br>공급자 오류와 별도 분류 | [test_llm_registry](../../../../manyak-ai/tests/unit/test_llm_registry.py), [test_llm_openai_sdk](../../../../manyak-ai/tests/unit/test_llm_openai_sdk.py) |
| 스트림 종료와 취소 | 소비자 중도 이탈, 정상 종료, 모델 오류와 요청 취소 | 모델 스트림 닫음<br>취소를 `LLM_ERROR`로 보고하지 않음<br>정리 실패가 원래 실패를 덮지 않음 | [test_chat_llm](../../../../manyak-ai/tests/unit/test_chat_llm.py), [test_llm_openai_sdk](../../../../manyak-ai/tests/unit/test_llm_openai_sdk.py) |
| 판정과 이미지 작업 회수 | 대기·본문 전송 중 연결 종료, HTTP 전송 중 취소 | 진행 중 작업 취소 후 정리 완료까지 회수<br>요청 취소를 이미지 시간 초과로 바꾸지 않음 | [test_chat_api](../../../../manyak-ai/tests/test_chat_api.py), [test_chat_child_image](../../../../manyak-ai/tests/unit/test_chat_child_image.py), [test_child_image_upload](../../../../manyak-ai/tests/unit/test_child_image_upload.py) |
| 오류 기록 | 본문·판정·선택지 실패 | 기능, 모델, 공급자, 재호출 횟수와 지연 기록<br>형식 오류는 `invalid_ai_response`로 구분 | [test_chat_llm](../../../../manyak-ai/tests/unit/test_chat_llm.py), [test_chat_judgement](../../../../manyak-ai/tests/unit/test_chat_judgement.py), [test_chat_choices](../../../../manyak-ai/tests/unit/test_chat_choices.py) |
| 이미지 관측 | 성공, 실패, 대상 없음과 취소 | 해당 상태와 사유 기록<br>이미지 결과 관측에 URL, 이미지 데이터와 인물 이름 제외 | [test_chat_api](../../../../manyak-ai/tests/test_chat_api.py), [test_chat_child_image](../../../../manyak-ai/tests/unit/test_chat_child_image.py) |
| 모듈 경계 | 서비스에서 SDK 직접 사용 | 공통 모델 호출 모듈 사용<br>검사 대상 SDK 범위는 테스트 코드 기준 | [test_llm_gateway_boundary](../../../../manyak-ai/tests/unit/test_llm_gateway_boundary.py) |

<br>

### 7-2-8 통합 테스트

| 확인 항목 | 입력과 상황 | 기대 결과 | 테스트 코드 |
|---|---|---|---|
| 컴파일과 채팅 연결 | 저장된 `StorySpec`을 컴파일 응답으로 변환한 뒤 채팅 요청에 전달 | 설정, 시작 설정, 주요 사건과 엔딩이 프롬프트 슬롯에 반영<br>미치환 슬롯 없음 | [test_compile_chat_chaining](../../../../manyak-ai/tests/integration/test_compile_chat_chaining.py) |
| 이미지 연결 경로 | 본문 SDK 출력과 다운로드·편집 HTTP 대체<br>업로드 함수는 성공 URL 또는 기존 오류를 반환하는 가짜 함수 사용<br>성공, 다운로드 실패, 시간 초과, 호출량 제한과 잘못된 이미지 | SSE 이미지와 저장 마커 일치<br>성공 시 새 URL, 실패 시 기본 이미지 유지<br>같은 입력의 재생성 상태 분리 | [test_chat_api](../../../../manyak-ai/tests/test_chat_api.py)의 `test_child_image_from_body_sdk_through_edit_http_to_sse` |
| 업로드 결과 연결 | 실제 업로드 함수 실행, HTTP 통신은 가짜 응답으로 대체 | 업로드 결과를 채팅 완료 응답에 반영 | [test_chat_child_image](../../../../manyak-ai/tests/unit/test_chat_child_image.py)의 `test_real_upload_result_reaches_chat_completion` |
| 실제 본문 서비스 | 고정 스토리와 이전 대화로 조립 후 `stream_chat_turn` 호출 | 빈 본문 아님, 오류 없이 완료<br>본문에 선택지 블록 없음<br>실제 모델명과 사용량 수신 | [test_chat_live](../../../../manyak-ai/tests/integration/test_chat_live.py)의 `test_chat_turn_live` |
| 실제 채팅 턴 HTTP | 고정 요청을 ASGI 클라이언트로 전송 | 200 SSE, `completed`와 비어 있지 않은 `aiOutput`<br>`choices=[]`, `retryCount=0`, 입력 사용량 수신 | [test_chat_live](../../../../manyak-ai/tests/integration/test_chat_live.py)의 `test_chat_turn_full_path_live` |
| 실제 선택지 HTTP | 고정 본문을 `ai_output`으로 전달 | 선택지 3개, 빈 문구 없음<br>모델, 공급자, 토큰과 보완 횟수 메타 수신 | [test_chat_live](../../../../manyak-ai/tests/integration/test_chat_live.py)의 `test_chat_choices_full_path_live` |

<br>

| 미포함 범위 | 현재 상태 |
|---|---|
| 사건과 엔딩의 실제 모델 판정 | 일반 테스트는 가짜 판정 사용<br>현재 채팅 라이브 입력에는 판정 대상 없음 |
| 실제 실시간 이미지 전체 경로 | 다운로드, 이미지 편집과 저장소 PUT을 모두 실제로 연결하는 채팅 라이브 테스트 없음 |
| 채팅 완료 본문에서 선택지까지 연속 실행 | 라이브 선택지 요청은 별도 고정 본문 사용<br>직전 라이브 턴 결과를 넘기는 흐름은 검사하지 않음 |
| 운영 네트워크와 사용자 복구 | ASGI 호출은 프록시, 실제 SSE 연결, 백엔드 저장과 클라이언트 재접속을 검증하지 않음 |
| 선택지 모델 변경 | 현재 라이브 테스트는 `provider="deepseek"`를 기대함<br>다른 허용 모델 설정까지 일반화한 검증 아님 |
