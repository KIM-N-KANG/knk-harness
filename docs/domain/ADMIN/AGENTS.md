# ADMIN

관리자 인증과 권한, 감사 로그, 운영 대시보드 지표, 회원 조회를 다룬다. 다른 도메인 데이터를 바꾸는 운영 기능은 그 데이터를 관리하는 도메인이 정하고 ADMIN은 관리자 자체의 것만 정한다.

세트별 명세는 하위 폴더에 두고 각 세트의 문서 역할은 그 폴더의 `AGENTS.md`가 안내한다. 파일 구성은 세트 종류별 작성 가이드를 따르며 해당 없는 문서는 만들지 않는다. ([제품 Spec 작성 가이드](../../reference/PRODUCT-SPEC-WRITING-GUIDE.md), [AI](../../reference/AI-SPEC-WRITING-GUIDE.md), [백엔드](../../reference/BACKEND-SPEC-WRITING-GUIDE.md), [클라이언트](../../reference/CLIENT-SPEC-WRITING-GUIDE.md) 명세 작성 가이드)

<br>

### 세트

| 세트 | 다루는 것 |
|---|---|
| [`BACKEND/`](BACKEND/AGENTS.md) | 관리자 로그인과 토큰, 권한 판정, 감사 로그, 대시보드 지표, 회원 조회 |
| [`WEB/`](WEB/AGENTS.md) | 관리자 페이지의 사이드바, 대시보드 그룹의 개요와 도메인별 지표 화면, 이프 내역, BFF 호출, 쿠키 보관 |

- 세트마다 `DECISIONS.md`를 두고 이 도메인 결정의 이력을 기록한다.
- 세트 사이에 같은 사실을 두 번 정하지 않는다. 계약은 정하는 쪽(BACKEND의 계약 문서)이 기준이고 다른 세트는 참조한다.
