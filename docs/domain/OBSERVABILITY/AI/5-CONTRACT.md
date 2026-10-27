# 5. 계약

이 문서는 에이전트가 읽는 설정 파일, 자료 원천, 서비스 지도, 진단 요청과 진단 보고의 필드, 실행 폴더의 파일, 슬랙 메시지의 내용을 정한다.

필드의 의미는 3 태스크 정의에, 모델이 부르는 도구의 정의는 6-1 AI 실행에, 설정 파일 위치와 비밀값 출처는 7-4 배포에 있다. ([3-3 이상 후보](3-TASK-DEFINITION.md#3-3-이상-후보), [3-4 운영자 요청](3-TASK-DEFINITION.md#3-4-운영자-요청), [3-5 진단](3-TASK-DEFINITION.md#3-5-진단), [3-6 대화](3-TASK-DEFINITION.md#3-6-대화), [6-1-5 도구 정의와 권한](6-1-AI-EXECUTION.md#6-1-5-도구-정의와-권한), [7-4-4 환경 변수와 비밀 정보](7-4-DEPLOYMENT.md#7-4-4-환경-변수와-비밀-정보))

시각 필드는 모두 ISO 8601에 시간대 오프셋을 붙여 쓴다. 자료 원천의 시각은 UTC로 저장되어 있고 보고의 시각 필드에는 그대로 옮긴다. 보고 문장 안의 시각과 슬랙 메시지의 시각은 `slack.timezone`의 `HH:MM`으로 쓴다. ([6-1-4 프롬프트](6-1-AI-EXECUTION.md#6-1-4-프롬프트)와 [5-9 슬랙 메시지](#5-9-슬랙-메시지))

<br>

### 5-1 연동 대상과 방식

| 대상 | 방향 | 방식 | 권한 |
|---|---|---|---|
| OpenSearch | 읽기 | 탐지기: 검색 API에 집계 질의<br>모델: OpenSearch MCP 서버의 검색 도구 | 에이전트용 읽기 전용 사용자. 5-3-3의 역할 |
| CloudWatch | 읽기 | 탐지기: 지표 조회 API<br>모델: CloudWatch MCP 서버의 지표와 경보 도구 | 읽기 전용 AWS 자격의 지표와 경보 읽기 |
| AMP | 읽기 | 모델: Prometheus MCP 서버의 PromQL 도구. `prometheus.workspace_url`이 있을 때만 | 읽기 전용 AWS 자격의 질의 |
| Application Auto Scaling | 읽기 | 확장 이력 도구가 확장 활동 조회 API를 부름 | 읽기 전용 AWS 자격의 확장 활동 읽기 |
| Parameter Store | 읽기 | 설정 위치가 `ssm:`인 실행이 시작 때 설정 파일을 담은 파라미터를 읽음 | 2단계: 태스크 역할의 그 파라미터 읽기 |
| Secrets Manager | 읽기 | 비밀값 출처가 Secrets Manager인 실행이 시작 때 비밀 하나를 읽음<br>출처가 비밀 파일이면 같은 키를 담은 파일을 읽음 | 2단계: 태스크 역할의 그 비밀 읽기 |
| 모델 API | 호출 | Claude Agent SDK의 세션 | API 키 |
| 슬랙 | 양방향 | 소켓 모드. `slack.channel` 채널 하나에 알림을 올리고 봇 멘션과 스레드 메시지를 받음. 운영자 요청의 멘션 메시지에 반응을 달고 지움 | 봇 토큰과 앱 토큰. 그 채널의 읽기와 쓰기. 반응 쓰기(`reactions:write`) |
| 코드 저장소 | 읽기 | `code_repositories`의 저장소를 코드 사본으로 받고 진단 세션을 열기 전에 갱신함 | 공개 저장소는 자격 없음. 비공개 저장소는 내용 읽기만 가진 토큰 |
| 운영자 | 출력 | 실행 폴더의 파일과 슬랙 | 파일 쓰기 |

<br>

### 5-2 설정 파일

대상 서비스와 운영 환경에 맞춰 바꾸는 값은 YAML 설정 파일 하나로 받는다. 서비스 지도도 이 파일의 한 절에 둔다. 비밀값은 설정 파일에 두지 않는다.

<br>

**1. 읽기와 덮어쓰기**

| 항목 | 규칙 |
|---|---|
| 위치 | 환경 변수 `DIAG_CONFIG`로 받음. 파일 경로이거나 `ssm:` 뒤에 Parameter Store 파라미터 이름 |
| 상대 경로 | 경로 값(`session_dir`)이 상대 경로면 설정 파일이 있는 폴더 기준. 환경 변수로 덮어쓴 값도 같음<br>설정 위치가 `ssm:`이면 상대 경로를 받지 않음 |
| 우선순위 | 환경 변수, 설정 파일, 코드 기본값 순 |
| 덮어쓰기 이름 | 키 경로의 점을 밑줄로 바꾸고 대문자로 바꾼 뒤 앞에 `DIAG_`를 붙임. `limits.queries`는 `DIAG_LIMITS_QUERIES`<br>`DIAG_CONFIG`, `DIAG_SECRET_ID`, `DIAG_SECRETS_FILE`은 덮어쓰기가 아님 |
| 덮어쓰기 대상 | 문자열, 숫자, 불리언 값만. 배열과 배열 안의 값은 설정 파일에서만 바꿈 |
| 값 변환 | 환경 변수의 문자열을 키의 타입으로 바꿈. 불리언은 `true`와 `false`만 받음 |
| 받지 않는 값 | 아래 항목 표, 5-3 표, 5-4 표에 없는 키<br>해당 키와 이름이 일치하지 않는 `DIAG_` 환경 변수<br>키의 타입으로 바꿀 수 없는 값<br>IANA 시간대 이름이 아닌 `slack.timezone`<br>빠진 필수 항목 |

<br>

**2. 항목**

코드 기본값은 마냑에서 쓰는 값이다. 환경마다 달라 기본값을 둘 수 없는 항목은 필수다.

| 키 | 타입 | 기본값 | 의미 | 덮어쓰는 환경 변수 |
|---|---|---|---|---|
| `service_name` | 문자열 | 필수 | 시스템 프롬프트에 넣는 대상 서비스 이름 | `DIAG_SERVICE_NAME` |
| `aws.region` | 문자열 | `ap-northeast-2` | CloudWatch, AMP, Application Auto Scaling, Secrets Manager, Parameter Store를 부르는 지역 | `DIAG_AWS_REGION` |
| `aws.profile` | 문자열 | 빈 값 | 1단계에서 쓰는 읽기 전용 역할의 AWS 프로필 이름. 빈 값이면 기본 자격 체인(2단계는 태스크 역할)<br>탐지기, 확장 이력 도구, AWS MCP 서버가 같은 자격을 씀 | `DIAG_AWS_PROFILE` |
| `opensearch.url` | 문자열 | 필수 | OpenSearch 주소 | `DIAG_OPENSEARCH_URL` |
| `opensearch.user` | 문자열 | 필수 | 에이전트용 읽기 전용 사용자. 비밀번호는 비밀값 `OPENSEARCH_PASSWORD` | `DIAG_OPENSEARCH_USER` |
| `opensearch.log_index` | 문자열 | 필수 | 로그 인덱스 패턴 | `DIAG_OPENSEARCH_LOG_INDEX` |
| `opensearch.span_index` | 문자열 | `otel-v1-apm-span-*` | 스팬 인덱스 패턴 | `DIAG_OPENSEARCH_SPAN_INDEX` |
| `prometheus.workspace_url` | 문자열 | 빈 값 | AMP 작업 공간 주소. 빈 값이면 Prometheus MCP 서버를 띄우지 않음 | `DIAG_PROMETHEUS_WORKSPACE_URL` |
| `fields.log.<항목>` | 문자열 | 5-3의 로그 인덱스 표 | 로그 필드 이름 대응표 | 항목마다. `DIAG_FIELDS_LOG_TIMESTAMP` 등 |
| `fields.span.<항목>` | 문자열 | 5-3의 스팬 인덱스 표 | 스팬 필드 이름 대응표 | 항목마다. `DIAG_FIELDS_SPAN_DURATION` 등 |
| `redact_fields` | 문자열 배열 | `message`, `device_id_hash`, `session_id`, `request_id`, `span.attributes.http@url` | 식별자 제거 목록. 모델이 보면 안 되는 로그와 스팬의 필드 경로<br>OpenSearch 읽기 사용자의 역할이 이 필드를 FLS로 빼고 시작 검사가 그 결과를 확인함<br>`message`는 운영 로그의 메시지 원문이며 `span.attributes.http@url`은 채팅 ID 같은 경로 식별자가 든 요청 주소 | 없음 |
| `detection.queue_spans` | 문자열 배열 | 빈 배열 | 대기 스팬으로 보는 스팬 이름. 비어 있으면 대기 지연 신호를 판정하지 않음 | 없음 |
| `detection.queue_latency_seconds` | 숫자 | `1` | 대기 지연 신호의 1분 p95 기준 | `DIAG_DETECTION_QUEUE_LATENCY_SECONDS` |
| `detection.failure_ratio` | 숫자 | `0.01` | 실패율 신호 기준 | `DIAG_DETECTION_FAILURE_RATIO` |
| `detection.error_level` | 문자열 | `ERROR` | 오류 로그로 세는 `fields.log.level` 값 | `DIAG_DETECTION_ERROR_LEVEL` |
| `detection.error_logs_per_minute` | 정수 | `10` | 오류 로그 신호의 서비스별 1분 건수 기준 | `DIAG_DETECTION_ERROR_LOGS_PER_MINUTE` |
| `detection.saturation_percent` | 숫자 | `70` | 자원 포화 신호 기준 | `DIAG_DETECTION_SATURATION_PERCENT` |
| `detection.min_samples` | 정수 | `20` | 진입 지연, 대기 지연, 실패율 신호를 판정하는 해당 분의 최소 건수 | `DIAG_DETECTION_MIN_SAMPLES` |
| `detection.confirm_window_minutes` | 정수 | `5` | 신호 확정에 사용하는 최근 분 수 | `DIAG_DETECTION_CONFIRM_WINDOW_MINUTES` |
| `detection.confirm_minutes` | 정수 | `3` | 확정 구간 안에서 조건을 넘어야 신호를 확정하는 분 수 | `DIAG_DETECTION_CONFIRM_MINUTES` |
| `detection.close_quiet_minutes` | 정수 | `10` | 모든 신호가 조건을 넘지 않은 채 지나면 이상 후보를 닫는 분 수. 판정하지 않은 분이 끼면 다시 셈. 4-1-2 | `DIAG_DETECTION_CLOSE_QUIET_MINUTES` |
| `service_map` | 객체 | 필수 | 서비스 지도. 5-4 | 5-4 표 |
| `model.id` | 문자열 | `claude-sonnet-5-5` | 진단 턴과 대화 턴의 모델 식별자 | `DIAG_MODEL_ID` |
| `model.effort` | 문자열 | `medium` | 추론 강도. `low`, `medium`, `high` | `DIAG_MODEL_EFFORT` |
| `limits.queries` | 정수 | `25` | 진단 턴의 조회 횟수 | `DIAG_LIMITS_QUERIES` |
| `limits.diagnosis_seconds` | 정수 | `300` | 진단 턴 시간 | `DIAG_LIMITS_DIAGNOSIS_SECONDS` |
| `limits.diagnosis_turns` | 정수 | `30` | 진단 턴의 SDK 턴 수 | `DIAG_LIMITS_DIAGNOSIS_TURNS` |
| `limits.conversation_turns` | 정수 | `20` | 대화 턴의 SDK 턴 수 | `DIAG_LIMITS_CONVERSATION_TURNS` |
| `limits.diagnosis_usd` | 숫자 | `0.50` | 진단 턴의 SDK 비용 한도 | `DIAG_LIMITS_DIAGNOSIS_USD` |
| `limits.session_usd` | 숫자 | `2.00` | 세션 비용 한도 | `DIAG_LIMITS_SESSION_USD` |
| `limits.daily_usd` | 숫자 | `5.00` | 하루 비용 상한 | `DIAG_LIMITS_DAILY_USD` |
| `limits.session_lifetime_hours` | 정수 | `24` | 세션이 운영자 메시지를 받는 시간. 이상 후보는 닫은 뒤부터 세고 운영자 요청은 보고를 올린 뒤부터 셈 | `DIAG_LIMITS_SESSION_LIFETIME_HOURS` |
| `session_dir` | 문자열 | 필수 | SDK 세션 파일 폴더 | `DIAG_SESSION_DIR` |
| `slack.channel` | 문자열 | 필수 | 알림 채널 ID. 멘션도 이 채널에서만 받음 | `DIAG_SLACK_CHANNEL` |
| `slack.timezone` | 문자열 | `UTC` | 슬랙 메시지와 보고 문장에 쓰는 시각의 시간대. IANA 시간대 이름. 5-9와 6-1-4 | `DIAG_SLACK_TIMEZONE` |
| `code_repositories[]` | 배열 | 필수. 1개 이상 | 코드 사본으로 받는 저장소 | 없음 |
| `code_repositories[].name` | 문자열 | 필수 | 보고의 `code_ref.repo` 값과 서비스 지도의 저장소 이름 | 없음 |
| `code_repositories[].clone_url` | 문자열 | 필수 | clone 주소 | 없음 |
| `code_repositories[].branch` | 문자열 | 필수 | 진단 세션마다 맞추는 브랜치. 운영에 반영되는 브랜치 | 없음 |

<details>
<summary><b>설정 파일 예시(마냑 1단계)</b></summary>

<br>

공개 저장소에 두는 예시 설정 파일이다. OpenSearch 주소와 사용자, AWS 프로필 이름, 슬랙 채널 ID는 합성 값이다. 서비스 지도는 5-4 예시를 그대로 넣는다.

```yaml
service_name: 마냑
aws:
  region: ap-northeast-2
  profile: diagnosis-readonly
opensearch:
  url: https://opensearch.example.com
  user: diagnosis-reader
  log_index: manyak-logs-prod-*
  span_index: otel-v1-apm-span-*
prometheus:
  workspace_url: ""
fields:
  log:
    timestamp: "@timestamp"
    service: service
    level: level
    event_name: event_name
    endpoint: endpoint
    http_method: http_method
    status_code: status_code
    duration: duration_ms
    error_code: error_code
    trace_id: traceId
  span:
    start_time: startTime
    end_time: endTime
    service: serviceName
    name: name
    trace_group: traceGroup
    parent_span_id: parentSpanId
    duration: durationInNanos
    duration_unit: nanoseconds
    status_code: status.code
    db_statement: "span.attributes.jdbc@query[0]"
    trace_id: traceId
redact_fields: [message, device_id_hash, session_id, request_id, "span.attributes.http@url"]
detection:
  queue_spans: [chat.turn.queue]
  queue_latency_seconds: 1
  failure_ratio: 0.01
  error_level: ERROR
  error_logs_per_minute: 10
  saturation_percent: 70
  min_samples: 20
  confirm_window_minutes: 5
  confirm_minutes: 3
  close_quiet_minutes: 10
model:
  id: claude-sonnet-5-5
  effort: medium
limits:
  queries: 25
  diagnosis_seconds: 300
  diagnosis_turns: 30
  conversation_turns: 20
  diagnosis_usd: 0.50
  session_usd: 2.00
  daily_usd: 5.00
  session_lifetime_hours: 24
session_dir: runs/sessions
slack:
  channel: C0123456789
  timezone: UTC
code_repositories:
  - { name: manyak-server, clone_url: "https://github.com/KIM-N-KANG/manyak-server.git", branch: main }
  - { name: manyak-ai, clone_url: "https://github.com/KIM-N-KANG/manyak-ai.git", branch: main }
  - { name: manyak-notification, clone_url: "https://github.com/KIM-N-KANG/manyak-notification.git", branch: main }
  - { name: manyak-terraform, clone_url: "https://github.com/KIM-N-KANG/manyak-terraform.git", branch: dev }
service_map:
  # 5-4 예시의 components와 latency_slo
```

</details>

<br>

### 5-3 자료 원천

필드 이름은 설정의 `fields.log`와 `fields.span`으로 받는다. 탐지기의 집계 질의와 시스템 프롬프트의 자료 위치 안내가 이 이름을 쓴다. 표의 기본값은 마냑 자료의 값이다.

<br>

**1. 로그 인덱스**

인덱스 패턴은 `opensearch.log_index`로 받는다. 마냑의 로그 인덱스 이름은 `manyak-logs-<환경>-<yyyy.MM.dd>`이다.

| 키 | 기본값 | 타입 | 쓰임 |
|---|---|---|---|
| `fields.log.timestamp` | `@timestamp` | 시각 | 분 묶음 |
| `fields.log.service` | `service` | 문자열 | 서비스별 묶음. 서비스 지도의 `log_service` 값 |
| `fields.log.level` | `level` | 문자열 | 오류 로그 신호. 값이 `detection.error_level`과 같으면 오류 로그 |
| `fields.log.event_name` | `event_name` | 문자열 | 사건 이름별 묶음 |
| `fields.log.endpoint` | `endpoint` | 문자열 | 요청 경로별 묶음 |
| `fields.log.http_method` | `http_method` | 문자열 | 요청 경로와 함께 묶음 |
| `fields.log.status_code` | `status_code` | 정수 | 상태 코드별 묶음 |
| `fields.log.duration` | `duration_ms` | 정수 | 요청 처리 시간 집계 |
| `fields.log.error_code` | `error_code` | 문자열 | 오류 코드별 묶음 |
| `fields.log.trace_id` | `traceId` | 문자열 | 스팬 인덱스와 연결 |

<br>

**2. 스팬 인덱스**

인덱스 패턴은 `opensearch.span_index`로 받는다.

| 키 | 기본값 | 타입 | 쓰임 |
|---|---|---|---|
| `fields.span.start_time` | `startTime` | 시각 | 분 묶음 |
| `fields.span.service` | `serviceName` | 문자열 | 서비스별 묶음. 서비스 지도의 `span_service` 값 |
| `fields.span.name` | `name` | 문자열 | 스팬 이름별 묶음 |
| `fields.span.trace_group` | `traceGroup` | 문자열 | 진입 스팬 이름. 요청 경로별 묶음 |
| `fields.span.parent_span_id` | `parentSpanId` | 문자열 | 비어 있으면 진입 스팬 |
| `fields.span.end_time` | `endTime` | 시각 | 스팬 끝 시각 |
| `fields.span.duration` | `durationInNanos` | 정수 | 지연 집계 |
| `fields.span.duration_unit` | `nanoseconds` | 문자열 | `fields.span.duration`의 단위. `nanoseconds`, `microseconds`, `milliseconds` |
| `fields.span.status_code` | `status.code` | 정수 | 2이면 오류 |
| `fields.span.db_statement` | `span.attributes.jdbc@query[0]` | 문자열 | DB 쿼리문별 묶음 |
| `fields.span.trace_id` | `traceId` | 문자열 | 로그 인덱스와 연결 |

<br>

**3. OpenSearch 읽기 사용자의 역할**

탐지기와 OpenSearch MCP 서버는 `opensearch.user` 하나로 질의한다. 이 사용자는 세분화된 접근 제어(FGAC)의 역할 하나에 매핑한다.

| 항목 | 값 |
|---|---|
| 인덱스 권한 | `opensearch.log_index`와 `opensearch.span_index` 패턴의 읽기만 |
| 필드 수준 보안 | 역할에 FLS 제외 필드 목록을 둠. 목록은 `redact_fields`와 같음 |
| 클러스터 권한 | 쓰기와 설정 변경 권한 없음 |

FLS로 뺀 필드는 검색 결과, 집계, 건수 질의 어디에도 나오지 않는다. MCP 서버가 문서를 그대로 반환해도 메시지 원문과 식별자는 모델에 전달되지 않는다.

<br>

**4. 인프라 지표**

탐지기와 CloudWatch MCP 서버가 CloudWatch에서 읽는다.

| 네임스페이스 | 지표 | 차원 | 통계 |
|---|---|---|---|
| `AWS/ECS` | `CPUUtilization`과 `MemoryUtilization` | `ClusterName`과 `ServiceName` | Average와 Maximum |
| `AWS/RDS` | `CPUUtilization`, `DatabaseConnections`, `FreeableMemory`, `ReadLatency`, `WriteLatency`, `DiskQueueDepth` | `DBInstanceIdentifier` | Maximum |
| `AWS/ElastiCache` | `EngineCPUUtilization`과 `CurrConnections` | `CacheClusterId` | Maximum |
| `AWS/ApplicationELB` | `RequestCount`, `HTTPCode_Target_5XX_Count`, `HTTPCode_ELB_5XX_Count` | `LoadBalancer` | Sum |
| `AWS/ApplicationELB` | `TargetResponseTime` | `LoadBalancer` | p95 |

탐지기는 1분 주기로 읽는다. 모델은 표 밖의 지표도 CloudWatch MCP 서버로 읽을 수 있다.

<br>

**5. 앱 지표**

`prometheus.workspace_url`이 있으면 Prometheus MCP 서버가 그 AMP 작업 공간을 PromQL로 읽는다. 마냑은 앱 지표를 AMP로 보내고 운영 설정에 이 값을 채운다. 값이 비어 있으면 앱 지표 없이 진단한다. 탐지기는 앱 지표를 읽지 않는다.

<br>

**6. 확장 이력**

| 자료 | 필드 | 쓰임 |
|---|---|---|
| 확장 활동 | `StartTime`, `Description`, `Cause`, `StatusCode` | 태스크 수 변경 시각과 이유 |

경보 이력은 CloudWatch MCP 서버의 경보 도구로 읽는다.

<br>

### 5-4 서비스 지도

설정 파일의 `service_map` 절이다. 운영자가 관리하고 에이전트는 시작할 때 한 번 읽는다. 동시성 상한, 태스크 크기, 확장 정책 같은 설계값은 두지 않고 그 값이 있는 파일의 위치만 둔다.

| 필드 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `service_map.components[]` | 배열 | 필수 | 구성 요소 목록 |
| `service_map.components[].name` | 문자열 | 필수 | 보고에서 지목하는 이름 |
| `service_map.components[].kind` | 문자열 | 필수 | `service`, `executor`, `database`, `cache`, `load_balancer`, `autoscaling` |
| `service_map.components[].parent` | 문자열 | 선택 | 실행기와 오토스케일링이 속한 서비스의 `name` |
| `service_map.components[].log_service` | 문자열 | 선택 | 로그 `fields.log.service` 필드의 값 |
| `service_map.components[].span_service` | 문자열 | 선택 | 스팬 `fields.span.service` 필드의 값 |
| `service_map.components[].metric_dimensions` | 객체 | 선택 | CloudWatch 지표 차원 이름과 값 |
| `service_map.components[].repository` | 문자열 | 선택 | 그 구성 요소의 코드를 담은 `code_repositories[].name` |
| `service_map.components[].paths[]` | 문자열 배열 | 선택 | 설정과 인프라 파일 위치 힌트. `<저장소 이름>/<저장소 루트 기준 경로>`이고 glob을 받음 |
| `service_map.components[].description` | 문자열 | 선택 | 모델에 전달하는 한 줄 설명 |
| `service_map.latency_slo[]` | 배열 | 필수 | 요청 경로별 지연 기준 |
| `service_map.latency_slo[].trace_group` | 문자열 | 필수 | 스팬 `fields.span.trace_group` 필드의 값 |
| `service_map.latency_slo[].p95_seconds` | 숫자 | 필수 | 1분 p95 기준 |

`repository`와 `paths[]`의 저장소 이름은 `code_repositories[].name` 중 하나여야 한다.

<details>
<summary><b>서비스 지도 예시(마냑 운영 환경)</b></summary>

<br>

지표 차원은 운영 계정에서 확인한 값이고 파일 위치는 각 저장소의 운영 반영 브랜치에서 확인한 경로다. 지연 기준은 운영 진입 스팬 p95 기준선의 약 1.5배이고 기준선이 1초보다 짧은 요청은 1~2초를 둔다.

```yaml
service_map:
  components:
    - name: manyak-server
      kind: service
      log_service: manyak-server
      span_service: manyak-server
      metric_dimensions: { ClusterName: manyak-prod, ServiceName: manyak-prod }
      repository: manyak-server
      paths:
        - manyak-server/src/main/resources/application*.yml
        - manyak-terraform/terraform/envs/prod/ecs.tf
        - manyak-terraform/terraform/envs/prod/prod.auto.tfvars
    - name: manyak-server 채팅 턴 실행기
      kind: executor
      parent: manyak-server
      repository: manyak-server
      paths:
        - manyak-server/src/main/kotlin/com/knk/manyak/chat/config/ChatSseConfig.kt
        - manyak-server/src/main/resources/application.yml
      description: 채팅 턴을 태스크당 정해진 수까지 동시에 실행하고 나머지는 큐에서 기다림. 대기 시간은 chat.turn.queue 스팬
    - name: manyak-server 오토스케일링
      kind: autoscaling
      parent: manyak-server
      paths: [manyak-terraform/terraform/envs/prod/autoscaling.tf]
    - name: manyak-ai
      kind: service
      log_service: manyak-ai
      span_service: manyak-ai
      metric_dimensions: { ClusterName: manyak-prod, ServiceName: manyak-prod-ai }
      repository: manyak-ai
      paths:
        - manyak-ai/src/core/config.py
        - manyak-terraform/terraform/envs/prod/ai.tf
    - name: manyak-ai 오토스케일링
      kind: autoscaling
      parent: manyak-ai
      paths: [manyak-terraform/terraform/envs/prod/autoscaling.tf]
    - name: manyak-notification
      kind: service
      log_service: manyak-notification
      span_service: manyak-notification
      metric_dimensions: { ClusterName: manyak-prod, ServiceName: manyak-prod-notification }
      repository: manyak-notification
      paths:
        - manyak-notification/src/main/resources/application.yml
        - manyak-terraform/terraform/envs/prod/notification.tf
    - name: manyak-notification 오토스케일링
      kind: autoscaling
      parent: manyak-notification
      paths: [manyak-terraform/terraform/envs/prod/autoscaling.tf]
    - name: manyak-postgres
      kind: database
      metric_dimensions: { DBInstanceIdentifier: manyak-prod-pg }
      paths:
        - manyak-terraform/terraform/envs/prod/main.tf
        - manyak-terraform/terraform/modules/data/main.tf
    - name: manyak-redis
      kind: cache
      metric_dimensions: { CacheClusterId: manyak-prod-redis }
      paths: [manyak-terraform/terraform/modules/data/main.tf]
      description: 주 노드 manyak-prod-redis, 복제 노드 manyak-prod-redis-rg-001
    - name: manyak-alb
      kind: load_balancer
      metric_dimensions: { LoadBalancer: app/manyak-prod-alb/6bff84d38528448d }
      paths: [manyak-terraform/terraform/modules/edge/main.tf]
  latency_slo:
    - { trace_group: "http post /api/v1/chats/{chatId}/turns/stream", p95_seconds: 45 }
    - { trace_group: "http post /api/v1/chats/{chatId}/turns/{turnId}/choices", p95_seconds: 5 }
    - { trace_group: "http post /api/v1/chats", p95_seconds: 2 }
    - { trace_group: "http get /api/v1/stories", p95_seconds: 1 }
```

</details>

<br>

### 5-5 이상 후보

| 필드 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `candidate_id` | 문자열 | 필수 | `c-` 뒤에 연 시각을 `yyyyMMddHHmm`으로 붙임 |
| `opened_at` | 시각 | 필수 | 연 시각 |
| `first_signal_at` | 시각 | 필수 | 가장 이른 신호의 첫 시각 |
| `closed_at` | 시각 | 선택 | 닫은 시각. 열려 있으면 `null` |
| `signals[]` | 배열 | 필수 | 1개 이상 |
| `signals[].type` | 문자열 | 필수 | `entry_latency`, `queue_latency`, `failure_rate`, `error_logs`, `resource_saturation` |
| `signals[].target` | 문자열 | 필수 | 진입 스팬 이름, 대기 스팬 이름, 서비스 이름 중 신호 종류에 맞는 것<br>자원 포화는 `구성 요소 이름/지표 이름`<br>신호 종류와 대상이 확정 판정의 키 |
| `signals[].first_at` | 시각 | 필수 | 조건을 처음 넘은 분 |
| `signals[].peak_value` | 숫자 | 필수 | 붙은 동안의 최댓값 |
| `signals[].threshold` | 숫자 | 필수 | 기준값 |
| `signals[].unit` | 문자열 | 필수 | `seconds`, `ratio`, `count`, `percent` |
| `skip_reason` | 문자열 | 선택 | 진단을 부르지 않은 이유. `daily_budget_exceeded`. 진단했으면 `null` |

<br>

### 5-6 운영자 요청

| 필드 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `mention_id` | 문자열 | 필수 | `m-` 뒤에 요청 시각을 `yyyyMMddHHmmss`로 붙임 |
| `text` | 문자열 | 필수 | 멘션 표기를 뺀 메시지 원문 |
| `requested_at` | 시각 | 필수 | 멘션 메시지의 슬랙 시각 |
| `channel` | 문자열 | 필수 | 슬랙 채널 ID |
| `thread_ts` | 문자열 | 필수 | 보고를 올릴 스레드의 키. 멘션 메시지가 스레드 안에 있으면 그 스레드의 첫 메시지 타임스탬프이며 그렇지 않으면 멘션 메시지의 타임스탬프 |
| `skip_reason` | 문자열 | 선택 | 진단을 부르지 않은 이유. `daily_budget_exceeded`. 진단했으면 `null` |


<br>

### 5-7 진단 보고

문장으로 쓰는 필드의 수치 단위와 시각 표기는 6-1-4의 보고 규칙을 따른다.

| 필드 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `diagnosis_id` | 문자열 | 필수 | 진단 요청의 ID. 이상 후보는 `candidate_id`이고 운영자 요청은 `mention_id` |
| `diagnosed_at` | 시각 | 필수 | 진단을 끝낸 실제 시각 |
| `verdict` | 문자열 | 필수 | `incident`, `not_incident`, `undetermined` |
| `headline` | 객체 | 필수 | 슬랙 보고 메시지의 짧은 칸. 5-9 |
| `headline.impact` | 문자열 | 조건부 | 영향 칸. 영향받은 경로와 수치와 기준. `incident`일 때 필수이며 그렇지 않으면 `null` |
| `headline.cause` | 문자열 | 조건부 | 원인 칸. 원인을 요약한 명사구. `incident`일 때와 의심 구성 요소가 있는 `undetermined`일 때 필수이며 그렇지 않으면 `null` |
| `headline.scope` | 문자열 | 조건부 | 확인한 범위 칸. 확인한 요청 경로와 구간. `not_incident`와 `undetermined`일 때 필수이며 그렇지 않으면 `null` |
| `headline.figures` | 문자열 | 조건부 | 주요 수치 칸. 판정을 뒷받침하는 수치와 기준. `not_incident`와 `undetermined`일 때 필수이며 그렇지 않으면 `null` |
| `impact` | 객체 | 조건부 | `incident`일 때 필수이며 그렇지 않으면 `null` |
| `impact.trace_groups[]` | 배열 | 필수 | 영향받은 진입 스팬 이름 |
| `impact.summary` | 문자열 | 필수 | 수치가 든 한 문장 |
| `first_anomaly_at` | 시각 | 조건부 | `incident`일 때 필수이며 그렇지 않으면 `null` |
| `suspects[]` | 배열 | 조건부 | `incident`일 때 1~3개. `undetermined`는 0~3개. `not_incident`는 빈 배열 |
| `suspects[].component` | 문자열 | 필수 | 서비스 지도의 `components[].name` |
| `suspects[].hypothesis` | 문자열 | 필수 | 원인 가설 한 문장 |
| `ruled_out[]` | 문자열 배열 | 필수 | 조회로 정상임을 확인해 원인에서 뺀 것. 항목마다 짧은 이름. 0개 이상 |
| `evidence[]` | 배열 | 조건부 | `incident`와 `not_incident`는 1개 이상. 근거 하나에 `query_ref`와 `code_ref` 중 하나만 둠. 원인 가설을 직접 받치는 근거가 앞 |
| `evidence[].observation` | 문자열 | 필수 | 관찰 한 문장 |
| `evidence[].query_ref` | 정수 | 조건부 | 조회 근거의 조회 기록 번호. 코드 근거면 `null` |
| `evidence[].value` | 숫자 | 조건부 | 조회 근거에서 조회 결과에 있는 값. 코드 근거면 `null` |
| `evidence[].code_ref` | 객체 | 조건부 | 코드 근거의 위치. 조회 근거면 `null` |
| `evidence[].code_ref.repo` | 문자열 | 필수 | `code_repositories[].name` 중 하나 |
| `evidence[].code_ref.path` | 문자열 | 필수 | 저장소 루트 기준 파일 경로. 코드, application 설정, terraform 파일 모두 됨 |
| `evidence[].code_ref.start_line` | 정수 | 필수 | 인용 범위의 첫 줄. 1부터 셈 |
| `evidence[].code_ref.end_line` | 정수 | 필수 | 인용 범위의 끝 줄. `start_line` 이상 |
| `evidence[].code_ref.quote` | 문자열 | 필수 | 범위 안에 그대로 있는 문장 |
| `evidence[].verified` | 불리언 | 필수 | 보고 검사기가 채움 |
| `actions` | 객체 | 조건부 | `incident`일 때 필수이며 그렇지 않으면 `null` |
| `actions.immediate[]` | 배열 | 필수 | 즉시 완화. 1개 이상. 첫 항목이 1순위 |
| `actions.improvement[]` | 배열 | 필수 | 개선 방향. 1개 이상. 첫 항목이 1순위 |
| `usage` | 객체 | 필수 | 진단 실행기가 채움 |
| `usage.model` | 문자열 | 필수 | 모델 식별자 |
| `usage.queries` | 정수 | 필수 | 조회 횟수 |
| `usage.input_tokens` | 정수 | 필수 | |
| `usage.output_tokens` | 정수 | 필수 | |
| `usage.cost_usd` | 숫자 | 필수 | |
| `usage.elapsed_seconds` | 숫자 | 필수 | |

글자 상한은 `headline`의 칸과 `ruled_out[]`을 `, `로 이은 글이 40자, `actions`의 항목이 60자, `suspects[].hypothesis`가 120자, `evidence[].observation`이 80자다. 글자 수는 유니코드 문자 단위로 센다. 상한은 제출 입력 스키마에 두지 않고 출력 간 조건으로도 검사하지 않는다. 넘은 값은 보고에 그대로 기록하고 슬랙 연결기가 메시지에서만 줄인다(5-9). 메시지의 표시 길이 때문에 진단이 실행 실패로 끝나는 것을 막기 위해서다.

<details>
<summary><b>진단 보고 예시(LLM 응답 대기 장애)</b></summary>

<br>

운영 진단 보고 하나를 이 계약의 지연 기준과 보고 규칙에 맞춰 고쳐 쓴 예시다. 문장 안의 시각은 `slack.timezone` `Asia/Seoul` 기준이다. 근거의 `value`는 조회 결과에 있는 나노초 값 그대로이고 관찰 문장은 초와 ms로 바꿔 썼다. 비용은 토큰 수에 `claude-sonnet-5-5`의 단가를 곱한 값이다.

```json
{
  "diagnosis_id": "m-20261026101712",
  "diagnosed_at": "2026-10-26T10:18:02Z",
  "verdict": "incident",
  "headline": {
    "impact": "채팅 턴 p95 68초 (기준 45초)",
    "cause": "LLM 응답 대기(gemini)",
    "scope": null,
    "figures": null
  },
  "impact": {
    "trace_groups": ["http post /api/v1/chats/{chatId}/turns/stream"],
    "summary": "채팅 턴 스트림 p95가 18:16부터 기준 45초를 넘어 18:50 구간에 68초에 이르렀고 다른 경로는 기준 안이며 실패는 없다."
  },
  "first_anomaly_at": "2026-10-26T09:16:00Z",
  "suspects": [
    {
      "component": "manyak-ai",
      "hypothesis": "턴 스트림 시간 대부분을 manyak-ai의 llm.stream 스팬이 외부 LLM 제공자의 스트리밍 응답을 기다리는 데 써서 서버 자원이나 큐와 무관하게 기준을 넘는다."
    }
  ],
  "ruled_out": ["큐 대기", "CPU", "오류"],
  "evidence": [
    { "observation": "manyak-ai POST /api/v1/chat/turns 평균 34.0초로 서버 스트림 평균과 거의 같음", "query_ref": 5, "value": 34008976481.90625, "code_ref": null, "verified": true },
    { "observation": "manyak-ai llm.stream 스팬 평균 21.4초", "query_ref": 5, "value": 21417135902.28125, "code_ref": null, "verified": true },
    { "observation": "chat.turn.queue 스팬 평균 2.4ms로 실행기 대기는 원인이 아님", "query_ref": 3, "value": 2353175.785714286, "code_ref": null, "verified": true },
    { "observation": "채팅 턴 스트림 p95가 18:50 구간에 68.3초", "query_ref": 1, "value": 68348337740, "code_ref": null, "verified": true },
    { "observation": "스토리 목록 p95는 최대 63ms로 기준 1초 안", "query_ref": 1, "value": 62659445, "code_ref": null, "verified": true },
    { "observation": "채팅 턴 실행기 활성 스레드 최댓값 1로 동시 실행 상한에 닿지 않음", "query_ref": 6, "value": 1, "code_ref": null, "verified": true },
    { "observation": "manyak-server CPU 최댓값 12.9%", "query_ref": 7, "value": 12.895404487848284, "code_ref": null, "verified": true }
  ],
  "actions": {
    "immediate": ["LLM 제공자 상태와 gemini 지연 확인", "지연이 큰 모델을 쓰는 채팅은 빠른 모델로 일시 전환"],
    "improvement": ["llm.stream 모델별 p95 경보", "llm.stream 종료 뒤 요청 종료까지 구간에 스팬 추가", "제공자 지연 때 대체 모델로 넘기는 정책 검토"]
  },
  "usage": {
    "model": "claude-sonnet-5-5",
    "queries": 7,
    "input_tokens": 271422,
    "output_tokens": 4610,
    "cost_usd": 0.222,
    "elapsed_seconds": 49.0
  }
}
```

</details>

<br>

### 5-8 실행 폴더

실행마다 폴더 하나를 만든다. 폴더는 실행 인자로 받은 상위 경로 아래에 두고 이름은 시작 시각이다. 상위 경로는 1단계면 운영자 PC의 폴더이고 2단계면 태스크의 임시 저장소다.

| 파일 | 내용 | 쓰는 때 |
|---|---|---|
| `run.json` | 실행 단계, 설정 위치와 해시, 적용한 설정값 전체와 덮어쓴 환경 변수 이름, 코드 사본의 저장소별 커밋, MCP 서버 패키지 버전, 프롬프트 해시 | 시작 때 |
| `candidates.jsonl` | 이상 후보의 상태 한 건에 한 줄. 같은 ID는 마지막 줄이 최신 상태 | 열 때, 진단을 생략할 때, 신호가 붙거나 최댓값이 바뀔 때, 닫을 때, 열린 채 실행이 끝날 때 덧붙임 |
| `mentions.jsonl` | 운영자 요청 한 건에 한 줄 | 멘션을 받을 때 |
| `reports/<diagnosis_id>.json` | 진단 보고 | 진단이 끝날 때 |
| `queries/<diagnosis_id>.jsonl` | 모델 메시지와 조회 한 건에 한 줄. 조회는 번호, 도구, 인자, 결과 | 메시지와 조회마다 |
| `failures.jsonl` | 실행 실패 한 건에 한 줄 | 실행 실패 때 |
| `sessions.jsonl` | 세션과 스레드의 짝 한 건에 한 줄. 같은 세션은 마지막 줄이 최신 상태 | 보고를 올릴 때, 비용이 갱신될 때, 세션을 끝낼 때 덧붙임 |

실행 실패한 진단 요청은 `reports/`에 파일이 없고 `failures.jsonl`에 줄이 있다. 진단을 부르지 않은 진단 요청은 `reports/`와 `failures.jsonl` 어디에도 없고 `candidates.jsonl`이나 `mentions.jsonl`의 `skip_reason`이 채워져 있다.

**`failures.jsonl`**

| 필드 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `diagnosis_id` | 문자열 | 필수 | 진단 요청의 ID |
| `failed_at` | 시각 | 필수 | 실패한 실제 시각 |
| `stage` | 문자열 | 필수 | `query`(MCP 서버 연결 실패), `model`(모델 호출 실패), `report`(출력 간 조건을 두 번 어김, 제출 입력 스키마 위반, 같은 요청의 보고가 이미 있음), `budget`(제출 요청 뒤에도 미제출, 5분 소진, 진단 턴 비용 한도 도달), `notify`(슬랙 게시 실패), `session`(세션 복원 실패, 세션 비용 초과, 대화 턴 모델 호출 실패) |
| `reason` | 문자열 | 필수 | 실패 원인 한 문장. 비밀값과 식별자를 넣지 않음 |
| `usage` | 객체 | 필수 | 진단 보고의 `usage`와 같은 필드. `notify`와 `session`은 그 시점까지의 세션 누적값 |

**`sessions.jsonl`**

| 필드 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `diagnosis_id` | 문자열 | 필수 | 진단 요청의 ID |
| `session_id` | 문자열 | 필수 | Agent SDK가 준 세션 ID |
| `channel` | 문자열 | 필수 | 슬랙 채널 ID |
| `thread_ts` | 문자열 | 필수 | 스레드의 키. 이상 후보는 알림 메시지의 타임스탬프이며 운영자 요청은 그 요청의 `thread_ts` |
| `opened_at` | 시각 | 필수 | 보고를 올린 실제 시각 |
| `closed_at` | 시각 | 선택 | 세션을 끝낸 실제 시각. 열려 있으면 `null` |
| `cost_usd` | 숫자 | 필수 | 세션 누적 비용 |

<br>

### 5-9 슬랙 메시지

채널은 설정의 `slack.channel` 하나다. 메시지에는 집계값, 구성 요소 이름, 파일 위치만 들어가고 식별자는 들어가지 않는다. 보고 파일 이름인 `diagnosis_id`도 올리지 않는다. 보고 파일은 실행 폴더에서 찾는다.

코드가 메시지에 넣는 시각은 `slack.timezone` 시간대로 바꿔 `HH:MM`만 보인다. 모델이 작성한 글의 시각은 모델이 같은 시간대의 `HH:MM`으로 쓰고(6-1-4) 코드는 바꾸지 않는다. 금액은 달러를 소수 둘째 자리로 반올림해 `$0.11`처럼 쓴다.

**1. 보고 메시지**

진단 보고 하나에 보고 메시지 하나를 올린다. 이상 후보의 보고는 채널에 새 메시지로 올리고 그 메시지 아래가 세션의 스레드가 된다. 운영자 요청의 보고는 그 요청의 `thread_ts` 스레드에 답글로 올린다.

보고 메시지는 아래 Block Kit 블록을 위에서부터 차례로 쓴다. 알림 미리보기에 보이는 대체 텍스트 `text`에는 머리 줄을 넣는다. 판정에 따라 보이는 블록과 칸이 다르고 보이지 않는 것은 뺀다.

| 순서 | 블록 | 내용 | 보이는 조건 |
|---|---|---|---|
| 1 | `header` | 머리 줄. 아래 판정 표의 머리 표시. `suspects[0].component`가 있으면 `<머리 표시> · <component>`로 붙임 | 모두 |
| 2 | `section`의 `fields` | 판정 표의 칸을 차례로 하나씩 넣음. 칸마다 mrkdwn `*<칸 이름>:* <값>`이고 두 칸씩 한 줄로 보임 | 모두 |
| 3 | `section`의 `text` | mrkdwn 한 줄 `*원인 가설:* <suspects[0].hypothesis>` | `suspects`가 있을 때 |
| 4 | `section`의 `text` | mrkdwn 첫 줄 `*주요 근거*` 아래에 근거 한 줄씩 `• <observation>`. 보고의 근거 순서대로 앞에서 3개까지 넣음<br>`verified`가 거짓인 근거는 관찰 앞에 `⚠ `를 붙여 `• ⚠ <observation>`으로 씀<br>`code_ref`가 있는 근거는 관찰 뒤에 파일 위치를 붙여 `` • <observation> (`<파일 이름>:<start_line>`) ``으로 씀. 파일 이름은 `code_ref.path`의 마지막 부분 | `evidence`가 있을 때 |
| 5 | `section`의 `text` | mrkdwn 두 줄 `*지금 할 일:* <actions.immediate[0]>`과 `*개선 방향:* <actions.improvement[0]>` | `incident` |
| 6 | `context` | mrkdwn 한 줄 `<근거 요약> · 조회 <usage.queries>회 · <usage.elapsed_seconds>초 · $<usage.cost_usd>`. 경과 시간은 반올림한 정수 초 | 모두 |

| `verdict` | 머리 표시 | 칸과 순서 |
|---|---|---|
| `incident` | `🔴 장애` | 영향, 원인, 첫 이상, 배제한 원인 |
| `not_incident` | `🟢 이상 없음` | 확인한 범위, 주요 수치, 배제한 원인 |
| `undetermined` | `🟡 판단 불가` | 확인한 범위, 주요 수치, 원인, 배제한 원인 |

| 칸 | 값의 출처 |
|---|---|
| 영향 | `headline.impact` |
| 원인 | `headline.cause`. `undetermined`는 값이 있을 때만 보임 |
| 첫 이상 | `first_anomaly_at`을 `slack.timezone`으로 바꾼 `HH:MM` |
| 배제한 원인 | `ruled_out[]`을 `, `로 이은 글. 비어 있으면 칸을 뺌 |
| 확인한 범위 | `headline.scope` |
| 주요 수치 | `headline.figures` |

| 근거 | 근거 요약 |
|---|---|
| 모든 근거의 `verified`가 참 | `근거 <근거 수>개 중 <근거 수>개 검증` |
| `verified`가 거짓인 근거가 있음 | `⚠ 근거 <근거 수>개 중 <거짓인 근거 수>개 검증 실패` |
| 근거 없음 | 근거 요약과 뒤의 ` · `를 빼고 줄이 `조회`로 시작함 |

칸, 원인 가설, 근거의 관찰, 할 일 줄의 값이 5-7의 글자 상한을 넘으면 상한보다 한 자 적게 남기고 끝에 `…`를 붙인다. 근거 줄은 관찰만 줄이고 `⚠ `와 파일 위치는 줄이지 않는다. 보고 파일의 값은 그대로 둔다. `impact.summary`, 두 번째부터의 원인 가설, 네 번째부터의 근거, 두 번째부터의 조치는 메시지에 넣지 않는다. 운영자가 스레드에서 자세히 물으면 대화 턴이 보고 요약으로 풀어 답한다. ([6-1-7 대화 턴](6-1-AI-EXECUTION.md#6-1-7-대화-턴))

<details>
<summary><b>보고 메시지 예시</b></summary>

<br>

장애 예시는 5-7 예시 보고를 `slack.timezone` `Asia/Seoul`로 올린 메시지다.

```json
{
  "text": "🔴 장애 · manyak-ai",
  "blocks": [
    { "type": "header", "text": { "type": "plain_text", "text": "🔴 장애 · manyak-ai" } },
    {
      "type": "section",
      "fields": [
        { "type": "mrkdwn", "text": "*영향:* 채팅 턴 p95 68초 (기준 45초)" },
        { "type": "mrkdwn", "text": "*원인:* LLM 응답 대기(gemini)" },
        { "type": "mrkdwn", "text": "*첫 이상:* 18:16" },
        { "type": "mrkdwn", "text": "*배제한 원인:* 큐 대기, CPU, 오류" }
      ]
    },
    { "type": "section", "text": { "type": "mrkdwn", "text": "*원인 가설:* 턴 스트림 시간 대부분을 manyak-ai의 llm.stream 스팬이 외부 LLM 제공자의 스트리밍 응답을 기다리는 데 써서 서버 자원이나 큐와 무관하게 기준을 넘는다." } },
    { "type": "section", "text": { "type": "mrkdwn", "text": "*주요 근거*\n• manyak-ai POST /api/v1/chat/turns 평균 34.0초로 서버 스트림 평균과 거의 같음\n• manyak-ai llm.stream 스팬 평균 21.4초\n• chat.turn.queue 스팬 평균 2.4ms로 실행기 대기는 원인이 아님" } },
    { "type": "section", "text": { "type": "mrkdwn", "text": "*지금 할 일:* LLM 제공자 상태와 gemini 지연 확인\n*개선 방향:* llm.stream 모델별 p95 경보" } },
    { "type": "context", "elements": [{ "type": "mrkdwn", "text": "근거 7개 중 7개 검증 · 조회 7회 · 49초 · $0.22" }] }
  ]
}
```

슬랙에서는 아래처럼 보인다.

```text
🔴 장애 · manyak-ai
영향: 채팅 턴 p95 68초 (기준 45초)     원인: LLM 응답 대기(gemini)
첫 이상: 18:16                        배제한 원인: 큐 대기, CPU, 오류
원인 가설: 턴 스트림 시간 대부분을 manyak-ai의 llm.stream 스팬이 외부 LLM 제공자의 스트리밍 응답을 기다리는 데 써서 서버 자원이나 큐와 무관하게 기준을 넘는다.
주요 근거
• manyak-ai POST /api/v1/chat/turns 평균 34.0초로 서버 스트림 평균과 거의 같음
• manyak-ai llm.stream 스팬 평균 21.4초
• chat.turn.queue 스팬 평균 2.4ms로 실행기 대기는 원인이 아님
지금 할 일: LLM 제공자 상태와 gemini 지연 확인
개선 방향: llm.stream 모델별 p95 경보
근거 7개 중 7개 검증 · 조회 7회 · 49초 · $0.22
```

장애 아님 예시는 근거 4개 가운데 둘째의 `verified`가 거짓이고 셋째가 코드 근거인 합성 예시다. 의심 구성 요소와 조치가 없어 원인 가설과 조치 블록이 빠진다. 블록 형식은 장애 예시와 같으므로 주요 근거 블록과 표시 결과만 적는다.

```json
{ "type": "section", "text": { "type": "mrkdwn", "text": "*주요 근거*\n• 채팅 턴 스트림 p95 최대 31.2초로 기준 45초 안\n• ⚠ manyak-server CPU 최댓값 41%로 여유 있음\n• 채팅 스트림 실행기 동시 실행 상한은 64 (`application.yml:111`)" } }
```

```text
🟢 이상 없음
확인한 범위: 18:00~19:00 채팅 턴, 스토리 목록     주요 수치: 채팅 턴 p95 31초 (기준 45초)
배제한 원인: 큐 대기, CPU
주요 근거
• 채팅 턴 스트림 p95 최대 31.2초로 기준 45초 안
• ⚠ manyak-server CPU 최댓값 41%로 여유 있음
• 채팅 스트림 실행기 동시 실행 상한은 64 (application.yml:111)
⚠ 근거 4개 중 1개 검증 실패 · 조회 4회 · 38초 · $0.05
```

판단 불가 예시는 의심 구성 요소, 근거, 배제한 원인이 없는 합성 예시다. 칸 둘과 `context`만 남는다.

```text
🟡 판단 불가
확인한 범위: 18:10~18:40 전체 진입 스팬     주요 수치: 18:22 이후 스팬 0건
조회 3회 · 31초 · $0.04
```

</details>

실행 실패는 보고 메시지 대신 실패 단계와 사유를 `❌ 실행 실패 · <stage> · <reason>` 한 줄로 올린다. 이상 후보의 실패는 채널에 올리고 운영자 요청의 실패는 그 스레드에 올린다. 하루 비용 상한을 넘어 이상 후보의 진단을 그날 처음 생략할 때는 상한 금액과 진단을 다시 시작하는 시각을 `⏸ 진단 생략 · 하루 비용 상한 $<limits.daily_usd> · <HH:MM>에 다시 시작` 한 줄로 채널에 올린다. 다시 시작하는 시각은 다음 UTC 0시이고 `slack.timezone`이 `Asia/Seoul`이면 `09:00`이다. 같은 날 다음 생략에는 올리지 않는다. 운영자 요청을 하루 상한 때문에 생략하면 같은 내용을 그 스레드에 매번 올린다. 이 한 줄 안내와 2의 메시지는 블록 없이 mrkdwn 글로 올린다.

**2. 멘션과 스레드 메시지**

| 방향 | 내용 |
|---|---|
| 운영자 → 에이전트 | 세션 스레드 밖에서 봇을 멘션한 사람 메시지는 운영자 요청<br>세션 스레드 안의 사람 메시지는 멘션 여부와 관계없이 대화 턴의 사용자 메시지<br>봇 자신의 메시지는 넘기지 않음 |
| 에이전트 → 운영자 | 대화 턴의 답변 글을 스레드에 올림<br>코드가 답변 끝에 비용 줄 `이번 답변 $<턴 비용> · 세션 누적 $<세션 비용>`을 붙임. 턴 비용은 그 대화 턴의 결과 메시지 사용량으로 계산한 비용이고 세션 비용은 그 턴을 더해 `sessions.jsonl`에 쓴 `cost_usd` |
| 코드 → 운영자 | 세션 종료(수명 경과나 비용 초과)와 대화 턴 실패를 한 줄로 올림. 비용 초과와 대화 턴 실패는 실행 실패 `session`이라 1의 실행 실패 형식을 씀 |

**3. 반응**

운영자 요청의 멘션 메시지에만 반응을 달아 진행 상태를 보인다. 이상 후보의 보고에는 사람 메시지가 없고 세션 스레드 안의 대화 턴 메시지에는 답변이 바로 오므로 반응을 달지 않는다. 반응은 보조 표시이므로 추가나 삭제에 실패해도 진단과 보고를 계속한다.

| 때 | 반응 |
|---|---|
| 멘션을 받아 `mentions.jsonl`에 씀 | `eyes`를 닮 |
| 그 요청의 보고를 스레드에 올림 | `eyes`를 지우고 `white_check_mark`를 닮 |
| 그 요청이 실행 실패로 끝나거나 진단을 생략함 | `eyes`를 지우고 `x`를 닮 |
