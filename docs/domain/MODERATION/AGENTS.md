# MODERATION

게시물 검수, 15세 이용가 모드, 사용자 입력 검수를 다룬다. 지금은 단순한 검수만 두고 위반 패턴 수집과 벤치마크는 규모가 커진 뒤 확장한다.

세트별 명세는 하위 폴더에 두고, 각 세트의 문서 역할과 읽는 순서는 그 폴더의 `AGENTS.md`가 안내한다. 파일 구성은 세트 종류별 작성 가이드를 따르며 해당 없는 문서는 만들지 않는다. ([제품 Spec 작성 가이드](../../REFERENCE/PRODUCT-SPEC-WRITING-GUIDE.md), [AI](../../REFERENCE/AI-SPEC-WRITING-GUIDE.md) · [백엔드](../../REFERENCE/BACKEND-SPEC-WRITING-GUIDE.md) · [클라이언트](../../REFERENCE/CLIENT-SPEC-WRITING-GUIDE.md) 명세 작성 가이드)

<br>

### 세트

| 세트 | 다루는 것 |
|---|---|
| `AI/` | 검수 판정, 재시도와 보류, 15세 모드 프롬프트 |
| [`BACKEND/`](BACKEND/AGENTS.md) | 검수 요청과 상태, 제출본 회차, 결과 반영과 노출 제한, 재시도와 보류, 용량 예산 |
| `CLIENT/` | 공통 클라이언트 계약과 하위 WEB, ANDROID 세트. 이관 전에는 기존 공통 Spec과 플랫폼 Spec, Design, ADR을 함께 확인 |

- 세트마다 `DECISIONS.md`를 두고 이 도메인 결정의 이력을 기록한다.
- 세트 사이에 같은 사실을 두 번 정하지 않는다. 계약은 정하는 쪽(BACKEND의 계약 문서)이 기준이고 다른 세트는 참조한다.
