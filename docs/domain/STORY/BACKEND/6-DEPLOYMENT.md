# 6. 배포

이 문서는 STORY 도메인이 포함된 서버의 배포 단위와 의존 대상, 배포 경로, 이 도메인이 읽는 환경 변수와 시크릿, 설정 변경, 적용과 복구 절차를 정한다.

서버 전체 배포 절차 중 STORY 도메인과 관련된 항목만 다룬다.

대기 한도는 오류 처리에, 관측 스택과 조회 도구는 관측에 있다. ([5-3-5 재시도와 시간 한도](5-3-ERROR-HANDLING.md#5-3-5-재시도와-시간-한도), [5-4-1 관측 스택](5-4-OBSERVABILITY.md#5-4-1-관측-스택))

<br>

### 6-1 배포 단위와 의존성

배포 단위는 서버 컨테이너 하나다. STORY만 따로 배포하지 않는다. 다음은 이 도메인이 기동과 처리에 쓰는 의존 대상이다.

| 의존 대상 | 내용 | STORY 도메인이 쓰는 것 |
|---|---|---|
| PostgreSQL | 기동 시 마이그레이션 적용 | 스토리, 제작 진행, 생성 요청, 초안, 카탈로그 테이블 |
| AI 서버 | 운영은 독립 ECS 서비스, 개발은 같은 태스크의 컨테이너 | 스토리라인, 컴파일<br>스텁이면 불필요 |
| S3 assets 버킷과 CloudFront | Terraform 관리 | 생성 및 업로드 이미지 경로의 쓰기와 HEAD<br>버킷 CORS(PUT, HEAD) |
| OpenSearch | 로그 도메인 재사용, 인덱스 `stories-{env}` | 검색과 색인 |
| Redis | 게스트 체험 카운터 | PAYMENT 도메인의 서비스로 접근 |
| Data Prepper | 트레이스를 받아 OpenSearch에 적재 | 트레이스 전송 |

<br>

| 의존 대상 | 연결과 설정 실패 시 동작 |
|---|---|
| AI 서버 | 주소에 `http` 또는 `https` 스킴이나 호스트가 없으면 기동 실패<br>호출 실패와 대기 한도 초과는 AI 실패로 응답 |
| PostgreSQL | 연결 불가는 기동 실패 |
| S3 assets 버킷 | 버킷과 이미지 제공 기본 URL 중 하나라도 비면 생성 이미지 업로드 생략<br>인물 이미지와 표지 URL은 `null`로 저장<br>업로드 presign은 사용 불가로 응답<br>업로드 경로의 IAM 권한이나 CORS 설정이 없으면 저장소가 업로드를 거부 |
| OpenSearch | 엔드포인트가 비면 검색은 사용 불가로 응답하고 색인은 생략<br>엔드포인트에 스킴이나 경로가 있으면 기동 실패<br>인덱스 없음은 빈 목록<br>질의 실패는 사용 불가로 응답하고 WARN<br>색인 실패는 WARN만 남기고 스토리 저장은 진행 |
| Redis | 지연 연결이라 기동은 진행<br>회원 체험 카운터 장애는 예약 실패로 보고 크레딧 경로로 폴백, WARN<br>운영 health는 Redis를 분리 |
| Data Prepper | 추적을 켜고 주소가 비면 기동 실패<br>추적이 꺼지면 스팬을 만들되 전송하지 않음 |
| Slack 웹훅 | 미설정이면 신고 알림 생략 |
| 공식 계정 설정 | 비어 있으면 오리지널 목록이 빈 값<br>UUID 형식이 아니면 기동 실패 |
| 프리셋 CDN 주소 | 비어 있으면 프리셋 키가 남은 스토리의 표지가 `null` |

<br>

### 6-2 배포 경로

테스트와 빌드를 마친 뒤 이미지를 게시하고 배포한다. `main` push는 같은 소스 트리의 `dev` 성공 실행이 있으면 테스트를 다시 실행하지 않는다. `dev`로 PR을 올리면 테스트와 빌드만 한다.

| 단계 | 개발 | 운영 |
|---|---|---|
| 자동 시작 | `dev` push | `main` push |
| 머지 규칙 | 기능 브랜치에서 `dev`로 squash | `release/vX.Y.Z`에서 `main`으로 merge commit |
| 이미지 태그 | 커밋 SHA 앞 7자리, 환경 태그 `dev` | 커밋 SHA 앞 7자리, 배포 시 `latest` 승격<br>실패하면 이전 digest로 복원 |
| 상태 검사 | 배포 완료, 서버와 AI 컨테이너 정상, health `UP` | 동일 |

<br>

### 6-3 환경 변수와 시크릿

환경 변수가 설정 파일의 값보다 우선한다. 설정은 기동 시 읽으므로 변경 뒤 새 태스크를 시작해야 적용된다. 값은 Terraform이 태스크 정의에 주입하고 시크릿은 Secrets Manager에서 주입한다. AWS 자원에는 태스크 역할로 접근하므로 별도 접근 키를 주입하지 않는다. 이 도메인이 읽는 설정만 적는다. 기본값이 "빈 값"이면 변수가 없어도 빈 문자열로 기동한다. "없음"이면 변수가 없을 때 기동에 실패한다.

<br>

**1. AI 연동**

| 이름 | 기본값 | 주입 출처 | 비고 |
|---|---|---|---|
| `MANYAK_AI_BASE_URL` | 없음 | 운영 태스크 환경 변수, Cloud Map 내부 주소<br>개발 태스크 환경 변수 `http://localhost:8000` | |
| `MANYAK_AI_STORY_STUB` | `false` | 주입 없음 | |

<br>

**2. 이미지 저장소**

| 이름 | 기본값 | 주입 출처 | 비고 |
|---|---|---|---|
| `MANYAK_IMAGE_BASE_URL` | `https://cdn.manyak.app` | 주입 없음 | 프리셋 이미지 키를 URL로 조합할 때만 사용 |
| `MANYAK_CHARACTER_IMAGE_BUCKET`, `MANYAK_CHARACTER_IMAGE_REGION`, `MANYAK_CHARACTER_IMAGE_BASE_URL` | 빈 값 | 개발과 운영 태스크 환경 변수, assets 버킷과 CDN 주소 | 버킷과 base URL이 둘 다 있어야 활성화<br>이름은 인물 이미지용이지만 표지와 업로드도 같이 사용 |
| `MANYAK_CHARACTER_IMAGE_ENDPOINT` | 빈 값 | 주입 없음 | 비어 있으면 AWS 기본 S3 주소 |
| `AWS_REGION` | `ap-northeast-2` | 태스크 실행 환경 | |

<br>

**3. 검색**

| 이름 | 기본값 | 주입 출처 | 비고 |
|---|---|---|---|
| `MANYAK_OPENSEARCH_ENDPOINT` | 빈 값 | 개발과 운영 태스크 환경 변수, 로그 도메인 엔드포인트 | 스킴과 경로 없는 호스트 |
| `MANYAK_OPENSEARCH_STORY_INDEX` | `stories-dev` | 개발 `stories-dev`, 운영 `stories-prod` | |
| `MANYAK_OPENSEARCH_REINDEX_ON_STARTUP` | `false` | 개발과 운영 Terraform 변수 | |

<br>

**4. 정책과 한도**

| 이름 | 기본값 | 주입 출처 | 비고 |
|---|---|---|---|
| `MANYAK_OFFICIAL_USER_PUBLIC_ID` | 빈 값 | 개발과 운영 태스크 정의에 환경별 값을 직접 기록 | 오리지널 필터의 공식 계정 |
| `MANYAK_CREDIT_STORY_CREATION_COST` | 250 | 주입 없음 | 런타임 값은 PAYMENT 정책이 우선 |
| `MANYAK_GUEST_TRIAL_STORYLINE_LIMIT` | 5 | 주입 없음 | |
| `MANYAK_GUEST_TRIAL_STORY_CREATION_LIMIT` | 1 | 주입 없음 | |

<br>

**5. 관측**

| 이름 | 기본값 | 주입 출처 | 비고 |
|---|---|---|---|
| `MANYAK_TRACING_ENABLED` | `false` | 운영 Terraform 변수 | |
| `MANYAK_OTLP_TRACES_ENDPOINT` | 빈 값 | 추적을 켠 운영 환경에 Data Prepper 내부 주소 주입 | 추적을 켜면 필수 |
| `MANYAK_TRACING_SAMPLING` | `1.0` | 주입 없음 | |
| `MANYAK_OTLP_METRICS_ENABLED` | `false` | 운영 Terraform 변수, 전송 URL과 인증 헤더는 Secrets Manager | Grafana Cloud로 전송 |
| `SENTRY_DSN` | 빈 값 | 개발과 운영 Secrets Manager | |
| `SENTRY_ENVIRONMENT` | `local` | 개발과 운영 태스크 환경 변수 | |
| `MANYAK_SLACK_REPORT_WEBHOOK_URL` | 빈 값 | 운영 Secrets Manager | |

<br>

### 6-4 배포 조건

| 확인 항목 | 기준 | 자동 여부와 한계 |
|---|---|---|
| 와이어 계약 변경 | 응답 형식이 바뀌면 서버와 클라이언트를 함께 배포<br>AI 계약이 바뀌면 서버와 AI 서버를 함께 배포 | 수동 검토<br>개발은 같은 태스크를 두 레포가 갱신하므로 순서를 워크플로가 보장하지 않음<br>운영은 서버와 AI가 별도 서비스라 순서를 수동으로 맞춤|
| S3 경로 권한과 CORS | Terraform apply가 서버 배포보다 먼저<br>늦으면 저장소가 업로드를 거부하고 새 스토리의 표지는 `null` | 수동 적용<br>서버 배포 워크플로는 Terraform 상태를 검사하지 않음 |
| 컬럼 제거 | 그 컬럼을 읽는 구버전 태스크가 사라진 다음 릴리스에서 수행<br>롤링 중 구버전 SELECT 실패 방지 | 수동 검토 |
| 마이그레이션 | 기동 시 실행하므로 새 마이그레이션은 해당 코드보다 먼저 적용<br>마이그레이션은 재실행해도 같은 결과 | 기동 시 자동 적용<br>마이그레이션 경로 변경 PR은 `tbls lint`와 `dbdoc/` 비교가 CI 자동 |
| 코드 테스트 | 전체 테스트 통과 | CI 자동 |
| 컨테이너 기동 | 컨테이너 헬스체크와 `/actuator/health` `UP` | CI 자동<br>AI 서버 실제 호출과 검색, 업로드 동작은 검사하지 않음 |

<br>

### 6-5 설정 변경

| 변경 대상 | 변경 위치와 적용 | 확인 조건 |
|---|---|---|
| 공식 계정 | 환경별 태스크 정의 값 변경 후 Terraform apply | 해당 환경 DB에 그 public_id의 사용자 존재<br>오리지널 목록 응답 |
| PENDING 회수 기준 | 설정 속성 변경 후 새 태스크 | 컴파일 읽기 제한 시간보다 길게 유지 |
| 완성 소모 이프 | 운영 중 조정은 `credit_policies`의 `story_creation_cost` 오버라이드, 스냅샷 갱신 주기 60초<br>기본값 변경은 코드 수정 후 재빌드 | 최소값 1 이상<br>정책 반영 뒤 완성 요청의 차감량 |
| 검색 재색인 | 해당 환경의 Terraform 변수 `search_reindex_on_startup=true`로 apply 후 `false`로 되돌림 | 기동 로그에 재색인 실패 WARN 없음<br>검색 결과에 기존 스토리 포함 |
| 화풍 카탈로그 | `art_styles` 행을 SQL로 추가하거나 비활성화<br>이름, 설명, 순서 변경<br>신규 화풍은 AI가 지원을 배포한 뒤 활성화 | 화풍 목록 응답<br>`ANIME`은 기본값이라 비활성화하지 않음 |
| 이미지 저장소 | assets 모듈 출력이 태스크 정의로 전달되므로 버킷과 CDN 변경 후 Terraform apply | presign 201, 업로드 PUT 200, 새 스토리의 표지 URL |
| 추적과 지표 전송 | 운영 Terraform 변수 `tracing_enabled`, `enable_otlp_metrics` 변경 후 apply | 지표는 시크릿의 전송 URL과 인증 헤더가 먼저 채워져야 함<br>추적은 수집기 FGAC 권한이 먼저 |

<br>

### 6-6 적용과 복구

**1. 적용 순서**

와이어 계약이 바뀌면 배포 조건의 순서를 먼저 맞춘다.

| 순서 | 작업 | 확인 항목 |
|---|---|---|
| 1 | 설정과 인프라 확인 | 새 시크릿 키의 주입 참조, S3 경로 권한과 CORS, OpenSearch 인덱스, 마이그레이션 순서<br>Terraform 변경은 서버 배포보다 먼저 apply |
| 2 | 동반 배포 확인 | AI 서버, 클라이언트와 함께 배포해야 하는 변경인지와 그 순서 |
| 3 | 배포 실행 | 운영은 AI 레포의 배포와 겹치지 않는지 확인 |
| 4 | 적용 결과 확인 | 배포 후 확인 항목 |

<br>

**2. 진행 중인 요청**

| 상황 | 처리와 한계 |
|---|---|
| 운영 롤링 교체 중 진행 중인 컴파일 | ALB 타깃 해제 대기 240초가 컴파일과 이미지 단계의 제한 시간 합보다 길므로 기존 태스크에서 완료<br>새 태스크로 이전하지 않음 |
| 태스크 강제 종료 중 진행 중인 컴파일 | 생성 요청 행이 `PENDING`으로 남고 클라이언트는 응답을 받지 못함<br>같은 요청 ID 재요청은 회수 기준 시간 동안 진행 중으로 거절<br>그 뒤 회수해 재실행<br>이미 저장된 간편 제작 결과는 요청 회수 시 응답 재구성 |
| 개발 stop-then-start | 교체 중 모든 요청 실패<br>데이터 컨테이너 재시작 |
| AI 호출 중 AI 서버 교체 | 호출이 끊기면 AI 실패로 응답, 요청 행 `FAILED`<br>같은 요청 ID 재요청으로 재실행 |

<br>

**3. 복구**

자동 복구가 실행돼도 서비스가 정상으로 돌아오지 않았을 수 있으므로 실제 서버 상태를 확인한다.

| 상황 | 복구 방식 | 한계와 확인 사항 |
|---|---|---|
| 새 태스크 헬스체크 실패 | 직전 배포로 자동 복귀 | 환경 태그가 실패한 이미지를 가리킬 수 있으므로 다음 재배포 전에 태그 확인 |
| 배포는 정상이나 동작 오류 | revert 커밋 릴리스 또는 이전 이미지를 환경 태그로 다시 태깅한 뒤 새 배포 | health 기반 자동 복구는 동작 오류를 탐지하지 않음 |
| 마이그레이션 적용 후 되돌리기 | 적용된 마이그레이션은 되돌리지 않음 | 새 컬럼은 구버전 코드와 호환하게 추가 |
| 설정 오류 | 잘못된 Terraform 값이나 시크릿을 이전 호환 값으로 복구 후 apply | 이미지 태그 복원만으로 설정은 복원되지 않음 |

<br>

### 6-7 배포 후 확인

| 확인 항목 | 자료 | 기준 |
|---|---|---|
| 기동 | 해당 배포 ID의 태스크 상태, 헬스체크 `/actuator/health`, 스모크 테스트 | 의도한 이미지로 기동, `UP` |
| 완성 실패 | `manyak.story.creation.duration`의 `failure` 비율 | 배포 전과 같은 수준 |
| AI 호출 | `ai_call_logs`의 `STARTED` 잔존 | 호출 중 중단 없음 |
| 검색 | 색인 실패 WARN, 검색 응답 | WARN 없음, 검색 성공 |
| 장르와 표지 | `GET /stories/genres` 응답, 새 스토리의 표지 `null` | 계약과 일치 |
| 이미지 업로드 | presign 응답과 업로드 PUT | 발급과 업로드 성공 |

<br>

### 6-8 배포 실패 진단

| 실패 상황 | 확인할 자료와 위치 | 원인별 조치 |
|---|---|---|
| 기동 중 설정 검증 실패 | 시작 로그의 예외 메시지 | AI 주소 스킴과 호스트, OpenSearch 엔드포인트 형식, 공식 계정 UUID, 추적 주소 누락 중 해당 값 수정 후 apply |
| health 정상, 생성이 AI 실패로 응답 | 요청 ID의 `ai_call_logs`, AI 서버 로그, AI 주소 | AI 서비스 상태와 내부 주소 확인<br>제한 시간 초과와 AI 오류 응답 구분 |
| 검색이 사용 불가로 응답 | 시작 로그의 인덱스 초기화 WARN, OpenSearch 엔드포인트, 태스크 역할 권한 | 엔드포인트 미주입, 인덱스 초기화 실패, 질의 실패를 구분 |
| 이미지 업로드 실패 | 이미지 저장소 환경 변수 3종, 버킷 CORS, 태스크 역할의 업로드 경로 권한 | 미설정은 presign이 사용 불가로 응답<br>권한과 CORS 문제는 저장소가 업로드 거부<br>Terraform apply 순서 확인 |
| 새 스토리의 표지가 `null` | 이미지 저장소 환경 변수, S3 업로드 경로 권한 | 업로드 생략 조건과 권한 문제를 구분 |
