# STORY

스토리 탐색, 간편·일반 제작, 상세, 공개와 공유, 검색, 오리지널 스토리를 다룬다. 검색은 스토리에서만 쓰므로 별도 도메인으로 두지 않는다.

세트별 명세는 하위 폴더에 두고, 각 세트의 문서 역할과 읽는 순서는 그 폴더의 `AGENTS.md`가 안내한다. 파일 구성은 세트 종류별 작성 가이드를 따르며 해당 없는 문서는 만들지 않는다. ([제품 Spec 작성 가이드](../../reference/PRODUCT-SPEC-WRITING-GUIDE.md), [AI](../../reference/AI-SPEC-WRITING-GUIDE.md) · [백엔드](../../reference/BACKEND-SPEC-WRITING-GUIDE.md) · [클라이언트](../../reference/CLIENT-SPEC-WRITING-GUIDE.md) 명세 작성 가이드)

<br>

### 세트

| 세트 | 다루는 것 |
|---|---|
| [`AI/`](AI/AGENTS.md) | 스토리라인 생성, 컴파일, 인물 이미지와 썸네일 생성 |
| [`BACKEND/`](BACKEND/AGENTS.md) | 스토리 저장과 조회, 제작 흐름, 초안, 공개 스냅샷, 검색 색인, AI 서버 호출 |
| [`CLIENT/`](CLIENT/AGENTS.md) | 탐색, 상세, 간편 제작과 일반 제작의 공통 계약, WEB과 ANDROID의 플랫폼 구현 및 검증 |

- 세트마다 `DECISIONS.md`를 두고 이 도메인 결정의 이력을 기록한다.
- 세트 사이에 같은 사실을 두 번 정하지 않는다. 계약은 정하는 쪽(BACKEND의 계약 문서)이 기준이고 다른 세트는 참조한다.
