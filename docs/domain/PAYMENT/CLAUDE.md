# PAYMENT

이프(내부 재화), 충전 결제, 가입·출석·초대 보상, 체험 한도, 원장을 다룬다.

세트별 명세는 하위 폴더에 두고, 각 세트의 문서 역할과 읽는 순서는 그 폴더의 `CLAUDE.md`가 안내한다. 파일 구성은 세트 종류별 작성 가이드를 따르며 해당 없는 문서는 만들지 않는다. ([제품 Spec 작성 가이드](../../REFERENCE/PRODUCT-SPEC-WRITING-GUIDE.md), [AI](../../REFERENCE/AI-SPEC-WRITING-GUIDE.md) · [백엔드](../../REFERENCE/BACKEND-SPEC-WRITING-GUIDE.md) · [클라이언트](../../REFERENCE/CLIENT-SPEC-WRITING-GUIDE.md) 명세 작성 가이드)

<br>

### 1. 세트

| 세트 | 다루는 것 | 상태 |
|---|---|---|
| `BACKEND/` | 원장과 동시성, 결제 검증과 웹훅, 보상 지급과 만료, 정책 값 | 미작성 |
| `WEB/` | 충전 화면, 잔액과 차감 표시, 결제 결과 처리 | 미작성 |
| `ANDROID/` | 충전 화면, 잔액과 차감 표시, 결제 결과 처리 | 미작성 |

- 세트마다 `DECISIONS.md`를 두고 이 도메인 결정의 이력을 기록한다. 기존 ADR 항목은 이관하면서 옮긴다.
- 세트 사이에 같은 사실을 두 번 정하지 않는다. 계약은 정하는 쪽(BACKEND의 계약 문서)이 기준이고 다른 세트는 참조한다.

<br>

### 2. 이관 원본

아래 기존 문서의 해당 절을 이 도메인으로 옮긴다. 이관이 끝날 때까지 기존 문서가 기준이다.

- `docs/spec/2-user-stories.md 2-10`
- `docs/spec/3-2-web-spec.md 3-2-6`
- `docs/spec/3-3-android-spec.md 3-3-6`
- `docs/spec/4-backend-server-spec.md 이프·결제 API와 데이터 모델`
- `docs/design/2-backend-server-design.md 2-3 원장과 동시성`
- `docs/adr/2-backend-server-adr.md BE-009~012, 033`
