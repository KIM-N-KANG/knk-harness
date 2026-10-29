# 백엔드 운영 관측

기준은 기존 메트릭 문서의 Spring Boot 4.0.6과 Micrometer 1.16.5다. 코드와 수신 데이터의 검증 범위는 각 항목에 표시한다.

## 2-4. 메트릭과 운영 연동

구조화 로그·Sentry·`ai_call_logs`가 개별 사건을 남긴다면, 메트릭은 시계열 집계로 RED(Rate·Error·Duration)와 **AI 호출 지연**을 봅니다. Micrometer로 계측하고 **OTLP push**로 Grafana Cloud에 보냅니다. Prometheus·Grafana를 별도 EC2에 자체 호스팅하지 않습니다: 단일 인스턴스 운영에서 스크레이프 대상과 관리 대상을 늘리는 비용이 이득보다 큽니다.

**수집 경로**: `OtlpMeterRegistry`(micrometer-registry-otlp)가 step 주기마다 Grafana Cloud OTLP 게이트웨이로 push합니다. 운영은 스크레이프 엔드포인트(`/actuator/prometheus`)를 **노출하지 않습니다**. push 방식이라 인바운드 경로가 필요 없고, 노출하면 인증 없이 내부 지표가 공개됩니다. actuator 노출 목록은 운영에서 `health,info`를 유지하고 로컬에만 `prometheus`를 더합니다: export 내용을 눈으로 확인하는 용도이자, 로컬 Compose의 Prometheus가 긁는 대상입니다. **pull 경로는 로컬 전용이며 운영 구성으로 승격하지 않습니다**([`4-deployment.md §4-8`](../../operations/DEPLOYMENT.md)).

**지표 카탈로그**

| 메트릭 | 태그 | 출처 | 용도 |
| --- | --- | --- | --- |
| `http.server.requests` | `uri`(경로 템플릿)·`method`·`status`·`outcome` | Spring Boot 자동 | RED: 요청률·5xx 오류율·p95 응답시간 |
| `manyak.ai.call.duration` | `feature`(enum 4종)·`outcome`(`success`/`failure`) | `AiCallRecorder` | AI API 호출 지연·실패율. `ai_call_logs.latency_ms`와 같은 구간을 재는 집계 뷰 |
| `manyak.story.creation.duration` | `outcome`(`success`/`failure`/`rejected`) | `SimpleStoryCreationService` | 간편 스토리 완성 처리시간(AI 호출 + 저장 포함) |
| JVM·프로세스·DB 커넥션 풀 | 바인더별 기본 태그 | Micrometer 기본 바인더(자동 등록) | CPU·힙·GC·스레드·커넥션 풀: 이름은 아래 표 |

기본 바인더 지표는 대시보드 패널 단위로 묶어 씁니다.

| 패널 | 메트릭 |
| --- | --- |
| CPU | `process.cpu.usage`·`system.cpu.usage`·`system.load.average.1m` |
| 힙 | `jvm.memory.used`·`jvm.memory.max`·`jvm.memory.committed`·`jvm.memory.usage.after.gc` |
| GC | `jvm.gc.pause`·`jvm.gc.overhead`·`jvm.gc.memory.allocated` |
| 스레드 | `jvm.threads.live`·`jvm.threads.states` |
| DB 커넥션 풀 | `hikaricp.connections.{active,idle,pending,max}` **또는** `jdbc.connections.{active,idle,max}` |

DB 커넥션 풀은 **둘 중 하나만 고릅니다.** `hikaricp.*`(Hikari 자체 tracker)와 `jdbc.*`(Boot pool metadata)가 함께 등록되어 같은 값을 두 이름으로 내보내므로, 두 계열로 패널을 만들면 중복입니다. `jvm.gc.pause`는 GC가 실제로 발생한 뒤에야 나타나므로 기동 직후 패널이 비어 보이는 것이 정상입니다.

위 이름은 바인더 실측 기준이며, 전체 앱 컨텍스트에서 최종 등록까지 확인한 것은 아닙니다. 로컬 기동 후 `/actuator/prometheus`로 확인합니다(서버 레포 `http/common/metrics-prometheus.http`).

**카디널리티 규칙**: 메트릭 태그에는 **고유값을 넣지 않습니다**. `user_id`·`story_id`·`chat_id`·`request_id`·`device_id_hash`는 금지이며, 개별 추적은 구조화 로그와 `ai_call_logs`의 몫입니다. 태그는 유한 enum으로만 둡니다(`feature` 4종 × `outcome` 2종 = 8 시계열). `uri`는 Spring이 경로 변수를 템플릿(`/api/v1/stories/{storyId}`)으로 치환해 적재하므로 안전합니다.

