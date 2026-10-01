# 7-4 배포

인프라 구조와 공통 배포 절차는 배포 설계를 따른다. ([배포 설계](../../design/4-deployment.md))

<br>

### 7-4-1 배포 단위

간편 제작과 채팅을 AI 서버 이미지 하나로 배포한다. 프롬프트도 이미지에 포함하므로 변경 시 다시 빌드한다.

| 항목 | 구성 |
|---|---|
| 실행 | FastAPI, `uvicorn`, 포트 8000 |
| 배치 | 백엔드와 같은 ECS 태스크 <br> 태스크 내부 주소로 호출 |
| 외부 요청 | 백엔드에서 수신 <br> 인증, 이프 지불과 결과 저장도 백엔드 담당 |
| 포함 | `src/`, `prompt/`, 운영 의존성 |
| 제외 | `tests/`, `experiment/`, `scripts/`, `.env`, 개발 의존성 |
| 정책 파일 | 별도 파일 없음 <br> 작성 규칙은 프롬프트 템플릿에 포함 |
| 평가 CLI | 미구현 |

<br>

| 의존 대상 | 연결 실패 시 동작 |
|---|---|
| 백엔드 | 생성 요청 수신 불가 |
| 텍스트 모델 API | 필수 키 누락 시 시작 실패 <br> 호출 실패 시 502 |
| 이미지 모델 API | 필수 설정 오류 시 시작 실패 <br> 실행 중 생성 실패 시 컴파일 200과 이미지 `error` 출력 |
| Sentry | 오류 보고 없이 동작 |
| Langfuse | 추적 없이 동작 |

<br>

### 7-4-2 배포 경로

