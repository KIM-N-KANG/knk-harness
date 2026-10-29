# NOTIFICATION

푸시 토큰, FCM과 웹 푸시, 알림 동의, 검수 완료 알림, 알림 서비스 분리를 다룬다. 다른 도메인과 결합도가 낮아 별도로 둔다.

세트별 명세는 하위 폴더에 두고, 각 세트의 문서 역할은 그 폴더의 `AGENTS.md`가 안내한다. 파일 구성은 세트 종류별 작성 가이드를 따르며 해당 없는 문서는 만들지 않는다. ([제품 Spec 작성 가이드](../../reference/PRODUCT-SPEC-WRITING-GUIDE.md), [AI](../../reference/AI-SPEC-WRITING-GUIDE.md) · [백엔드](../../reference/BACKEND-SPEC-WRITING-GUIDE.md) · [클라이언트](../../reference/CLIENT-SPEC-WRITING-GUIDE.md) 명세 작성 가이드)

<br>

### 세트

| 세트 | 다루는 것 |
|---|---|
| [`BACKEND/`](BACKEND/AGENTS.md) | 토큰 등록과 정리, 발송 자격, 메시지 큐 중계, 알림 서비스 |
| [`CLIENT/`](CLIENT/AGENTS.md) | 공지와 알림함, 푸시 등록과 수신 및 동의, WEB과 ANDROID 구현 및 검증 |

- 세트마다 `DECISIONS.md`를 두고 이 도메인 결정의 이력을 기록한다.
- 세트 사이에 같은 사실을 두 번 정하지 않는다. 계약은 정하는 쪽(BACKEND의 계약 문서)이 기준이고 다른 세트는 참조한다.
