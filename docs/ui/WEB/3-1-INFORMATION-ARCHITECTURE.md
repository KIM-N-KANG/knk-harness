# 3-1 화면 구성: 웹

기준: [공통 화면](../3-1-INFORMATION-ARCHITECTURE.md), [웹 요구사항](2-2-REQUIREMENTS.md).

<br>

### 3-1-1 셸과 문서

| 경로 | 접근과 구성 |
|---|---|
| `/`, `/chats`, `/studio`, `/my` | 게스트와 회원, 네 탭과 상단 헤더 |
| `/about` | 게스트와 회원, 새 탭. 링크 없는 로고 헤더와 서비스 안내 |
| `/app` | 누구나, 앱 소개 미리보기와 기기별 이동, 앱 배너 없음 |
| 없는 경로 | 미존재 안내, 홈 링크. 같은 사이트의 이전 기록이 있을 때 이전 화면 버튼 |

법적 문서와 회원 하위 경로는 [ACCOUNT 경로](../../domain/ACCOUNT/CLIENT/WEB/3-1-INFORMATION-ARCHITECTURE.md), 작품은 [STORY 경로](../../domain/STORY/CLIENT/WEB/3-1-INFORMATION-ARCHITECTURE.md), 채팅과 피드백은 [CHAT 경로](../../domain/CHAT/CLIENT/WEB/3-1-INFORMATION-ARCHITECTURE.md), 이프는 [PAYMENT 경로](../../domain/PAYMENT/CLIENT/WEB/3-1-INFORMATION-ARCHITECTURE.md), 공지와 알림은 [NOTIFICATION 경로](../../domain/NOTIFICATION/CLIENT/WEB/3-1-INFORMATION-ARCHITECTURE.md)를 따른다.

`/create`는 `/studio`로, `/create/story`와 `/stories/new`는 `/studio/story/simple`로 영구 이동한다. `/studio/story`는 현재 제작 방식 선택이다. 과거 영구 이동 응답을 저장한 브라우저는 간편 제작으로 바로 갈 수 있다. `/more` 계열의 구경로는 미존재 화면이며 별도 호환 경로를 두지 않는다.
