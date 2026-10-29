# 공용 서비스 인터페이스

도메인 API의 요청과 응답은 제공자 세트의 계약에서 관리한다. 클라이언트는 해당 도메인의 서버 계약을 입력으로 참조한다. ([도메인 목록](../domain/AGENTS.md))

<br>

### 백엔드 공용 규칙

공개 비즈니스 API의 접두어는 /api/v1이다. 내부 알림 API는 /internal의 전체 경로를 쓰며 이 접두어를 붙이지 않는다. JSON 필드는 camelCase, 시각은 ISO 8601 UTC, 문자 수는 UTF-16 코드 유닛 기준이다. 공개 식별자와 엔드포인트별 입력 조건은 각 계약을 따른다.

| 인터페이스 | 계약 |
|---|---|
| GET /actuator/health | 종합 상태 |
| GET /actuator/health/liveness | 컨테이너 활성 |
| GET /actuator/health/readiness | 준비 상태. 운영은 Redis 검사 비활성 |
| 운영 Actuator | health와 info만 노출. 메트릭은 OTLP push, prometheus 스크레이프는 로컬 전용 |
| GET /v3/api-docs, /swagger-ui.html | 비운영 API 문서. 운영은 springdoc 기능 비활성으로 404 |

공통 오류 형식은 각 BACKEND 계약의 공통 규칙, 요청 연결과 수집 제한은 분석 기준을 따른다. ([ACCOUNT 공통 응답](../domain/ACCOUNT/BACKEND/CONTRACT.md#공통-규칙과-헤더), [분석과 관측](ANALYTICS.md))

<br>

### AI 상태 확인

| 항목 | 계약 |
|---|---|
| 요청 | GET /api/v1/health, 요청 본문 없음 |
| 처리 | LLM을 호출하지 않음 |
| 성공 | HTTP 200, JSON |
| status | string, ok |
| version | string, 앱 버전 |

AI의 도메인별 요청 표기, 모델 호출과 오류 형식은 각 AI 세트에서 관리한다. 상태 확인 성공은 실제 모델 호출과 품질 검증을 뜻하지 않는다.