**히스토그램 비용**: p95를 서버측에서 계산하려면 percentile histogram이 필요한데, 시계열 하나가 `le` 버킷 수만큼 불어납니다. Micrometer Timer의 기본 구간은 1ms\~30s이고 이때 버킷은 **69개**입니다(micrometer 1.16.5 실측). 엔드포인트 39개 × 상태 코드 3\~5종 × 69이면 8k\~13k로 Grafana Cloud 무료 티어 한도(10k active series)에 걸리므로, 메트릭별 기대 구간을 좁혀 버킷을 자릅니다.

| 메트릭 | 구간 | 버킷 수(실측) | 근거 |
| --- | --- | ---: | --- |
| (기본값 참고) | 1ms\~30s | 69 | Micrometer `AbstractTimerBuilder` 기본 |
| `http.server.requests` | 10ms\~10s | 47 | 일반 HTTP 응답 구간 |
| `manyak.ai.call.duration` | 100ms\~240s | 54 | AI 타임아웃 최대 180초(compile)보다 **위**여야 타임아웃 직전 분포가 보인다 |
| `manyak.story.creation.duration` | 100ms\~240s | 54 | 위와 같음(스토리 완성 = compile 호출 포함) |

버킷 수는 **scrape 프레임 기준**입니다: `registry.scrape`가 실제로 뱉는 `_bucket` 라인 수(min/max clamp 경계와 `+Inf` 포함)이고, Grafana Cloud가 과금·집계에서 보는 것도 이 프레임입니다. `PercentileHistogramBuckets.buckets`의 순수 버킷 집합을 직접 세면 프레임 차이로 일관되게 3 적게 나옵니다(66·44·51). 100ms\~240s의 54는 100ms\~120s(49)에 상한 확대분 +5를 더한 값이고, 증가분 +5는 두 프레임에서 동일합니다.

상한은 **타임아웃보다 높게** 둡니다. 같거나 낮으면 느린 정상 호출이 `+Inf` 구간에 합쳐져 타임아웃 직전의 p95·p99를 구분할 수 없습니다.

`http.server.requests`의 10초 상한은 **의도적으로 AI 대기 엔드포인트를 덮지 않습니다.** 그 경로의 지연은 전용 `manyak.*` 타이머가 담당하고, HTTP 히스토그램 상한을 올리면 버킷이 엔드포인트 수만큼 곱해져 비용이 큽니다. 대신 AI 엔드포인트의 HTTP p95는 10초에서 상한값으로 집계된다는 점을 알고 받아들입니다.

**환경 구분**: `service.name` 하나로 가릅니다. 운영은 `spring.application.name`(=`manyak-server`)이 그대로 리소스 속성이 되고, 로컬만 `OTEL_SERVICE_NAME=manyak-server-local`로 덮어씁니다. Grafana Cloud는 `service.name`을 모든 메트릭의 **`service_name` 라벨**로 승격하므로 조인 없이 환경을 나눌 수 있습니다(PromQL 필터도 `service_name="manyak-server"`: 로컬 실습으로 확인). `deployment.environment` 리소스 속성은 `target_info`에만 실려 조회 때마다 조인이 필요하므로 쓰지 않습니다.

**조회 시 이름·단위 주의**: 같은 Timer라도 노출 경로에 따라 메트릭 이름이 다릅니다. 로컬 `/actuator/prometheus`에는 `manyak_story_creation_duration_seconds_*`로 나오지만 **Grafana Cloud에는 `manyak_story_creation_duration_milliseconds_*`로 도착합니다**(OTLP 전송의 기본 시간 단위가 달라 이름까지 바뀜). 대시보드·알림 쿼리는 기억에 의존하지 말고 Grafana Metrics browser에서 실제 수신된 이름을 먼저 확인합니다.

**전송 주기**: 운영 60초, 로컬 10초. 주기가 짧을수록 DPM(datapoints per minute) 과금이 비례해 늘고, 단일 인스턴스 서비스에서 60초보다 촘촘한 해상도가 주는 이득은 없습니다.

