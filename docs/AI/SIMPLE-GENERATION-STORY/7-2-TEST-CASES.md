# 7-2 테스트 케이스

코드 경로와 실행 명령은 `manyak-ai` 저장소 기준이다.

<br>

### 7-2-1 테스트 범위

| 종류 | 확인 범위 | 모델 호출 | 실행 |
|---|---|---|---|
| 단위 | 입력 검증, 프롬프트 조립, 보완과 출력 변환 | 가짜 출력과 예외로 대체 | 로컬, CI |
| API | HTTP 상태, 출력 형식과 메타 | 가짜 출력과 예외로 대체 | 로컬, CI |
| 실제 모델 통합 | 생성부터 최종 출력까지 연결 | 실제 공급자 호출 | 수동 실행 <br> `RUN_LIVE_TESTS=1` 필요 |
| 컴파일과 채팅 연결 | 컴파일 결과의 채팅 프롬프트 반영 | 저장된 명세 사용 | 로컬, CI |

- 백엔드 저장과 CDN은 테스트 범위에서 제외한다.
- 채팅과 공유하는 코드를 변경하면 채팅 테스트도 실행한다.
- 생성 문장의 일치 여부와 내용 성능은 검사하지 않는다.

<br>

**외부 의존성 대체**

| 대상 | 방법 |
|---|---|
| 텍스트 호출 | `install_llm_sdk`로 가짜 SDK 설치 또는 `_complete_json` 대체 |
| 이미지 호출 | 이미지 생성 함수와 `_safe` 함수 대체 |
| 오류 기록 | 보고 함수 대체 후 전달 인자 확인 |
| 호출 관측 | 일반 테스트에서 비활성화 <br> 관측 실패 테스트에서는 가짜 SDK 사용 |
| 인증 정보 | 일반 테스트에 더미 키 사용 |

<details>
<summary><b>실행 명령</b></summary>

<br>

| 실행 | 명령 | 조건 |
|---|---|---|
| 일반 테스트 | `./scripts/test.sh` | Docker `python:3.11-slim` <br> 실제 모델 호출 제외 |
| 단위 테스트 | `./scripts/test.sh tests/unit` | 위와 같음 |
| 실제 모델 포함 | `./scripts/test.sh --live` | `.env`의 실제 키 필요 <br> 호출 비용 발생 |
| CI | `pytest --cov --cov-report=term-missing --cov-fail-under=90` | `src/` 분기 커버리지 90% 이상 <br> 린트와 타입 검사 미실행 |

실행 결과는 대상 커밋, 명령과 통과, 실패, 건너뜀 건수를 PR에 기록한다.

</details>

<br>

### 7-2-2 스토리라인 생성

