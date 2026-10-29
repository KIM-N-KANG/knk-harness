# 3 백엔드 런타임 설정

설정 이름과 기본값은 기존 통합 문서의 기준 코드 `d4fe174` 및 알림 관련 후속 기록을 보존한다. 실제 적용값은 배포 기록으로 확인하며 도메인별 설정이 변경되면 해당 세트의 배포 계약을 우선한다.

### 3-1 런타임 설정

값은 배포 파이프라인이 주입하며 문서·레포에 싣지 않습니다.

| 환경 변수 | 필수 | 용도 |
| --- | --- | --- |
| `MANYAK_DB_URL` · `MANYAK_DB_USERNAME` · `MANYAK_DB_PASSWORD` | 예 | PostgreSQL 연결 |
| `SPRING_DATA_REDIS_HOST` · `SPRING_DATA_REDIS_PORT` | 예(운영) | Redis 연결. 로컬 기본 `localhost:6379` |
| `MANYAK_AI_BASE_URL` | 예 | AI 서버 base URL(scheme 포함). 기동 시 scheme·host를 검증해 잘못된 값이면 부팅 실패(스텁 모드에서는 불필요). 연결 5초·이벤트 간 60초 등 타임아웃은 `manyak.ai.*` 프로퍼티([§4-3-3](../../domain/AGENTS.md#1-도메인과-세트)) |
| `MANYAK_AI_CHAT_STUB` · `MANYAK_AI_STORY_STUB` | 아니오 | AI 스텁 토글(`manyak.ai.chat.stub` · `manyak.ai.story.stub`). `true`면 실제 AI 호출 없이 스텁 응답: 채팅 스텁은 고정 서사 문구에 `userInput` 앞 24자를 에코해 3자 청크로 스트리밍하고 고정 선택지 3개를 반환, 스토리 스텁은 결정적 더미 스토리라인 3개(`"[스텁] 스토리라인 N: {장르}"`)·더미 compile을 즉답합니다. 스텁 호출은 meta `model`·`provider`가 `"stub"`으로 `ai_call_logs`에서 구분됩니다. 미설정·`false`가 기본(실제 호출)이고 환경 변수가 프로필 yaml보다 우선하므로 임의 환경에서 켤 수 있습니다. 프로필 기본값은 local=`true`·prod=`false` |
| `MANYAK_IMAGE_BASE_URL` | 아니오 | 이미지 CDN base URL(기본 `https://cdn.manyak.app`): `imageKey` → 서빙 URL 조합용(`{base}/{prefix}/{imageKey}.png`, `_sm` 변형 포함: [§4-3-9](../../domain/AGENTS.md#1-도메인과-세트)) |
| `MANYAK_CREDIT_*` | 아니오 | 이프 정책값 오버라이드: `SIGNUP_REWARD`(1000) · `INVITE_REWARD`(2000) · `INVITE_MONTHLY_CAP`(10) · `ATTENDANCE_REWARD`(250) · `STORY_CREATION_COST`(250) · `CHAT_TURN_COST`(20) · `POLICY_REFRESH_{ENABLED(true), INTERVAL_MS(60000)}` · `RECONCILIATION_{ENABLED(true), INTERVAL_MS(900000), INITIAL_DELAY_MS(60000), CHARGE_AGE_THRESHOLD(PT15M)}` |
| `MANYAK_GUEST_TRIAL_*` | 아니오 | 게스트 체험 한도 오버라이드: `STORYLINE_LIMIT`(5) · `STORY_CREATION_LIMIT`(1) · `CHAT_TURN_LIMIT`(5) |
| `MANYAK_CORS_ALLOWED_ORIGINS` | 예 | CORS 허용 origin(콤마 구분) |
| `MANYAK_AUTH_JWT_SECRET` | 예 | access JWT HS256 키(32바이트 이상). 미주입 시 기본값이 빈 문자열이라 기동 실패(잘못된 운영 기동 조기 차단). JWT issuer·TTL은 `manyak.auth.jwt.*` yml 전용(환경 변수 바인딩 없음) |
| `MANYAK_GOOGLE_CLIENT_IDS` | 예 | Google OAuth client ID 목록(콤마 구분). 값이 없으면 모든 Google 로그인을 거부 |
| `MANYAK_KAKAO_CLIENT_IDS` | 카카오 로그인 사용 시 예 | 같은 카카오 디벨로퍼스 앱의 REST API 키(웹 `aud`)와 네이티브 앱 키(Android `aud`) 목록. 플랫폼 키가 빠지면 해당 플랫폼 로그인만 401이고, 값이 없으면 모든 Kakao 로그인을 거부. Google에는 영향 없음 |
| `MANYAK_FCM_SERVICE_ACCOUNT_JSON` | 아니오 | Firebase 서비스 계정 JSON **원문**. 비어 있으면 FCM 빈을 만들지 않아 푸시 설정 없이 기동하고 발송하지 않습니다([§4-3-5](../../domain/AGENTS.md#1-도메인과-세트) 발송 모듈). 앱과 같은 Firebase 프로젝트에서 발급. Secrets Manager `manyak/<env>/app` JSON에 키로 넣고, **태스크 정의 `secrets`에 그 키를 노출하는 terraform apply가 함께 필요**합니다: 값만 넣으면 컨테이너에 들어가지 않습니다(dev·prod 모두 Terraform 참조가 존재하며 실제 활성화는 배포 기록으로 확인) |
| `MANYAK_PUSH_WEB_ICON_URL` | 아니오 | 웹 푸시 알림 아이콘 URL. 기본값 `https://manyak.app/icons/icon-192.png` |
| `MANYAK_OPENSEARCH_ENDPOINT` | 아니오 | 검색 저장소 OpenSearch 엔드포인트(`https://` 없이 호스트, KNK-1141). 비어 있으면 검색 503·색인을 건너뛰고 기동합니다. 인증은 태스크 역할 SigV4라 시크릿이 없습니다([§4-3-1](../../domain/AGENTS.md#1-도메인과-세트) 스토리 검색) |
| `MANYAK_OPENSEARCH_STORY_INDEX` | 아니오 | 스토리 검색 인덱스 이름. 기본 `stories-dev`, 운영은 `stories-prod` |
| `MANYAK_OPENSEARCH_REINDEX_ON_STARTUP` | 아니오 | `true`면 기동 시 전체 재색인 1회. 초기 적재·복구용이며 끝나면 되돌립니다(켜 두면 배포마다 재색인) |
| `MANYAK_ANALYTICS_DEVICE_ID_PEPPER` | 아니오 | `device_id` 해시 pepper. 미설정 시 구 이름 `MANYAK_ANALYTICS_ANONYMOUS_ID_PEPPER`로 폴백(전환기), 둘 다 없으면 무염 해시 |
| `MANYAK_ANALYTICS_AMPLITUDE_ENABLED` · `MANYAK_AMPLITUDE_API_KEY` | 아니오 | 서버 분석 이벤트(`server_*`) Amplitude 발행. `ENABLED` 기본 `false`, 켜려면 `true` + API 키 필요(둘 중 하나 없으면 발행하지 않음) |
| `MANYAK_AMPLITUDE_BASE_URL` | 아니오 | Amplitude HTTP V2 base URL. 기본 `https://api2.amplitude.com`(EU는 `https://api.eu.amplitude.com`). `application.yml` 전용(`.env.example` 미포함) |
| `MANYAK_SLACK_FEEDBACK_WEBHOOK_URL` | 아니오 | 피드백 Slack 알림. 미설정 시 알림 생략 |
| `MANYAK_ASSET_BASE_URL` | 아니오 | 프로필 프리셋 이미지 서빙 base URL(기본 `https://api.manyak.app`): `profile_image_url = {base}/profile-presets/{명사}.png`([§4-5](../../domain/ACCOUNT/BACKEND/5-1-SECURITY.md)). 후속 S3/CDN 전환은 이 값 치환만으로 됨 |
| `MANYAK_GOOGLE_FORM_FEEDBACK_ID` · `MANYAK_GOOGLE_FORM_FEEDBACK_{BODY,EMAIL,PLATFORM,APP_VERSION}_ENTRY` · `MANYAK_GOOGLE_FORM_BASE_URL` | 아니오 | 피드백 구글 폼 적재(KNK-618, [§4-3-4](../../domain/AGENTS.md#1-도메인과-세트)). form ID 미설정이면 건너뜀: live form ID는 운영에만 둬 로컬 실행이 실 스프레드시트를 오염시키지 않음. entry ID는 공개 식별자라 yml 기본값 보유, base URL은 테스트 mock 전용 오버라이드 |
| `SENTRY_DSN` · `SENTRY_ENVIRONMENT` · `SENTRY_TRACES_SAMPLE_RATE` | 아니오 | Sentry 연동. DSN 미설정 시 비활성 |
| `MANYAK_OTLP_METRICS_ENABLED` | 아니오 | 메트릭 OTLP push 토글(`management.otlp.metrics.export.enabled`). 기본 `false`: 켠 채 endpoint를 주지 않으면 레지스트리가 `localhost:4318`로 불필요하게 전송합니다([§2-1](2-OBSERVABILITY.md#2-1-메트릭과-운영-연동)) |
| `MANAGEMENT_OTLP_METRICS_EXPORT_URL` · `MANAGEMENT_OTLP_METRICS_EXPORT_HEADERS_AUTHORIZATION` | 메트릭 사용 시 예([배포 Design §6](../../operations/DEPLOYMENT.md#6-런타임-설정과-시크릿)) | 운영용 Grafana Cloud URL과 인증 헤더. AI 컨테이너의 OTel 설정과 충돌하지 않도록 Spring 전용 이름을 사용합니다. 운영 URL은 `/v1/metrics`까지 포함해야 하며 인증값은 `Basic …` 형식입니다. 로컬의 표준 `OTEL_*` 변수는 경로를 자동으로 붙이고 헤더 공백을 인코딩합니다. 실제 값은 문서에 기록하지 않습니다 |
| `OTEL_SERVICE_NAME` | 아니오 | 리소스 `service.name` 오버라이드. 미설정 시 `spring.application.name`(=`manyak-server`)이 쓰이므로 **운영은 주입하지 않습니다**. 로컬만 `manyak-server-local`로 구분합니다 |

| 추가 환경 변수 | 필수 조건 | 용도 |
| --- | --- | --- |
| `MANYAK_GROBLE_WEBHOOK_SECRET` | Groble 사용 시 | webhook HMAC 검증. 비어 있으면 관련 주문 생성·webhook 503 |
| `MANYAK_GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` · `MANYAK_GOOGLE_PLAY_PACKAGE_NAME` | Google Play 사용 시 | 구매 검증·voided 대사. 비어 있으면 구매는 503, 대사는 실행하지 않음 |
| `MANYAK_CHARACTER_IMAGE_BUCKET` · `MANYAK_CHARACTER_IMAGE_REGION` · `MANYAK_CHARACTER_IMAGE_BASE_URL` | 생성 이미지 저장 시 | S3 업로드·URL 생성. 필요한 설정과 prefix IAM을 함께 공급 |
| `MANYAK_SLACK_REPORT_WEBHOOK_URL` | 신고 알림 사용 시 | 신고 전용 알림. 신고 저장과 알림 성공을 구분 |

환경별 태스크 참조·IAM·재배포는 [배포 Design](../../operations/DEPLOYMENT.md#6-런타임-설정과-시크릿)을 따릅니다. 설정 코드의 존재는 외부 결제·푸시·관측이 활성화되었다는 증거가 아닙니다.
