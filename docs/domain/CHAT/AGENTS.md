# CHAT

채팅 목록, 채팅 플레이, SSE 스트리밍, 선택지, 실시간 인물 이미지, 엔딩, 응답 피드백을 다룬다.

세트별 명세는 하위 폴더에 두고, 각 세트의 문서 역할과 읽는 순서는 해당 폴더의 `AGENTS.md`에 정리한다. 파일 구성은 세트 종류별 작성 가이드를 따르며 해당 없는 문서는 만들지 않는다. ([제품 Spec 작성 가이드](../../reference/PRODUCT-SPEC-WRITING-GUIDE.md), [AI](../../reference/AI-SPEC-WRITING-GUIDE.md) · [백엔드](../../reference/BACKEND-SPEC-WRITING-GUIDE.md) · [클라이언트](../../reference/CLIENT-SPEC-WRITING-GUIDE.md) 명세 작성 가이드)

<br>

### 세트

| 세트 | 다루는 것 |
|---|---|
| [`AI/`](AI/AGENTS.md) | 턴 본문 생성, 선택지 생성, 실시간 이미지 생성, 평가 모델 |
| [`BACKEND/`](BACKEND/AGENTS.md) | 채팅 생성과 기록, 모델 선택과 모델별 차감, 턴 스트리밍 중계, 재생성, 선택지, 진행 상태와 엔딩 도달, 실시간 이미지, 공유, 피드백 |
| [`CLIENT/`](CLIENT/AGENTS.md) | 공통 플레이와 공유, 피드백, WEB과 ANDROID의 입력, 수신 및 복구, 상태와 검증 |

- 세트마다 `DECISIONS.md`를 두고 이 도메인 결정의 이력을 기록한다.
- 세트 사이에 같은 사실을 두 번 정하지 않는다. 다른 세트는 계약을 정한 쪽(BACKEND의 계약 문서)을 기준으로 삼는다.
