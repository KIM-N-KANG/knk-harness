# MODERATION

게시물 검수, 15세 이용가 모드, 사용자 입력 검수를 다룬다. 지금은 단순한 검수만 두고 위반 패턴 수집과 벤치마크는 규모가 커진 뒤 확장한다.

세트별 명세는 하위 폴더에 두고, 각 세트의 문서 역할과 읽는 순서는 그 폴더의 `CLAUDE.md`가 안내한다. 파일 구성은 세트 종류별 작성 가이드를 따르며 해당 없는 문서는 만들지 않는다. ([제품 Spec 작성 가이드](../../REFERENCE/PRODUCT-SPEC-WRITING-GUIDE.md), [AI](../../REFERENCE/AI-SPEC-WRITING-GUIDE.md) · [백엔드](../../REFERENCE/BACKEND-SPEC-WRITING-GUIDE.md) · [클라이언트](../../REFERENCE/CLIENT-SPEC-WRITING-GUIDE.md) 명세 작성 가이드)

<br>

### 1. 세트

| 세트 | 다루는 것 | 상태 |
|---|---|---|
| `AI/` | 검수 판정, 재시도와 보류, 15세 모드 프롬프트 | 미작성 |
| `BACKEND/` | 검수 요청과 상태, 제출본 식별, 결과 반영과 노출 제한 | 미작성 |
| `WEB/` | 검수 상태 표시, 반려 안내 | 미작성 |
| `ANDROID/` | 검수 상태 표시, 반려 안내 | 미작성 |

- 세트마다 `DECISIONS.md`를 두고 이 도메인 결정의 이력을 기록한다. 기존 ADR 항목은 이관하면서 옮긴다.
- 세트 사이에 같은 사실을 두 번 정하지 않는다. 계약은 정하는 쪽(BACKEND의 계약 문서)이 기준이고 다른 세트는 참조한다.

<br>

### 2. 이관 원본

아래 기존 문서의 해당 절을 이 도메인으로 옮긴다. 이관이 끝날 때까지 기존 문서가 기준이다.

- `docs/spec/3-2-web-spec.md 3-2-7`
- `docs/spec/3-3-android-spec.md 3-3-7`
- `docs/spec/4-backend-server-spec.md 검수 API`
- `docs/spec/5-ai-server-spec.md 검수 절`
- `docs/design/3-ai-server-design.md 3-5 게시물 검수의 구현 상태`
