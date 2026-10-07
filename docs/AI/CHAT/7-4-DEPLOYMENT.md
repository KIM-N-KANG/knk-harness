# 7-4 배포

본 문서는 채팅 AI 서버의 배포와 설정 변경, 장애 시 복구 절차를 정한다.

배포 단위와 경로, 환경 변수, 배포 전후 검사와 실패 진단 방법을 다룬다.

<br>

### 7-4-1 배포 단위

채팅, 간편 제작과 검수를 AI 서버 컨테이너 이미지 하나로 배포한다. 채팅만의 독립 실행 파일이나 워커는 없다. 프롬프트도 이미지에 포함되므로 변경 시 다시 빌드한다.

| 항목 | 구성 |
|---|---|
| 실행 | Python 3.11 기반, FastAPI와 `uvicorn`, 포트 8000<br>비관리자 `appuser`로 실행 |
| 포함 | `src/`, `prompt/`, `pyproject.toml`로 설치한 운영 의존성 |
| 제외 | 최종 이미지에 테스트, 실험 자료, 스크립트와 개발 의존성 복사 안 함<br>`.env`는 빌드 컨텍스트에서도 제외 |
| 프롬프트 | 본문, 판정, 선택지와 이미지 템플릿을 같은 이미지에 포함 |
| 상태 | 채팅 상태와 대화 기록은 백엔드가 관리<br>AI 서버는 요청 간 결과 저장·재전송 안 함 |
| 외부 연결 | 백엔드 요청, 텍스트·이미지 모델 API, 기본 이미지 CDN, 서명 URL의 이미지 저장소 |

<br>

| 의존 대상 | 연결·설정 실패 시 동작 |
|---|---|
| 텍스트 공급자 | 필요한 모델·키·호출 설정 오류는 기동 검사 실패<br>실행 중 본문 실패는 SSE `error`, 판정·선택지는 정해진 복구 적용 |
| 이미지 공급자 | OpenAI 키와 이미지 설정 오류는 기동 실패<br>실행 중 실패는 기본 이미지 유지 |
| CDN와 이미지 업로드 | 주소·호스트 검증 또는 전송 실패 시 기본 이미지 유지 |
| 관측 도구 | 관측 초기화 실패로 생성 서비스를 중단하지 않음 |

<br>

### 7-4-2 배포 경로

테스트와 서버 기동을 확인한 뒤 이미지를 게시하고 배포한다. 이미지는 AMD·Intel용과 ARM용으로 만들며, 기동 검사는 한 종류에서만 한다. ([docker-image.yml](../../../../manyak-ai/.github/workflows/docker-image.yml))

`dev`로 PR을 올리면 테스트와 빌드만 한다.

| 단계 | 개발 | 운영 |
|---|---|---|
| 자동 시작 | `dev` push | `main` push |
| 이미지 게시 | GHCR `manyak-ai`, 커밋 SHA 앞 7자리 태그 | ECR `manyak-ai`, 커밋 SHA 앞 7자리 태그 |
| 배포 대상 선택 | 실행 커밋이 최신 `dev`가 아니면 배포 생략 | 배포 작업 시점의 `main` HEAD 선택<br>그 이미지가 아직 없으면 배포 생략 |
| 환경 태그 | 배포 작업에서 `dev` 갱신 | 배포 작업에서 `latest` 갱신 |
| ECS 대상 | 클러스터·서비스 `manyak-dev` | 클러스터 `manyak-prod`, 서비스 `manyak-prod-ai` |
| AWS 인증과 리전 | GitHub OIDC, `ap-northeast-2` | 동일 |
| 적용 | `force-new-deployment` | 기존 서비스 안정 대기 후 `force-new-deployment` |
| 상태 검사 | 해당 배포 완료, AI 컨테이너 상태와 백엔드 health | 해당 배포 ID로 시작한 모든 태스크의 AI `HEALTHY`와 desired 수 일치 |

<br>

**환경별 서비스 구성**

| 환경 | 구성 | 배포 영향 |
|---|---|---|
| 운영 | AI와 백엔드를 독립 서비스로 실행<br>AI 태스크: `ai`, `log_router`, AI는 `essential=true`<br>백엔드의 AI 연결 주소: `http://ai.manyak-prod.local:8000` (Cloud Map) | AI 태스크만 교체, 백엔드 재시작 없음<br>AI 서비스의 최소 정상 비율 100%, 최대 200% |
| 개발 | 백엔드, AI와 데이터 컨테이너를 같은 태스크에 배치<br>최소 정상 비율 0%, 최대 100% | 교체 중 서비스 중단과 데이터 컨테이너 재시작 가능 |

