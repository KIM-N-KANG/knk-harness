# ACCOUNT

게스트와 회원 모델, 소셜 로그인, 동의, 게스트 데이터 이관, 프로필, 탈퇴와 재가입, 초대를 다룬다.

세트별 명세는 하위 폴더에 두고, 각 세트의 문서 역할과 읽는 순서는 그 폴더의 `AGENTS.md`가 안내한다. 파일 구성은 세트 종류별 작성 가이드를 따르며 해당 없는 문서는 만들지 않는다. ([제품 Spec 작성 가이드](../../reference/PRODUCT-SPEC-WRITING-GUIDE.md), [AI](../../reference/AI-SPEC-WRITING-GUIDE.md) · [백엔드](../../reference/BACKEND-SPEC-WRITING-GUIDE.md) · [클라이언트](../../reference/CLIENT-SPEC-WRITING-GUIDE.md) 명세 작성 가이드)

<br>

### 세트

| 세트 | 다루는 것 |
|---|---|
| [`BACKEND/`](BACKEND/AGENTS.md) | 소셜 인증과 동의, 세션과 토큰, 게스트 이관, 계정 연동, 프로필, 페르소나, 탈퇴와 재가입, 초대 |
| [`CLIENT/`](CLIENT/AGENTS.md) | 공통 계정 계약, WEB과 ANDROID의 차이, 구현과 검증 |

- 세트마다 `DECISIONS.md`를 두고 이 도메인 결정의 이력을 기록한다.
- 세트 사이에 같은 사실을 두 번 정하지 않는다. 계약은 정하는 쪽(BACKEND의 계약 문서)이 기준이고 다른 세트는 참조한다.
