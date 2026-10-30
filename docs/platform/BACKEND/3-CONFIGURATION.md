# 3 백엔드 런타임 설정

설정 이름과 기본값은 서버 dev `32ae380`의 `application.yml`과 프로파일 yml(`application-{local,dev,prod}.yml`)을 기준으로 한다. 실제 적용값은 배포 기록으로 확인하며 도메인별 설정이 바뀌면 해당 세트의 배포 계약을 우선한다. 설정 코드가 있다는 사실은 외부 결제, 푸시, 관측이 켜져 있다는 증거가 아니다.

값은 배포 파이프라인이 주입하며 문서와 레포에 싣지 않는다. 표의 기본값은 yml에 적힌 값이고 빈 값은 "없음"으로 적는다. `MANAGEMENT_*`, `SPRING_*`처럼 yml에 자리 표시가 없는 이름은 Spring 환경 변수 바인딩으로 프로퍼티에 들어간다.

<br>

### 3-1 연결과 인증

| 환경 변수 | 기본값 | 필수 | 용도 |
| --- | --- | --- | --- |
| `MANYAK_DB_URL`, `MANYAK_DB_USERNAME`, `MANYAK_DB_PASSWORD` | 없음 | 예 | PostgreSQL 연결. 프로파일 yml에서 읽는다 |
| `SPRING_DATA_REDIS_HOST`, `SPRING_DATA_REDIS_PORT` | `localhost`, `6379` | 예(운영) | Redis 연결. 포트는 `MANYAK_REDIS_PORT`로도 줄 수 있다 |
| `MANYAK_AI_BASE_URL` | 없음 | 예 | AI 서버 base URL(scheme 포함). 기동 시 scheme과 host를 검증해 잘못된 값이면 부팅 실패. 연결 5초, 이벤트 간 60초 등 타임아웃은 `manyak.ai.*` 프로퍼티 ([CHAT 4-2-6 이어쓰기](../../domain/CHAT/BACKEND/4-2-CONTRACT.md#4-2-6-이어쓰기)) |
| `MANYAK_AI_CHAT_STUB`, `MANYAK_AI_STORY_STUB`, `MANYAK_AI_MODERATION_STUB` | 프로파일별 | 아니오 | AI 스텁 토글(`manyak.ai.{chat,story,moderation}.stub`). `true`면 실제 AI 호출 없이 고정 응답을 돌려주고 `ai_call_logs`의 `model`, `provider`가 `stub`이다. 프로파일 기본은 local `true`, dev와 prod `false`. 환경 변수가 프로파일 yml보다 우선한다 |
| `MANYAK_INTERNAL_SHARED_SECRET` | 없음 | 예(원격 알림) | `/internal/**` 공유 시크릿. manyak-notification이 이 값으로 서버 내부 경로를 호출한다 ([NOTIFICATION 5-1-6](../../domain/NOTIFICATION/BACKEND/5-1-SECURITY.md#5-1-6-내부-경로-보호)) |
| `MANYAK_CORS_ALLOWED_ORIGINS` | 없음 | 예 | CORS 허용 origin(콤마 구분) |
| `MANYAK_AUTH_JWT_SECRET` | 없음 | 예 | access JWT HS256 키(32바이트 이상). 비어 있으면 기동 실패. issuer와 TTL은 `manyak.auth.jwt.*` yml 전용 |
| `MANYAK_AUTH_CONSENT_GATE_ENABLED`, `MANYAK_AUTH_CONSENT_TOKEN_TTL` | `false`, `PT10M` | 아니오 | 소셜 가입 전 동의 확인 단계와 동의 대기 코드 수명 ([ACCOUNT 4-1](../../domain/ACCOUNT/BACKEND/4-1-PIPELINES.md)) |
| `MANYAK_GOOGLE_CLIENT_IDS` | 없음(local은 더미) | 예 | Google OAuth client ID 목록(콤마 구분). 비어 있으면 모든 Google 로그인을 거부 |
| `MANYAK_KAKAO_CLIENT_IDS` | 없음(local은 더미) | 카카오 로그인 사용 시 예 | 같은 카카오 앱의 REST API 키(웹 `aud`)와 네이티브 앱 키(Android `aud`) 목록. 플랫폼 키가 빠지면 그 플랫폼 로그인만 401 |
| `MANYAK_LEGAL_TERMS_VERSION`, `MANYAK_LEGAL_PRIVACY_VERSION`, `MANYAK_LEGAL_GUEST_PRIVACY_VERSION` | `v1.4`, `v1.8`, `v1.0` | 아니오 | 현행 약관과 처리방침 버전. 동의 확인 기준 |
| `MANYAK_OFFICIAL_USER_PUBLIC_ID` | 없음 | 아니오 | 오리지널 스토리를 소유한 공식 계정 공개 ID. 비어 있으면 오리지널 필터가 빈 결과 |
| `AWS_REGION` | `ap-northeast-2` | 아니오 | OpenSearch, SQS, 관리자 인프라 조회의 리전 |

<br>

### 3-2 재화와 체험 한도

| 환경 변수 | 기본값 | 용도 |
| --- | --- | --- |
| `MANYAK_CREDIT_SIGNUP_REWARD`, `MANYAK_CREDIT_INVITE_REWARD`, `MANYAK_CREDIT_INVITE_MONTHLY_CAP`, `MANYAK_CREDIT_ATTENDANCE_REWARD` | `1000`, `2000`, `10`, `250` | 가입, 초대, 출석 보상과 초대 월 상한 |
| `MANYAK_CREDIT_STORY_CREATION_COST`, `MANYAK_CREDIT_CHAT_IMAGE_COST` | `250`, `0` | 간편 제작과 채팅 이미지 단가. 채팅 턴 단가는 모델별 가격이 정하며 별도 환경 변수가 없다 ([PAYMENT 4-1](../../domain/PAYMENT/BACKEND/4-1-PIPELINES.md)) |
| `MANYAK_CREDIT_POLICY_REFRESH_ENABLED`, `MANYAK_CREDIT_POLICY_REFRESH_INTERVAL_MS` | `true`, `60000` | 정책 오버라이드 갱신 |
| `MANYAK_CREDIT_RECONCILIATION_ENABLED`, `..._INTERVAL_MS`, `..._INITIAL_DELAY_MS`, `..._CHARGE_AGE_THRESHOLD` | `true`, `900000`, `60000`, `PT15M` | 선차감 대사 배치 ([PAYMENT 4-1-15](../../domain/PAYMENT/BACKEND/4-1-PIPELINES.md#4-1-15-선차감-대사)) |
| `MANYAK_GUEST_TRIAL_STORYLINE_LIMIT`, `..._STORY_CREATION_LIMIT`, `..._CHAT_TURN_LIMIT`, `..._CHAT_IMAGE_LIMIT` | `5`, `1`, `5`, `5` | 게스트 체험 한도 |
| `MANYAK_GROBLE_WEBHOOK_SECRET` | 없음 | 그로블 웹훅 HMAC 검증. 비어 있으면 주문 생성과 웹훅이 503 |

<br>

### 3-3 채팅, 스토리, 검색, 이미지

| 환경 변수 | 기본값 | 용도 |
| --- | --- | --- |
| `MANYAK_CHAT_COMPACT_ENABLED`, `MANYAK_CHAT_COMPACT_INTERVAL_TURNS`, `MANYAK_CHAT_COMPACT_TIMEOUT_SECONDS` | `false`, `10`, `300` | 대화 요약 켜기, 요약 주기(턴), AI 요약 대기 한도 ([CHAT 4-1](../../domain/CHAT/BACKEND/4-1-PIPELINES.md)) |
| `MANYAK_CHAT_SSE_CONCURRENCY`, `MANYAK_CHAT_SSE_QUEUE_CAPACITY` | `64`, `100` | 채팅 SSE 작업 동시 실행 수와 대기열 크기 |
| `MANYAK_AI_MODERATION_TIMEOUT`, `..._POOL_SIZE`, `..._RETRY_DELAYS`, `..._REQUEST_BUDGET_BYTES`, `..._RECLAIM_AFTER`, `..._POLL_INTERVAL`, `..._POLL_ENABLED` | `180s`, `4`, `1m,5m`, `41943040`, `300s`, `1000`, `true` | 스토리 검수 요청과 재시도, 회수 주기 ([MODERATION 4-1](../../domain/MODERATION/BACKEND/4-1-PIPELINES.md)) |
| `MANYAK_OPENSEARCH_ENDPOINT` | 없음 | 스토리 검색 OpenSearch 호스트(`https://` 없이). 비어 있으면 검색 503이고 색인을 건너뛴다. 인증은 태스크 역할 SigV4 ([STORY 4-2-3](../../domain/STORY/BACKEND/4-2-CONTRACT.md#4-2-3-검색)) |
| `MANYAK_OPENSEARCH_STORY_INDEX` | `stories-dev` | 검색 인덱스 이름. 운영은 `stories-prod` |
| `MANYAK_OPENSEARCH_REINDEX_ON_STARTUP` | `false` | `true`면 기동 시 전체 재색인 1회. 복구용이며 끝나면 되돌린다 |
| `MANYAK_IMAGE_BASE_URL` | `https://cdn.manyak.app` | 이미지 CDN base URL. `imageKey`로 서빙 URL을 만든다 ([CHAT 4-1-13](../../domain/CHAT/BACKEND/4-1-PIPELINES.md#4-1-13-실시간-이미지)) |
| `MANYAK_CHARACTER_IMAGE_BUCKET`, `..._REGION`, `..._BASE_URL`, `..._ENDPOINT` | 없음 | 생성 이미지 S3 업로드와 URL. `ENDPOINT`는 로컬 MinIO 같은 S3 호환 저장소용 |
| `MANYAK_ASSET_BASE_URL` | `https://api.manyak.app`(dev는 `https://dev-api.manyak.app`) | 프로필 프리셋 이미지 base URL |

<br>

### 3-4 알림

| 환경 변수 | 기본값 | 용도 |
| --- | --- | --- |
| `MANYAK_PUSH_MODE` | `local` | 발송 요청 전달 방식. `local`은 서버 안에서 처리, `remote`는 아웃박스를 거쳐 큐로 보내 manyak-notification이 소비 ([NOTIFICATION 3-1](../../domain/NOTIFICATION/BACKEND/3-1-SOFTWARE-ARCHITECTURE.md)) |
| `MANYAK_PUSH_QUEUE_URL` | 없음 | 원격 모드의 SQS 큐 URL. local 프로파일의 원격 모드는 Kafka(`SPRING_KAFKA_BOOTSTRAP_SERVERS`, 기본 `localhost:9092`) |
| `MANYAK_FCM_SERVICE_ACCOUNT_JSON` | 없음 | Firebase 서비스 계정 JSON 원문. 비어 있으면 FCM 빈을 만들지 않고 발송하지 않는다. Secrets Manager에 키를 넣고 태스크 정의에 노출하는 terraform apply가 함께 필요 |
| `MANYAK_PUSH_WEB_BASE_URL`, `MANYAK_PUSH_WEB_ICON_URL` | `https://manyak.app`, `https://manyak.app/icons/icon-192.png` | 딥링크 base URL과 웹 푸시 아이콘 |
| `MANYAK_PUSH_ATTENDANCE_REMINDER_ENABLED`, `..._CRON`, `..._TITLE`, `..._BODY` | `true`, `0 0 9 * * *`, yml 문구 | 출석 리마인드 배치와 기본 문구 |
| `MANYAK_PUSH_CREDIT_EXPIRY_REMINDER_ENABLED`, `..._CRON`, `..._TITLE`, `..._BODY` | `true`, `0 0 10 * * *`, yml 문구 | 이프 만료 예정 알림 배치와 기본 문구 |
| `MANYAK_PUSH_PROMOTION_ENABLED`, `MANYAK_PUSH_PROMOTION_INTERVAL_MS`, `MANYAK_PUSH_CAMPAIGN_SENDING_TTL` | `true`, `60000`, `PT30M` | 관리자 캠페인 발송 회차 주기와 발송 중 상태 만료 |
| `MANYAK_PUSH_TEMPLATE_REFRESH_ENABLED`, `MANYAK_PUSH_TEMPLATE_REFRESH_INTERVAL_MS` | `true`, `300000` | 알림 문구 오버라이드 갱신 |
| `MANYAK_SLACK_FEEDBACK_WEBHOOK_URL`, `MANYAK_SLACK_REPORT_WEBHOOK_URL`, `MANYAK_SLACK_MODERATION_WEBHOOK_URL` | 없음 | 피드백, 신고, 검수 보류 Slack 알림. 검수 보류는 비어 있으면 신고 웹훅을 쓴다. 비어 있으면 알림만 생략 |
| `MANYAK_GOOGLE_FORM_FEEDBACK_ID`, `..._BODY_ENTRY`, `..._EMAIL_ENTRY`, `..._PLATFORM_ENTRY`, `..._APP_VERSION_ENTRY`, `MANYAK_GOOGLE_FORM_BASE_URL` | form ID는 prod만 기본값, entry ID와 base URL은 yml 기본값 | 피드백 구글 폼 적재. form ID가 비어 있으면 건너뛴다 ([CHAT 4-2-11](../../domain/CHAT/BACKEND/4-2-CONTRACT.md#4-2-11-피드백-등록)) |

<br>

### 3-5 관측과 분석

| 환경 변수 | 기본값 | 용도 |
| --- | --- | --- |
| `MANYAK_OTLP_METRICS_ENABLED` | `false` | 메트릭 OTLP 전송 토글. 켠 채 URL을 주지 않으면 `localhost:4318`로 보낸다 ([2-1](2-OBSERVABILITY.md#2-1-메트릭과-운영-연동)) |
| `MANAGEMENT_OTLP_METRICS_EXPORT_URL`, `MANAGEMENT_OTLP_METRICS_EXPORT_AGGREGATIONTEMPORALITY` | 없음 | 메트릭 사용 시 필수. 운영은 내부 OTel Collector의 `/v1/metrics`와 `cumulative`. AMP 인증은 Collector의 IAM과 SigV4가 맡는다 |
| `MANYAK_TRACING_ENABLED`, `MANYAK_TRACING_SAMPLING`, `MANYAK_OTLP_TRACES_ENDPOINT` | `false`, `1.0`, 없음 | 트레이스 전송. endpoint는 전체 URL(예 `http://collector:4318/v1/traces`). 표준 `OTEL_EXPORTER_OTLP_ENDPOINT`는 메트릭 설정이 가로채므로 쓰지 않는다 |
| `SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_TRACES_SAMPLE_RATE` | 없음, `local`(dev는 `dev`), `0.0` | Sentry. DSN이 없으면 비활성 |
| `MANYAK_ANALYTICS_DEVICE_ID_PEPPER` | 없음 | `device_id` 해시 pepper. 없으면 옛 이름 `MANYAK_ANALYTICS_ANONYMOUS_ID_PEPPER`, 둘 다 없으면 무염 해시 |
| `MANYAK_ANALYTICS_AMPLITUDE_ENABLED`, `MANYAK_AMPLITUDE_API_KEY`, `MANYAK_AMPLITUDE_BASE_URL` | `false`, 없음, `https://api2.amplitude.com` | 서버 분석 이벤트(`server_*`) 발행. 켜고 API 키가 있어야 보낸다 |

`OTEL_SERVICE_NAME`은 주입하지 않는다. 없으면 `spring.application.name`(`manyak-server`)이 `service.name`이 되고 Collector가 이를 `job` 라벨로 옮긴다. 로컬만 `manyak-server-local`로 구분한다.

<br>

### 3-6 관리자

| 환경 변수 | 기본값 | 용도 |
| --- | --- | --- |
| `MANYAK_AMPLITUDE_SECRET_KEY`, `MANYAK_AMPLITUDE_TEAM_COHORT_ID`, `MANYAK_AMPLITUDE_DASHBOARD_BASE_URL` | 없음, 없음, `https://amplitude.com` | 관리자 지표의 Amplitude 조회 키, 팀 계정 코호트, 대시보드 링크 ([ADMIN 6](../../domain/ADMIN/BACKEND/6-DEPLOYMENT.md)) |
| `MANYAK_ADMIN_DASHBOARD_EXCLUDED_USER_IDS` | yml 목록 | DB 지표에서 뺄 팀 계정 내부 ID |
| `MANYAK_ADMIN_PUSH_OPENS_MEASURED_FROM` | 없음 | 푸시 열람 측정 시작일(KST `YYYY-MM-DD`) |
| `MANYAK_ADMIN_LANGFUSE_HOST`, `..._PUBLIC_KEY`, `..._SECRET_KEY`, `..._ENVIRONMENT`, `..._RETENTION_DAYS` | 없음, `30`일 | AI 비용 지표의 Langfuse 조회 |
| `MANYAK_ADMIN_INFRA_ECS_CLUSTER`, `..._ECS_SERVICES`, `..._ALB`, `..._RDS_INSTANCE`, `..._REDIS_NODES`, `..._OPENSEARCH_DOMAIN`, `..._AWS_ACCOUNT_ID` | 없음 | 운영 인프라 지표의 CloudWatch 조회 대상 |
| `MANYAK_PLAY_STATS_BUCKET`, `MANYAK_PLAY_STATS_PACKAGE_NAME`, `MANYAK_PLAY_STATS_SA_KEY_BASE64` | yml 버킷, `app.manyak`, 없음 | Google Play 설치 보고서(GCS) 조회. 키가 없으면 앱 설치 지표가 비어 있다 |

<br>

환경별 태스크 참조, IAM, 재배포는 [배포 설계](../../operations/DEPLOYMENT.md#6-런타임-설정과-시크릿)를 따른다.
