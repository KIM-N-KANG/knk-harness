# NOTIFICATION

푸시 토큰, FCM과 웹 푸시, 알림 동의, 검수 완료 알림, 알림 서비스 분리를 다룬다. 다른 도메인과 결합도가 낮아 별도로 둔다.

세트별 명세는 하위 폴더에 두고, 각 세트의 문서 역할과 읽는 순서는 그 폴더의 `CLAUDE.md`가 안내한다. 파일 구성은 세트 종류별 작성 가이드를 따르며 해당 없는 문서는 만들지 않는다. ([제품 Spec 작성 가이드](../../REFERENCE/PRODUCT-SPEC-WRITING-GUIDE.md), [AI](../../REFERENCE/AI-SPEC-WRITING-GUIDE.md) · [백엔드](../../REFERENCE/BACKEND-SPEC-WRITING-GUIDE.md) · [클라이언트](../../REFERENCE/CLIENT-SPEC-WRITING-GUIDE.md) 명세 작성 가이드)

<br>

### 1. 세트

| 세트 | 다루는 것 | 상태 |
|---|---|---|
| `BACKEND/` | 토큰 등록과 정리, 발송 자격, 메시지 큐 중계, 알림 서비스 | 미작성 |
| `WEB/` | 권한 요청, 토큰 등록, 수신 처리와 이동 | 미작성 |
| `ANDROID/` | 권한 요청, 토큰 등록, 수신 처리와 이동 | 미작성 |

- 세트마다 `DECISIONS.md`를 두고 이 도메인 결정의 이력을 기록한다. 기존 ADR 항목은 이관하면서 옮긴다.
- 세트 사이에 같은 사실을 두 번 정하지 않는다. 계약은 정하는 쪽(BACKEND의 계약 문서)이 기준이고 다른 세트는 참조한다.

<br>

### 2. 이관 원본

아래 기존 문서의 해당 절을 이 도메인으로 옮긴다. 이관이 끝날 때까지 기존 문서가 기준이다.

- `docs/spec/3-3-android-spec.md 3-3-5`
- `docs/design/1-2-android-design.md 1-2-6 푸시와 알림`
- `docs/spec/4-backend-server-spec.md 알림 API`
- `docs/adr/2-backend-server-adr.md BE-035`
- `docs/adr/1-2-web-adr.md W-018`
- `docs/adr/1-3-android-adr.md A-032~034`
