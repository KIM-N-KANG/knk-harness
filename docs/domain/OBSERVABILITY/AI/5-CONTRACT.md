# 5. 계약

이 문서는 에이전트가 읽는 자료 원천, 시스템 설명서, 이상 후보와 진단 보고의 필드, 실행 폴더의 파일을 정한다.

필드의 의미는 3 태스크 정의에 있다. ([3-3 이상 후보](3-TASK-DEFINITION.md#3-3-이상-후보), [3-4 진단](3-TASK-DEFINITION.md#3-4-진단))

시각은 모두 ISO 8601에 시간대 오프셋을 붙여 쓴다. 자료 원천의 시각은 UTC로 저장돼 있고 보고에는 그대로 옮긴다.

<br>

### 5-1 연동 대상과 방식

| 대상 | 방향 | 방식 | 권한 |
|---|---|---|---|
| OpenSearch | 읽기 | 검색 API에 집계 질의 | 재생: 재생용 OpenSearch 관리자 계정<br>실시간: loadtest OpenSearch 읽기 계정 |
| CloudWatch 지표 | 읽기 | 재생: 보관 파일<br>실시간: 지표 조회 API | 지표 읽기 |
| Application Auto Scaling, CloudWatch 경보 | 읽기 | 재생: 보관 파일<br>실시간: 확장 활동과 경보 이력 조회 API | 이력 읽기 |
| 모델 API | 호출 | 도구 사용을 지원하는 대화 API | API 키 |
| 운영자 | 출력 | 실행 폴더의 파일 | 파일 쓰기 |

<br>

### 5-2 자료 원천

**1. 로그 인덱스**

인덱스 이름은 `manyak-logs-<환경>-<yyyy.MM.dd>`다. 재생용 OpenSearch에는 보관한 `manyak-logs-loadtest-*` 인덱스를 같은 이름으로 적재한다.

| 필드 | 타입 | 쓰임 |
|---|---|---|
| `@timestamp` | 시각 | 분 묶음 |
| `service` | 문자열 | 서비스별 묶음. `manyak-server`, `manyak-ai`, `manyak-notification` |
| `level` | 문자열 | 오류 로그 신호. `ERROR`, `WARN`, `INFO` |
| `event_name` | 문자열 | 사건 이름별 묶음 |
| `endpoint` | 문자열 | 요청 경로별 묶음 |
| `http_method` | 문자열 | 요청 경로와 함께 묶음 |
| `status_code` | 정수 | 상태 코드별 묶음 |
| `duration_ms` | 정수 | 요청 처리 시간 집계 |
| `error_code` | 문자열 | 오류 코드별 묶음 |
| `message` | 문자열 | 표본 메시지 |
| `traceId` | 문자열 | 스팬 인덱스와 연결 |

`device_id_hash`, `session_id`, `request_id`는 조회 결과에서 뺀다.

<br>

**2. 스팬 인덱스**

인덱스 이름은 `otel-v1-apm-span-*`다.

| 필드 | 타입 | 쓰임 |
|---|---|---|
| `startTime` | 시각 | 분 묶음 |
| `serviceName` | 문자열 | 서비스별 묶음. `manyak-server-loadtest`, `manyak-ai` |
| `name` | 문자열 | 스팬 이름별 묶음 |
| `traceGroup` | 문자열 | 진입 스팬 이름. 요청 경로별 묶음 |
| `parentSpanId` | 문자열 | 비어 있으면 진입 스팬 |
| `durationInNanos` | 정수 | 지연 집계 |
| `status.code` | 정수 | 2이면 오류 |
| `span.attributes.jdbc@query[0]` | 문자열 | DB 쿼리문별 묶음 |
| `traceId` | 문자열 | 로그 인덱스와 연결 |

<br>

**3. 지표**

| 네임스페이스 | 지표 | 차원 | 통계 |
|---|---|---|---|
| `AWS/ECS` | `CPUUtilization`, `MemoryUtilization` | `ClusterName`, `ServiceName` | Average, Maximum |
| `AWS/RDS` | `CPUUtilization`, `DatabaseConnections`, `FreeableMemory`, `ReadLatency`, `WriteLatency`, `DiskQueueDepth` | `DBInstanceIdentifier` | Maximum |
| `AWS/ElastiCache` | `EngineCPUUtilization`, `CurrConnections` | `CacheClusterId` | Maximum |
| `AWS/ApplicationELB` | `RequestCount`, `HTTPCode_Target_5XX_Count`, `HTTPCode_ELB_5XX_Count` | `LoadBalancer` | Sum |
| `AWS/ApplicationELB` | `TargetResponseTime` | `LoadBalancer` | p95 |

주기는 1분이다. 재생 모드의 보관 파일은 지표 하나가 `label`, `timestamps`, `values`를 가진 객체이고 `label`은 `네임스페이스|지표|차원값|통계`다.

<br>

**4. 확장과 경보 이력**

| 자료 | 필드 | 쓰임 |
|---|---|---|
| 확장 활동 | `StartTime`, `Description`, `Cause`, `StatusCode` | 태스크 수 변경 시각과 이유 |
| 경보 이력 | `AlarmName`, `Timestamp`, `HistorySummary`, `HistoryData` | 경보 상태 변화와 변화 시점의 최근 값 |

<br>

### 5-3 시스템 설명서

운영자가 관리하는 YAML 파일이다. 에이전트는 시작할 때 한 번 읽는다.

| 필드 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `components[]` | 배열 | 필수 | 구성 요소 목록 |
| `components[].name` | 문자열 | 필수 | 보고에서 지목하는 이름 |
| `components[].kind` | 문자열 | 필수 | `service`, `executor`, `database`, `cache`, `load_balancer`, `autoscaling` |
| `components[].parent` | 문자열 | 선택 | 실행기와 오토스케일링이 속한 서비스의 `name` |
| `components[].log_service` | 문자열 | 선택 | 로그 `service` 값 |
| `components[].span_service` | 문자열 | 선택 | 스팬 `serviceName` 값 |
| `components[].metric_dimensions` | 객체 | 선택 | 지표 차원 이름과 값 |
| `components[].capacity` | 객체 | 선택 | `tasks`, `cpu`, `memory_mb`, `concurrency`, `queue_capacity` 중 해당하는 값 |
| `components[].scaling` | 객체 | 선택 | 오토스케일링에만. `metric`, `target_percent`, `min_tasks`, `max_tasks`, `evaluation_minutes` |
| `components[].description` | 문자열 | 선택 | 모델에 전달하는 한 줄 설명 |
| `latency_slo[]` | 배열 | 필수 | 요청 경로별 지연 기준 |
| `latency_slo[].trace_group` | 문자열 | 필수 | 스팬 `traceGroup` 값 |
| `latency_slo[].p95_seconds` | 숫자 | 필수 | 1분 p95 기준 |

<details>
<summary><b>시스템 설명서 예시(loadtest 환경)</b></summary>

<br>

```yaml
components:
  - name: manyak-server
    kind: service
    log_service: manyak-server
    span_service: manyak-server-loadtest
    metric_dimensions: { ClusterName: manyak-loadtest, ServiceName: manyak-loadtest }
    capacity: { tasks: 2, cpu: 1.0, memory_mb: 2048 }
  - name: manyak-server 채팅 턴 실행기
    kind: executor
    parent: manyak-server
    capacity: { concurrency: 4, queue_capacity: 100 }
    description: 채팅 턴을 태스크당 concurrency개까지 동시에 실행하고 나머지는 큐에서 기다림. 대기 시간은 chat.turn.queue 스팬
  - name: manyak-server 오토스케일링
    kind: autoscaling
    parent: manyak-server
    scaling: { metric: CPUUtilization, target_percent: 70, min_tasks: 2, max_tasks: 4, evaluation_minutes: 3 }
  - name: manyak-ai
    kind: service
    log_service: manyak-ai
    span_service: manyak-ai
    metric_dimensions: { ClusterName: manyak-loadtest, ServiceName: manyak-loadtest-ai }
    capacity: { tasks: 2, cpu: 0.5, memory_mb: 1024 }
  - name: manyak-ai 오토스케일링
    kind: autoscaling
    parent: manyak-ai
    scaling: { metric: CPUUtilization, target_percent: 70, min_tasks: 2, max_tasks: 4, evaluation_minutes: 3 }
  - name: manyak-postgres
    kind: database
    metric_dimensions: { DBInstanceIdentifier: manyak-loadtest-pg }
  - name: manyak-redis
    kind: cache
    metric_dimensions: { CacheClusterId: manyak-loadtest-redis-rg-001 }
  - name: manyak-alb
    kind: load_balancer
    metric_dimensions: { LoadBalancer: app/manyak-loadtest-alb/f219f41263495cd0 }
latency_slo:
  - { trace_group: "http post /api/v1/chats/{chatId}/turns/stream", p95_seconds: 15 }
  - { trace_group: "http post /api/v1/chats/{chatId}/turns/{turnId}/choices", p95_seconds: 15 }
  - { trace_group: "http post /api/v1/chats", p95_seconds: 2 }
  - { trace_group: "http get /api/v1/stories", p95_seconds: 1 }
```

</details>

<br>

### 5-4 이상 후보

| 필드 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `candidate_id` | 문자열 | 필수 | `c-` 뒤에 연 시각을 `yyyyMMddHHmm`으로 붙임 |
| `opened_at` | 시각 | 필수 | 연 감시 시각 |
| `first_signal_at` | 시각 | 필수 | 가장 이른 신호의 첫 시각 |
| `closed_at` | 시각 | 선택 | 닫은 감시 시각. 열려 있으면 `null` |
| `signals[]` | 배열 | 필수 | 1개 이상 |
| `signals[].type` | 문자열 | 필수 | `entry_latency`, `queue_latency`, `failure_rate`, `error_logs`, `resource_saturation` |
| `signals[].target` | 문자열 | 필수 | 진입 스팬 이름, 대기 스팬 이름, 서비스 이름, 구성 요소 이름 중 신호 종류에 맞는 것 |
| `signals[].first_at` | 시각 | 필수 | 조건을 처음 넘은 분 |
| `signals[].peak_value` | 숫자 | 필수 | 붙은 동안의 최댓값 |
| `signals[].threshold` | 숫자 | 필수 | 기준값 |
| `signals[].unit` | 문자열 | 필수 | `seconds`, `ratio`, `count`, `percent` |

<br>

### 5-5 진단 보고

| 필드 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `candidate_id` | 문자열 | 필수 | 이상 후보의 ID |
| `diagnosed_at` | 시각 | 필수 | 진단을 끝낸 실제 시각 |
| `verdict` | 문자열 | 필수 | `incident`, `not_incident`, `undetermined` |
| `impact` | 객체 | 조건부 | `incident`일 때 필수, 아니면 `null` |
| `impact.trace_groups[]` | 배열 | 필수 | 영향받은 진입 스팬 이름 |
| `impact.summary` | 문자열 | 필수 | 수치가 든 한두 문장 |
| `first_anomaly_at` | 시각 | 조건부 | `incident`일 때 필수, 아니면 `null` |
| `suspects[]` | 배열 | 조건부 | `incident`일 때 1~3개. `undetermined`는 0~3개. `not_incident`는 빈 배열 |
| `suspects[].component` | 문자열 | 필수 | 시스템 설명서의 `components[].name` |
| `suspects[].hypothesis` | 문자열 | 필수 | 원인 가설 |
| `evidence[]` | 배열 | 조건부 | `incident`와 `not_incident`는 1개 이상 |
| `evidence[].query_ref` | 정수 | 필수 | 조회 기록의 번호 |
| `evidence[].observation` | 문자열 | 필수 | 관찰 한 문장 |
| `evidence[].value` | 숫자 | 필수 | 조회 결과에 있는 값 |
| `evidence[].verified` | 불리언 | 필수 | 보고 검사기가 채움 |
| `actions` | 객체 | 조건부 | `incident`일 때 필수, 아니면 `null` |
| `actions.immediate[]` | 배열 | 필수 | 즉시 완화. 1개 이상 |
| `actions.improvement[]` | 배열 | 필수 | 개선 방향. 1개 이상 |
| `usage` | 객체 | 필수 | 진단 실행기가 채움 |
| `usage.model` | 문자열 | 필수 | 모델 식별자 |
| `usage.queries` | 정수 | 필수 | 조회 횟수 |
| `usage.input_tokens` | 정수 | 필수 | |
| `usage.output_tokens` | 정수 | 필수 | |
| `usage.cost_usd` | 숫자 | 필수 | |
| `usage.elapsed_seconds` | 숫자 | 필수 | |

<details>
<summary><b>진단 보고 예시(채팅 턴 큐 대기 장애)</b></summary>

<br>

보고는 합성 예시이고 수치는 KNK-1598의 측정값이다.

```json
{
  "candidate_id": "c-202610080450",
  "diagnosed_at": "2026-10-15T09:12:41+09:00",
  "verdict": "incident",
  "impact": {
    "trace_groups": ["http post /api/v1/chats/{chatId}/turns/stream"],
    "summary": "채팅 턴 스트림 p95가 04:46Z부터 16.2초로 기준 15초를 넘고 04:51Z에 48.3초에 이름. 읽기 요청은 p95 0.05초 이하로 영향 없음."
  },
  "first_anomaly_at": "2026-10-08T04:46:00Z",
  "suspects": [
    {
      "component": "manyak-server 채팅 턴 실행기",
      "hypothesis": "태스크당 동시 실행 4개가 상한이라 동시 사용자 25명부터 턴이 큐에서 대기함. CPU에 여유가 있어 자원 문제가 아니라 설정 상한 문제."
    }
  ],
  "evidence": [
    { "query_ref": 2, "observation": "chat.turn.queue 스팬 p95가 04:46Z~05:00Z 구간에서 48.6초", "value": 48.6, "verified": true },
    { "query_ref": 3, "observation": "같은 구간 manyak-ai POST /api/v1/chat/turns p95는 10.4초로 부하 전과 같음", "value": 10.4, "verified": true },
    { "query_ref": 5, "observation": "manyak-server CPU 최댓값 36%", "value": 36, "verified": true },
    { "query_ref": 6, "observation": "manyak-server 확장 활동 0건", "value": 0, "verified": true }
  ],
  "actions": {
    "immediate": ["manyak-server 태스크 수를 2에서 4로 올려 동시 실행 수를 8에서 16으로 늘림"],
    "improvement": ["채팅 턴 실행기의 동시 실행 수를 설정으로 빼고 기본값을 CPU 여유에 맞게 올림", "큐 대기 p95를 경보 조건에 추가함"]
  },
  "usage": {
    "model": "claude-opus-5-5",
    "queries": 7,
    "input_tokens": 41200,
    "output_tokens": 2310,
    "cost_usd": 0.158,
    "elapsed_seconds": 94.2
  }
}
```

</details>

<br>

### 5-6 실행 폴더

실행 하나가 폴더 하나를 만든다. 폴더 이름은 실행 모드와 시작 시각이다.

| 파일 | 내용 | 쓰는 때 |
|---|---|---|
| `run.json` | 실행 모드, 감시 구간, 시스템 설명서 경로와 해시, 모델 식별자, 프롬프트 해시 | 시작 때 |
| `candidates.jsonl` | 이상 후보 한 건에 한 줄 | 열 때 쓰고 닫을 때 `closed_at`을 채운 줄을 덧붙임 |
| `reports/<candidate_id>.json` | 진단 보고 | 진단이 끝날 때 |
| `queries/<candidate_id>.jsonl` | 모델 메시지와 조회 한 건에 한 줄. 조회는 번호, 도구, 인자, 결과 | 메시지와 조회마다 |
| `failures.jsonl` | 실행 실패 한 건에 한 줄 | 실행 실패 때 |

실행 실패한 이상 후보는 `reports/`에 파일이 없고 `failures.jsonl`에 줄이 있다.

| 필드 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `candidate_id` | 문자열 | 필수 | 이상 후보의 ID |
| `failed_at` | 시각 | 필수 | 실패한 실제 시각 |
| `stage` | 문자열 | 필수 | `query`(조회 실패), `model`(모델 호출 실패), `report`(출력 간 조건을 두 번 어김), `budget`(조회 25회나 5분 소진 후 미제출) |
| `reason` | 문자열 | 필수 | 실패 원인 한 문장. 비밀값과 식별자를 넣지 않음 |
| `usage` | 객체 | 필수 | 진단 보고의 `usage`와 같은 필드 |