**OTLP는 기본으로 끕니다.** 레지스트리는 모든 프로파일에서 자동 구성되며 endpoint가 없으면 `http://localhost:4318/v1/metrics`로 전송을 시도합니다. 환경에 관계없이 endpoint와 헤더를 먼저 넣고 `MANYAK_OTLP_METRICS_ENABLED=true`를 설정합니다. 메트릭 전송 실패는 사용자 요청에 영향을 주지 않게 격리합니다([Spec §4-7](../../reference/ANALYTICS.md#6-6-관측-구현)).

**미주입과 빈 값은 다릅니다.** Spring Boot 4.0.6의 `PropertiesConfigAdapter.obtain`은 null만 검사합니다. URL이 빈 문자열이면 기본값을 찾지 않고 빈 값 그대로 micrometer에 전달합니다.

| URL 속성 상태 | 결과 |
| --- | --- |
| 미주입(null) | `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` → `OTEL_EXPORTER_OTLP_ENDPOINT` → `http://localhost:4318/v1/metrics` 순으로 찾아 전송 |
| 빈 문자열(`""`) | 빈 URL로 push 시도. localhost로 보내는 요청이 아니라 매 step 전송 오류 |

운영 시크릿 JSON에서 키를 빈 값으로 두면 이 경로를 타므로 **OTLP 키는 빈 값으로 남기지 않습니다.** 끄려면 키를 넣지 않거나, 토글을 `false`로 둡니다.

`OtlpConfig`는 `System.getenv`에서 표준 `OTEL_*` 변수를 직접 읽습니다. Spring `Environment`와 프로파일을 거치지 않으므로 운영에서는 충돌을 피하려고 Spring 전용 변수명을 씁니다([§2-5](CONFIGURATION.md#2-5-런타임-설정)).

**측정 범위 주의**: `manyak.story.creation.duration`은 실제 생성 콜백만 감쌉니다. AI 호출 없이 저장된 결과를 돌려주는 **조회 경로 두 가지는 의도적으로 제외**합니다: ① 멱등 재요청(`recordOrRun`의 COMPLETED replay: [§4-3-2](../../domain/AGENTS.md#1-도메인과-세트))은 콜백 자체가 실행되지 않아 자연히 빠지고, ② 회수 재실행 재구성은 콜백은 타지만 AI·저장이 없어 `aiCallLogId`가 `null`인 것으로 판별해 제외합니다. 포함하면 아주 짧은 시간이 섞여 p95가 실제 생성 비용보다 낙관적으로 왜곡됩니다.

**실패는 다시 둘로 나눕니다**. `outcome`이 3값인 이유입니다.

| 값 | 의미 | 걸리는 시간 |
| --- | --- | --- |
| `success` | 생성·저장까지 끝난 호출 | 수 초\~180초 |
| `failure` | 생성을 시도하다 깨진 호출: AI compile 실패(502·타임아웃)·응답 검증 실패·저장 경합 | 수 초\~180초 |
| `rejected` | 생성 시도 **이전에** 거부된 4xx: 세션 없음(404)·소유권(403)·이미 생성됨(409)·태그 오류(400)·이프 부족과 게스트 한도(402) | 밀리초(DB 조회 몇 번) |

**판별 기준은 HTTP 상태가 아니라 compile 시작 여부입니다.** compile을 마친 뒤에도 4xx가 날 수 있기 때문입니다: 같은 세션에 `requestId`가 다른 완성 요청 둘이 겹치면 둘 다 잠금 없는 초기 검사를 통과해 compile을 호출하고, 진 쪽이 잠금을 잡은 뒤 409(세션 소실 시 404)를 던집니다. 이건 AI 호출을 이미 마친 **실제 생성 실패**이므로 `failure`입니다. 따라서 compile 진입 여부를 먼저 보고, 진입했으면 상태 코드와 무관하게 `failure`, 진입 전 4xx만 `rejected`, 그 외(5xx·비 HTTP 예외)는 `failure`입니다.

4xx를 `failure`에서 떼는 이유는 두 갈래를 한 히스토그램에 섞으면 **거부 비중에 따라 실패 p95가 요동치기** 때문입니다. 거부가 늘수록 밀리초 표본이 늘어 p95가 오히려 **낮아지므로**, AI가 실제로 느려지는데 지표는 개선된 것처럼 보이는 역전이 생깁니다. 실패 건수 알림도 404 급증만으로 오발화합니다. **알림과 p95는 `outcome="failure"`만 봐야 합니다.** 태그 값이 2에서 3으로 늘어도 유한 enum이라 카디널리티는 안전합니다(위 카디널리티 규칙).

**알림**: 임계값은 운영 데이터가 쌓인 뒤 정합니다. 서버가 중단되면 지표가 No Data 상태가 되므로, 알림 규칙에서 이 상태를 무시할지 별도 심각도로 다룰지도 함께 정합니다. AI 호출 지연·실패율 알림도 운영 기준선을 확인한 뒤 추가합니다([배포 Design §4-9](../../operations/DEPLOYMENT.md#4-9-검수-관측-롤백)).

**현재 구현하지 않은 범위.** Langfuse는 트레이스 연결 식별자를 헤더로 전달하는 데까지 구현돼 있습니다. 사용자 반응을 도메인 데이터로 검증해 저장하고 score로 발행하는 경로(선택지 상호작용 API, 생성 버전 연결, outbox, Langfuse 클라이언트)는 코드에 없습니다. 계약은 [Spec §4-7](../../reference/ANALYTICS.md#6-6-관측-구현)에 있습니다.

운영 readiness는 Redis를 검사하지 않습니다(`management.health.redis.enabled=false`). 재활성 시점은 정하지 않았습니다.
