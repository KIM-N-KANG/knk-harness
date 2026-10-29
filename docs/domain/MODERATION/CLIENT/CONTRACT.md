# MODERATION 클라이언트 연동 계약

기준: [요구사항](REQUIREMENTS.md), [화면 흐름](INTERACTION-FLOWS.md).

<br>

### 신고 API

제공자는 [STORY 백엔드 신고 계약](../../STORY/BACKEND/CONTRACT.md#신고)이다. 클라이언트 문서의 도메인 분류로 API 소유권을 옮기지 않는다.

| 항목 | 사용 |
|---|---|
| 요청 | 인증된 `POST /api/v1/stories/{storyId}/reports` |
| reason | SPAM, INAPPROPRIATE, ETC 중 선택한 하나 |
| detail | 선택 문자열, 최대 500자. 비어 있거나 공백뿐이면 null |
| 웹 변환 | 상세의 앞뒤 공백을 제거한 뒤 빈 값이면 null |
| Android 변환 | 공백뿐이면 null, 그 밖의 문자열은 유지 |
| 성공 | 201, 응답 본문 없음 |
| 실패 | 400 입력 오류, 403 정지 계정, 404 부재 및 접근 불가와 네트워크 오류를 성공으로 처리하지 않음 |

신고 이벤트는 [분석 계약](../../../reference/ANALYTICS.md#안드로이드-앱-보강-이벤트--phase-2--구현knk-1178)의 공용 이름과 source를 사용한다. 상세 입력 원문은 분석에 보내지 않는다.

<br>

### 검수 경계

일반 제작 제출본의 상태와 의미는 [MODERATION 백엔드 계약](../BACKEND/CONTRACT.md), 클라이언트의 폼 대응과 거절 입력 복원은 [STORY 연동 계약](../../STORY/CLIENT/CONTRACT.md)을 따른다. 신고 요청과 검수 제출본을 같은 요청으로 취급하지 않는다.
