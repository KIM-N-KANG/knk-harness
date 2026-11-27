# 5. 계약

이 문서는 에이전트가 읽는 설정과 비밀값, 자료 원천, 서비스 지도, 진단 요청과 진단 보고의 필드, 실행 폴더의 파일, 슬랙 메시지를 정한다.

필드의 의미는 3 태스크 정의에 있고 모델이 호출하는 도구는 4-1 인지 구조에 있다. ([3-2 진단](3-TASK-DEFINITION.md#3-2-진단), [3-3 대화](3-TASK-DEFINITION.md#3-3-대화), [4-1-2 진단 전략](4-1-DESIGN-COGNITIVE-ARCHITECTURE.md#4-1-2-진단-전략))

시각 필드는 ISO 8601에 시간대 오프셋을 붙여 쓰고 UTC로 기록한다. 보고 문장과 슬랙 메시지 안의 시각은 설정의 시간대로 바꾼 `HH:MM`이다.

<br>

### 5-1 연동 대상과 방식

| 대상 | 방식 | 권한 |
|---|---|---|
| OpenSearch | 감시는 검색 API에 집계 질의<br>모델은 OpenSearch MCP의 검색 도구 | 에이전트용 사용자 |
| CloudWatch | 감시는 메트릭 조회 API<br>모델은 CloudWatch MCP의 메트릭과 경보 도구<br>지표 차원을 설정한 구성 요소가 있을 때만 씀 | AWS 자격 증명 |
| Prometheus | 모델만 PromQL 도구로 읽음<br>기본은 자체 도구가 HTTP API를 부름<br>AMP는 Prometheus MCP로 읽음 | 읽기 사용자의 비밀번호<br>AMP는 AWS 자격 증명 |
| Application Auto Scaling | 확장 이력 도구가 확장 활동을 조회함<br>CloudWatch와 같은 조건 | AWS 자격 증명 |
| Parameter Store와 Secrets Manager | 설정 위치나 비밀 이름으로 지정했을 때 시작 때 읽음 | AWS 자격 증명 |
| 모델 API | Claude Agent SDK의 세션 | API 키 |
| 슬랙 | 소켓 모드<br>채널에 알림을 올리고 에이전트 멘션과 스레드 메시지를 받음<br>멘션 메시지에 이모지 반응을 붙임 | 봇 토큰과 앱 토큰 |
| 코드 저장소 | 설정의 저장소를 코드 사본으로 받음 | 비공개 저장소는 토큰 |

<br>

### 5-2 설정 파일

대상 서비스와 운영 환경에 맞춰 바꾸는 값은 YAML 설정 파일로 받는다. 비밀값은 설정 파일에 두지 않는다.

| 규칙 | 내용 |
|---|---|
| 위치 | 환경 변수 `DIAG_CONFIG`<br>파일 경로이거나 `ssm:` 뒤에 Parameter Store 파라미터 이름 |
| 우선순위 | 환경 변수, 설정 파일, 코드 기본값 순 |
| 덮어쓰기 | 키 경로의 점을 밑줄로 바꾸고 대문자로 바꾼 뒤 앞에 `DIAG_`를 붙인 환경 변수<br>`limits.queries`는 `DIAG_LIMITS_QUERIES`<br>문자열, 숫자, 불리언 값만 덮어씀<br>배열은 설정 파일에서만 바꿈 |
| 잘못된 값 | 정의되지 않은 키, 타입이 맞지 않는 값, 빠진 필수 항목이 있으면 시작하지 않고 문제마다 이름과 이유를 한 줄씩 기록함<br>값은 기록하지 않음 |

| 묶음 | 내용 |
|---|---|
| 대상 서비스 | 시스템 프롬프트에 넣는 서비스 이름 |
| AWS | 지역과 로컬 실행에서 쓰는 프로필 |
| OpenSearch | 주소, 읽기 사용자, 로그와 스팬 인덱스 패턴 |
| Prometheus | 주소와 읽기 사용자, 또는 AMP 작업 공간 주소<br>둘 다 비우면 앱 메트릭 도구를 띄우지 않음 |
| 필드 이름 | 로그와 스팬의 필드 이름 대응 |
| 식별자 제거 목록 | 모델이 보면 안 되는 필드<br>기본은 로그 메시지 원문, 기기 해시, 세션 ID, 요청 ID, 스팬의 요청 주소 |
| 탐지 기준값 | 신호별 기준, 분당 최소 건수, 확정과 닫기와 진단 대기에 쓰는 시간, 대기 스팬 이름 |
| 모델 | 모델 식별자 `claude-sonnet-5-5`와 추론 강도 `medium` |
| 한도 | 조회 횟수, 진단 시간, 진단과 세션과 하루의 비용, 세션 수명 |
| 슬랙 | 채널 ID와 시간대 |
| 코드 저장소 | 저장소마다 이름, clone 주소, 브랜치<br>커밋을 고정할 수 있음 |
| 서비스 지도 | 구성 요소 목록과 지연 기준 |
| 실행 모드 | 실시간이나 재생<br>재생이면 가상 시계 구간, 원본 인덱스, 보관 메트릭 파일 |

서비스 이름, OpenSearch 주소와 사용자와 로그 인덱스, 슬랙 채널, 코드 저장소, 서비스 지도, 세션 파일 폴더는 기본값이 없어 반드시 적는다.

**환경 변수와 비밀값**

| 환경 변수 | 의미 |
|---|---|
| `DIAG_CONFIG` | 설정 파일 위치 |
| `DIAG_SECRET_ID` | Secrets Manager 비밀 이름 |
| `DIAG_SECRETS_FILE` | 비밀 파일 경로<br>운영과 로컬 실행에서 씀<br>`DIAG_SECRET_ID`와 둘 중 하나만 설정함 |

비밀값은 환경 변수로 받지 않는다. 코드가 시작할 때 아래 키를 읽어 그 값을 쓰는 프로세스에만 넘긴다.

| 비밀 키 | 사용처 |
|---|---|
| `ANTHROPIC_API_KEY` | Agent SDK 하위 프로세스 |
| `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN` | 슬랙 연결 |
| `OPENSEARCH_PASSWORD` | 감시와 OpenSearch MCP |
| `PROMETHEUS_PASSWORD` | Prometheus 자체 도구<br>AMP를 쓰면 비워 둠 |
| `GITHUB_READ_TOKEN` | 코드 사본<br>비공개 저장소가 없으면 비워 둠 |

<br>

### 5-3 자료 원천

| 자료 | 사용 필드 |
|---|---|
| 로그 인덱스 | 시각, 서비스, 수준, 사건 이름, 요청 경로와 메서드, 상태 코드, 처리 시간, 오류 코드, 트레이스 ID |
| 스팬 인덱스 | 시작 시각과 끝 시각, 서비스, 스팬 이름, 진입 스팬 이름, 부모 스팬 ID<br>걸린 시간과 그 단위, 상태 코드, DB 쿼리문, 트레이스 ID |

실제 필드 이름은 설정으로 받아 감시의 집계 질의와 시스템 프롬프트에서 사용한다. 부모 스팬 ID가 없거나 비어 있으면 진입 스팬이다. 스팬 상태 코드가 2이면 오류다.

| 읽기 사용자 권한 | 내용 |
|---|---|
| 인덱스 권한 | 로그와 스팬 인덱스 패턴의 읽기만 |
| 필드 수준 보안 | 식별자 제거 목록의 필드를 역할에서 제외함 |
| 클러스터 권한 | 쓰기와 설정 변경 권한 없음 |

감시와 OpenSearch MCP는 이 사용자로 질의한다.

| 탐지 대상 | 메트릭 | 통계 |
|---|---|---|
| ECS 서비스 | CPU와 메모리 사용률 | 평균과 최대 |
| RDS | CPU, 연결 수, 여유 메모리, 읽기와 쓰기 지연, 디스크 대기 | 최대 |
| ElastiCache | 엔진 CPU와 연결 수 | 최대 |
| 로드밸런서 | 요청 수, 5xx 수 | 합계 |
| 로드밸런서 | 대상 응답 시간 | p95 |

모델은 표 밖의 메트릭도 CloudWatch MCP로 읽을 수 있다. 앱 메트릭은 모델만 읽고 서비스는 `job` 라벨로 구분한다.

<br>

### 5-4 서비스 지도

설정 파일의 `service_map` 절이다. 운영자가 관리하고 에이전트는 시작할 때 한 번 읽는다. 동시성 상한, 태스크 크기, 확장 정책 같은 설계값은 두지 않고 그 값이 있는 파일의 위치만 둔다.

| 필드 | 필수 | 의미 |
|---|---|---|
| `components[].name` | 필수 | 보고에서 지목하는 이름 |
| `components[].kind` | 필수 | `service`, `executor`, `database`, `cache`, `load_balancer`, `autoscaling` |
| `components[].parent` | 선택 | 실행기와 오토스케일링이 속한 서비스의 이름 |
| `components[].log_service`, `components[].span_service` | 선택 | 로그와 스팬에 적힌 이 구성 요소의 서비스 이름 |
| `components[].metric_dimensions` | 선택 | CloudWatch 메트릭 차원 |
| `components[].repository` | 선택 | 코드를 담은 저장소 이름 |
| `components[].paths[]` | 선택 | 설정과 인프라 파일 위치<br>`<저장소 이름>/<경로>`이고 glob을 받음 |
| `components[].docs[]` | 선택 | 스펙과 설계 문서 위치<br>형식은 `paths[]`와 같음 |
| `components[].description` | 선택 | 모델에 전달하는 한 줄 설명 |
| `latency_slo[].trace_group` | 필수 | 진입 스팬 이름 |
| `latency_slo[].p95_seconds` | 필수 | 그 요청 경로의 1분 p95 기준 |

<details>
<summary><b>서비스 지도 예시(일부)</b></summary>

<br>

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
    - name: manyak-server 채팅 턴 실행기
      kind: executor
      parent: manyak-server
      repository: manyak-server
      paths: [manyak-server/src/main/kotlin/com/knk/manyak/chat/config/ChatSseConfig.kt]
      description: 채팅 턴을 태스크당 정해진 수까지 동시에 실행하고 나머지는 큐에서 기다림
    - name: manyak-postgres
      kind: database
      metric_dimensions: { DBInstanceIdentifier: manyak-prod-pg }
      paths: [manyak-terraform/terraform/modules/data/main.tf]
  latency_slo:
    - { trace_group: "http post /api/v1/chats/{chatId}/turns/stream", p95_seconds: 45 }
    - { trace_group: "http get /api/v1/stories", p95_seconds: 1 }
```

</details>

<br>

### 5-5 이상 후보

| 필드 | 필수 | 의미 |
|---|---|---|
| `candidate_id` | 필수 | `c-` 뒤에 연 시각을 `yyyyMMddHHmm`으로 붙임 |
| `opened_at` | 필수 | 연 시각 |
| `first_signal_at` | 필수 | 가장 이른 신호의 첫 시각 |
| `closed_at` | 선택 | 닫은 시각<br>열려 있으면 `null` |
| `signals[].type` | 필수 | `entry_latency`, `queue_latency`, `failure_rate`, `error_logs`, `resource_saturation` |
| `signals[].target` | 필수 | 진입 스팬 이름, 대기 스팬 이름, 서비스 이름 중 신호 종류에 맞는 것<br>자원 포화는 `구성 요소 이름/메트릭 이름` |
| `signals[].first_at` | 필수 | 조건을 처음 넘은 시각<br>분 단위 |
| `signals[].peak_value`, `signals[].threshold` | 필수 | 후보가 열려 있는 동안의 최댓값과 기준값 |
| `signals[].unit` | 필수 | `seconds`, `ratio`, `count`, `percent` |
| `skip_reason` | 선택 | 진단하지 않은 이유 `daily_budget_exceeded`<br>진단했으면 `null` |
| `follow_up_id` | 선택 | 후속 진단의 진단 ID<br>`candidate_id` 뒤에 `-f`를 붙임<br>없으면 `null` |

후속 진단은 새 진단 턴으로 실행하고 보고는 첫 보고의 스레드에 올린다. 그 스레드의 이후 대화는 후속 진단의 세션으로 이어진다.

<br>

### 5-6 운영자 요청

| 필드 | 필수 | 의미 |
|---|---|---|
| `mention_id` | 필수 | `m-` 뒤에 요청 시각을 `yyyyMMddHHmmss`로 붙이고 `-`와 메시지 타임스탬프의 소수부 여섯 자리를 붙임 |
| `text` | 필수 | 멘션 표기를 뺀 메시지 원문 |
| `requested_at` | 필수 | 멘션 메시지의 슬랙 시각 |
| `channel`, `thread_ts` | 필수 | 보고를 올릴 채널과 스레드<br>멘션이 스레드 안에 있으면 그 스레드이고 아니면 멘션 메시지가 스레드의 첫 메시지 |
| `skip_reason` | 선택 | 진단하지 않은 이유 `daily_budget_exceeded`<br>진단했으면 `null` |

<br>

### 5-7 진단 보고

모델은 보고 제출 도구로 아래 필드 중 `diagnosed_at`, `evidence[].verified`, `usage`를 뺀 나머지를 제출한다. 문장 필드의 수치는 초, ms, %, 건처럼 읽기 쉬운 단위로 쓰고 `evidence[].value`에는 조회 결과의 값을 그대로 넣는다.

| 필드 | 필수 조건 | 의미 |
|---|---|---|
| `diagnosis_id` | 항상 | 진단 요청의 ID |
| `diagnosed_at` | 항상 | 진단을 끝낸 시각<br>코드가 채움 |
| `verdict` | 항상 | `incident`, `not_incident`, `undetermined` |
| `headline.impact` | `incident` | 영향받은 경로와 수치와 기준 |
| `headline.cause` | `incident`, 의심 구성 요소가 있는 `undetermined` | 원인을 요약한 명사구 |
| `headline.scope`, `headline.figures` | `not_incident`, `undetermined` | 확인한 요청 경로와 구간, 판정을 뒷받침하는 수치와 기준 |
| `impact.trace_groups[]`, `impact.summary` | `incident` | 영향받은 진입 스팬 이름과 수치가 든 한 문장 |
| `first_anomaly_at` | `incident` | 첫 이상 시각 |
| `suspects[]` | `incident`는 1~3개, `undetermined`는 0~3개 | `component`는 서비스 지도의 이름, `hypothesis`는 원인 가설 한 문장 |
| `ruled_out[]` | 항상<br>0개 이상 | 원인에서 뺀 것의 짧은 이름 |
| `evidence[]` | `incident`와 `not_incident`는 1개 이상 | 원인 가설을 직접 받치는 근거가 앞 |
| `evidence[].observation` | 근거마다 | 관찰 한 문장 |
| `evidence[].query_ref`, `evidence[].value` | 조회 근거 | 조회 기록 번호와 그 결과에 있는 값 |
| `evidence[].code_ref` | 코드 근거 | `repo`, `path`, `start_line`, `end_line`, `quote`<br>`path`는 저장소 루트 기준이고 `quote`는 그 줄 범위에 그대로 있는 문장 |
| `evidence[].verified` | 근거마다 | 근거 검증 결과<br>코드가 채움 |
| `actions.immediate[]`, `actions.improvement[]` | `incident`<br>각 1개 이상 | 즉시 조치와 근본 조치 |
| `usage` | 항상 | `model`, `queries`, `input_tokens`, `output_tokens`, `cost_usd`, `elapsed_seconds`<br>코드가 채움 |

필수 조건에 해당하지 않으면 `null`이나 빈 배열이다. 이 조건이 출력 간 조건이고 코드가 제출 때 검사한다. 근거 하나에는 `query_ref`와 `code_ref` 중 하나만 둔다.

| 필드 | 글자 상한 |
|---|---|
| `headline`의 칸, `ruled_out[]`을 이은 글 | 40자 |
| `actions`의 항목 | 60자 |
| `evidence[].observation` | 80자 |
| `suspects[].hypothesis` | 120자 |

상한은 제출 때 검사하지 않는다. 넘은 값은 보고에 그대로 기록하고 슬랙 메시지에서만 줄인다.

<details>
<summary><b>진단 보고 예시(LLM 응답 대기 장애)</b></summary>

<br>

운영 진단 보고를 고쳐 쓴 예시다. 근거는 일곱 개 가운데 셋만 옮겼다.

```json
{
  "diagnosis_id": "m-20261026101712",
  "diagnosed_at": "2026-10-26T10:18:02Z",
  "verdict": "incident",
  "headline": { "impact": "채팅 턴 p95 68초 (기준 45초)", "cause": "LLM 응답 대기(gemini)", "scope": null, "figures": null },
  "impact": {
    "trace_groups": ["http post /api/v1/chats/{chatId}/turns/stream"],
    "summary": "채팅 턴 스트림 p95가 18:16부터 기준 45초를 넘어 68초에 이르렀고 다른 경로는 기준 안이며 실패는 없다."
  },
  "first_anomaly_at": "2026-10-26T09:16:00Z",
  "suspects": [
    { "component": "manyak-ai", "hypothesis": "턴 스트림 시간 대부분을 manyak-ai의 llm.stream 스팬이 외부 LLM 제공자의 응답을 기다리는 데 쓴다." }
  ],
  "ruled_out": ["큐 대기", "CPU", "오류"],
  "evidence": [
    { "observation": "manyak-ai llm.stream 스팬 평균 21.4초", "query_ref": 5, "value": 21417135902.28125, "code_ref": null, "verified": true },
    { "observation": "chat.turn.queue 스팬 평균 2.4ms로 실행기 대기는 원인이 아님", "query_ref": 3, "value": 2353175.785714286, "code_ref": null, "verified": true },
    { "observation": "manyak-server CPU 최댓값 12.9%", "query_ref": 7, "value": 12.895404487848284, "code_ref": null, "verified": true }
  ],
  "actions": {
    "immediate": ["LLM 제공자 상태와 gemini 지연 확인"],
    "improvement": ["llm.stream 모델별 p95 경보"]
  },
  "usage": { "model": "claude-sonnet-5-5", "queries": 7, "input_tokens": 271422, "output_tokens": 4610, "cost_usd": 0.222, "elapsed_seconds": 49.0 }
}
```

</details>

<br>

### 5-8 실행 폴더

실행 인자로 받은 상위 경로 아래에 실행마다 시작 시각 이름의 폴더를 만든다.

| 파일 | 내용 |
|---|---|
| 상위 경로의 `daily-cost.jsonl` | 비용 장부<br>그날 비용과 하루 상한 안내 여부 |
| `run.json` | 적용한 설정값과 덮어쓴 환경 변수 이름, 코드 사본의 커밋, 공식 MCP 버전, 프롬프트 해시 |
| `candidates.jsonl` | 이상 후보의 상태<br>같은 ID는 마지막 줄이 최신 |
| `mentions.jsonl` | 운영자 요청 |
| `reports/<diagnosis_id>.json` | 진단 보고 |
| `queries/<diagnosis_id>.jsonl` | 모델 메시지와 조회<br>조회는 번호, 도구, 인자, 결과 |
| `failures.jsonl` | 실행 실패<br>진단 ID, 시각, 단계, 원인 한 문장, 그때까지의 사용량 |
| `sessions.jsonl` | 세션과 스레드의 짝, 연 시각과 닫은 시각, 누적 비용<br>같은 세션은 마지막 줄이 최신 |

| 실행 실패 단계 | 의미 |
|---|---|
| `query` | 공식 MCP 연결 실패 |
| `model` | 모델 호출 실패 |
| `report` | 출력 간 조건을 두 번 어김, 제출 형식 위반, 같은 요청의 보고가 이미 있음 |
| `budget` | 조회 한도 뒤에도 미제출, 시간 소진, 진단 비용 한도 도달 |
| `notify` | 슬랙 게시 실패<br>보고 파일은 남음 |
| `session` | 세션 복원 실패, 세션 비용 초과, 대화 턴 모델 호출 실패 |

실패 원인 문장에는 비밀값과 식별자를 넣지 않는다.

<br>

### 5-9 슬랙 메시지

이상 후보 보고는 채널에 새 메시지로 올리고 운영자 요청 보고는 해당 요청의 스레드에 답글로 올린다. 메시지에는 식별자와 진단 ID를 넣지 않는다.

| 순서 | 줄 | 내용 | 표시 조건 |
|---|---|---|---|
| 1 | 제목 줄 | 판정 표시<br>의심 구성 요소가 있으면 첫 번째 의심 구성 요소의 이름을 붙임 | 항상 |
| 2 | 요약 칸 | 판정에 맞는 칸을 두 칸씩 한 줄로 | 항상 |
| 3 | 원인 가설 | 첫 번째 의심 구성 요소의 원인 가설 | 의심 구성 요소가 있을 때 |
| 4 | 주요 근거 | 앞에서 3개<br>검증에 실패한 근거는 앞에 `⚠`를 붙이고 코드 근거는 뒤에 `파일 이름:줄`을 붙임 | 근거가 있을 때 |
| 5 | 조치 | 즉시 조치의 첫 항목과 근본 조치의 첫 항목 | 장애 |
| 6 | 맨 아랫줄 | 근거 검증 요약, 조회 횟수, 걸린 초, 비용 | 항상 |

| 판정 | 제목 | 요약 칸 |
|---|---|---|
| 장애 | `🔴 장애` | 영향, 원인, 첫 이상, 배제한 원인 |
| 장애 아님 | `🟢 이상 없음` | 확인한 범위, 주요 수치, 배제한 원인 |
| 판단 불가 | `🟡 판단 불가` | 확인한 범위, 주요 수치, 원인(있을 때), 배제한 원인 |

글자 상한을 넘은 값은 상한보다 한 자 적게 남기고 끝에 `…`를 붙인다. 금액은 소수 둘째 자리 달러로 쓴다.

```text
🔴 장애 · manyak-ai
영향: 채팅 턴 p95 68초 (기준 45초)     원인: LLM 응답 대기(gemini)
첫 이상: 18:16                        배제한 원인: 큐 대기, CPU, 오류
원인 가설: 턴 스트림 시간 대부분을 manyak-ai의 llm.stream 스팬이 외부 LLM 제공자의 응답을 기다리는 데 쓴다.
주요 근거
• manyak-ai llm.stream 스팬 평균 21.4초
• chat.turn.queue 스팬 평균 2.4ms로 실행기 대기는 원인이 아님
• manyak-server CPU 최댓값 12.9%
즉시 조치: LLM 제공자 상태와 gemini 지연 확인
근본 조치: llm.stream 모델별 p95 경보
근거 7개 중 7개 검증 · 조회 7회 · 49초 · $0.22
```

| 그 밖의 메시지 | 형식 |
|---|---|
| 실행 실패 | `❌ 실행 실패 · <단계> · <원인>`<br>이상 후보는 채널에 올리고 운영자 요청은 그 스레드에 올림 |
| 진단 생략 | `⏸ 진단 생략 · 하루 비용 상한 $<상한> · <HH:MM>에 다시 시작`<br>이상 후보는 그날 첫 생략에만 채널에 올리고 운영자 요청은 매번 그 스레드에 올림 |
| 대화 턴의 답변 | 답변 글 끝에 `이번 답변 $<턴 비용> · 세션 누적 $<세션 비용>`을 붙임 |
| 세션 종료 | 수명 경과나 비용 초과를 한 줄로 알림 |

| 수신 메시지 | 처리 |
|---|---|
| 세션 스레드 밖에서 에이전트를 멘션한 메시지 | 운영자 요청 |
| 세션 스레드 안의 사람 메시지 | 멘션 여부와 관계없이 대화 턴 |
| 에이전트 자신의 메시지 | 넘기지 않음 |

운영자 요청의 멘션 메시지에는 받았을 때 `eyes` 반응을 달고, 보고를 올리면 `white_check_mark`로, 실행 실패나 진단 생략이면 `x`로 바꾼다. 반응에 실패해도 진단과 보고를 계속한다.

<br>

### 5-10 평가 사례와 채점

재현 평가와 재생 모드가 같은 YAML 사례 파일을 쓴다.

| 사례의 항목 | 의미 |
|---|---|
| 이름 | 결과 파일 이름에 씀 |
| 설정 파일 | 그 사례의 보관 자료 인덱스, 보관 메트릭 파일, 고정 커밋을 담은 설정 |
| 요청 문장 | 재현 평가에서 운영자 요청으로 보내는 문장 |
| 재생 구간 | 재생 모드의 가상 시계 시작과 끝<br>없으면 재생 모드에서 건너뜀 |
| 기대 판정 | 장애, 장애 아님, 판단 불가 |
| 장애 시작 시각과 허용 시간 | 재생 모드에서 감지 시간을 재는 기준 |
| 기대 구성 요소 | 의심 구성 요소 중 하나 이상이 이 목록에 있어야 함 |
| 원인 핵심어 | 원인 가설과 원인 칸에 있어야 하는 말<br>묶음마다 그 안의 말 중 하나 이상이 있어야 함 |
| 코드 근거 경로 | 코드 근거의 경로가 하나 이상 일치해야 함 |
| 조치 핵심어 | 근본 조치에 있어야 하는 말<br>묶는 규칙은 원인 핵심어와 같음 |
| 정답 원인과 조치 | LLM 판정의 기준이 되는 문장 |

채점 결과에는 사례별 판정, 구성 요소, 원인, 코드 근거 경로, 조치의 일치 여부와 근거 검증률, 조회 횟수, 비용, 시간이 들어간다. 재생 모드는 이상 후보를 연 가상 시각, 감지까지 걸린 시간, 장애 구간 밖에서 연 이상 후보 수를 더한다. 같은 사례를 여러 번 돌리면 항목마다 통과 비율을 낸다.
