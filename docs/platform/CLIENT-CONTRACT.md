# 공용 클라이언트 연동 계약

기준: [요구사항](../experience/REQUIREMENTS.md), [화면 표현](../experience/LAYOUT.md).

<br>

### 식별 정보

| 값 | 의미와 처리 |
|---|---|
| `X-Manyak-Device-Id` | 분석의 논리 device_id와 같은 값. 일반 요청에서 누락 가능하나 게스트 체험 대상과 최초 회원 체험 시드에서는 필수 |
| `X-Manyak-Session-Id` | 분석의 논리 session_id. 모든 경로에서 best-effort |
| 헤더 누락 | 일반 요청은 거부하지 않고 서버에서 unknown으로 보완. 필수 device ID 누락은 서버 계약의 오류 처리 |
| `X-Manyak-Request-Id` | 백엔드가 생성해 응답하는 상관관계 값. 클라이언트가 생성하지 않음 |
| 제작 본문 `requestId` | 제작 멱등과 복구용 별도 값. 응답 request ID와 혼용하지 않음 |

식별자 수명과 수집 제한은 [분석 기준](../reference/ANALYTICS.md#식별자-정책)을 따른다. 게스트와 최초 회원의 체험 조건은 [PAYMENT 계약](../domain/PAYMENT/CLIENT/CONTRACT.md), 인증 정보는 [ACCOUNT 계약](../domain/ACCOUNT/CLIENT/CONTRACT.md)을 따른다.

<br>

### 응답과 날짜

| 입력 | 처리 |
|---|---|
| 오류 응답 | `ApiErrorResponse {timestamp, status, code, message, path, details[]}`. details는 `{field, message}[]` |
| 삭제 204 | 완료 안내와 목록 반영 |
| 삭제 404 | 무음 성공으로 목록 반영 |
| 다른 삭제 실패 | 낙관적 제거 복원과 실패 안내 |
| 수정 요청 403 | “수정 권한이 없어요” 안내 후 상세 복귀. 수정 폼 최초 조회 실패는 도메인 진입 계약으로 구분 |
| 서버 시각 | createdAt, expiresAt, updatedAt은 ISO 8601 UTC |
| 절대 날짜 | 이프 내역 발생일과 만료일, 상세와 제작 카드 날짜는 Asia/Seoul로 변환한 YYYY-MM-DD. 문자열 앞 열 글자 자르기와 기기 시간대 사용 금지 |
| 상대 날짜 | 채팅 목록의 상대 시간과 오늘 및 어제는 기기 시간대. 웹 제작 카드의 당일 상대 표시는 STORY의 예외 적용 |

채팅 입력 출처와 선택지 연결은 [CHAT 계약](../domain/CHAT/CLIENT/CONTRACT.md), 제작의 부모 요청 연결은 [STORY 계약](../domain/STORY/CLIENT/CONTRACT.md)을 따른다. 회원 정보 조회를 별도의 인증 판정으로 사용하지 않는다.
