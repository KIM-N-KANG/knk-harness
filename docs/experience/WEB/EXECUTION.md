# 웹 앱 실행

기준: [상태 관리](STATE-MANAGEMENT.md).

<br>

### 이동과 레이어 정리

1. Navigation API의 현재 바로 아래 기록에서 더미를 제외하고 같은 문서인지 판정한다. API 미지원은 문서 진입 이후 history.length 증가에서 더미를 제외한 값으로 판정한다. replace는 진입 기록으로 간주하지 않는다.
2. 헤더 뒤로가기는 기록이 있으면 back, 없으면 도메인의 기본 경로로 replace한다. 탭은 replace와 scroll=false를 사용한다.
3. 탭 복귀는 가장 가까운 아래 탭으로 history.go한 뒤 필요한 경우 다른 탭을 push한다. 기록이 없거나 이전 문서이면 replace한다.
4. 오버레이 push와 되감기는 큐로 직렬화한다. 더미 state는 null로 둔다. Next의 __NA 없는 객체 state에 따른 전체 리로드를 피한다.
5. 사용자 활성화가 없으면 더미를 쌓지 않으며 guard만 첫 pointerdown 또는 keydown에서 쌓는다. close는 소비, guard는 필요할 때 다시 적재한다.
6. 캡처 popstate는 최상위 주인에게만 전달한다. 잠금으로 열림이 유지되면 더미를 다시 쌓고 주인 없는 칸은 소비한다. 주소가 다르면 상태를 버리고 Next에 넘긴다.
7. 되감기 1초 안에 popstate가 없으면 큐를 비운다. 이탈 확인은 더미를 먼저 정리하고 실제 이전 화면으로 이동한다. 실제 이동 popstate는 Next에 전달해 URL과 DOM이 함께 바뀌게 한다.

<br>

### 레이아웃과 입력

루트와 루트 오류 화면은 100dvh를 쓰고 lang=ko, viewport-fit=cover와 안전 영역을 적용한다. iOS에서만 viewport maximum-scale=1을 추가하고 Next가 메타 요소를 교체하면 다시 적용한다. iOS 핀치 확대를 유지하며 Android의 핀치를 막지 않는다. 키보드는 VisualViewport와 화면 입력 로직으로 처리한다.

html과 body의 배경은 테마를 따르고 절대 위치 가상 요소가 프레임 밖 좌우 여백만 칠한다. 같은 너비 토큰을 사용하며 포인터 입력을 통과시킨다. Drawer의 바깥 넘침 장식을 제거하고 min-height=0인 내부 본문만 스크롤한다. 처리 중에는 포인터 닫기도 잠근다.

줄바꿈은 공용 규칙의 keep-all, break-word를 사용한다. p와 li에는 pretty, 제목에는 balance의 longhand를 적용해 nowrap을 덮어쓰지 않는다. 스트리밍 본문은 재배치 방지를 위해 auto이며 긴 flex 텍스트만 필요한 최소 폭과 anywhere 예외를 둔다.

지연 로딩 기본은 250ms, 장르 검색은 200ms다. 완료 즉시 내용을 보여주며 최소 표시 시간을 강제하지 않는다.

가로 마우스 드래그는 주 버튼과 5px 문턱으로 판정하고 뒤 클릭을 한 번 차단한다. 터치와 펜은 네이티브 스크롤을 쓴다. 스냅은 드래그 중 끄고 가까운 시작점으로 이동한 뒤 scrollend 또는 1초 상한에서 복원한다. 영역 진입 때 넘침을 측정하고 드래그 커서는 문서 루트에서 유지한다.

<br>

### 앱 안내와 인앱 브라우저

| 실행 | 처리 |
|---|---|
| 대상 판정 | UA, 터치, 설치 상태와 경로. 인앱은 알려진 토큰, Android wv, iOS Safari 부재를 함께 판단 |
| Android 앱 열기 | manyak 스킴과 app.manyak 패키지 intent. market_referrer에 배너 또는 공유 링크 귀속값. browser_fallback_url 없이 0.7초 뒤 스토어 앱 시도 |
| 스토어 귀속 | utm_source=manyak_web, utm_medium=app_banner 또는 share_link |
| iOS 외부 열기 | 카카오는 전용 openExternal, Instagram과 Threads는 iOS x-safari 또는 Android intent, 그 밖의 iOS는 x-safari. 1.5초 실패 안내 |
| 반복과 숨김 | 이전 타이머 취소, 페이지가 한 번 숨겨졌으면 복귀해도 실패 안내 없음 |
| 설치 안내 | Safari 버전으로 iPhone 26 이상 판정. 네 이미지 스냅 영역은 시트 스와이프 닫기에서 제외 |
| 닫기 포커스 | 아래 화면에 임시 tabindex=-1로 포커스, blur 뒤 제거 |
| 앱 공유 | 서버 HTML에 미리보기 제공, 클라이언트 자동 이동. pageshow.persisted이면 이전 대기 취소 |

인앱 감지는 서버에서 false이며 클라이언트 판정만으로 진입을 차단하거나 자동 탈출하지 않는다. 호스트의 당겨 닫기를 막는 문서 앵커는 body 아래 1px을 확보하고 scroll=0만 1로 복구한다. 키보드 때문에 1보다 내려간 위치는 되돌리지 않으며 안쪽 overscroll-contain을 유지한다. 소셜 로그인은 ACCOUNT의 팝업 흐름을 따른다.

<br>

### 메타데이터

canonical은 각 페이지가 소유하며 루트에 홈 canonical을 두지 않는다. 공유 조회 실패는 기본 제목과 noindex, nofollow를 반환하되 클라이언트 조회를 유지한다. WebSite와 Organization JSON-LD에 alternateName과 공식 SNS sameAs를 포함하고 인라인 JSON의 <를 이스케이프한다.
