# 3-1 화면 구성: 웹

기준: [공통 화면](../3-1-INFORMATION-ARCHITECTURE.md), [웹 요구사항](2-2-REQUIREMENTS.md).

<br>

### 3-1-1 URL과 접근

| 화면 | URL | 조건 |
|---|---|---|
| 공지 목록 | /notices | 게스트와 회원 |
| 공지 상세 | /notices/[noticeId] | 게스트와 회원, 공지 푸시 링크와 같은 경로 |
| 알림함 | /notifications | 회원, 게스트는 로그인으로 replace |
| 알림 설정 | /my/notifications | 회원, 게스트는 로그인으로 replace |

홈, 채팅과 제작 헤더는 게스트 로그인 버튼 오른쪽에 공지 확성기, 회원은 종 버튼 하나를 둔다. 회원 판정 전에는 공간을 유지한 빈 자리로 두어 공지에서 알림으로 깜빡이지 않게 한다. 마이 헤더에는 두지 않는다.