워크플로는 테스트, 컨테이너 상태 검사, 이미지 게시, ECS 배포 순서로 실행한다.  ([배포 워크플로](../../../../manyak-ai/.github/workflows/docker-image.yml), [배포 설계 4-7 배포 절차](../../design/4-deployment.md#4-7-배포-절차))

| 단계 | 개발 | 운영 |
|---|---|---|
| 시작 | `dev` 푸시 | `main` 푸시 |
| 빌드 | 저장소 루트의 `Dockerfile` <br> `.dockerignore` 적용 | 동일 |
| 이미지 게시 | GHCR, 커밋 SHA 태그 | ECR, 커밋 SHA 태그 |
| 배포 태그 | `dev` 갱신 | `latest` 갱신 |
| 적용 | ECS 서비스의 새 배포 강제 실행 | 동일 |
| AWS 인증 | GitHub OIDC | 동일 |

<br>

| 배포 제어 | 동작 |
|---|---|
| 단계 실패 | 후속 단계 실행 중단 |
| 이전 커밋의 늦은 빌드 완료 | 브랜치 최신 커밋이 아니면 배포 생략 |
| 환경 태그 갱신 | 빌드 시점이 아닌 배포 작업에서 갱신 |
| 백엔드와 동시 배포 | 저장소별 워크플로에서 같은 ECS 태스크 배포 가능 |

<br>

**수정할 위치**

| 대상 | 원본 |
|---|---|
| 이미지 구성 | [Dockerfile](../../../../manyak-ai/Dockerfile), [.dockerignore](../../../../manyak-ai/.dockerignore) |
| 빌드와 배포 자동화 | [docker-image.yml](../../../../manyak-ai/.github/workflows/docker-image.yml) |
| 운영 태스크와 환경 변수 | [운영 ECS 설정](../../../../manyak-terraform/terraform/envs/prod/ecs.tf) |
| 운영 모델 Parameter | [ai-model-config.tf](../../../../manyak-terraform/terraform/envs/prod/ai-model-config.tf) |
| 개발 인프라 | [개발 환경 설정](../../../../manyak-terraform/terraform/envs/dev/main.tf) |
| 로컬 통합 실행 | `manyak-infra`의 Compose |

<br>

### 7-4-3 배포 조건

AI 성능 평가 방법은 미정이다. ([6-4 AI 평가 방법](6-4-AI-EVALUATION-METHOD.md))

린트와 타입 검사는 자동화하지 않았다. 실제 모델 통합 테스트도 자동 차단 조건에 포함되지 않으므로 실행 결과나 미실행 여부를 PR에 남긴다. ([7-2-7 통합 테스트](7-2-TEST-CASES.md#7-2-7-통합-테스트))

| 확인 항목 | 기준 | 확인 위치 | 자동 여부 |
|---|---|---|---|
| 입출력 계약 | 계약 문서 선반영 <br> 비호환 변경은 백엔드 대응 후 배포 | PR | 수동 |
| 테스트 | 전체 통과 <br> `src/` 분기 커버리지 90% 이상 | 테스트 작업 | 자동 |
| 컨테이너 상태 | `/api/v1/health` 200과 `status: ok` | 이미지 상태 검사 작업 | 자동 |
| Langfuse 초기화 | 더미 키와 운영 조건에서 활성화 로그 출력 | 이미지 상태 검사 작업 | 자동 |
| 통합 테스트 | 프롬프트, 모델 또는 호출 코드 변경 시 실행 | 로컬 실행 결과, PR | 수동 |
| 템플릿 버전 | 변경한 템플릿의 `version`, `updated` 갱신 | PR | 수동 |
| 병합 | PR 승인 | GitHub | 수동 |
| AI 성능 평가 | 평가 방법과 합격 기준 미정 | 평가 방법 문서 | 미정 |

<br>

### 7-4-4 환경 변수와 비밀 정보

- 설정 우선순위는 환경 변수, `.env`, 코드 기본값 순서다. 변수 이름은 대소문자를 구분하지 않으며 미정의 변수는 무시한다.
- 운영과 개발의 비밀값은 Secrets Manager에서 주입하고 로컬은 git에서 제외된 `.env`를 사용한다.
- 설정은 시작 시 읽으므로 변경 후 새 태스크를 실행해야 한다.
- 비밀값은 AI 담당자가 등록하고 배포 담당자가 Terraform의 주입 설정을 반영한다.
- 아래 기본값은 코드 기준이며 운영 Parameter의 실제 값은 미확인이다. 채팅 전용 변수는 제외한다.

변수 정의는 설정 모듈을 따른다. ([config.py](../../../../manyak-ai/src/core/config.py))

<br>

**1. 비밀 정보와 연결 주소**

| 이름 | 의미 | 필수 | 기본값 | 운영과 개발의 출처 |
|---|---|---|---|---|
| `DEEPSEEK_API_KEY` | DeepSeek 키 | 필수 | 없음 | Secrets Manager |
| `OPENAI_API_KEY` | OpenAI 키 <br> 텍스트와 이미지 공용 | 선택한 모델이 OpenAI이면 필수 | 빈 값 | Secrets Manager |
| `GEMINI_API_KEY` | Google 키 | 선택한 모델이 Gemini이면 필수 | 빈 값 | Secrets Manager |
| `ANTHROPIC_API_KEY` | Anthropic 키 | 선택한 모델이 Anthropic이면 필수 | 빈 값 | 주입하지 않음 |
| `SENTRY_DSN` | Sentry 주소 | 선택 | 빈 값 <br> 미설정 시 보고 안 함 | Secrets Manager |
| `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` | Langfuse 키 | 선택 | 빈 값 <br> 미설정 시 비활성화 | 운영 Secrets Manager |
| `LANGFUSE_HOST` | Langfuse 주소 | 선택 | 일본 리전이 아닌 주소 | 운영 Secrets Manager <br> 일본 리전 주소 필요 |

<br>

**2. 설정값**

| 이름 | 의미 | 타입 | 기본값 | 운영의 출처 | 개발의 출처 |
|---|---|---|---|---|---|
| `STORYLINES_MODEL` | 스토리라인 모델 | 문자열 | `deepseek-flash` | SSM Parameter Store | 태스크 정의의 환경 변수 |
| `STORY_COMPILE_MODEL` | 컴파일 모델 | 문자열 | `gpt-5.6-terra` | SSM Parameter Store | 태스크 정의의 환경 변수 |
| `IMAGE_MODEL` | 이미지 모델 | 문자열 | `gpt-image-2.5-flare` | 주입 안 함 <br> 코드 기본값 | 같음 |
| `IMAGE_QUALITY` | 이미지 화질 | `low`, `medium`, `high` | `low` | 주입하지 않음 | 같음 |
| `IMAGE_SIZE` | 인물 이미지 크기 | `가로x세로` | `1024x768` | 주입하지 않음 | 같음 |
| `IMAGE_TIMEOUT` | 이미지 한 장의 제한 시간(초) | 실수 | `60.0` | 주입하지 않음 | 같음 |
| `DEEPSEEK_API_URL`, `OPENAI_API_URL`, `ANTHROPIC_API_URL`, `GEMINI_API_URL` | 공급자 주소 | 문자열 | DeepSeek 공식 주소 <br> 나머지는 SDK 기본 | 주입하지 않음 | 같음 |
| `SENTRY_ENVIRONMENT` | 환경 이름 <br> Langfuse 활성 조건에도 사용 | 문자열 | `local` | 태스크 정의 | 태스크 정의 |
| `SENTRY_TRACES_SAMPLE_RATE` | Sentry 성능 추적의 표본 비율 | 실수 | `0.0` | 주입하지 않음 | 같음 |

<br>

### 7-4-5 설정 변경

자동 모델 전환과 누적 비용에 따른 호출 중단은 구현하지 않았다. 설정 변경 시에도 배포 조건을 적용한다. ([7-4-3 배포 조건](#7-4-3-배포-조건))

| 변경 대상 | 변경 위치와 적용 | 조건 |
|---|---|---|
| 텍스트 모델 | 운영: SSM Parameter 변경 후 새 배포 <br> 개발: Terraform 환경 변수 변경 후 적용 | 등록된 모델과 공급자 키 필요 |
| 이미지 모델, 화질, 크기, 시간, 공급자 주소 | Terraform에 환경 변수 추가 후 적용 | 모델 등록부와 시작 검사 통과 |
| 프롬프트, 추론 설정, 출력 토큰, 온도, 보완 횟수, 텍스트 제한 시간 | 코드 수정 후 이미지 재빌드와 배포 | 서비스 상수와 모델 등록부에 반영 |
| 모델 이름 | 모델 등록부, 모델 설정, Langfuse 단가 함께 변경 | 이름 불일치 시 시작 실패 또는 비용 집계 누락 |
| 새 공급자 | 해당 공급자 키 주입 | 키 누락 시 시작 실패 |
| Langfuse 단가 구간 | 코드 metadata와 Langfuse 등록 함께 변경 | 구간 불일치 시 비용 오집계 |

<br>

| 적용 규칙 | 동작 |
|---|---|
| 설정 검증 | 모델 등록, 키와 호출 설정 검사 <br> 실패 시 새 태스크 시작 중단 |
| 운영 Parameter | Terraform에서 기존 값 덮어쓰기 안 함 <br> Terraform 기본값 변경만으로 운영 값 변경 안 됨 |
| 컴파일 공급자 변경 | 공급자별 프롬프트 선택 <br> 출력 `meta.prompt_versions`로 적용 버전 확인 |
| 긴급 설정 변경 | 우선 변경 후 통합 테스트 실행 <br> 실행 결과 기록 |

<br>

### 7-4-6 적용과 복구

배포와 복구 시 이미지 digest, 설정 조합과 확인 결과를 배포 기록에 남긴다.

**1. 적용 순서**

| 순서 | 작업 | 확인 항목 |
|---|---|---|
| 1 | 설정 준비 | 비밀값 등록, 태스크 주입 설정, 모델 호환성 |
| 2 | 백엔드 배포 순서 결정 | 필드 추가는 AI 선배포 가능 <br> 필드 삭제, 이름과 타입 변경은 백엔드 대응 후 배포 |
| 3 | PR 병합과 배포 | 대상 브랜치, 워크플로 실행 결과 |
| 4 | 적용 버전 확인 | 새 배포 식별자, 실행 태스크의 이미지 digest와 상태 |
| 5 | 실제 생성 확인 | 스토리라인과 컴파일 각 1건 |
| 6 | 배포 기록 | 시각, 커밋 SHA, 이미지 digest, 설정 변경 범위와 확인 결과 |

<br>

**2. 진행 중인 요청**

| 상황 | 처리 |
|---|---|
| 태스크 교체 | 새 태스크 시작 후 이전 태스크 종료 |
| 이전 태스크에서 생성 중 종료 | 요청 실패 <br> 새 태스크로 작업 이전 안 함 |
| 실패한 컴파일 | 백엔드 환불과 사용자 재요청 |
| 개발 태스크 교체 | 단일 태스크로 중단 허용 <br> 같은 태스크의 DB와 Redis도 재시작 |

<br>

**3. 복구**

운영 워크플로는 태그 변경 전 `latest`의 digest를 보관하고 배포 실패 시 복원한다. ECS 자동 복구만으로 이전 이미지 복원을 보장하지 않는다. ([배포 설계 4-9 검수와 롤백](../../design/4-deployment.md#4-9-검수-관측-롤백))

| 문제 | 복구 대상 | 방법 |
|---|---|---|
| 새 코드 결함, 프롬프트 변경 후 결과 악화 | 이미지 | 이전 정상 digest로 환경 태그 복원 <br> 새 배포 후 생성 확인 |
| 모델 설정 문제 | 설정과 이미지 | 이전 모델 설정과 호환되는 이미지로 복원 |
| 모델 이름 변경 후 실패 | 설정과 이미지 | 이전 이름을 지원하는 등록부까지 복원 |
| 새 태스크 시작 실패 | 설정 | 이전 태스크 유지 <br> 시작 검사에서 실패한 설정 수정 후 재배포 |


<br>

### 7-4-7 배포 후 확인

- 백엔드 상태와 별개로 AI 컨테이너 상태를 확인한다.
- 확인 기간과 배포 전후 차이의 허용 기준은 미정이다. 운영 목표값은 운영 요구사항을 따른다.
- 개발 환경은 Langfuse 없이 출력과 Sentry로 확인한다. 운영 DB, 캐시와 배포 방식은 개발 검증 범위에 포함되지 않는다.

운영 목표와 지표의 계산은 해당 문서를 따른다. ([2-2 운영 요구사항](2-2-OPERATION-REQUIREMENTS.md), [7-3-4 지표](7-3-OBSERVABILITY.md#7-3-4-지표))

| 시점 | 확인 항목 | 자료 | 기준 |
|---|---|---|---|
| 배포 직후 | AI 컨테이너 상태 | 워크플로와 상태 확인 주소 | 정상 상태 |
| 배포 직후 | 스토리라인과 컴파일 각 1건 | 대상 환경 앱 또는 API | 200, 인물 이미지와 썸네일 출력 |
| 배포 직후 | 모델과 프롬프트 버전 | 출력 `meta`, 운영 Langfuse | 의도한 모델과 템플릿 버전 일치 |
| 다음 날 | 새 오류와 오류 증가 | Sentry 일일 요약 | 배포 전과 비교 |
| 확인 기간 | 재호출, 인물 누락, 이미지 실패, 시간과 비용 | 운영 지표 | 배포 전후 변화와 운영 목표 확인 |

<br>

### 7-4-8 배포 실패 진단

실패한 실행의 커밋 SHA, 배포 시각과 배포 ID로 대상 태스크를 찾는다. AWS 리전은 `ap-northeast-2`, 클러스터와 서비스 이름은 개발 `manyak-dev`, 운영 `manyak-prod`이다. ([배포 워크플로](../../../../manyak-ai/.github/workflows/docker-image.yml))

| 실패 상황 | 확인할 로그와 설정 | 조회 경로 | 원인별 조치 |
|---|---|---|---|
| 빌드, 테스트 또는 이미지 게시 실패 | 실패 단계의 오류와 스택 | [GitHub Actions](https://github.com/KIM-N-KANG/manyak-ai/actions/workflows/docker-image.yml)에서 해당 커밋 실행 → 실패한 작업과 단계 | 테스트 실패는 해당 코드 수정 <br> 빌드, 인증, 게시 실패는 Dockerfile 또는 워크플로 설정 수정 |
| ECS 배포 실패 | 서비스 이벤트, 배포 상태 <br> 태스크의 `stoppedReason`, 컨테이너의 `reason`, `exitCode` | [ECS](https://ap-northeast-2.console.aws.amazon.com/ecs/v2/home?region=ap-northeast-2)에서 대상 클러스터 → 서비스 이벤트와 종료된 태스크 <br> 배포 시각과 `startedBy`의 배포 ID 대조 | 이미지 가져오기, 비밀값 주입, 권한 또는 네트워크 오류는 해당 설정 수정 <br> 컨테이너 종료는 아래 시작 로그 확인 |
| AI 서버 시작 실패 | `ai` 컨테이너의 시작 예외와 상태 검사 오류 | [CloudWatch 로그](https://ap-northeast-2.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-2#logsV2:log-groups)에서 `/ecs/manyak-dev` 또는 `/ecs/manyak-prod` → `firelens/` 스트림 <br> 배포 시각, `ecs_task_arn`, `container_name`으로 대상 로그 조회 | 설정 오류는 설정 수정 후 새 배포 <br> 코드나 템플릿 결함은 이전 정상 이미지로 복구 |
| 모델 설정 또는 키 주입 오류 | 태스크 정의의 `ai` 환경 변수와 `secrets` 참조 <br> 시작 로그의 모델 등록, 필수 키 검사 오류 | ECS의 실패 태스크 → 해당 태스크 정의 <br> 운영 모델은 연결된 SSM Parameter, 키는 Secrets Manager의 참조와 실행 역할 권한 확인 | 모델 이름과 공급자 키의 주입 설정 대조 <br> 키 원문 출력 없이 누락 여부 확인 <br> 수정과 복구는 [7-4-5 설정 변경](#7-4-5-설정-변경), [7-4-6 적용과 복구](#7-4-6-적용과-복구) 적용 |
| 배포 후 생성 실패 | Sentry 오류와 스택 <br> 운영 Langfuse의 모델 호출 기록 | [7-3-1 요청 조회](7-3-OBSERVABILITY.md#7-3-1-요청-조회)의 식별자와 [7-3-3 오류 확인](7-3-OBSERVABILITY.md#7-3-3-오류-확인)의 `feature`, `error_code`로 조회 | 원인별 조치는 7-3-3 적용 <br> 실패 출력과 복구 범위는 [7-1 오류 처리](7-1-ERROR-HANDLING.md) 적용 |
