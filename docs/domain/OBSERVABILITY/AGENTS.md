# OBSERVABILITY

로그, 트레이스, 지표의 수집과 저장, Sentry 연결, Langfuse 연결, 장애 진단 에이전트를 다룬다. 제품 기능과 결합도가 낮아 별도로 둔다. 태스크별 Langfuse 기록 항목은 각 AI 세트의 관측 문서가 정하고 Amplitude 제품 분석은 이 도메인에 넣지 않는다.

세트별 명세는 하위 폴더에 두고, 각 세트의 문서 역할과 읽는 순서는 그 폴더의 `AGENTS.md`가 안내한다. 파일 구성은 세트 종류별 작성 가이드를 따르며 해당 없는 문서는 만들지 않는다. ([제품 Spec 작성 가이드](../../REFERENCE/PRODUCT-SPEC-WRITING-GUIDE.md), [AI](../../REFERENCE/AI-SPEC-WRITING-GUIDE.md), [백엔드](../../REFERENCE/BACKEND-SPEC-WRITING-GUIDE.md) 명세 작성 가이드)

<br>

### 1. 세트

| 세트 | 다루는 것 | 상태 |
|---|---|---|
| [`AI/`](AI/AGENTS.md) | 관측 자료 감시, 이상 탐지, 장애 진단 보고 | 1~5, 6-4 작성 |
| `BACKEND/` | 로그 필드와 스팬 이름 계약, 수집 경로, 저장소, Sentry와 Langfuse 연결 | 미작성 |

- 세트마다 `DECISIONS.md`를 두고 이 도메인 결정의 이력을 기록한다.
- 세트 사이에 같은 사실을 두 번 정하지 않는다. 로그 필드와 스팬 이름은 BACKEND 세트가 정하고 AI 세트는 그 이름을 자료 원천으로 참조한다.

<br>

### 2. 이관 원본

아래 기존 문서의 해당 절을 이 도메인으로 옮긴다. 이관이 끝날 때까지 기존 문서가 기준이다.

- `docs/spec/4-backend-server-spec.md 4-7 운영과 관측`
- `docs/spec/5-ai-server-spec.md 5-6 운영과 관측`
- `docs/design/4-deployment.md 4-9 검수, 관측, 롤백`
- `docs/adr/2-backend-server-adr.md BE-056`
- `docs/adr/3-ai-server-adr.md Langfuse 원문 관측과 실패 격리`
- `docs/adr/4-deployment-adr.md DEP-009`
