# ACCOUNT

게스트와 회원 모델, 소셜 로그인, 동의, 게스트 데이터 이관과 핸드오프, 프로필, 탈퇴와 재가입, 초대를 다룬다.

세트별 명세는 하위 폴더에 두고, 각 세트의 문서 역할과 읽는 순서는 그 폴더의 `CLAUDE.md`가 안내한다. 파일 구성은 세트 종류별 작성 가이드를 따르며 해당 없는 문서는 만들지 않는다. ([제품 Spec 작성 가이드](../../REFERENCE/PRODUCT-SPEC-WRITING-GUIDE.md), [AI](../../REFERENCE/AI-SPEC-WRITING-GUIDE.md) · [백엔드](../../REFERENCE/BACKEND-SPEC-WRITING-GUIDE.md) · [클라이언트](../../REFERENCE/CLIENT-SPEC-WRITING-GUIDE.md) 명세 작성 가이드)

<br>

### 1. 세트

| 세트 | 다루는 것 | 상태 |
|---|---|---|
| `BACKEND/` | 인증과 세션, 토큰, 동의 기록, 이관, 프로필, 초대 코드 | 미작성 |
| `WEB/` | 로그인과 동의 흐름, 게스트 상태, 프로필 화면 | 미작성 |
| `ANDROID/` | 로그인과 동의 흐름, 게스트 상태, 프로필 화면 | 미작성 |

- 세트마다 `DECISIONS.md`를 두고 이 도메인 결정의 이력을 기록한다. 기존 ADR 항목은 이관하면서 옮긴다.
- 세트 사이에 같은 사실을 두 번 정하지 않는다. 계약은 정하는 쪽(BACKEND의 계약 문서)이 기준이고 다른 세트는 참조한다.

<br>

### 2. 이관 원본

아래 기존 문서의 해당 절을 이 도메인으로 옮긴다. 이관이 끝날 때까지 기존 문서가 기준이다.

- `docs/spec/2-user-stories.md 2-1, 2-9`
- `docs/spec/3-1-client-spec.md 3-1-6`
- `docs/spec/3-2-web-spec.md 3-2-2`
- `docs/spec/4-backend-server-spec.md 4-5 인증과 권한, 계정 API`
- `docs/adr/2-backend-server-adr.md BE-003~008, 022~027, 029, 034`
- `docs/adr/1-2-web-adr.md W-002~005, 011~016`
