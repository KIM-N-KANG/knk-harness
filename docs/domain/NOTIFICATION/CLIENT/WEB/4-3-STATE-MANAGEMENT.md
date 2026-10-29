# 4-3 웹 NOTIFICATION 상태 관리

기준: [공통 상태](../4-3-STATE-MANAGEMENT.md), [웹 구성](4-2-COMPONENT-ARCHITECTURE.md).

<br>

### 4-3-1 저장과 캐시

| 위치 | 값과 수명 |
|---|---|
| localStorage | manyak:notice-read-ids, 읽은 공지 ID JSON 배열 최대 100개, 기기 귀속 |
| Query 캐시 | 공지 무한 목록과 상세. 알림은 category별 infinite 목록, 회원 판정 전 조회 비활성 |
| 읽음 스냅숏 | /api/v1/users/me/notifications 접두어의 모든 분류 페이지. 모두 읽음 실패 때 복원 |
| localStorage | manyak:push-token, 등록에 성공한 토큰. 회원 종료 때 삭제 요청과 SDK 폐기 |
| 기기 플래그 | manyak:push-permission-asked, 권한을 한 번 물었는지 판정 |
| 회원 기록 | manyak:marketing-consent:{userId}, 첫 거절과 재진입 및 재질문 종료 |
| 탭 외부 스토어 | 첫 질문 답과 재질문 신호, 루트 시트가 구독 |

공지 상세를 받으면 ID를 최신으로 옮기며 구독한 목록과 배지가 같은 기록을 읽는다. 서버 렌더의 푸시 지원 스냅숏은 미지원으로 둔다. 회원 상태가 해제되거나 컴포넌트가 해제되면 토큰 재동기화 이벤트 리스너를 제거한다.
