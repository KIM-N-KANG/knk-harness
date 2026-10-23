# 7-4 배포

<br>

### 7-4-1 배포 단위와 경로

검수, 간편 제작과 채팅을 AI 서버 이미지 하나로 배포한다. 코드와 프롬프트 변경은 이미지 재빌드가 필요하다.

| 항목 | 구성 |
|---|---|
| 실행 | Python 3.11, FastAPI와 `uvicorn`, 포트 8000 |
| 포함 | `src/`, `prompt/`, 운영 의존성 |
| 제외 | 테스트, 개발 의존성, `.env` |
| 개발 배포 | `dev` push → GHCR → ECS `manyak-dev` |
| 운영 배포 | `main` push → ECR → ECS `manyak-prod-ai`<br>배포 시점의 `main` HEAD 이미지 사용 |
| 자동 검사 | 전체 테스트와 커버리지 90% 이상<br>컨테이너 health와 Langfuse 초기화 검사 |

<br>

### 7-4-2 검수 설정

설정은 환경 변수, `.env`, 코드 기본값 순으로 적용하며 변경 후 새 컨테이너를 실행한다.

| 환경 변수 | 코드 기본값 | 의미 |
|---|---|---|
| `MODERATION_MODEL` | `gpt-6-luna` | 기본 검수 모델 |
| `MODERATION_FALLBACK_MODEL` | `deepseek-flash` | 대체 검수 모델 |
| `MODERATION_IMAGE_TIMEOUT` | `30.0` | 이미지 전체 준비 제한 시간, 초 |
| `MODERATION_IMAGE_MAX_BYTES` | `33554432` | 이미지 한 장의 크기 상한, 바이트 |
| `MODERATION_CALL_TIMEOUT` | `60.0` | 모델 호출 1회 제한 시간, 초 |
| `MODERATION_REQUEST_TIMEOUT` | `150.0` | 검수 요청 전체 제한 시간, 초 |
| `IMAGE_PARENT_ALLOWED_HOSTS` | `["cdn.manyak.app", "dev-cdn.manyak.app"]` | 다운로드 허용 호스트 |
| `OPENAI_API_KEY`, `DEEPSEEK_API_KEY` | 비밀값 | 기본 구성의 공급자 인증 키 |

<br>

### 7-4-3 적용 확인

| 대상 | 확인 기준 |
|---|---|
| 모델 | 등록된 모델이며 이미지 입력과 해당 JSON 출력 방식 지원 |
| 공급자 인증 | 선택한 모델의 키 주입<br>검수에만 필요한 키의 누락은 기동 검사 대신 호출 시 실패할 수 있음 |
| 프롬프트 | 변경 시 `version`과 `updated` 갱신 |
| 배포 이미지 | 대상 커밋과 실행 이미지 digest 일치, AI health 정상 |
| 검수 결과 | 텍스트와 이미지 요청의 응답이 계약과 일치<br>HTTP 200 안의 승인, 반려와 검수 실패 구분 |
| 관측 | 제출본 식별자로 요청 조회, 적용 모델과 프롬프트 버전 확인 |

<br>

### 7-4-4 복구

| 상황 | 처리 |
|---|---|
| 운영 배포나 health 실패 | 워크플로가 이전 `latest` digest 복원 후 새 배포 요청<br>복구 배포의 완료와 health는 별도 확인 |
| 코드나 프롬프트 문제 | 이전 정상 이미지와 호환 설정으로 복원 |
| 모델, 키 또는 허용 호스트 문제 | 해당 설정 복원 후 재배포<br>이미지 복원만으로 외부 설정은 복원되지 않음 |
| 컨테이너 교체 중 요청 종료 | 새 컨테이너로 진행 중 검수를 이전하거나 이어받지 않음 |
