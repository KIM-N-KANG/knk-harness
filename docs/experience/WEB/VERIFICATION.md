# 웹 공용 검증

기준: [공통 검증](../VERIFICATION.md), [웹 실행](EXECUTION.md).

기존 QA의 ID, 조건과 자동화 연결을 보존한다. 자동화 표시는 이번 실행이나 배포 완료가 아니다. MY-NAV-05의 회원 공지 버튼은 알림함 도입 전 기록이다. 현재 회원 헤더는 NOTIFICATION의 알림함 버튼으로 판정한다.

<br>

### 마이 메뉴와 테마

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
|---|---|---|---|---|---|---|
| MY-MENU-02 | P1 | 게스트 | 메뉴·카드 구성 확인 | 화면(테마 변경)·알림(공지사항만, 알림 설정 없음)·기타(서비스 안내·피드백) 섹션만 표시. 이벤트(친구 초대)·계정(로그아웃·회원 탈퇴) 섹션과 이프 카드는 없음 | ✅ e2e `my/my-page`·`visual/my-visual` | FE-SCREEN-008 |
| MY-MENU-05 | P1 | 회원 | 메뉴 구성 확인 | 이벤트(친구 초대) / 화면(테마 변경) / 알림(알림 설정 → 공지사항 순) / 기타(서비스 안내 → 피드백 순) / 계정(기본 전경색 로그아웃 → 위험색 회원 탈퇴 순) 5개 섹션 표시 | ✅ e2e `visual/my-visual` | FE-SCREEN-008, FE-SCREEN-011 진입점 |
| MY-MENU-17 | P1 | 게스트/회원 | 피드백 메뉴 탭 | `/my/feedback`으로 이동 | ◐ e2e `my/my-page`(링크 표시만) | CHAT-US-016, [웹 라우팅](INFORMATION-ARCHITECTURE.md#셸과-문서) |
| MY-MENU-18   | P1  | 게스트/회원                                       | 테마 변경 메뉴 반복 탭      | 시스템 설정 → 라이트 모드 → 다크 모드 순으로 순환. 왼쪽 아이콘(모니터·해·달)과 오른쪽 문구가 함께 바뀌고 테마 즉시 적용 | ✅ e2e `my/my-page`                            | 구현(`theme-menu-item`)                      |

<br>

### 서비스 안내

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
|---|---|---|---|---|---|---|
| MY-INFO-01 | P1 | 게스트/회원 | 마이 기타 섹션 "서비스 안내" 메뉴(피드백 위) 탭 | 메뉴 오른쪽에 새 창 아이콘 표시. 원래 `/my` 탭을 유지한 채 새 탭에서 `/about`을 열고, 뒤로가기 없는 링크 없는 마냑 로고 헤더 아래 본문 `h1` "서비스 안내"와 게스트 이용 안내·AI 콘텐츠 안내 등 섹션 표시. 게스트 이용 안내 제목 아래에 웹 브라우저 전용 안내 표시 | ✅ e2e `my/service-info`·`visual/my-visual` | CLIENT-US-002, FE-SCREEN-011 진입점 |
| MY-INFO-02 | P1 | 페이지 표시됨 | 이프 안내 섹션이 없는지 확인 | "이프 안내" 제목과 이프 수치 고지 문구가 화면에 없어야 함. 수치는 각 사용 지점(STORY-INFO-10·CHAT-INPUT-20·MY-CREDITS-17·MY-MENU-22)이 서버 값으로 표시 | ✅ e2e `my/service-info` | FE-SCREEN-011 콘텐츠 규칙, §3-1-7 이프 정책 수치 표시, KNK-1095 |
| MY-INFO-03 | P1 | 페이지 표시됨 | 게스트 이용 안내 문구 확인 | FE-SCREEN-011의 게스트 동의 후 체험, 브라우저 저장 한계와 최초 로그인 1회 이관 안내를 표시하고 체험 한도 수치는 복제하지 않음 | ✅ e2e `my/service-info` | FE-SCREEN-011, 웹 사용자 모델 |
| MY-INFO-05 | P2 | 페이지 표시됨 | 문의 섹션 확인 | 회원 탈퇴 문구·탈퇴 문의 이메일은 표시되지 않고, 피드백 위치 안내가 링크 없는 텍스트로 표시됨 | ✅ e2e `my/service-info` | FE-SCREEN-011, KNK-1068 |
| MY-INFO-06 | P2 | `/about` 직접 진입 | 헤더의 마냑 로고 탭 | 로고는 링크가 아니라 이동하지 않음. 헤더에 링크 없음 | ✅ e2e `my/service-info` | [웹 문서 열람](REQUIREMENTS.md#지원과-접근성) |
| MY-INFO-07 | P2 | 게스트/회원 각각 | `/about` 직접 진입 | 라우트 가드 없이 양쪽 모두 동일한 본문 열람 가능 | ◐ e2e `my/service-info`(게스트만) | FE-SCREEN-011 검수 기준 |
| MY-INFO-08 | P1 | 페이지 표시됨 | 브라우저 탭 제목 확인 | "서비스 안내 - 마냑" 표시 | ✅ e2e `my/service-info` | FE-SCREEN-011, [웹 문서 제목](REQUIREMENTS.md#지원과-접근성) |

<br>

### 내비게이션

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
|---|---|---|---|---|---|---|
| MY-NAV-01 | P0 | 임의 탭 화면 | 하단 탭 구성 확인 | 홈·채팅·제작·마이 순서의 4개 링크. 각 링크에 24px 아이콘과 보이는 라벨을 함께 표시 | ✅ e2e `my/my-page`·`smoke/navigation` | CLIENT-US-001, [웹 탭 이동](EXECUTION.md#이동과-레이어-정리), KNK-988 |
| MY-NAV-02 | P0 | 홈에서 시작 | 탭으로 홈 → 채팅 → 제작 → 마이 → 홈 순회 | 각 경로(`/`·`/chats`·`/studio`·`/my`)로 이동. 홈은 로고만, 나머지는 섹션 라벨이 표시됨 | ✅ e2e `smoke/navigation` | CLIENT-US-001, [웹 라우팅](INFORMATION-ARCHITECTURE.md#셸과-문서), KNK-988·994·1012 |
| MY-NAV-03 | P1 | 임의 탭 화면 | 활성 탭 표시 확인 | 모든 아이콘·라벨에 같은 전경색을 적용. 현재 경로와 정확히 일치하는 탭에만 filled 아이콘·`aria-current="page"`를 적용하고 나머지는 outline 아이콘 | ✅ e2e `smoke/navigation` | [웹 라우팅](INFORMATION-ARCHITECTURE.md#셸과-문서), KNK-988 |
| MY-NAV-04 | P1 | 홈 → 채팅 → 제작 → 마이 순 탭 이동 | 브라우저 뒤로가기 | 탭 이동은 `replace`라 히스토리에 쌓이지 않음(탭 전환 이력을 되짚지 않고 탭 진입 이전 화면·이탈로 이동) | 수동 | [웹 화면 전환](INTERACTION-FLOWS.md#기록과-뒤로가기) |
| MY-NAV-05 | P1 | 각 탭 화면 | 상단 헤더 확인 | 홈은 로고만 보이고 `h1` "홈"은 `sr-only`. 채팅·제작·마이는 20px semibold 섹션 라벨을 보더 없이 표시. 게스트의 홈·채팅·제작에는 오른쪽 secondary 로그인 버튼과 그 오른쪽 공지사항 아이콘 버튼을, 회원에게는 공지사항 버튼만 표시하고 마이에는 둘 다 표시하지 않음(공지 케이스는 MY-NOTICES) | ✅ e2e `smoke/navigation`·`stories/story-list` | [웹 헤더](LAYOUT.md#셸과-공용-요소), KNK-988·1012 |
| MY-NAV-06 | P1 | `/my/feedback`·`/my/invite`·`/my/account-deletion`·`/login` | 각 화면 진입 | 상단 헤더·하단 탭 없이 뒤로가기 헤더만 표시 | 수동 | [웹 검수](#마이-메뉴와-테마) |
| MY-NAV-07 | P2 | 하단 안전 영역이 있는 기기(iOS 등) | 하단 탭 확인 | 링크 상하 패딩 16px + `safe-area-inset-bottom` 추가 확보로 탭이 잘리지 않음 | ◐ e2e `smoke/navigation`(패딩만) | [웹 검수](#마이-메뉴와-테마) |
| MY-NAV-08 | P2 | 구경로 `/more`·`/more/invite`·`/more/feedback` 진입 | 관찰 | 리다이렉트 없이 Not Found 표시(구경로 shim을 두지 않는 방침) | 수동 | [웹 화면 전환](INTERACTION-FLOWS.md#기록과-뒤로가기) |
| MY-NAV-09 | P1 | iOS Safari 실기기, 회원 또는 게스트 | 아무 화면을 새로고침한 뒤 하단 탭으로 다른 화면에 이동 → 입력 칸(예: 마이 > 피드백 본문)을 탭 → 두 손가락으로 벌림 | 입력 칸에 포커스해도 화면이 확대되지 않고, 두 손가락으로 벌리면 확대됨. Android Chrome에서도 두 손가락 확대가 됨 | ◐ e2e `smoke/ios-input-zoom-lock`(viewport 값만) | [웹 모바일 검수](REQUIREMENTS.md#지원과-접근성), [웹 레이아웃](EXECUTION.md#이동과-레이어-정리), KNK-1605 |
| MY-NAV-10 | P2 | 없는 경로 | 새 탭·외부 링크로 바로 진입 / 사이트 안에서 이동해 진입 | "페이지를 찾을 수 없어요"와 홈 링크. 같은 사이트의 이전 기록이 있을 때만 "이전 화면으로" 버튼이 함께 보이고 누르면 이전 화면으로 돌아감 | ✅ e2e `smoke/navigation` | 웹 Spec 라우팅 FE-SCREEN-999, KNK-1613 |

<br>

### 문서 배경

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
|---|---|---|---|---|---|---|
| MY-BACKGROUND-01 | P2 | 모바일 폭, 게스트 또는 회원 | 마이에서 라이트, 다크, 시스템 테마를 전환하고 화면 이동 | 문서와 앱 배경이 같은 테마로 이어지고 가로 스크롤이 없음 | 수동 | [웹 반응형 계약](LAYOUT.md#셸과-공용-요소) |
| MY-BACKGROUND-02 | P2 | 앱 셸보다 넓은 데스크톱 화면 | 창 크기를 셸 너비 전후로 바꾸고 테마 전환 및 하단 탭 조작 | 중앙 셸 너비 유지, 좌우 여백만 별도 배경 표시, 배경 장식이 입력을 차단하지 않음 | 수동 | [웹 반응형 계약](LAYOUT.md#셸과-공용-요소) |
| MY-BACKGROUND-03 | P2 | iOS Safari와 홈 화면 설치 PWA 실기기 | 첫 진입, 화면 이동, 테마 변경, Safari 도구 막대 표시 전환, PWA 카카오 로그인 복귀 및 키보드 열기와 닫기 후 상하 안전 영역 확인 | 문서 배경이 앱과 이어지고 앱 프레임이 동적 뷰포트 높이를 따름. 하단 빈 공간이나 탭 및 입력 영역 가림이 없음. 브라우저 자체 툴바 효과는 제외 | 수동 | [웹 반응형 계약](LAYOUT.md#셸과-공용-요소) |
| MY-BACKGROUND-04 | P2 | 루트 오류 화면, 모바일과 데스크톱 폭 | 라이트 및 다크 테마에서 오류 화면 확인 | 일반 화면과 동일한 문서 배경 및 좌우 여백 규칙과 동적 뷰포트 높이 적용 | 수동 | [웹 반응형 계약](LAYOUT.md#셸과-공용-요소) |

<br>

### 앱 안내 배너

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
|---|---|---|---|---|---|---|
| ONBD-BANNER-01 | P0 | Android Chrome, 첫 접속 | 홈 진입 | 헤더 위에 Android 배너(앱 아이콘, 앱 이름과 문구 두 줄, 앱 열기, 닫기) 표시 | ✅ e2e `smoke/app-banner` | [앱 안내 배너](LAYOUT.md#셸과-공용-요소) |
| ONBD-BANNER-02 | P1 | Android Chrome | 새 탭으로 2, 3, 4번째 접속 | 2, 4번째는 미노출, 3번째는 노출 | ✅ e2e `smoke/app-banner` | 같음 |
| ONBD-BANNER-03 | P0 | Android 카카오톡 인앱 | 접속할 때마다 진입 | 매 접속 Android 배너 표시 | ✅ e2e `smoke/app-banner` | 같음 |
| ONBD-BANNER-04 | P0 | Android, KNK-1632 반영 앱 설치 | 스토리 상세에서 앱 열기 | 앱이 열리고 같은 스토리 상세로 진입 | ◐ e2e `smoke/app-banner`(링크 주소만) | 같음, KNK-1632 |
| ONBD-BANNER-05 | P0 | Android, 앱 미설치 | 앱 열기 | 플레이스토어 앱의 마냑 페이지가 열림. 인앱 브라우저에서도 Play 웹페이지가 아니라 플레이스토어 앱으로 이동 | 수동 | 같음 |
| ONBD-BANNER-06 | P1 | Android, 앱 설치 | 스토리 상세가 아닌 화면에서 앱 열기 | 앱 홈이 열림 | ◐ e2e `smoke/app-banner`(링크 주소만) | 같음 |
| ONBD-BANNER-07 | P0 | iOS 카카오톡, 인스타그램 인앱 | 열기 | 외부 브라우저에서 같은 화면이 열림 | 수동 | 같음 |
| ONBD-BANNER-08 | P1 | iOS 인앱, 외부 전환이 막힌 앱 | 열기 후 1.5초 대기 | 외부 브라우저 안내 시트가 열리고 링크 복사하기로 현재 주소가 복사됨 | ✅ e2e `smoke/app-banner`(시트 표시) | 같음 |
| ONBD-BANNER-09 | P1 | iPhone Safari 26 이상, 첫 접속 | 추가하기, 기기 뒤로가기 | 스크린샷 4장 안내 시트가 열리고 뒤로가기로 닫히며 화면은 그대로 | ✅ e2e `smoke/app-banner` | 같음 |
| ONBD-BANNER-10 | P1 | iOS, 안내대로 홈 화면에 추가 | 홈 화면 아이콘으로 실행 | 배너가 보이지 않음 | 수동 | 같음 |
| ONBD-BANNER-11 | P1 | Android Chrome, 첫 접속 | 닫기, 같은 탭 새로고침, 새 탭으로 2, 3번째 접속 | 닫은 탭에서는 다시 보이지 않고 3번째 접속에 다시 표시 | ✅ e2e `smoke/app-banner` | 같음 |
| ONBD-BANNER-12 | P1 | Android Chrome, 데스크톱 | 서비스 안내, 이용약관, 개인정보 처리방침, 데스크톱 홈 진입 | 배너 미노출. 문서 화면만 본 접속은 세지 않음 | ✅ e2e `smoke/app-banner` | 같음 |
| ONBD-BANNER-13 | P2 | 기기 동작 줄이기 설정 | 배너 표시와 닫기 | 높이 애니메이션 없이 표시되고 사라짐 | 수동 | 같음 |
| ONBD-BANNER-14 | P2 | Android Chrome, 홈 목록 스크롤 | 배너 닫기 후 탭 전환 왕복 | 탭별 스크롤 위치 복원이 어긋나지 않음 | 수동 | 같음 |
| ONBD-BANNER-15 | P2 | Android, 앱 미설치 | 앱 열기로 설치 | Play Console 설치 귀속에 `utm_source=manyak_web`, `utm_medium=app_banner`가 남음 | 수동 | 같음 |
| ONBD-BANNER-16 | P1 | iOS Chrome 또는 iOS 18 이하 Safari, 첫 접속 | 추가하기 | 스크린샷 없이 텍스트 2단계와 공유 버튼 안내가 보임 | ✅ e2e `smoke/app-banner`(iOS Chrome) | 같음 |
| ONBD-BANNER-17 | P1 | iPhone Safari 26 실기기 | 안내 시트에서 스크린샷을 좌우로 넘기고 실제로 따라 하기 | 가로 스와이프가 시트 닫기와 겹치지 않고, 안내대로 홈 화면에 추가됨. 스크린샷에서 개인 정보가 보이지 않음 | 수동 | 같음 |
| ONBD-BANNER-18 | P2 | Android Chrome, 배너 표시 | 키보드나 스크린 리더로 닫기 | 배너가 사라지고 포커스가 배너 아래 화면으로 이동 | ✅ e2e `smoke/app-banner` | 같음 |
| ONBD-BANNER-19 | P2 | iOS 인앱 | 열기를 1.5초 안에 여러 번 누르기, 또는 전환된 뒤 1.5초 안에 돌아오기 | 실패 안내 이벤트는 한 번만 나가고, 전환됐다 돌아온 경우에는 실패 안내 시트를 띄우지 않음 | ✅ e2e `smoke/app-banner` | 같음 |
| ONBD-BANNER-20 | P0 | Android 인스타그램 인앱, 앱 미설치 | 앱 열기 후 0.7초 대기 | 플레이스토어 앱의 마냑 페이지가 열림. 카카오톡, Chrome에서는 플레이스토어가 한 번만 열림 | ◐ e2e `smoke/app-banner`(이동과 취소만) | 같음, [W-041](DECISIONS.md#w-041) |

<br>

### 앱 공유 링크

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
|---|---|---|---|---|---|---|
| ONBD-APPLINK-01 | P1 | 데스크톱 또는 iOS 브라우저 | `/app` 열기 | 웹 홈(`/`)으로 교체 이동하고 뒤로가기가 `/app`으로 돌아오지 않음 | ✅ e2e `smoke/app-share` | [앱 공유 링크](LAYOUT.md#셸과-공용-요소) |
| ONBD-APPLINK-02 | P0 | 카카오톡 스크래퍼 UA(`kakaotalk-scrap`) | `/app` 첫 HTML 요청 | `og:title`·`og:description`·`og:image`(절대 URL)·`og:url`(`/app`)·`twitter:card`가 들어 있고 `robots`는 `noindex, follow` | ✅ e2e `smoke/app-share` | 같음 |
| ONBD-APPLINK-03 | P0 | Android, 앱 미설치 | `/app` 열기 후 0.7초 대기 | 플레이스토어의 마냑 페이지가 열림(귀속값 `utm_medium=share_link`). 카카오톡 인앱은 외부 브라우저 열기를 거쳐 1.4초 안에 열림 | ◐ e2e `smoke/app-share`(카카오톡 UA의 이동만) | 같음 |
| ONBD-APPLINK-04 | P1 | Android, 앱 설치 | `/app` 열기 | 앱 홈이 열리고 플레이스토어는 열리지 않음. 앱에서 돌아오면 `/app`에 머물며 "Google Play에서 받기" 버튼이 보임 | ◐ e2e `smoke/app-share`(머무는 화면만) | 같음 |
| ONBD-APPLINK-05 | P2 | 실기기 카카오톡 대화방 | `https://manyak.app/app` 보내기 | 제목 "마냑", 홈 설명, 브랜드 이미지로 미리보기가 그려짐 | 수동 | 같음 |

<br>

CLIENT-US-001은 MY-NAV와 MY-BACKGROUND, CLIENT-US-002는 MY-INFO, CLIENT-US-003은 MY-MENU, CLIENT-US-004는 ONBD-BANNER와 ONBD-APPLINK로 연결한다. 새 케이스의 컬럼은 ID, P, 사전조건, 절차, 기대 결과, 자동화와 근거 순서다. 근거에는 현재 유저 스토리 ID와 계약을 연결한다.

MY-MENU-15, MY-INFO-04, ONBD-GUEST 전체, ONBD-INVITE-06과 ONBD-BANNER-21은 재사용하지 않는다. 통합과 폐기 근거는 Git 이력에 보존한다.
