# 4-3 상태 관리: 안드로이드

기준: [공통 상태](../4-3-STATE-MANAGEMENT.md), [Android 구성](4-2-COMPONENT-ARCHITECTURE.md).

<br>

### 4-3-1 저장 위치와 수명

| 상태 | 기준 |
|---|---|
| 공지 읽음 | 기기 DataStore notice_read_ids의 최신순 JSON 배열, UserScopedStore에 참여하지 않음 |
| 공지 안 읽음 | 셸 수명 ViewModel이 목록 첫 페이지와 읽은 ID 흐름으로 계산. 첫 페이지 20건 범위 |
| 알림함 | 회원 그래프 ViewModel의 두 분류 목록과 선택, 디스크 복제 없음. 탭별 스크롤은 저장 가능한 화면 상태 |
| 알림 읽음 | 목록과 읽음 요청을 같은 Mutex로 직렬화. 모두 읽음 실패는 양쪽 목록과 수 복원 |
| 토큰 | 앱 수명 등록기. 동일 세션 generation의 성공한 같은 토큰 중복 등록 없음. 별도 토큰 저장과 재전송 큐 없음 |
| 보류 진입 | 루트 ViewModel과 SavedStateHandle. 프로세스 복원 때 최초 Intent를 다시 읽지 않음 |
| 광고 질문 | 회원 DataStore marketing-consent. 거절 0, 1, 2와 첫 거절 뒤 재진입 횟수. 이전 물었음 값은 한 번 거절로 해석 |
| 권한 질문 | 설치 단위 플래그. 로그아웃에 유지 |
| 검수 화면 | 프로세스 메모리의 대기 제출본과 표시 결과. 디스크 복원 안 함 |

공지 읽음 쓰기 실패는 조용히 무시해 다음에 점이 다시 보일 수 있다. 개인 표시 알림은 UserScopedStore 정리에서 cancelAll한다. 계정 전환을 넘어 수신 대기 메시지를 보관하지 않는다.