<br>

**수정·확인할 위치**

| 대상 | 원본 |
|---|---|
| 이미지 구성 | [Dockerfile](../../../../manyak-ai/Dockerfile), [.dockerignore](../../../../manyak-ai/.dockerignore) |
| 빌드·게시·배포·자동 복구 | [docker-image.yml](../../../../manyak-ai/.github/workflows/docker-image.yml) |
| 설정 기본값 | [config.py](../../../../manyak-ai/src/core/config.py) |
| 운영 모델 Parameter 선언 | [ai-model-config.tf](../../../../manyak-terraform/terraform/envs/prod/ai-model-config.tf) |
| 운영 AI 서비스와 태스크 정의 | [ai.tf](https://github.com/KIM-N-KANG/manyak-terraform/blob/8c0ddaf1e7c33e810d313d191b6016e97a045c85/terraform/envs/prod/ai.tf) |
| 운영 백엔드와 AI 연결 | [ecs.tf](https://github.com/KIM-N-KANG/manyak-terraform/blob/8c0ddaf1e7c33e810d313d191b6016e97a045c85/terraform/envs/prod/ecs.tf) |
| 개발 인프라 정의 | [dev/main.tf](../../../../manyak-terraform/terraform/envs/dev/main.tf), [compute-ecs](../../../../manyak-terraform/terraform/modules/compute-ecs/main.tf) |
| 로컬 통합 실행 | [docker-compose.yml](../../../../manyak-infra/docker-compose.yml)<br>`CHAT_MODEL`과 `STORYLINES_MODEL`의 기본값 `deepseek-v4-flash`를 현재 등록된 모델명으로 변경 |

<br>

### 7-4-3 배포 조건

| 확인 항목 | 기준 | 자동 여부와 한계 |
|---|---|---|
| 계약 호환성 | 요청 필드, SSE·JSON 출력과 백엔드 소비 방식 일치 | 수동 검토<br>필드의 선택 여부와 기본값까지 확인 |
| 코드 테스트 | 전체 테스트 통과, `src/` 분기 커버리지 90% 이상 | CI 자동 |
| 이미지 기동 | `/api/v1/health` 200, `status: ok` | CI 자동<br>공급자에 실제 생성 요청하지 않음 |
| 관측 초기화 | 더미 키와 JP·prod 조건에서 health와 Langfuse 활성 로그 확인 | CI 자동<br>실제 운영 기록 전송 성공을 검사한 것은 아님 |
| 프롬프트 버전 | 변경한 템플릿의 `version`, `updated` 반영 | 수동 검토 |
| 채팅 통합 검증 | 본문, 판정, 이미지와 선택지의 변경된 경로 검증 | 기존 자동·라이브 범위 구분<br>실제 모델 테스트는 CI 자동 차단 조건 아님 |
| 린트·타입 검사 | 해당 워크플로에 단계 없음 | 미자동화 |

<br>

### 7-4-4 환경 변수와 비밀 정보

환경 변수, `.env`, 코드 기본값 순서로 설정을 읽는다. 변수명은 대소문자를 구분하지 않고 미정의 값은 무시한다. 설정은 프로세스 시작 시 구성하므로 변경 뒤 새 프로세스·태스크가 필요하다.

<br>

**1. 공급자와 비밀 정보**

같은 서버의 다른 기능에 설정 오류가 있으면 채팅도 기동하지 못할 수 있다.


| 이름 | 의미·타입 | 필수 조건과 코드 기본값 | 로컬 인프라의 주입 |
|---|---|---|---|
| `DEEPSEEK_API_KEY` | 키, 문자열 | 설정 필드에 기본값 없음<br>DeepSeek 선택 시 유효한 키 필요 | 개발·운영 Secrets Manager 참조 |
| `OPENAI_API_KEY` | 텍스트·이미지 공용 키, 문자열 | 기본 빈 값<br>공통 이미지 기동 검사에서 필수 | 개발·운영 Secrets Manager 참조 |
| `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` | 다른 태스크·모델의 공급자 키, 문자열 | 기본 빈 값, 선택 모델에 따라 필요 | Gemini 참조 있음, Anthropic 참조 없음 |
| `DEEPSEEK_API_URL` | 문자열 | 기본 `https://api.deepseek.com` | AI 태스크에 별도 주입 없음 |
| `OPENAI_API_URL`, `ANTHROPIC_API_URL`, `GEMINI_API_URL` | 선택 문자열 | 기본 `None`, SDK 기본 주소 사용 | AI 태스크에 별도 주입 없음 |

<br>

**2. 모델과 이미지 설정**

| 이름 | 의미·타입 | 코드 기본값 | 로컬 인프라의 출처·조건 |
|---|---|---|---|
| `CHAT_MODEL` | 본문·판정 모델, 문자열<br>선택지 모델은 별도 설정 | `deepseek-flash` | 운영 SSM Parameter, 개발 태스크 환경 변수<br>채팅 실행 명세의 프로덕션 모델은 `gpt-6-luna` |
| `CHAT_CHOICE_MODEL` | 선택지 모델, 문자열 | `deepseek-flash` | 개발·운영 Terraform에 별도 주입 없음 |
| `IMAGE_MODEL` | 공통 이미지 모델, 문자열 | `gpt-image-2.5-flare` | 별도 주입 없음, 이미지 등록부에 있어야 함 |
| `IMAGE_QUALITY` | 문자열 열거값 | `low` | `low`, `medium`, `high` |
| `IMAGE_SIZE` | 크기 문자열 | `1024x768` | 양의 정수 `가로x세로` 형식 |
| `IMAGE_TIMEOUT` | 이미지 호출 제한 시간, 초, 실수 | `60.0` | 0보다 큰 유한값<br>전체 이미지 작업은 최대 30초 |
| `IMAGE_PARENT_ALLOWED_HOSTS` | 호스트 목록, JSON 배열 | `cdn.manyak.app`, `dev-cdn.manyak.app` | 별도 주입 없음<br>기본 이미지 다운로드 대상 |
| `IMAGE_UPLOAD_ALLOWED_HOSTS` | 호스트 목록, JSON 배열 | `[]` | 개발·운영 Terraform에서 이미지 버킷의 리전별 S3 호스트로 주입<br>비어 있으면 업로드 거부 |

<br>

**3. 관측 설정**

운영 추적 환경 변수는 `local.tracing_environment`에서 구성하고 AI 태스크에 전달한다. ([trace-collector.tf](https://github.com/KIM-N-KANG/manyak-terraform/blob/8c0ddaf1e7c33e810d313d191b6016e97a045c85/terraform/envs/prod/trace-collector.tf), [ai.tf](https://github.com/KIM-N-KANG/manyak-terraform/blob/8c0ddaf1e7c33e810d313d191b6016e97a045c85/terraform/envs/prod/ai.tf))

| 이름 | 타입·코드 기본값 | 인프라의 출처와 조건 |
|---|---|---|
| `APP_VERSION` | 문자열, `0.4.3` | 별도 주입 없음<br>커밋 SHA 자동 주입 아님 |
| `SENTRY_DSN` | 문자열, 빈 값 | 개발·운영 Secrets Manager의 AI DSN 참조 |
| `SENTRY_ENVIRONMENT` | 문자열, `local` | 개발·운영 태스크의 환경명 |
| `SENTRY_TRACES_SAMPLE_RATE` | 실수, `0.0` | 별도 주입 없음 |
| `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` | 문자열, 빈 값 | 운영 Secrets Manager 참조, 개발 미주입 |
| `LANGFUSE_HOST` | 문자열, `https://cloud.langfuse.com` | 운영 Secrets Manager 참조<br>활성화에는 JP 주소 필요 |
| `LANGFUSE_SAMPLE_RATE` | 문자열, `1.0` | 별도 주입 없음<br>초기화 시 0~1 수치로 검사 |
| `MANYAK_TRACING_ENABLED` | 불리언, `false` | 운영 Terraform의 `tracing_enabled=true`일 때 AI 태스크에 `true` 주입<br>비활성 시 주입 없음 |
| `MANYAK_OTLP_TRACES_ENDPOINT` | 문자열, 빈 값 | 같은 조건에서 Data Prepper의 내부 수집 주소 주입<br>포트 `21890`, 경로 `/v1/traces`<br>비활성 시 주입 없음 |

<br>

### 7-4-5 설정 변경

운영 모델은 Parameter 값을 직접 변경해야 하며, 코드 기본값 수정이나 이미지 재배포만으로는 바뀌지 않는다.

| 변경 대상 | 변경 위치와 적용 | 확인 조건 |
|---|---|---|
| 본문·판정 모델 | 운영은 실제 태스크의 `CHAT_MODEL` 주입 원본 확인 후 변경·재배포 | 모델 등록, 공급자 키, 스트리밍과 JSON 판정 모두 지원 |
| 선택지 모델 | `CHAT_CHOICE_MODEL` 주입 설정 추가·변경 후 재배포 | 본문 모델과 별도로 검증, 선택지 JSON 출력과 보완 경로 확인 |
| 이미지 모델·화질·크기·시간 | 환경 변수 변경 후 재배포 | 공통 이미지 기동 검사, 편집 API와 기본 이미지 대체 검증<br>간편 제작에도 영향 |
| 다운로드·업로드 허용 호스트 | 호스트 JSON 배열 변경 후 재배포 | 백엔드가 전달하는 실제 URL의 호스트와 일치<br>허용되지 않은 주소 차단 유지 |
| 프롬프트·추론 설정·출력 토큰·보완 횟수·본문 제한 시간 | 템플릿·서비스 상수·모델 등록부 변경 후 이미지 재빌드 | 관련 계약, 버전과 테스트 함께 반영 |
| 관측·표본 비율 | 환경 설정 변경 후 재배포 | 원문 수집 조건, 실제 계측 활성 여부와 집계 표본 확인 |
| 모델 비용 | Langfuse 모델 단가와 호출 metadata 대조 | 새 모델·단가 구간의 비용 누락 또는 중복 방지 |

<br>

### 7-4-6 적용과 복구

**1. 적용 순서**

API 변경 시 기존 백엔드와의 호환성을 확인하고 배포 순서를 맞춘다. ([5 계약](5-CONTRACT.md))

| 순서 | 작업 | 확인 항목 |
|---|---|---|
| 1 | 배포 대상 확인 | 환경, 대상 커밋, 이미지 digest, 실제 서비스와 태스크 정의<br>운영 AI 대상이 `manyak-prod-ai`인지 확인 |
| 2 | 설정·호환성 확인 | 필요한 키의 주입 참조, 모델 등록, 이미지 허용 호스트<br>백엔드가 새 요청·응답을 소비할 수 있는지 확인 |
| 3 | 테스트와 이미지 검사 | CI 결과, 변경 경로의 통합 검증과 미실행 범위 |
| 4 | 배포 실행 | 해당 환경 워크플로와 배포 ID 확인<br>운영은 실행 커밋과 실제 선택된 main HEAD를 구분 |
| 5 | 적용 결과 확인 | 해당 배포의 실행 태스크, digest, AI health와 생성 결과 |
| 6 | 기록 | 배포 시각, 대상 SHA, digest, 설정 변경 범위, 검수·복구 결과<br>비밀값 제외 |

<br>

**2. 진행 중인 요청**

| 상황 | 처리와 한계 |
|---|---|
| 교체 중 기존 요청 | 새 태스크로 진행 중 작업을 이전하거나 이어받지 않음 |
| SSE 연결 종료 | 모델 스트림 닫기, 판정·이미지 작업 취소와 회수 |
| 생성·업로드 후 연결 종료 | 공급자 비용과 저장된 이미지가 자동으로 되돌아가지는 않음 |
| 컨테이너 강제 종료 | 애플리케이션 정리·관측 flush의 완료를 보장하지 못함 |

<br>

**3. 복구**

자동 복구가 실행돼도 ECS 서비스가 정상으로 돌아오지 않았을 수 있으므로 실제 서버 상태를 확인한다.

| 상황 | 복구 방식 | 한계·확인 사항 |
|---|---|---|
| 운영 태그 승격 후 배포·health 실패 또는 취소 | 워크플로가 승격 전 `latest` digest 복원 후 새 배포 요청 | 복구 배포의 안정화 완료까지 기다리지 않음<br>실제 완료·health 별도 확인 |
| 승격 전 `latest` 없음 | 자동 복구할 이전 digest 없음 | 경고만 남음, 정상 이미지 선택 필요 |
| 복구용 새 배포 요청 실패 | 태그는 복원되었어도 실행 태스크는 그대로일 수 있음 | 서비스 배포 상태 확인 후 후속 조치 |
| 개발 배포 실패 | 현재 개발 작업에 운영과 같은 태그 복원 단계 없음 | `dev` 태그와 실행 태스크를 함께 확인 |
| 배포는 정상이나 품질 악화 | 검증한 이전 이미지와 설정 조합으로 복원 후 재검수 | health 기반 자동 복구는 품질 악화를 탐지하지 않음 |
| 모델·키·허용 호스트 설정 오류 | 잘못된 주입값을 이전 호환 설정으로 복구 | 이미지 태그 복원만으로 SSM·Secrets Manager 값이 복원되지 않음 |

<br>

### 7-4-7 배포 후 확인

| 확인 항목 | 자료 | 기준 |
|---|---|---|
| 배포와 기동 | 해당 배포 ID, 태스크 digest, AI 컨테이너 상태 | 의도한 이미지로 기동, health 정상 |
| 본문·판정 | 채팅 SSE와 완료 필드 | 본문 전달, `completed` 수신, 사건·엔딩 필드 형식 일치<br>HTTP 200만으로 성공 판정 안 함 |
| 선택지 | 별도 선택지 API | 3개와 메타 반환<br>생성 성공과 대체 문구 사용 구분 |
| 실시간 이미지 | 이미지 슬롯이 있는 턴과 관측 | 생성·업로드 성공 시 새 URL 연결<br>실패 시 기본 이미지와 본문 유지 |
| 모델·프롬프트 | 응답 메타와 Langfuse | 의도한 모델·버전 일치<br>본문과 선택지 설정을 각각 확인 |
| 시간·오류·비용 | 배포 전후 같은 조건의 지표 | 본문 전달, 판정 실패, 이미지 대체와 선택지 보완을 구분해 비교 |
| 공유 기능 | 공통 코드·설정 변경 시 간편 제작·검수의 관련 테스트 | 채팅 변경으로 공유 서버의 기동과 다른 기능이 깨지지 않음 |

<br>

### 7-4-8 배포 실패 진단

워크플로 실행 ID, 실제 배포 대상 SHA, ECS 배포 ID와 이미지 digest로 실패 대상을 좁힌다. 운영에서는 오래된 실행이 최신 main HEAD를 배포할 수 있으므로 실행 화면의 커밋만으로 이미지를 판단하지 않는다.

| 실패 상황 | 확인할 자료와 위치 | 원인별 조치 |
|---|---|---|
| 테스트·빌드·게시 실패 | GitHub Actions의 실패 단계<br>Dockerfile, 의존성 선언과 레지스트리 인증 | 코드·빌드·인증 문제를 구분하고 해당 원본 수정 |
| 배포가 생략됨 | 최신 SHA 게이트와 main HEAD 이미지 조회 결과 | 의도된 생략인지, 이미지 게시가 아직 끝나지 않았는지 구분<br>미게시와 조회 인증·네트워크 실패를 혼동하지 않음 |
| 운영 서비스 조회와 배포 실패 | ECS `manyak-prod`의 `manyak-prod-ai` 존재와 실제 정의<br>`ai.tf`, 워크플로 IAM 권한과 서비스 이벤트 | 서비스 이름, 태스크 정의와 배포 권한 대조<br>대상이나 권한 오류 수정 후 재배포 |
| 태스크 시작 실패 | `stoppedReason`, 컨테이너 `reason`·`exitCode`, 시작 로그 | 이미지 pull, 키·Parameter 주입 권한, 모델 설정과 템플릿 로드 실패 구분 |
| health 실패 | 해당 배포의 `ai` 상태와 시작 로그 | 백엔드 health만으로 AI 정상 판단 안 함<br>운영 워크플로가 안내하는 로그 그룹은 `/ecs/manyak-prod-ai`; 실제 로그 설정과 대조 |
| health 정상, 본문 생성 실패 | `request_id`의 Sentry·Langfuse, 실제 모델과 공급자 응답 | 키의 형식 검사 통과와 공급자 인증 성공 구분 |
| 이미지만 기본 이미지로 유지 | `child_image`, 다운로드·업로드 기록 | 슬롯, 기본 이미지 대상, 허용 호스트, 업로드 주소와 마감 확인 |
| 관측 기록 없음 | 관측 환경값·키 주입 참조·초기화 로그·표본 비율 | 생성 실패와 관측 비활성·전송 실패 구분 |
| 복구 뒤에도 실패 | 복원 태그 digest, 실행 태스크와 설정값의 버전 | 태그만 복원되었는지, 복구 배포 완료 여부와 설정 호환성 확인 |
