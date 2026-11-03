# 4-3 상태 관리: 웹

<br>

### 4-3-1 저장과 수명

| 값 | 저장과 정리 |
|---|---|
| 상세와 목록 | Query 캐시. 상세는 진입마다 다시 읽고 첫 조회 종료 전 로딩 |
| 입력 모드 | localStorage `manyak:chat-input-mode`, `block` 또는 `plain` |
| 추천과 이미지 | localStorage `manyak:chat-choices-enabled`, `manyak:chat-realtime-image-enabled`, 문자열 true 또는 false |
| 모델과 긴 응답 | 서버 상세와 Query 캐시. 기기 저장 없음 |
| 투어와 추천 힌트 | localStorage `manyak:chat-tour-seen`, `manyak:chat-choices-hint-seen` |
| 이미지 안내 완료 횟수 | localStorage `manyak:chat-completed-turn-count`, 3에서 증가 중단 |
| 안내 예약과 표시 | 컴포넌트 수명. 생성 중 타이머 취소, 종료 뒤 재예약 |
| 스트림 | 현재 생성 ID, 진행 조각, 요청 스냅샷, 소진한 생성 ID, 진행 블록이 대신하는 턴 ID. 취소와 언마운트에서 수신 정리 |
| 메뉴 화면 | 메뉴 시트 컴포넌트 수명의 메뉴 또는 이프 내역. 시트를 열 때 메뉴로 초기화 |
| 입력 수정 편집 | 채팅방 컴포넌트 수명의 대상 턴 ID와 고치던 입력. 기기에 저장하지 않음 |
| 로딩 높이 | 대기가 흐름에 놓인 시점에 최소 높이를 보관. 첫 응답 뒤에 측정하지 않음 |
| 모델 배포 호환 | 상세에 모델 코드가 없으면 기존 정책의 턴 비용 사용. 코드가 있는데 목록에 없으면 비용 미확정 |

계정 귀속 목록과 로그인 전 입력 보관은 ACCOUNT 상태 관리에서 정한다. ([ACCOUNT 웹 상태](../../../ACCOUNT/CLIENT/WEB/4-3-STATE-MANAGEMENT.md), [공통 4-3](../4-3-STATE-MANAGEMENT.md))
