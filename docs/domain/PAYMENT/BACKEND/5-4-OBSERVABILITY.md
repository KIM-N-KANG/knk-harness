# 5-4 관측

이 문서는 PAYMENT 도메인의 관측 스택, 요청을 추적할 식별자, 구조화 로그 이벤트, 오류 확인 위치, 지표, 트레이스, 알림, 수집 조건, 분석 이벤트를 정한다.

비밀값과 개인정보 취급 규칙은 보안에, 오류 로그 수준은 오류 처리에 있다. ([5-1-7 비밀값과 개인정보](5-1-SECURITY.md#5-1-7-비밀값과-개인정보), [5-3-8 로그와 Sentry](5-3-ERROR-HANDLING.md#5-3-8-로그와-sentry))

<br>

### 5-4-1 관측 스택

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    S["`**서버**
PAYMENT 도메인`"]
    S -->|표준 출력 JSON| F["`**FireLens**
Fluent Bit`"]
    F -->|로그 인덱스| OS["`**OpenSearch**`"]
    F --> CW["`**CloudWatch**
안전망`"]
    S -->|OTLP 트레이스| DP["`**Data Prepper**`"]
    DP -->|트레이스 인덱스| OS
    OS --> OD["`**OpenSearch Dashboards**`"]
    S -->|OTLP 지표, 결제 결과 카운터| G["`**Grafana Cloud**`"]
    S -->|5xx| SE["`**Sentry**`"]
    SE -->|일일 요약| SL["`**Slack**`"]
    S -->|출석, 결제 이벤트| AM["`**Amplitude**`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef ext fill:#F4F6F4,stroke:#9BA99E,color:#253C2C
    class S comp
    class F,OS,CW,DP,OD,G,SE,SL,AM ext
```

<br>

### 5-4-2 상관관계 식별자

상관관계 필터는 모든 요청의 MDC에 다음 값을 기록한다. 로그와 Sentry는 같은 식별자 값을 사용한다.

| MDC 필드 | 값 | 규칙 |
|---|---|---|
| `request_id` | `req_` + UUID | 요청 헤더 값을 쓰고 없으면 생성<br>응답 헤더로 반환 |
| `session_id` | `X-Manyak-Session-Id` | 없으면 `unknown` |
| `device_id_hash` | `device_hash_` + SHA-256(pepper + 원본) 앞 16자 | 원본은 저장하지 않음 |
| `sentry_event_id` | Sentry 이벤트 ID | 5xx를 Sentry로 보낸 요청만 |
| `traceId`, `spanId` | 현재 스팬 | 트레이스 전송을 비활성화해도 생성해 로그에 포함 |

| 식별자 | 기록 위치 | 연결 대상 |
|---|---|---|
| `request_id` | 로그 MDC, Sentry 태그 | 한 요청의 로그 |
| 회원 내부 ID | 대사 로그 `user_id`, 체험 Redis 장애 WARN | 회원 |
| 주문 내부 ID | 웹훅 경고 | 주문 |
| 적립 행 ID | 회수 부족분 WARN | 구매 적립 |
| 차감 그룹 | 대사 로그 `ref_type`, `ref_id` | 소모 행 묶음 |
| 웹훅 멱등 키 | 수신 DEBUG | 그로블 전송 1건<br>검증에는 쓰지 않음 |

배치는 요청과 별개로 실행하므로 요청 ID가 없다. 스케줄러 로그는 이벤트 이름과 그룹 식별자로 찾는다.

<br>

### 5-4-3 구조화 로그 이벤트

구조화 로그는 `event_name`을 맨 앞에 둔 JSON 형식으로 INFO 수준에 기록한다. 이벤트 이름은 snake_case다. `prod`, `dev`, `jsonlog` 프로파일에서만 JSON 형식을 쓴다. 그 외에는 콘솔 패턴을 쓴다. JSON에는 `service=manyak-server`가 포함된다. 인코더는 MDC 값을 최상위 필드에 기록한다.

| 단위 | 기록 시점과 이름 | 기록 내용 |
|---|---|---|
| 모든 API 요청 | 응답 종료<br>`api_request_completed`, 5xx는 `api_request_failed` | `endpoint`, `http_method`, `status_code`, `duration_ms`<br>실패 시 예외 클래스 이름 또는 상태 이름을 `error_code`로 추가 |
| 정책 기동 적재 | 기동 직후<br>평문 INFO `credit_policy_effective` | 정책 키 6종의 현재 유효값 |
| 정책 변경 | 갱신에서 값이 바뀐 키<br>평문 INFO `credit_policy_changed` | `key`, `from`, `to`<br>종료 시각 만료도 다음 갱신에서 드러남 |
| 정책 적재 실패 | 갱신 실패<br>평문 WARN `credit_policy_load_failed` | 예외 |
| 정책 오버라이드 제외 | 갱신마다 한 번<br>평문 WARN `credit_policy_override_unknown_key`, `credit_policy_override_rejected` | `key`, `amount`, 유효한 키 목록 또는 `minimum`과 기본값 |
| 대사 보정 | 환불을 발행한 실행<br>`credit_reconciliation_refunded` | `groups_scanned`, `charges_scanned`, `refunds_emitted`<br>`charges_scanned`는 후보 조회로 읽은 `CHAT_TURN` 참조 차감 수 |
| 대사 실행 실패 | 실행 전체 예외<br>`credit_reconciliation_failed` | `error` |
| 대사 그룹 실패 | 그룹 처리 예외<br>`credit_reconciliation_group_failed` | `user_id`, `ref_type`, `ref_id`, `error` |
| 대사 차감 행 실패 | 채팅 턴 차감 행 처리 예외<br>`credit_reconciliation_charge_failed` | `user_id`, `transaction_id`, `error` |
| 혼합 단가 환불 | 단가가 섞인 그룹 단위 대사에 실제 환불<br>WARN `credit_reconciliation_mixed_unit_amount`<br>행 단위로 대사하는 채팅 턴에서는 발생하지 않음 | `user_id`, `ref_type`, `ref_id`, `min_unit_amount`, `max_unit_amount`, `refunds_emitted` |
| 웹훅 수신 | 서명 검증 뒤<br>평문 DEBUG | 이벤트 종류, 멱등 키 헤더 |
| 웹훅 무시 | 본문 불일치<br>평문 WARN | 무시 사유 |
| 역순 환불 금액 불일치 | 완료 처리<br>평문 WARN | 주문 내부 ID |
| 구매 환불 회수 부족분 | 회수<br>평문 WARN | 적립 행 ID, 부족 수량 |
| 체험 Redis 장애 | 회원 예약, 복원, 스냅샷<br>평문 WARN | 회원 내부 ID, 카운터, 예외 |
| 분석 이벤트 전송 실패 | 비동기 전송 실패<br>평문 WARN | 이벤트 이름, 예외 |
| 주문 소유자 식별 실패 | 웹훅 이벤트 발행 전<br>평문 WARN | 주문 내부 ID |

<details>
<summary><b>예시: 대사 보정 로그 1줄</b></summary>

<br>

예시에는 가상 값을 썼다. 로그 프레임워크가 붙이는 필드는 생략했다.

```json
{"@timestamp":"2026-10-16T01:23:45.678Z","message":"event_name=credit_reconciliation_refunded, groups_scanned=3, refunds_emitted=1","level":"INFO","traceId":"4bf92f3577b34da6a3ce929d0e0e4736","spanId":"00f067aa0ba902b7","event_name":"credit_reconciliation_refunded","groups_scanned":3,"refunds_emitted":1,"service":"manyak-server"}
```

</details>

<br>

### 5-4-4 오류 확인

| 기능 | 오류 조회 위치 |
|---|---|
| 그로블 결제 | 지표 `manyak.payment.groble.webhook`의 `result` 분포<br>웹훅 무시 WARN의 사유 |
| 결제 환불 | 웹훅 지표의 `refunded`<br>회수 부족분 WARN |
| 선차감과 환불 | 대사 로그 `credit_reconciliation_refunded`가 반복되면 호출 도메인의 환불 경로 점검<br>간편 제작의 혼합 단가 WARN<br>채팅 턴은 `credit_reconciliation_charge_failed` |
| 정책값 | 기동 로그 `credit_policy_effective`, 변경 로그, 오버라이드 제외 WARN |
| 체험 | Redis 장애 WARN<br>요청 로그의 `/api/v1/users/me/trials` 500 비율 |
| 잔액과 내역 | 요청 로그의 `/api/v1/users/me/credits/transactions` 400 비율 |

<br>

### 5-4-5 지표

| 지표 | 종류와 태그 | 의미 |
|---|---|---|
| `manyak.payment.groble.webhook` | Counter<br>`result` = `completed`, `refunded`, `marked`, `ignored`, `invalid` | 웹훅 처리 결과<br>`refunded`는 환불 회수와 선도착 환불을 소비한 완료, `marked`는 주문 없는 환불의 표식 보관, `invalid`는 검증 실패 |
| `http.server.requests` | Timer<br>`uri`, `method`, `status`, `outcome` | 이프 경로의 요청률, 오류율, 응답 시간 |

| 항목 | 기준과 제한 |
|---|---|
| 전송 여부 | 지표 전송을 켠 환경에서만 Grafana Cloud로 전송 |
| 전송 주기 | 60초 간격 |
| 카운트 시점 | 거래 처리 결과는 트랜잭션 커밋 뒤 기록하고 롤백된 처리는 세지 않음<br>검증 실패 `invalid`는 즉시 기록 |

<br>

### 5-4-6 트레이스

| 항목 | 내용 |
|---|---|
| 활성화와 표본 | 환경 변수로 켜며 기본값은 비활성 |
| 스팬 | HTTP 요청 스팬의 하위에 JDBC(QUERY만, 바인딩 값 제외), Redis 스팬 |
| 제외 | actuator 요청, Spring Security 내부 관측, 요청 밖의 루트 DB와 Redis 관측은 노이즈 필터가 제외<br>스케줄러의 DB 접근도 요청과 별개이므로 제외 |

<br>

### 5-4-7 알림

| 항목 | 기준 |
|---|---|
| 정기 보고 | 매일 오전 10시(KST), 지난 24시간 동안 발생한 운영 Sentry 오류 요약 |
| PAYMENT에서 수집하는 오류 | 500 예상하지 못한 예외, 게스트 체험 Redis 장애로 인한 500<br>4xx 거절, 웹훅 무시, 대사 보정, 정책 제외는 Sentry에 없어 보고에 포함되지 않음 |
| 지표 기반 알림 | PAYMENT 전용 규칙 없음 |

<br>

### 5-4-8 수집 조건과 실패 처리

**1. 데이터 범위**

| 데이터 | 현재 기록 방식 |
|---|---|
| 웹훅 시크릿 | 로그, Sentry, 지표에 기록하지 않음 |
| 웹훅 본문 | 기록하지 않음<br>이벤트 종류와 무시 사유만 기록 |
| 그로블 거래 식별자, 이벤트 ID | 로그에 기록하지 않음 |
| 디바이스 ID | 해시만 기록<br>원문은 분석 이벤트의 `device_id`로만 Amplitude에 전달<br>분석 이벤트 경로에서는 원문을 저장하지 않음 |
| 금액 | 대사 로그의 단가와 회수 부족분은 기록 |
| Sentry 요청 필드 | 기본 수집 |
| Sentry 이벤트 | 5xx만 캡처<br>기본 개인정보 수집 비활성화 |

<br>

**2. 수집 실패**

| 상황 | 처리 |
|---|---|
| 분석 이벤트 전송 실패 | 비동기 전송 실패를 WARN으로만 기록하고 재시도하지 않음 |
| 결제 이벤트 | 트랜잭션 커밋 뒤 발행<br>롤백되면 발행하지 않음 |
| 회원 식별 실패 | 주문 소유자의 공개 식별자를 찾지 못하면 WARN으로 기록하고 발행 생략 |
| 지표 전송 실패 | SDK로 배치 전송<br>실패분은 유실 |
| Sentry 캡처 실패 | SDK 내부에서 처리<br>DSN 없는 환경은 no-op |
| 대사 결과 로그 | 환불이 없는 실행은 기록하지 않음<br>기록이 없으면 보정할 것이 없었거나 그룹이 실패한 것이며 그룹 실패는 별도 로그로 확인 |
| 미수집과 누락 | 수집 비활성화, 기록 실패, 전송 유실을 구분<br>기록이 없다는 이유만으로 결제가 없었다고 판단하지 않음 |

<br>

### 5-4-9 분석 이벤트

**서버 이벤트**

Amplitude HTTP API로 비동기 발행한다. 분석 전송을 켜고 API 키가 있는 환경에서만 전송한다.

| 이벤트 | 시점 | 프로퍼티 |
|---|---|---|
| `server_credit_attendance_processed_succeeded` | 출석 보상 요청 처리 | `rewarded`, `amount` |
| `server_payment_order_processed_succeeded` | 웹 충전 주문 생성 커밋 | `product_id` |
| `server_payment_purchase_processed_succeeded` | 완료 통지로 구매 적립 커밋 | `product_id`, `price_krw`, `credit_amount` |
| `server_payment_refund_processed_succeeded` | 환불 통지로 회수 커밋 또는 선도착 환불을 소비한 완료 처리 커밋 | `product_id`, `reversal_shortfall` |

| 공통 프로퍼티 | 값 |
|---|---|
| `user_id` | 회원 공개 식별자<br>웹훅은 주문 소유자의 공개 식별자 |
| `device_id` | 요청 헤더 `X-Manyak-Device-Id` 원본<br>헤더가 없으면 생략<br>웹훅은 생략 |
| `session_id` | 정수 문자열일 때만 포함<br>웹훅은 생략 |
| `request_id`, `is_logged_in` | 요청 문맥<br>웹훅은 주문 소유자에게 붙이는 회원 이벤트이므로 `is_logged_in`은 `true` |
| `insert_id` | `{request_id}:{eventType}`<br>재시도 중복 제거 |
| `rewarded` | 이번 요청으로 출석 보상을 적립했으면 `true` |
| `amount` | 이번 요청으로 적립한 이프 |
| `product_id` | 상품 ID |
| `price_krw` | 결제 금액 |
| `credit_amount` | 적립 총량 |
| `reversal_shortfall` | 회수 때 이미 소진돼 돌려받지 못한 수량<br>회수 없이 환불 상태가 된 주문은 생략 |

- 출석 이벤트는 적립 여부와 무관하게 요청당 1회 발행한다. 거절된 요청에는 발행하지 않는다.
- 구매와 환불 이벤트는 처리 트랜잭션 커밋 뒤 발행한다. 무시한 통지와 재전송에는 이벤트를 발행하지 않는다. 적립 없이 환불 상태가 된 주문은 환불 이벤트만 발행한다.
- 가입과 초대의 보상 적립 이벤트는 계정 도메인이 발행한다. 소모와 환불은 스토리와 채팅 도메인의 이벤트로 확인한다.