입출력 기준은 계약 문서를 따른다. ([5-2 스토리라인 요청과 결과](5-CONTRACT.md#5-2-스토리라인-요청과-결과))

| 확인 항목 | 입력과 상황 | 기대 결과 | 테스트 코드 |
|---|---|---|---|
| 입력 검증 | 빈 값, `null`, 공백 <br> 잘못된 성별과 특징 타입, 중복 이름 | 빈 값 정규화 <br> 계약 위반 시 검증 오류 | [test_story_schemas](../../../../manyak-ai/tests/unit/test_story_schemas.py) <br> [test_request_validation](../../../../manyak-ai/tests/test_request_validation.py) |
| 프롬프트 조립 | 인물 정보 일부 누락, 주변 인물 없음 <br> 자리표시자가 포함된 이름 | 인물 블록과 미정 표기 반영 <br> 이름 안의 자리표시자 유지 | [test_storylines_characters](../../../../manyak-ai/tests/unit/test_storylines_characters.py) |
| 출력 형식과 번호 | 후보 또는 추천 정보 수 오류, 빈 줄거리 <br> 후보 번호 누락과 순서 오류 | 형식 위반 시 최대 2회 재생성 <br> 소진 시 502 <br> 번호는 재생성 없이 1, 2, 3으로 정리 | [test_story_llm_faults](../../../../manyak-ai/tests/unit/test_story_llm_faults.py) |
| 인물 누락과 보완 | 일부 후보의 주변 인물 누락 <br> 이름의 정규화 차이, 입력 이름 없음 | NFC 정규화 후 이름 대조 <br> 누락 후보만 보완 <br> 주인공과 이름 미입력 인물은 검사 제외 | [test_storylines_characters](../../../../manyak-ai/tests/unit/test_storylines_characters.py) <br> [test_storylines_refill](../../../../manyak-ai/tests/unit/test_storylines_refill.py) |
| 보완 병합과 종료 | 다른 후보 번호, 범위 밖 번호, 후보 형식 위반 <br> 보완 2회 뒤에도 인물 누락 | 지정한 후보만 병합 <br> 후보 형식 위반 시 원본 유지 <br> 누락 지속 시 현재 결과로 200, 경고 기록 | [test_storylines_refill](../../../../manyak-ai/tests/unit/test_storylines_refill.py) <br> [test_storylines_characters](../../../../manyak-ai/tests/unit/test_storylines_characters.py) |
| API와 메타 | 토큰 정보 없음, 재호출 발생 <br> 서비스와 HTTP에 동일 입력 | 토큰 `null`, 실제 `retry_count` 반영 <br> 없는 식별자 기록 제외 <br> 서비스와 HTTP의 프롬프트 및 출력 일치 | [test_storylines_api](../../../../manyak-ai/tests/test_storylines_api.py) |

<br>

### 7-2-3 컴파일

입출력 기준은 계약 문서를 따른다. ([5-3 컴파일 요청과 결과](5-CONTRACT.md#5-3-컴파일-요청과-결과))

| 확인 항목 | 입력과 상황 | 기대 결과 | 테스트 코드 |
|---|---|---|---|
| 명세 검증 | 인물과 사건 수 경계값 <br> 엔딩 개수와 `min_turns` 하한 | 허용 범위 통과 <br> 개수와 타입 위반 거부 | [test_story_compile](../../../../manyak-ai/tests/unit/test_story_compile.py) |
| 프롬프트와 템플릿 | 추가 정보와 로어북 누락 <br> Gemini 모델 선택 | 빈 입력 대체 문구 반영 <br> 최초 생성과 보완에 공급자별 템플릿 적용 | [test_story_compile](../../../../manyak-ai/tests/unit/test_story_compile.py) <br> [test_compile_characters](../../../../manyak-ai/tests/unit/test_compile_characters.py) |
| 입력 보존 | 생성 결과의 장르, 주인공 이름과 성별, 주변 인물 이름 변경 | 입력값 복원 <br> 비운 입력은 생성값 유지 <br> 보완 후 재적용 | [test_compile_protagonist](../../../../manyak-ai/tests/unit/test_compile_protagonist.py) <br> [test_compile_characters](../../../../manyak-ai/tests/unit/test_compile_characters.py) |
| 필수 블록과 입력 인물 | 빈 필수값, 잘못된 객체 타입 <br> 내부 식별자 누락, 인물 누락과 개수 불일치 | 누락 블록 추출 <br> 입력 인물 오류 시 카드 블록 전체 보완 <br> 이미지 생성 전에 처리 | [test_story_compile](../../../../manyak-ai/tests/unit/test_story_compile.py) <br> [test_compile_character_count](../../../../manyak-ai/tests/unit/test_compile_character_count.py) |
| 인물 필드와 병합 | 빈 이름, 중복 이름, 외형 누락 <br> 블록과 필드 동시 누락 | 입력 인물 우선 보존 <br> 요청한 위치와 필드의 유효한 값만 병합 <br> 카드 전체 보완 시 개별 필드 보완 제외 | [test_compile_characters](../../../../manyak-ai/tests/unit/test_compile_characters.py) |
| 부분 완료와 최종 실패 | 보완 후 엔딩 또는 외형 누락 <br> 필수 블록 누락이나 중복 이름 지속 | 엔딩 빈 배열, 외형 빈 문자열 허용 <br> 필수 블록과 이름 오류는 502 | [test_story_compile](../../../../manyak-ai/tests/unit/test_story_compile.py) <br> [test_compile_characters](../../../../manyak-ai/tests/unit/test_compile_characters.py) |
| 출력 변환과 API | 유효한 명세, 모델 오류 <br> 스토리라인 인물 명단 전달 | 설정과 사건, 엔딩 변환 <br> 설정 문서에서 외형 제외 <br> 계약에 맞는 메타와 오류 출력 <br> 인물 보완 실패 시 이미지 생성 없이 502 | [test_story_compile](../../../../manyak-ai/tests/unit/test_story_compile.py) <br> [test_story_compile_api](../../../../manyak-ai/tests/test_story_compile_api.py) <br> [test_story_character_count_flow](../../../../manyak-ai/tests/test_story_character_count_flow.py) |

<br>

### 7-2-4 인물 이미지 생성

생성 조건과 실패 출력은 해당 문서를 따른다. ([6-1-3 인물 이미지](6-1-AI-EXECUTION.md#6-1-3-인물-이미지), [7-1-5 실패 출력](7-1-ERROR-HANDLING.md#7-1-5-실패-출력))

| 확인 항목 | 입력과 상황 | 기대 결과 | 테스트 코드 |
|---|---|---|---|
| 프롬프트와 외형 | 외형 충족 또는 누락 <br> 템플릿 파일과 블록 누락 | 인물별 프롬프트 조립 <br> 외형 부족 시 호출 생략 <br> 템플릿 누락 시 예외 | [test_image_characters](../../../../manyak-ai/tests/unit/test_image_characters.py) |
| 인물별 결과 | 전원 성공, 일부 실패, 전원 실패 <br> 빈 인물 목록 | 인물별 성공과 실패 결과 유지 <br> 다른 인물의 결과 보존 | [test_image_characters](../../../../manyak-ai/tests/unit/test_image_characters.py) |
| 출력과 실패 코드 | 성공 이미지, 공급자 오류 <br> 생성 로직 전체 예외 | 이미지 이름과 형식, Base64 출력 <br> 실패 시 정해진 오류 코드 <br> 전체 예외 시 빈 배열, 컴파일 200 유지 | [test_compile_images](../../../../manyak-ai/tests/unit/test_compile_images.py) |
| 썸네일과 동시 생성 | 두 이미지 생성 실행 <br> 한쪽 생성 실패 | 두 작업 동시 실행 <br> 성공한 쪽의 결과 유지 | [test_compile_thumbnail](../../../../manyak-ai/tests/unit/test_compile_thumbnail.py) |

<br>

### 7-2-5 썸네일 생성

생성 조건과 실패 출력은 해당 문서를 따른다. ([6-1-4 썸네일](6-1-AI-EXECUTION.md#6-1-4-썸네일), [7-1-5 실패 출력](7-1-ERROR-HANDLING.md#7-1-5-실패-출력))

| 확인 항목 | 입력과 상황 | 기대 결과 | 테스트 코드 |
|---|---|---|---|
| 표지 인물 선택 | 외형 완성 인물 0명, 1명, 3명 이상 <br> 인물 없음 | 외형 완성 인물 중 앞의 최대 2명 사용 <br> 없으면 첫 인물의 일부 정보, 인물이 없으면 장르 사용 <br> 프롬프트에서 인물 이름 제외 | [test_image_thumbnail](../../../../manyak-ai/tests/unit/test_image_thumbnail.py) |
| 크기와 출력 | 정상 썸네일 생성 | 세로 3:4 크기 호출 <br> 이미지 이름과 형식, Base64 출력 | [test_compile_thumbnail](../../../../manyak-ai/tests/unit/test_compile_thumbnail.py) <br> [test_image_generation](../../../../manyak-ai/tests/unit/test_image_generation.py) |
| 실패 처리 | 공급자 오류, 예상하지 못한 예외 | 썸네일 객체와 오류 코드 유지 <br> 컴파일 200 및 인물 이미지 보존 | [test_compile_thumbnail](../../../../manyak-ai/tests/unit/test_compile_thumbnail.py) |

<br>

### 7-2-6 공통 오류 처리

오류 분류와 복구 한도는 오류 처리 문서를 따른다. ([7-1 오류 처리](7-1-ERROR-HANDLING.md))

| 확인 항목 | 입력과 상황 | 기대 결과 | 테스트 코드 |
|---|---|---|---|
| 텍스트 공급자 오류 | 시간 초과, 호출량 제한, 요청 거부와 연결 실패 | 분류별 502 메시지와 오류 기록 <br> 서비스의 추가 재호출 없음 | [test_story_llm_faults](../../../../manyak-ai/tests/unit/test_story_llm_faults.py) <br> [test_sentry](../../../../manyak-ai/tests/unit/test_sentry.py) |
| 텍스트 파싱 | 빈 본문, 깨진 JSON, 객체가 아닌 출력 <br> 코드 펜스로 감싼 JSON | 유효하지 않은 출력 구분 <br> 코드 펜스 제거 후 유효한 JSON 허용 | [test_story_llm_faults](../../../../manyak-ai/tests/unit/test_story_llm_faults.py) |
| 재생성 한도 | 유효하지 않은 출력 반복 <br> 최초 생성부터 60초 경과 | 횟수 소진 시 502 <br> 60초 이후 새 재생성 없음 <br> 남은 시간으로 호출 제한 조정, 최소 1초 | [test_story_llm_faults](../../../../manyak-ai/tests/unit/test_story_llm_faults.py) |
| 설정과 사용량 | 미등록 모델, 잘못된 키와 인자 <br> 모델 이름 또는 사용량 없음 | 설정 오류를 502로 변환하지 않음 <br> 이미지 시작 검사 실패 <br> 누락 모델명은 입력값, 누락 토큰은 `null` | [test_story_llm_faults](../../../../manyak-ai/tests/unit/test_story_llm_faults.py) <br> [test_image_generation](../../../../manyak-ai/tests/unit/test_image_generation.py) |
| 이미지 공급자 오류 | 시간 초과, 호출량 제한, 요청 거부 <br> 빈 데이터와 깨진 Base64 | 공통 이미지 예외로 변환 <br> 오류 문구를 정해진 코드로 변환 | [test_image_generation](../../../../manyak-ai/tests/unit/test_image_generation.py) <br> [test_compile_images](../../../../manyak-ai/tests/unit/test_compile_images.py) |
| 오류와 호출 기록 | 공급자 실패, 형식 변환 실패, 외형 부족 <br> 사용량 일부 누락과 출력 해석 실패 | 실패 기록, 외형 부족은 보고 제외 <br> 받은 사용량만 기록 <br> 이미지 바이너리 기록 제외 | [test_image_characters](../../../../manyak-ai/tests/unit/test_image_characters.py) <br> [test_compile_images](../../../../manyak-ai/tests/unit/test_compile_images.py) <br> [test_image_generation](../../../../manyak-ai/tests/unit/test_image_generation.py) |
| 관측 실패 | 초기화, 추적 시작과 종료 실패 | 생성 요청 처리 유지 | [test_langfuse](../../../../manyak-ai/tests/unit/test_langfuse.py) <br> [test_sentry](../../../../manyak-ai/tests/unit/test_sentry.py) |
| 모듈 경계 | 서비스의 SDK 직접 사용 | 공통 호출 모듈 사용 확인 <br> 자동 검사 범위는 OpenAI와 Anthropic | [test_llm_gateway_boundary](../../../../manyak-ai/tests/unit/test_llm_gateway_boundary.py) |

<br>

**자동 테스트가 없는 항목**

| 항목 | 현재 상태 |
|---|---|
| 백엔드 연결 종료 후 생성 지속, 중복 요청 | 테스트 없음 |
| SDK의 실제 재시도 횟수와 시간 | 설정값 전달만 검사 |
| 취소 전파, 코드 결함의 원래 예외 유지 | 별도 자동 검사 확인 안 됨 |
| 비밀값과 주소 하드코딩, 설정 직접 접근 | 자동 검사 없음 |
| 평가 CLI와 운영 생성 코드 공유 | 평가 CLI 미구현 |

<br>

### 7-2-7 통합 테스트

실제 모델 호출은 수동으로 실행하며, 컴파일과 채팅 연결 테스트는 모델 호출 없이 CI에서도 실행한다.

| 확인 항목 | 입력과 상황 | 기대 결과 | 테스트 코드 |
|---|---|---|---|
| 스토리라인 HTTP | 고정 입력 한 건 | 200, 후보 3편과 후보별 추천 정보 3개 <br> 빈 값 없음, 토큰 메타 확인 | [test_storylines_live](../../../../manyak-ai/tests/integration/test_storylines_live.py) |
| 컴파일 서비스 | 고정 입력 한 건 | 설정 문서 형식 <br> 첫 선택지 3개, 사건 3~5개, 엔딩 0개 또는 3개 <br> 토큰 메타 확인 | [test_story_compile_live](../../../../manyak-ai/tests/integration/test_story_compile_live.py) |
| 컴파일 보완 | 블록과 인물 필드가 함께 누락된 명세 | 보완 호출 한 번으로 요청한 부분만 수정 | [test_story_compile_live](../../../../manyak-ai/tests/integration/test_story_compile_live.py) |
| 이미지 생성 | 고정 프롬프트 | WebP 형식 <br> 썸네일의 세로 크기 확인 | [test_image_generation_live](../../../../manyak-ai/tests/integration/test_image_generation_live.py) |
| 컴파일과 채팅 연결 | 저장된 명세 | 설정, 주요 사건과 엔딩을 채팅 프롬프트에 반영 | [test_compile_chat_chaining](../../../../manyak-ai/tests/integration/test_compile_chat_chaining.py) |

<br>

| 미포함 범위 | 현재 상태 |
|---|---|
| 실제 모델을 쓰는 HTTP 컴파일 전체 경로 | 서비스 직접 호출만 검사 |
| 인물 정보 전체 공백, 주변 인물 5명, 로어북 포함 입력 | 실제 모델 통합 테스트 없음 |
| AI 평가용 벤치마크 연계 | 고정 입력 사용 <br> 평가 연계 기준 미정 |
