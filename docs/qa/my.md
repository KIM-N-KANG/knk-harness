# my

## 문서 정보

| 항목 | 값 |
| --- | --- |
| 버전 | 미기재 |
| 작성일 | 미기재 |
| 수정일 | 2026-10-24 |
| 대상 | 마냑 웹 프론트엔드 |
| 작성 목적 | 마이 메뉴와 계정·이프·초대 기능의 수동 QA와 E2E 검수 기준을 정의합니다. |
| 화면 | 마이 메뉴 `/my`·회원 탈퇴 `/my/account-deletion`·친구 초대 `/my/invite`·이프 충전 `/my/credits`·페르소나 관리와 생성 `/my/personas`·프로필 수정 `/my/profile/edit`(FE-SCREEN-008), 피드백 `/my/feedback`(FE-SCREEN-006), 서비스 안내 `/about`(FE-SCREEN-011), 공지사항 `/notices`·`/notices/[noticeId]`(FE-SCREEN-014), 알림함 `/notifications`(FE-SCREEN-015), 하단 탭 네비게이션([§3-2-4](../spec/3-2-web-spec.md)) |
| 기준 코드 | [manyak-web `9ab592f`](https://github.com/KIM-N-KANG/manyak-web/tree/9ab592f698d0baaf15d96c80161a5924e5c7f73c). 실행 결과·릴리스 포함 여부는 별도 기록 |
| 관련 스펙 | [`3-1-client-spec.md §3-1-3(FE-SCREEN-006·008·011·014·015)·§3-1-8`](../spec/3-1-client-spec.md), [`3-2-web-spec.md §3-2-4·§3-2-5·§3-2-6`](../spec/3-2-web-spec.md), [`2-user-stories.md §2-7·§2-8·§2-9·§2-10`](../spec/2-user-stories.md) |
| 관련 E2E | `manyak-web/e2e/my/my-page.spec.ts`, `e2e/my/account-deletion.spec.ts`, `e2e/my/invite.spec.ts`, `e2e/my/credits.spec.ts`, `e2e/my/service-info.spec.ts`, `e2e/my/login-page.spec.ts`, `e2e/feedback/feedback.spec.ts`, `e2e/stories/story-persona.spec.ts`, `e2e/my/personas.spec.ts`, `e2e/my/profile.spec.ts`, `e2e/notices/notices.spec.ts`, `e2e/notifications/notifications.spec.ts`, `e2e/smoke/navigation.spec.ts`, `e2e/smoke/ios-input-zoom-lock.spec.ts`, `manyak-web/e2e/visual/my-visual.spec.ts` |

## 읽는 순서

- [QA 공통 규칙](AGENTS.md)과 문서 정보의 관련 Spec·E2E를 먼저 확인합니다.
- 담당 화면의 케이스에서 사전 조건 → 절차 → 기대 결과를 확인하고 검수합니다.

## 목차

- [MY-MENU — 마이 메뉴 `/my`](#my-menu--마이-메뉴-my)
- [MY-ACCOUNT-DELETION — 회원 탈퇴 `/my/account-deletion` (FE-SCREEN-008, KNK-1052)](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-13-my-account-deletion-회원-탈퇴-myaccount-deletion-fe-screen-008-knk-1052)
- [MY-NOTIFICATIONS — 알림 설정 `/my/notifications` (KNK-1401)](../domain/NOTIFICATION/CLIENT/WEB/5-1-VERIFICATION.md#5-1-1-알림-설정과-푸시)
- [MY-CREDITS — 이프 충전 `/my/credits` (FE-SCREEN-008, KNK-1083·1092·1297)](../domain/PAYMENT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-2-충전과-내역-케이스)
- [MY-PERSONA — 페르소나 생성과 관리 `/my/personas` (FE-SCREEN-008, KNK-1469)](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-14-my-persona-페르소나-생성과-관리-mypersonas-fe-screen-008-knk-1469)
- [MY-PROFILE — 프로필 수정 `/my/profile/edit` (FE-SCREEN-008, KNK-1148)](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-15-my-profile-프로필-수정-myprofileedit-fe-screen-008-knk-1148)
- [MY-FEEDBACK — 피드백 `/my/feedback` (FE-SCREEN-006)](../domain/CHAT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-15-my-feedback-피드백-myfeedback-fe-screen-006)
- [MY-INVITE — 친구 초대 `/my/invite` (FE-SCREEN-008)](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-16-my-invite-친구-초대-myinvite-fe-screen-008)
- [MY-ONBOARD — 신규 가입 초대 코드 모달 바텀 시트 (FE-SCREEN-008)](#my-onboard--신규-가입-초대-코드-모달-바텀-시트-fe-screen-008)
- [MY-INFO — 서비스 안내 `/about` (FE-SCREEN-011)](#my-info--서비스-안내-about-fe-screen-011)
- [MY-NOTICES — 공지사항 `/notices` (FE-SCREEN-014, KNK-1817)](../domain/NOTIFICATION/CLIENT/WEB/5-1-VERIFICATION.md#5-1-2-공지사항)
- [MY-INBOX — 알림함 `/notifications` (FE-SCREEN-015, KNK-1826)](../domain/NOTIFICATION/CLIENT/WEB/5-1-VERIFICATION.md#5-1-3-알림함)
- [MY-NAV — 하단 탭 네비게이션·상단 헤더](#my-nav--하단-탭-네비게이션상단-헤더)
- [⚠️ 확인 필요](#️-확인-필요)

---

컬럼 정의와 우선순위 기준은 [`AGENTS.md`](AGENTS.md)를 따릅니다.

로그인·세션·연동은 [인증 QA](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md), 공통 화면 검수는 [QA 공통 항목](AGENTS.md#크로스커팅-항목)을 따릅니다.

## MY-MENU — 마이 메뉴 `/my`

계정과 프로필 케이스는 ACCOUNT 검증으로 옮겼다. ([MY-MENU](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-18-my-menu-계정과-프로필))

기준: [계약·구조](../spec/3-1-client-spec.md#fe-screen-008-로그인마이-페이지).

| ID          | P   | 사전조건                                               | 절차                                | 기대 결과                                                                                                                         | 자동화                                     | 근거                                      |
| ------------ | --- | ------------------------------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | -------------------------------------------- |
| MY-MENU-02 | P1 | 게스트 | 메뉴·카드 구성 확인 | 화면(테마 변경)·알림(공지사항만, 알림 설정 없음)·기타(서비스 안내·피드백) 섹션만 표시. 이벤트(친구 초대)·계정(로그아웃·회원 탈퇴) 섹션과 이프 카드는 없음 | ✅ e2e `my/my-page`·`visual/my-visual` | FE-SCREEN-008 |
| MY-MENU-05 | P1 | 회원 | 메뉴 구성 확인 | 이벤트(친구 초대) / 화면(테마 변경) / 알림(알림 설정 → 공지사항 순) / 기타(서비스 안내 → 피드백 순) / 계정(기본 전경색 로그아웃 → 위험색 회원 탈퇴 순) 5개 섹션 표시 | ✅ e2e `visual/my-visual` | FE-SCREEN-008, FE-SCREEN-011 진입점 |
| MY-MENU-17 | P1 | 게스트/회원 | 피드백 메뉴 탭 | `/my/feedback`으로 이동 | ◐ e2e `my/my-page`(링크 표시만) | CHAT-US-016, [웹 라우팅](../spec/3-2-web-spec.md#3-2-4-라우팅레이아웃공통-셸) |
| MY-MENU-18   | P1  | 게스트/회원                                       | 테마 변경 메뉴 반복 탭      | 시스템 설정 → 라이트 모드 → 다크 모드 순으로 순환. 왼쪽 아이콘(모니터·해·달)과 오른쪽 문구가 함께 바뀌고 테마 즉시 적용 | ✅ e2e `my/my-page`                            | 구현(`theme-menu-item`)                      |

## MY-ACCOUNT-DELETION — 회원 탈퇴 `/my/account-deletion` (FE-SCREEN-008, KNK-1052)

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-13 MY-ACCOUNT-DELETION: 회원 탈퇴 `/my/account-deletion` (FE-SCREEN-008, KNK-1052)](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-13-my-account-deletion-회원-탈퇴-myaccount-deletion-fe-screen-008-knk-1052))

<a id="my-credits--이프-충전-mycredits-fe-screen-008-knk-10831092-미배포"></a>

## MY-NOTIFICATIONS — 알림 설정 `/my/notifications` (KNK-1401)

NOTIFICATION 검증은 [웹](../domain/NOTIFICATION/CLIENT/WEB/5-1-VERIFICATION.md)과 [Android](../domain/NOTIFICATION/CLIENT/ANDROID/5-1-VERIFICATION.md)에서 관리한다.

## MY-CREDITS

PAYMENT 내용은 도메인 문서에서 관리한다. ([PAYMENT 웹 검증](../domain/PAYMENT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-2-충전과-내역-케이스))

## MY-PERSONA — 페르소나 생성과 관리 `/my/personas` (FE-SCREEN-008, KNK-1469)

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-14 MY-PERSONA: 페르소나 생성과 관리 `/my/personas` (FE-SCREEN-008, KNK-1469)](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-14-my-persona-페르소나-생성과-관리-mypersonas-fe-screen-008-knk-1469))

## MY-PROFILE — 프로필 수정 `/my/profile/edit` (FE-SCREEN-008, KNK-1148)

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-15 MY-PROFILE: 프로필 수정 `/my/profile/edit` (FE-SCREEN-008, KNK-1148)](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-15-my-profile-프로필-수정-myprofileedit-fe-screen-008-knk-1148))

## MY-FEEDBACK — 피드백 `/my/feedback` (FE-SCREEN-006)

CHAT 내용은 도메인 문서에서 관리한다. ([새 문서](../domain/CHAT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-15-my-feedback-피드백-myfeedback-fe-screen-006))

## MY-INVITE — 친구 초대 `/my/invite` (FE-SCREEN-008)

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-16 MY-INVITE: 친구 초대 `/my/invite` (FE-SCREEN-008)](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-16-my-invite-친구-초대-myinvite-fe-screen-008))

## MY-ONBOARD — 신규 가입 초대 코드 모달 바텀 시트 (FE-SCREEN-008)

신규 가입 첫 로그인 직후의 초대 코드 바텀 시트 케이스는 [`onboarding.md`](onboarding.md)의 ONBD-INVITE 섹션이 소유합니다. 코드 입력의 사유별 오류 규칙은 이 문서의 MY-INVITE 섹션과 공유합니다.

<a id="my-info--서비스-안내-about-fe-screen-011-미배포"></a>

## MY-INFO — 서비스 안내 `/about` (FE-SCREEN-011)

기준: [계약·구조](../spec/3-1-client-spec.md#fe-screen-011-서비스-안내).

| ID          | P   | 사전조건                                               | 절차                                | 기대 결과                                                                                                                         | 자동화                                     | 근거                                      |
| ------------ | --- | --------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- | -------------------------------------- |
| MY-INFO-01 | P1 | 게스트/회원 | 마이 기타 섹션 "서비스 안내" 메뉴(피드백 위) 탭 | 메뉴 오른쪽에 새 창 아이콘 표시. 원래 `/my` 탭을 유지한 채 새 탭에서 `/about`을 열고, 뒤로가기 없는 링크 없는 마냑 로고 헤더 아래 본문 `h1` "서비스 안내"와 게스트 이용 안내·AI 콘텐츠 안내 등 섹션 표시. 게스트 이용 안내 제목 아래에 웹 브라우저 전용 안내 표시 | ✅ e2e `my/service-info`·`visual/my-visual` | US-8-4, FE-SCREEN-011 진입점 |
| MY-INFO-02 | P1 | 페이지 표시됨 | 이프 안내 섹션이 없는지 확인 | "이프 안내" 제목과 이프 수치 고지 문구가 화면에 없어야 함. 수치는 각 사용 지점(STORY-INFO-10·CHAT-INPUT-20·MY-CREDITS-17·MY-MENU-22)이 서버 값으로 표시 | ✅ e2e `my/service-info` | FE-SCREEN-011 콘텐츠 규칙, §3-1-7 이프 정책 수치 표시, KNK-1095 |
| MY-INFO-03 | P1 | 페이지 표시됨 | 게스트 이용 안내 문구 확인 | FE-SCREEN-011의 게스트 동의 후 체험, 브라우저 저장 한계와 최초 로그인 1회 이관 안내를 표시하고 체험 한도 수치는 복제하지 않음 | ✅ e2e `my/service-info` | FE-SCREEN-011, 웹 사용자 모델 |
| MY-INFO-05 | P2 | 페이지 표시됨 | 문의 섹션 확인 | 회원 탈퇴 문구·탈퇴 문의 이메일은 표시되지 않고, 피드백 위치 안내가 링크 없는 텍스트로 표시됨 | ✅ e2e `my/service-info` | FE-SCREEN-011, KNK-1068 |
| MY-INFO-06 | P2 | `/about` 직접 진입 | 헤더의 마냑 로고 탭 | 로고는 링크가 아니라 이동하지 않음. 헤더에 링크 없음 | ✅ e2e `my/service-info` | [웹 문서 열람](../spec/3-2-web-spec.md#문서-열람과-검색-노출) |
| MY-INFO-07 | P2 | 게스트/회원 각각 | `/about` 직접 진입 | 라우트 가드 없이 양쪽 모두 동일한 본문 열람 가능 | ◐ e2e `my/service-info`(게스트만) | FE-SCREEN-011 검수 기준 |
| MY-INFO-08 | P1 | 페이지 표시됨 | 브라우저 탭 제목 확인 | "서비스 안내 - 마냑" 표시 | ✅ e2e `my/service-info` | FE-SCREEN-011, [웹 문서 제목](../spec/3-2-web-spec.md#문서-열람과-검색-노출) |

<a id="my-nav--하단-탭-네비게이션상단-헤더-3-2-3"></a>

## MY-NOTICES — 공지사항 `/notices` (FE-SCREEN-014, KNK-1817)

NOTIFICATION 검증은 [웹](../domain/NOTIFICATION/CLIENT/WEB/5-1-VERIFICATION.md)과 [Android](../domain/NOTIFICATION/CLIENT/ANDROID/5-1-VERIFICATION.md)에서 관리한다.

## MY-INBOX — 알림함 `/notifications` (FE-SCREEN-015, KNK-1826)

NOTIFICATION 검증은 [웹](../domain/NOTIFICATION/CLIENT/WEB/5-1-VERIFICATION.md)과 [Android](../domain/NOTIFICATION/CLIENT/ANDROID/5-1-VERIFICATION.md)에서 관리한다.

## MY-NAV — 하단 탭 네비게이션·상단 헤더

기준: [계약·구조](../spec/3-2-web-spec.md#화면-전환-규칙).

| ID          | P   | 사전조건                                               | 절차                                | 기대 결과                                                                                                                         | 자동화                                     | 근거                                      |
| ----------- | --- | ------------------------------------------------------ | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | ----------------------------------------- |
| MY-NAV-01 | P0 | 임의 탭 화면 | 하단 탭 구성 확인 | 홈·채팅·제작·마이 순서의 4개 링크. 각 링크에 24px 아이콘과 보이는 라벨을 함께 표시 | ✅ e2e `my/my-page`·`smoke/navigation` | US-8-1, [웹 탭 이동](../design/1-1-web-design.md#히스토리-처리), KNK-988 |
| MY-NAV-02 | P0 | 홈에서 시작 | 탭으로 홈 → 채팅 → 제작 → 마이 → 홈 순회 | 각 경로(`/`·`/chats`·`/studio`·`/my`)로 이동. 홈은 로고만, 나머지는 섹션 라벨이 표시됨 | ✅ e2e `smoke/navigation` | US-8-1, [웹 라우팅](../spec/3-2-web-spec.md#3-2-4-라우팅레이아웃공통-셸), KNK-988·994·1012 |
| MY-NAV-03 | P1 | 임의 탭 화면 | 활성 탭 표시 확인 | 모든 아이콘·라벨에 같은 전경색을 적용. 현재 경로와 정확히 일치하는 탭에만 filled 아이콘·`aria-current="page"`를 적용하고 나머지는 outline 아이콘 | ✅ e2e `smoke/navigation` | [웹 라우팅](../spec/3-2-web-spec.md#3-2-4-라우팅레이아웃공통-셸), KNK-988 |
| MY-NAV-04 | P1 | 홈 → 채팅 → 제작 → 마이 순 탭 이동 | 브라우저 뒤로가기 | 탭 이동은 `replace`라 히스토리에 쌓이지 않음(탭 전환 이력을 되짚지 않고 탭 진입 이전 화면·이탈로 이동) | 수동 | [웹 화면 전환](../spec/3-2-web-spec.md#화면-전환-규칙) |
| MY-NAV-05 | P1 | 각 탭 화면 | 상단 헤더 확인 | 홈은 로고만 보이고 `h1` "홈"은 `sr-only`. 채팅·제작·마이는 20px semibold 섹션 라벨을 보더 없이 표시. 게스트의 홈·채팅·제작에는 오른쪽 secondary 로그인 버튼과 그 오른쪽 공지사항 아이콘 버튼을, 회원에게는 공지사항 버튼만 표시하고 마이에는 둘 다 표시하지 않음(공지 케이스는 MY-NOTICES) | ✅ e2e `smoke/navigation`·`stories/story-list` | [웹 헤더](../design/1-1-web-design.md#상단-헤더하단-네비게이션), KNK-988·1012 |
| MY-NAV-06 | P1 | `/my/feedback`·`/my/invite`·`/my/account-deletion`·`/login` | 각 화면 진입 | 상단 헤더·하단 탭 없이 뒤로가기 헤더만 표시 | 수동 | [웹 검수](../spec/3-2-web-spec.md#3-2-7-검수) |
| MY-NAV-07 | P2 | 하단 안전 영역이 있는 기기(iOS 등) | 하단 탭 확인 | 링크 상하 패딩 16px + `safe-area-inset-bottom` 추가 확보로 탭이 잘리지 않음 | ◐ e2e `smoke/navigation`(패딩만) | [웹 검수](../spec/3-2-web-spec.md#3-2-7-검수) |
| MY-NAV-08 | P2 | 구경로 `/more`·`/more/invite`·`/more/feedback` 진입 | 관찰 | 리다이렉트 없이 Not Found 표시(구경로 shim을 두지 않는 방침) | 수동 | [웹 화면 전환](../spec/3-2-web-spec.md#화면-전환-규칙) |
| MY-NAV-09 | P1 | iOS Safari 실기기, 회원 또는 게스트 | 아무 화면을 새로고침한 뒤 하단 탭으로 다른 화면에 이동 → 입력 칸(예: 마이 > 피드백 본문)을 탭 → 두 손가락으로 벌림 | 입력 칸에 포커스해도 화면이 확대되지 않고, 두 손가락으로 벌리면 확대됨. Android Chrome에서도 두 손가락 확대가 됨 | ◐ e2e `smoke/ios-input-zoom-lock`(viewport 값만) | [웹 모바일 검수](../spec/3-2-web-spec.md#모바일-검수-기준), [웹 레이아웃](../design/1-1-web-design.md#레이아웃-구조), KNK-1605 |
| MY-NAV-10 | P2 | 없는 경로 | 새 탭·외부 링크로 바로 진입 / 사이트 안에서 이동해 진입 | "페이지를 찾을 수 없어요"와 홈 링크. 같은 사이트의 이전 기록이 있을 때만 "이전 화면으로" 버튼이 함께 보이고 누르면 이전 화면으로 돌아감 | ✅ e2e `smoke/navigation` | 웹 Spec 라우팅 FE-SCREEN-999, KNK-1613 |

## MY-BACKGROUND — 문서 배경과 좌우 여백

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
| --- | --- | --- | --- | --- | --- | --- |
| MY-BACKGROUND-01 | P2 | 모바일 폭, 게스트 또는 회원 | 마이에서 라이트, 다크, 시스템 테마를 전환하고 화면 이동 | 문서와 앱 배경이 같은 테마로 이어지고 가로 스크롤이 없음 | 수동 | [웹 반응형 계약](../spec/3-2-web-spec.md#반응형-모바일-전용) |
| MY-BACKGROUND-02 | P2 | 앱 셸보다 넓은 데스크톱 화면 | 창 크기를 셸 너비 전후로 바꾸고 테마 전환 및 하단 탭 조작 | 중앙 셸 너비 유지, 좌우 여백만 별도 배경 표시, 배경 장식이 입력을 차단하지 않음 | 수동 | [웹 반응형 계약](../spec/3-2-web-spec.md#반응형-모바일-전용) |
| MY-BACKGROUND-03 | P2 | iOS Safari와 홈 화면 설치 PWA 실기기 | 첫 진입, 화면 이동, 테마 변경, Safari 도구 막대 표시 전환, PWA 카카오 로그인 복귀 및 키보드 열기와 닫기 후 상하 안전 영역 확인 | 문서 배경이 앱과 이어지고 앱 프레임이 동적 뷰포트 높이를 따름. 하단 빈 공간이나 탭 및 입력 영역 가림이 없음. 브라우저 자체 툴바 효과는 제외 | 수동 | [웹 반응형 계약](../spec/3-2-web-spec.md#반응형-모바일-전용) |
| MY-BACKGROUND-04 | P2 | 루트 오류 화면, 모바일과 데스크톱 폭 | 라이트 및 다크 테마에서 오류 화면 확인 | 일반 화면과 동일한 문서 배경 및 좌우 여백 규칙과 동적 뷰포트 높이 적용 | 수동 | [웹 반응형 계약](../spec/3-2-web-spec.md#반응형-모바일-전용) |

## ⚠️ 확인 필요

이 문서의 자동화 표시는 이번 실행·배포 완료를 뜻하지 않습니다.

통합한 ID(번호 재사용 금지):

- `MY-MENU-15` → auth.md의 AUTH-LOGOUT-01
- `MY-INFO-04` → legal.md의 LEGAL-ENTRY-08
