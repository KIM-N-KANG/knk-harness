# my

## 문서 정보

| 항목 | 값 |
| --- | --- |
| 버전 | 미기재 |
| 작성일 | 미기재 |
| 수정일 | 2026-09-16 |
| 대상 | 마냑 웹 프론트엔드 |
| 작성 목적 | 마이 메뉴와 계정·이프·초대 기능의 수동 QA와 E2E 검수 기준을 정의합니다. |
| 화면 | 마이 메뉴 `/my`·회원 탈퇴 `/my/account-deletion`·친구 초대 `/my/invite`·이프 충전 `/my/credits`(FE-SCREEN-008), 피드백 `/my/feedback`(FE-SCREEN-006), 서비스 안내 `/about`(FE-SCREEN-011), 하단 탭 네비게이션([§3-2-4](../spec/3-2-web-spec.md)) |
| 기준 코드 | [manyak-web `9ab592f`](https://github.com/KIM-N-KANG/manyak-web/tree/9ab592f698d0baaf15d96c80161a5924e5c7f73c). 실행 결과·릴리스 포함 여부는 별도 기록 |
| 관련 스펙 | [`3-1-client-spec.md §3-1-3(FE-SCREEN-006·008·011)·§3-1-8`](../spec/3-1-client-spec.md), [`3-2-web-spec.md §3-2-4·§3-2-6`](../spec/3-2-web-spec.md), [`2-user-stories.md §2-7·§2-8·§2-9·§2-10`](../spec/2-user-stories.md) |
| 관련 E2E | `manyak-web/e2e/my/my-page.spec.ts`, `e2e/my/account-deletion.spec.ts`, `e2e/my/invite.spec.ts`, `e2e/my/credits.spec.ts`, `e2e/my/service-info.spec.ts`, `e2e/my/login-page.spec.ts`, `e2e/feedback/feedback.spec.ts`, `e2e/smoke/navigation.spec.ts`, `manyak-web/e2e/visual/my-visual.spec.ts` |

## 읽는 순서

- [QA 공통 규칙](AGENTS.md)과 문서 정보의 관련 Spec·E2E를 먼저 확인합니다.
- 담당 화면의 케이스에서 사전 조건 → 절차 → 기대 결과를 확인하고 검수합니다.

## 목차

- [MY-MENU — 마이 메뉴 `/my`](#my-menu--마이-메뉴-my)
- [MY-ACCOUNT-DELETION — 회원 탈퇴 `/my/account-deletion` (FE-SCREEN-008, KNK-1052)](#my-account-deletion--회원-탈퇴-myaccount-deletion-fe-screen-008-knk-1052)
- [MY-NOTIFICATIONS — 알림 설정 `/my/notifications` (KNK-1401)](#my-notifications--알림-설정-mynotifications-knk-1401)
- [MY-CREDITS — 이프 충전 `/my/credits` (FE-SCREEN-008, KNK-1083·1092·1297)](#my-credits--이프-충전-mycredits-fe-screen-008-knk-108310921297)
- [MY-FEEDBACK — 피드백 `/my/feedback` (FE-SCREEN-006)](#my-feedback--피드백-myfeedback-fe-screen-006)
- [MY-INVITE — 친구 초대 `/my/invite` (FE-SCREEN-008)](#my-invite--친구-초대-myinvite-fe-screen-008)
- [MY-ONBOARD — 신규 가입 초대 코드 모달 바텀 시트 (FE-SCREEN-008)](#my-onboard--신규-가입-초대-코드-모달-바텀-시트-fe-screen-008)
- [MY-INFO — 서비스 안내 `/about` (FE-SCREEN-011)](#my-info--서비스-안내-about-fe-screen-011)
- [MY-NAV — 하단 탭 네비게이션·상단 헤더](#my-nav--하단-탭-네비게이션상단-헤더)
- [⚠️ 확인 필요](#️-확인-필요)

---

컬럼 정의와 우선순위 기준은 [`AGENTS.md`](AGENTS.md)를 따릅니다.

로그인·세션·연동은 [인증 QA](auth.md), 공통 화면 검수는 [QA 공통 항목](AGENTS.md#크로스커팅-항목)을 따릅니다.

## MY-MENU — 마이 메뉴 `/my`

기준: [계약·구조](../spec/3-1-client-spec.md#fe-screen-008-로그인마이-페이지).

| ID          | P   | 사전조건                                               | 절차                                | 기대 결과                                                                                                                         | 자동화                                     | 근거                                      |
| ------------ | --- | ------------------------------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | -------------------------------------------- |
| MY-MENU-01 | P0 | 게스트 | `/my` 진입 | 프로필 영역에 "게스트" 표시 + 로그인 버튼. 로그아웃 버튼 없음 | ✅ e2e `my/my-page` | FE-SCREEN-008, [웹 헤더](../design/1-1-web-design.md#상단-헤더하단-네비게이션) |
| MY-MENU-02 | P1 | 게스트 | 메뉴·카드 구성 확인 | 화면(테마 변경)·기타(서비스 안내·피드백) 섹션만 표시. 이벤트(친구 초대)·계정(로그아웃·회원 탈퇴) 섹션과 이프 카드는 없음 | ✅ e2e `my/my-page`·`visual/my-visual` | FE-SCREEN-008 |
| MY-MENU-03   | P0  | 게스트                                            | 로그인 버튼 탭         | `/login`으로 이동(마이 → 로그인 진입점)                                                                                 | ✅ e2e `my/login-page`                         | US-9-1, FE-SCREEN-008 진입점                 |
| MY-MENU-04   | P0  | 회원 로그인 상태                                  | `/my` 진입             | 닉네임 표시 + 로그아웃·회원 탈퇴 메뉴 표시. 로그인 버튼 없음                                                            | ✅ e2e `my/my-page`·`my/account-deletion`     | FE-SCREEN-008                                |
| MY-MENU-05 | P1 | 회원 | 메뉴 구성 확인 | 이벤트(친구 초대) / 화면(테마 변경) / 알림(알림 설정) / 기타(서비스 안내 → 피드백 순) / 계정(기본 전경색 로그아웃 → 위험색 회원 탈퇴 순) 5개 섹션 표시 | ✅ e2e `visual/my-visual` | FE-SCREEN-008, FE-SCREEN-011 진입점 |
| MY-MENU-06   | P2  | 회원, `me` 응답에 `profileThumbnailBase64` 있음   | 프로필 이미지 확인     | base64 썸네일(`data:image/png;base64,...`)을 세션 이미지보다 우선해 원형으로 렌더                                       | ✅ e2e `my/my-page`                            | 구현(`profile-header`)                       |
| MY-MENU-07 | P1 | 회원 | 닉네임 아래 영역 확인 | 닉네임 아래 google → kakao 순서로 Chip 표시. Google만 연동이면 점선 "카카오 연동하기", 둘 다 연동이면 Chip 2개만 표시. 연동 실행·오류는 AUTH-LINK 담당 | ✅ e2e `my/my-page`·`visual/my-visual` | FE-SCREEN-008 계정 연동, KNK-740 |
| MY-MENU-08   | P2  | 회원, `me` 응답의 `linkedProviders`가 비었거나 없음 | 닉네임 아래 영역 확인  | 연동 Chip 행 자체를 렌더하지 않음(연동 버튼 2개가 잠깐 보이는 오해 방지)                                                | 수동                                           | FE-SCREEN-008 계정 연동, KNK-740             |
| MY-MENU-09   | P2  | 프로필 이미지 없음 또는 이미지 로드 실패          | 프로필 영역 확인       | 회색 원 placeholder로 대체. 레이아웃 깨짐 없음                                                                          | ◐ e2e `visual/my-visual`(이미지 없음 분기만)   | 구현(`profile-header`)                       |
| MY-MENU-10   | P1  | 회원                                              | 이프 카드 확인       | "내 이프" + 잔액(천 단위 콤마) 표시. 조회 중에는 스켈레톤                                                             | ◐ e2e `visual/my-visual`(잔액 표시만)          | US-10-1, FE-SCREEN-008                       |
| MY-MENU-16   | P2  | 세션 판별 중(`loading`)                           | `/my` 진입 직후 관찰   | 닉네임·이프 카드 자리에 스켈레톤 표시(게스트 UI 깜빡임 없음)                                                          | 수동                                           | 구현(`profile-header`·`credit-balance-card`) |
| MY-MENU-17 | P1 | 게스트/회원 | 피드백 메뉴 탭 | `/my/feedback`으로 이동 | ◐ e2e `my/my-page`(링크 표시만) | US-7-1, [웹 라우팅](../spec/3-2-web-spec.md#3-2-4-라우팅레이아웃공통-셸) |
| MY-MENU-18   | P1  | 게스트/회원                                       | 테마 변경 메뉴 반복 탭      | 시스템 설정 → 라이트 모드 → 다크 모드 순으로 순환. 왼쪽 아이콘(모니터·해·달)과 오른쪽 문구가 함께 바뀌고 테마 즉시 적용 | ✅ e2e `my/my-page`                            | 구현(`theme-menu-item`)                      |
| MY-MENU-19 | P2 | 회원, base64 썸네일 없음·세션 이미지가 환경별 프로필 프리셋 URL | 프로필 이미지 확인 | 운영 `api.manyak.app`과 개발 `dev-api.manyak.app`의 `/profile-presets/**` 이미지가 원형으로 렌더링 | 수동 | [웹 이미지 검증](../design/1-1-web-design.md#원격-이미지-최적화), KNK-832 |
| MY-MENU-20   | P0  | 회원                                              | 회원 탈퇴 메뉴 탭      | `/my/account-deletion`으로 이동. 사용자 제거 아이콘(`UserRemove02Icon`)과 위험색 문구 표시                               | ✅ e2e `my/account-deletion`                  | US-9-11, FE-SCREEN-008 회원 탈퇴            |
| MY-MENU-21 | P1 | 회원 | 이프 카드 확인 | 잔액 오른쪽에 강조색 버튼 "충전" 하나만 표시(출석 체크·내역 버튼은 없음). 탭하면 `/my/credits`로 이동 | ✅ e2e `my/credits`·`visual/my-visual` | FE-SCREEN-008 마이 페이지 회원 상태 구성, KNK-1092 |
| MY-MENU-22 | P2 | 회원 | 친구 초대 메뉴 확인 | "친구 초대" 라벨 아래에 작은 강조색 보조 문구 "하고 N 이프 받기" 표시(N은 `GET /credits/policies`의 `inviteReward`). 라벨과 이어 한 문장으로 읽힘 | ◐ e2e `visual/my-visual`(표시만) | FE-SCREEN-008 마이 페이지 회원 상태 구성, §3-1-7 이프 정책 수치 표시, KNK-1092·1095 |

## MY-ACCOUNT-DELETION — 회원 탈퇴 `/my/account-deletion` (FE-SCREEN-008, KNK-1052)

기준: [계약·구조](../spec/3-1-client-spec.md#fe-screen-008-로그인마이-페이지).

| ID          | P   | 사전조건                                               | 절차                                | 기대 결과                                                                                                                         | 자동화                                     | 근거                                      |
| ---------------------- | --- | --------------------------------- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------ |
| MY-ACCOUNT-DELETION-01 | P0 | 게스트 | 경로 직접 진입 | `/login`으로 replace 이동 | ✅ e2e `my/account-deletion` | [웹 접근 조건](../spec/3-2-web-spec.md#라우팅-테이블) |
| MY-ACCOUNT-DELETION-02 | P0  | 회원                              | 마이 메뉴에서 진입              | 뒤로가기 헤더 "회원 탈퇴" + 제목 "탈퇴하기 전에 / 아래 내용을 모두 확인해주세요" + 설명 "모든 항목을 확인해야 탈퇴할 수 있어요" + 확인 항목 4개 + 하단 "회원 탈퇴하기" CTA 표시. 하단 탭 없음 | ◐ e2e `my/account-deletion`·`visual/my-visual`  | US-9-11, FE-SCREEN-008 화면 구성     |
| MY-ACCOUNT-DELETION-03 | P0  | 화면 기본 상태                    | 체크박스를 순서대로 선택        | 하나라도 미선택이면 CTA 비활성. 잔여 이프 소멸·기존 서재 복구 불가·공개 콘텐츠 잔존 가능·같은 소셜 계정 재로그인 시 기존 계정 미복구를 모두 체크하면 CTA 활성                               | ✅ e2e `my/account-deletion`                    | FE-SCREEN-008 사전 확인              |
| MY-ACCOUNT-DELETION-04 | P1 | 미선택 체크박스와 하단 CTA 표시됨 | 기본·전체 선택 상태를 각각 확인 | 미선택 체크박스는 2px `muted-foreground/50` 보더, 선택 시 `primary` 채움에 체크 패스가 그려짐. 체크박스와 문구 사이는 16px. CTA는 활성·로딩 상태에 위험색 배경 사용 | ◐ e2e `visual/my-visual`(기본 상태만) | [웹 표현](../design/1-1-web-design.md#웹-표현-값), KNK-1052 |
| MY-ACCOUNT-DELETION-05 | P0  | 네 항목 전체 선택, 탈퇴 API 204   | "회원 탈퇴하기" 탭              | `DELETE /users/me`를 한 번 호출. 성공 뒤 사용자 캐시·복구 슬롯·분석 식별자와 BFF·NextAuth 세션을 정리하고 `/my`로 이동해 게스트 상태 표시                                                     | ◐ e2e `my/account-deletion`(요청·로그아웃·이동) | §3-1-7 회원 탈퇴                     |
| MY-ACCOUNT-DELETION-06 | P1  | 탈퇴 요청 응답 대기               | CTA 관찰                        | 버튼 크기를 유지한 중앙 스피너("회원 탈퇴 중") 표시 + CTA 비활성으로 중복 요청 차단                                                                                                           | ✅ e2e `my/account-deletion`                    | FE-SCREEN-008 요청 중 상태           |
| MY-ACCOUNT-DELETION-07 | P0  | 탈퇴 API 5xx·네트워크 실패        | CTA 탭                          | "회원 탈퇴에 실패했어요" 토스트 + 현재 경로·체크 상태 유지. 요청 종료 후 CTA가 다시 활성화되어 재시도 가능. 세션 만료가 확정된 401은 전역 세션 만료 흐름을 따름                               | ✅ e2e `my/account-deletion`(5xx)               | §3-1-7 회원 탈퇴 실패                |
| MY-ACCOUNT-DELETION-08 | P2 | `/my`에서 진입 | 뒤로가기 헤더 탭 | 탈퇴 요청 없이 `/my`로 복귀 | 수동 | [웹 헤더](../design/1-1-web-design.md#상단-헤더하단-네비게이션) |

<a id="my-credits--이프-충전-mycredits-fe-screen-008-knk-10831092-미배포"></a>

## MY-NOTIFICATIONS — 알림 설정 `/my/notifications` (KNK-1401)

기준: [웹 PWA 푸시](../spec/3-2-web-spec.md#pwa-푸시). E2E 빌드는 Firebase 키를 비워 푸시가 꺼진 상태라 브라우저 권한·토큰 등록·완성 직후 프롬프트는 실기기 수동 검증입니다.

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
| --- | --- | --- | --- | --- | --- | --- |
| MY-NOTIFICATIONS-01 | P0 | 게스트 | 경로 직접 진입 | `/login`으로 replace 이동 | ✅ e2e `my/notifications` | [웹 접근 조건](../spec/3-2-web-spec.md#라우팅-테이블) |
| MY-NOTIFICATIONS-02 | P0 | 회원 | 마이 > 알림 > "알림 설정" 탭 | 뒤로가기 헤더 "알림 설정" + (브라우저 알림을 못 받으면) 상태 배너 + 서비스 알림(켜짐)·광고 알림(꺼짐) 스위치 줄(광고 라벨 옆 개인정보 처리방침 외부 링크 아이콘). 야간 줄 없음. 조회 중에는 스위치 자리에 골격 | ✅ e2e `my/notifications` | 웹 PWA 푸시 알림 설정 화면 |
| MY-NOTIFICATIONS-03 | P0 | 회원, 광고 꺼짐 | 광고 알림 스위치 탭 | `PUT /users/me/push-settings`에 세 값 전체(`marketingPush: true`) 전송 → 처리 결과 다이얼로그(제목 + "전송자: …"·"일시: …"·"처리 내용: 광고 알림 수신 동의 완료" + 전체 폭 확인) → 닫으면 야간 광고 허용 줄 표시 | ✅ e2e `my/notifications` | 웹 PWA 푸시, §4-3-5 푸시 수신 동의 |
| MY-NOTIFICATIONS-04 | P0 | 회원, 광고·야간 켜짐 | 광고 알림 스위치 탭 | 야간도 함께 `false`인 본문 전송, "광고 알림 수신 동의 철회 완료" 통지, 야간 줄 사라짐 | ✅ e2e `my/notifications` | 웹 PWA 푸시 |
| MY-NOTIFICATIONS-05 | P1 | 회원 | 서비스 알림 스위치 탭 | 통지 없이 저장. 저장 5xx면 "알림 설정을 저장하지 못했어요" 토스트 + 스위치 원복 | ✅ e2e `my/notifications` | 웹 PWA 푸시 |
| MY-NOTIFICATIONS-06 | P1 | 설정 조회 5xx | 진입 | 목록 대신 "알림 설정을 불러오지 못했어요" + "다시 시도하기" 버튼. 재시도 성공 시 스위치 표시 | ✅ e2e `my/notifications` | 웹 PWA 푸시 |
| MY-NOTIFICATIONS-07 | P1 | 푸시 활성 빌드, 권한 `default` | 배너 확인 → "알림 켜기" 탭 | 배너 "브라우저 알림 설정이 꺼져 있어요" + 버튼, 스위치 줄은 비활성. 허용하면 배너가 사라지고 줄이 활성으로 바뀌며 토큰 PUT 발생. 거부하면 "브라우저 알림이 차단되어 있어요" 토스트와 차단 배너. 차단 배너의 "방법 보기"는 사이트 설정 허용 안내 다이얼로그를 연다 | 수동(실기기) | 웹 PWA 푸시 |
| MY-NOTIFICATIONS-08 | P1 | iOS Safari 탭(비설치본) | 배너 확인 | 홈 화면 추가 안내 배너, 버튼 없음, 스위치 줄 비활성 | 수동(실기기) | 웹 PWA 푸시 |
| MY-NOTIFICATIONS-09 | P2 | 회원, 광고 켜짐 | 야간 광고 허용 탭 | 야간만 `true`인 본문 전송, "야간 광고 알림 수신 동의 완료" 통지 | 수동 | 웹 PWA 푸시 |

## MY-CREDITS — 이프 충전 `/my/credits` (FE-SCREEN-008, KNK-1083·1092·1297)

기준: [계약·구조](../spec/3-1-client-spec.md#fe-screen-008-로그인마이-페이지).

| ID          | P   | 사전조건                                               | 절차                                | 기대 결과                                                                                                                         | 자동화                                     | 근거                                      |
| -------------- | --- | ------------------------------------------ | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- | ------------------------------------------- |
| MY-CREDITS-01 | P0 | 게스트 | 경로 직접 진입 | `/login`으로 replace 이동 | ✅ e2e `my/credits` | [웹 접근 조건](../spec/3-2-web-spec.md#라우팅-테이블) |
| MY-CREDITS-02 | P0 | 회원 | 마이 이프 카드 "충전" 탭 | `/my/credits`로 이동. 뒤로가기 헤더 "이프 충전" 표시, 하단 탭 없음. 진입 기본 탭은 구매 | ✅ e2e `my/credits` | FE-SCREEN-008 이프 충전, [웹 경로](../spec/3-2-web-spec.md#라우팅-테이블) |
| MY-CREDITS-03 | P1 | 회원 | 최상단 잔액 상자 확인 | 중립 배경 상자에 "내 이프" 라벨이 위, 잔액이 그 아래 오른쪽에 한 단계 큰 글자·천 단위 콤마로 표시. 값은 진입마다 다시 읽은 `creditBalance`이며 내역 합산이 아님 | ✅ e2e `my/credits` | FE-SCREEN-008 잔액 박스 |
| MY-CREDITS-04 | P0 | 회원, 내역 여러 건 | 내역 탭에서 목록 확인 | 최신순 목록. 한 줄은 사유 라벨·대상 스토리·날짜와 오른쪽 금액이고, 획득은 `+`·소모/소멸은 `-`에 절대값·천 단위 콤마. 줄 위아래 여백은 8px | ✅ e2e `my/credits` | FE-SCREEN-008 내역 목록·항목 구성·금액 표기 |
| MY-CREDITS-05  | P1  | 소모·사용 취소 행의 `title`이 null         | 항목 확인                  | 제목 줄에 "삭제된 스토리" 표시. 보상·소멸 행은 제목 줄 자체를 그리지 않음                                                                        | ✅ e2e `my/credits`           | FE-SCREEN-008 제목·날짜                     |
| MY-CREDITS-06  | P1  | `expiresAt`이 있는 획득·소멸 행            | 날짜 줄 확인               | `YYYY-MM-DD · YYYY-MM-DD 만료` 표시. 소멸 행의 만료일은 `expiresAt`이며 `createdAt`을 만료일로 읽지 않음                                          | ✅ e2e `my/credits`           | FE-SCREEN-008 제목·날짜                     |
| MY-CREDITS-24  | P1  | KST 자정~오전 9시에 적립된 행(예: `createdAt: 2026-09-01T15:10:00Z`) | 날짜 줄 확인 | 발생일·만료일 모두 KST 기준 날짜(`2026-09-02 · 2026-10-02 만료`). UTC 문자열을 그대로 잘라 하루 전으로 표시하지 않음 | ✅ 단위 — 웹 `lib/format-date`·`my/credits/utils/credit-transaction-display`, 앱 `DisplayDateTest` | §3-1-7 날짜 표시 기준 |
| MY-CREDITS-07 | P1 | 첫 조회 중 | 진입 직후·내역 탭 전환 직후 관찰 | 잔액 상자와 내역 목록 자리에 각각 골격 표시 | 수동 | FE-SCREEN-008 화면 상태 |
| MY-CREDITS-08 | P1 | 내역 0건 | 내역 탭 진입 | "아직 이프 내역이 없어요" 표시 | ✅ e2e `my/credits` | FE-SCREEN-008 화면 상태 |
| MY-CREDITS-09 | P0 | 첫 조회가 5xx·네트워크 오류 | 내역 탭 진입 | 목록 자리에 "이프 내역을 불러오지 못했어요"와 "다시 시도하기". 탭하면 다시 조회해 목록 표시하고, 조회 중에는 버튼이 "다시 시도 중..." 비활성 | ✅ e2e `my/credits` | FE-SCREEN-008 화면 상태 |
| MY-CREDITS-10 | P0 | `nextCursor`가 있는 목록 | 목록 끝까지 스크롤 | 받은 `nextCursor`를 그대로 실어 다음 페이지를 요청하고 아래에 이어 붙임. "더 보기" 버튼 없음 | ✅ e2e `my/credits` | FE-SCREEN-008 페이징, [웹 커서 목록](../design/1-1-web-design.md#커서-목록-패칭-웹) |
| MY-CREDITS-11 | P1 | 다음 페이지 조회가 실패 | 목록 끝까지 스크롤 | 이미 그린 목록을 지우지 않고 목록 아래 재시도 버튼만 표시하며 자동 재요청을 멈춤. 탭하면 다음 페이지를 이어 붙임 | ✅ e2e `my/credits`(실제 마지막 내역 로딩 후 스크롤) | FE-SCREEN-008 화면 상태, [웹 커서 목록](../design/1-1-web-design.md#커서-목록-패칭-웹), KNK-1207 |
| MY-CREDITS-12 | P2 | 서버가 라벨 없는 `reason`을 내려줌 | 항목 확인 | 그 줄만 "이프 변동"으로 그리고 나머지 목록은 그대로 표시 | 수동 | FE-SCREEN-008 항목 구성(라벨은 클라이언트 소유) |
| MY-CREDITS-13 | P2 | `/my`에서 진입 | 뒤로가기 헤더 탭 | `/my`로 복귀 | 수동 | [웹 헤더](../design/1-1-web-design.md#상단-헤더하단-네비게이션) |
| MY-CREDITS-14 | P1 | 내역 탭을 한 번 보고 `/my`로 돌아온 상태 | "충전" → 내역 탭으로 다시 진입 | 남겨 둔 목록을 그대로 쓰지 않고 첫 페이지부터 다시 조회(스크롤 위치도 목록 맨 위). 그사이 발생한 내역이 바로 보임. 탭을 무료 충전으로 옮겼다 돌아와도 같음(비활성 탭은 언마운트) | ✅ e2e `my/credits` | [웹 커서 목록](../design/1-1-web-design.md#커서-목록-패칭-웹), KNK-1083 |
| MY-CREDITS-15 | P1 | 회원 | 탭 줄 확인 | "구매"·"무료 충전"·"내역" 세 탭을 밑줄 탭으로 표시하고 진입 시 구매가 선택됨. 탭을 바꿔도 URL은 `/my/credits` 그대로 | ✅ e2e `my/credits` | FE-SCREEN-008 화면 골격, KNK-1092·1297 |
| MY-CREDITS-16 | P1 | 회원, 내역이 한 화면을 넘김 | 내역 탭에서 아래로 스크롤 | 잔액 상자와 탭 줄은 제자리에 남고 탭 패널만 스크롤됨 | ◐ e2e `visual/my-visual`(정적 상태만) | FE-SCREEN-008 화면 골격, KNK-1092 |
| MY-CREDITS-17 | P1 | 회원 | 무료 충전 탭 확인 | 중립 배경 상자에 "매일 출석하고 / 매일 N 이프 받으세요" 두 줄 제목(N은 `GET /credits/policies`의 `attendanceReward`), 그 아래 가로 전폭 강조색 "출석 하기" 버튼, 버튼 아래 오른쪽 정렬 보조 문구 2줄("매일 오전 00시에 초기화돼요" → "보상으로 받은 이프는 적립일로부터 30일 동안 사용할 수 있어요") 순으로 표시 | ✅ e2e `my/credits`·`visual/my-visual` | FE-SCREEN-008 무료 충전 탭, §3-1-7 이프 정책 수치 표시, KNK-1092·1095 |
| MY-CREDITS-18 | P1 | 회원, 오늘 미출석(`attendedToday: false`) | "출석 하기" 버튼 탭 | "출석 체크 보상으로 {amount} 이프를 받았어요" 토스트 + 잔액 상자 자동 갱신(me 재조회) + 버튼이 "출석 완료" 비활성으로 전환 | ✅ e2e `my/credits` | US-10-2 (구 MY-MENU-11) |
| MY-CREDITS-19 | P2 | 회원, 오늘 출석 완료(`attendedToday: true`) | 무료 충전 탭 진입 | 진입 시부터 "출석 완료" 비활성 버튼 표시(중복 적립 불가) | ✅ e2e `my/credits` | US-10-2, FE-SCREEN-008 검수 기준 (구 MY-MENU-12) |
| MY-CREDITS-20 | P2 | 출석 요청이 200 `rewarded: false`(서버 중복 판정) | "출석 하기" 탭 | "오늘은 이미 출석 체크했어요" 안내 토스트. 적립 없음 | 수동 | 구현(`use-claim-attendance`) (구 MY-MENU-13) |
| MY-CREDITS-21 | P2 | 출석 API가 5xx·네트워크 오류로 실패 | "출석 하기" 탭 | "출석 체크에 실패했어요" 토스트. 버튼은 다시 활성화되어 재시도 가능. 요청 중에는 문구 자리에 "출석 체크 중" 스피너 + 비활성 | 수동 | §3-1-7 이프·초대 (구 MY-MENU-14) |
| MY-CREDITS-22 | P1 | 회원 | 무료 충전 탭의 친구 초대 줄 탭 | 출석 상자 32px 아래에 마이와 같은 친구 초대 줄(라벨 + 강조색 "하고 N 이프 받기") 표시. 탭하면 `/my/invite`로 이동 | ✅ e2e `my/credits` | FE-SCREEN-008 무료 충전 탭, KNK-1092·1095 |
| MY-CREDITS-23 | P1 | 회원, 서버 `GET /credits/policies`의 `attendanceReward`가 평소와 다른 값(예: 운영 700이 아닌 dev의 350) | 무료 충전 탭 진입 | 출석 제목이 서버 값을 그대로 표시(배포 없이 따라감). 조회 실패·응답 전에는 수치 자리에 `000`을 쉬머와 함께 그리고 문구 골격은 유지 | ✅ e2e `my/credits` | §3-1-7 이프 정책 수치 표시, KNK-1095 |
| MY-CREDITS-25 | P0 | 회원 | 구매 탭 확인 | `GET /credits/products` 순서대로 한 줄씩 표시. 왼쪽 "N 이프"(기본), 오른쪽 강조색 "N원"(웹 가격) 버튼. 보너스가 있는 상품만 기본 아래 강조색·굵은 "+N 이프". 줄 사이 구분선 없이 16px 간격. 앱 가격은 노출하지 않음. 목록 아래 "구매한 이프는 적립일로부터 5년 동안 사용할 수 있어요" | ✅ e2e `my/credits`·`visual/my-visual` | §3-1-7 유료 충전, [웹 유료 충전](../spec/3-2-web-spec.md#유료-충전), KNK-1297 |
| MY-CREDITS-26 | P0 | 회원 | 가격 버튼 탭 | `POST /users/me/credits/orders`에 그 상품의 `productId`를 실어 보내고 201의 `paymentUrl`로 전체 이동. 요청 중에는 누른 버튼에 스피너, 모든 가격 버튼 비활성 | ✅ e2e `my/credits` | [웹 유료 충전](../spec/3-2-web-spec.md#유료-충전), KNK-1297 |
| MY-CREDITS-27 | P1 | 주문 생성이 4xx·5xx·네트워크 오류 | 가격 버튼 탭 | 이동하지 않고 "결제를 시작하지 못했어요" 토스트. 버튼은 다시 활성화되어 재시도 가능 | ✅ e2e `my/credits` | §3-1-7 유료 충전, KNK-1297 |
| MY-CREDITS-28 | P1 | 상품 조회가 5xx·네트워크 오류 | 구매 탭 진입 | 목록 자리에 "충전 상품을 불러오지 못했어요"와 "다시 시도하기". 탭하면 다시 조회해 목록 표시. 조회 중에는 줄 골격 표시 | ✅ e2e `my/credits` | §3-1-7 유료 충전, KNK-1297 |
| MY-CREDITS-29 | P0 | 결제창 이동 전 남긴 대기 주문이 있고 주문이 `PENDING`→`COMPLETED` | 결제창에서 `/my/credits`로 복귀 | 잔액 아래 "결제 확인" 카드에 스피너 + "결제를 확인하고 있어요"(2초 간격 조회). `COMPLETED`가 되면 "N 이프가 충전됐어요"(N은 `totalCredits`)로 바뀌고 잔액 상자가 `GET /auth/me` 재조회 값으로 갱신. `COMPLETED` 확정 시점에 대기 주문 기록이 삭제되고 카드는 남음. 닫기(X)로 카드가 사라짐 | ✅ e2e `my/credits` | §3-1-7 결제 결과, [웹 유료 충전](../spec/3-2-web-spec.md#유료-충전), KNK-1297, KNK-1314 |
| MY-CREDITS-30 | P1 | 대기 주문 조회가 404 | 복귀 | "확인할 수 없는 주문이에요" + 닫기. 다시 확인 버튼 없음 | ✅ e2e `my/credits` | §3-1-7 결제 결과, KNK-1297 |
| MY-CREDITS-31 | P1 | 대기 주문 조회가 5xx·네트워크 오류 | 복귀 | "결제 확인에 실패했어요"와 "다시 확인". 자동 재조회는 멈추고, 탭하면 처음부터 다시 폴링 | ✅ e2e `my/credits` | §3-1-7 결제 결과, KNK-1297 |
| MY-CREDITS-32 | P2 | 주문이 30회(약 60초) 조회 후에도 `PENDING` | 복귀 후 대기 | "아직 결제 확인이 안 됐어요"와 "다시 확인" 표시, 자동 조회 중단 | ✅ 단위 — 웹 `my/credits/utils/credit-order-confirmation` | §3-1-7 결제 결과, KNK-1297 |
| MY-CREDITS-33 | P2 | 대기 주문 없음 또는 24시간 지난 기록 | `/my/credits` 진입 | 확인 카드를 그리지 않음 | ✅ e2e `my/credits`(없음)·단위 `pending-credit-order-storage`(만료) | [웹 유료 충전](../spec/3-2-web-spec.md#유료-충전), KNK-1297 |
| MY-CREDITS-34 | P0 | 대기 주문이 `REFUNDED`(또는 `COMPLETED`·404)로 확정돼 카드가 표시된 상태 | 닫기 없이 새로고침 또는 재진입 | 확인 카드를 다시 그리지 않고 주문 재조회도 없음. 확인 중·60초 초과·조회 오류 상태는 기록이 남아 재진입 시 다시 확인 | ✅ e2e `my/credits` | [웹 유료 충전](../spec/3-2-web-spec.md#유료-충전), KNK-1314 |
| MY-CREDITS-35 | P1 | 가격 버튼 탭으로 주문 생성 성공 후 결제창으로 이동 | 브라우저 뒤로가기로 문서가 bfcache 복원(`pageshow` persisted) | 가격 버튼의 스피너·비활성이 풀려 다시 주문 가능 | ✅ e2e `my/credits`(이벤트 직접 발생) | [웹 유료 충전](../spec/3-2-web-spec.md#유료-충전), KNK-1314 |
| MY-CREDITS-37 | P1 | 무료 충전 탭 | 탭 내용을 아래로 당겼다 놓기 | STORY-LIST-30과 같은 표시자로 프로필(잔액·출석 여부)과 정책 수치를 다시 조회 | 수동 | 웹 Spec 화면 전환 규칙, KNK-1355 |
| MY-CREDITS-38 | P1 | 내역 탭, 목록이 맨 위 | 목록을 아래로 당겼다 놓기 | 같은 표시자로 내역을 첫 페이지부터 다시 조회하고 응답 전까지 기존 줄 유지. 구매 탭에는 당김 없음 | 수동 | 웹 Spec 화면 전환 규칙, KNK-1355 |
| MY-CREDITS-36 | P1 | 대기 주문 기록이 있는 회원 | 로그아웃·세션 만료 로그아웃·회원 탈퇴 | 대기 주문 기록 삭제. 같은 기기의 다음 계정에 이전 계정의 확인 카드가 뜨지 않음 | ✅ e2e `my/session-expiry`(만료)·수동(로그아웃·탈퇴) | [웹 유료 충전](../spec/3-2-web-spec.md#유료-충전), KNK-1314 |

## MY-FEEDBACK — 피드백 `/my/feedback` (FE-SCREEN-006)

기준: [계약·구조](../spec/3-1-client-spec.md#피드백-폼).

| ID          | P   | 사전조건                                               | 절차                                | 기대 결과                                                                                                                         | 자동화                                     | 근거                                      |
| ---------------- | --- | -------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ---------------------------- |
| MY-FEEDBACK-01 | P1 | 게스트/회원 | `/my/feedback` 진입 | 뒤로가기 헤더("피드백") + 제목("써보면서 아쉬웠던 점이 있나요?" / "불편한 점이나 바라는 기능을 알려주세요") + 안내("보내주신 피드백은 다음 개선에 꼼꼼히 참고할게요") + 본문 카운터 `0 / 500` + 이메일 필드("답변이 필요하시면 이메일을 남겨주세요") 표시. 하단 탭 없음 | ✅ e2e `visual/my-visual` | FE-SCREEN-006, [웹 라우팅](../spec/3-2-web-spec.md#3-2-4-라우팅레이아웃공통-셸) |
| MY-FEEDBACK-02   | P1  | 폼 표시됨                        | 본문 미입력 상태에서 제출 버튼 확인 | 본문이 비어 있어도 "피드백 보내기" 버튼은 활성화                                                                                                                                                                                                                        | ✅ e2e `feedback/feedback`                      | §3-1-8 피드백 폼               |
| MY-FEEDBACK-03   | P0  | 폼 표시됨                        | 본문+이메일 입력 → 제출(성공 응답)  | "소중한 피드백을 보내주셔서 감사해요" 토스트 + 폼 초기화. 페이로드 `{body, email, platform: "WEB"}` 전송                                                                                                                                                                | ✅ e2e `feedback/feedback`                      | US-7-1·7-3, FE-SCREEN-006    |
| MY-FEEDBACK-04   | P0  | 폼 표시됨                        | 이메일 없이 본문만 제출             | 정상 제출되고 `email: null`로 전송                                                                                                                                                                                                                                      | ✅ e2e `feedback/feedback`                      | US-7-2                       |
| MY-FEEDBACK-05   | P1  | 본문 비어 있음(공백만 입력 포함) | 제출 버튼 탭                        | 버튼 위에 "피드백 내용을 입력해주세요" 인라인 오류(`role=alert`). API 요청 없음. 유효한 본문을 입력하면 오류 즉시 제거                                                                                                                                                  | ◐ e2e `feedback/feedback`(요청 미발생은 미검증) | FE-SCREEN-006 상태표, §3-1-8   |
| MY-FEEDBACK-06   | P1  | 제출 요청 진행 중                | 폼 관찰                             | 본문·이메일 입력과 버튼 비활성화 + 버튼 크기를 유지한 중앙 스피너("피드백 전송 중")                                                                                                                                                                                     | ◐ e2e `feedback/feedback`(입력 비활성은 미검증) | FE-SCREEN-006 상태표         |
| MY-FEEDBACK-07   | P0  | 제출이 4xx·5xx로 실패            | 제출                                | "피드백 전송에 실패했어요" 토스트 + 입력값 유지(재제출 가능)                                                                                                                                                                                                            | ◐ e2e `feedback/feedback`(입력 유지는 미검증)   | US-7-3, FE-SCREEN-006 상태표 |
| MY-FEEDBACK-08   | P2  | 폼 표시됨                        | 본문 500자 초과 입력 시도           | 500자에서 입력 차단(`maxLength`) + 카운터 `500 / 500`. 이메일도 320자 제한                                                                                                                                                                                              | 수동                                            | §3-1-8 피드백 폼               |
| MY-FEEDBACK-09   | P2  | 본문 앞뒤에 공백 포함 입력       | 제출                                | `body`는 trim되어 전송. 이메일이 공백뿐이면 `null`로 전송                                                                                                                                                                                                               | 수동                                            | 구현(`use-feedback-form`)    |
| MY-FEEDBACK-10 | P2 | `/my`에서 진입 | 뒤로가기 헤더 탭 | `/my`(마이)로 복귀 | 수동 | [웹 헤더](../design/1-1-web-design.md#상단-헤더하단-네비게이션) |
| MY-FEEDBACK-11 | P2 | 폼 표시됨 | 필드·하단 CTA 여백 확인 | 피드백 내용과 이메일 필드의 행 간격은 24px, 필드 그룹 하단 여백은 32px. 스크롤 본문의 하단 fade 바로 아래에 추가 상단 패딩 없이 CTA 푸터가 붙음 | ✅ e2e `feedback/feedback`·`visual/my-visual` | [웹 레이아웃](../design/1-1-web-design.md#레이아웃-구조), KNK-1012 |

## MY-INVITE — 친구 초대 `/my/invite` (FE-SCREEN-008)

기준: [계약·구조](../spec/3-1-client-spec.md#fe-screen-008-로그인마이-페이지).

| ID          | P   | 사전조건                                               | 절차                                | 기대 결과                                                                                                                         | 자동화                                     | 근거                                      |
| -------------- | --- | ----------------------------------------------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------- | -------------------------------------- |
| MY-INVITE-01 | P0 | 게스트 | `/my/invite` 직접 진입 | `/login`으로 replace 이동(마이 메뉴에도 친구 초대 미노출 — MY-MENU-02) | ✅ e2e `my/invite` | [웹 화면 전환](../spec/3-2-web-spec.md#화면-전환-규칙), FE-SCREEN-008 |
| MY-INVITE-02   | P0  | 회원, 응답 fixture의 `monthlyRewardLimit=10` | 마이 → 친구 초대 메뉴 탭                | `/my/invite` 진입. 내 초대 코드 + "이번 달 받은 보상 N/10회" + 코드 복사·카카오톡 공유 버튼 + 코드 입력 폼 + 이용 안내 4개 항목 표시                         | ✅ e2e `my/invite`                 | US-10-2, FE-SCREEN-008 친구 초대       |
| MY-INVITE-03   | P1  | 코드 표시됨                                                                               | "코드 복사하기" 탭                      | 초대 코드 문자열만 클립보드에 저장 + "초대 코드를 복사했어요" 토스트                                                                                         | ✅ e2e `my/invite`                 | FE-SCREEN-008 코드 복사·공유           |
| MY-INVITE-04   | P2  | 클립보드 권한 거부 등 복사 실패                                                           | 코드 복사 탭                            | "초대 코드 복사에 실패했어요" 토스트                                                                                                                         | 수동                               | 구현(`invite-screen`)                  |
| MY-INVITE-05   | P1  | 카카오 SDK 초기화 완료                                                                    | "카카오톡 공유하기" 탭                  | 공유 메시지에 제목 "초대 코드 등록하고 N 이프 받기 🎁"(N은 `GET /credits/policies`의 `inviteReward`) + 본문 "초대 코드: {코드}" + "마냑 하러가기" 버튼(서비스 홈 링크) 전송                            | ✅ e2e `my/invite`                 | FE-SCREEN-008 코드 복사·공유           |
| MY-INVITE-06   | P1  | 카카오 JS 키 미설정 또는 SDK 로드 전·실패                                                 | 공유 버튼 확인                          | 버튼 비활성화. 공유 호출이 실패하면 "카카오톡 공유를 열지 못했어요" 토스트                                                                                   | 수동                               | FE-SCREEN-008 초대 코드 카드           |
| MY-INVITE-07   | P2  | 초대 화면 방문 후 뒤로가기로 이탈                                                         | 친구 초대 재진입                        | SDK 스크립트가 캐시돼도 공유 버튼이 활성 상태로 복구됨                                                                                                       | ✅ e2e `my/invite`                 | 구현(`use-kakao-share`)                |
| MY-INVITE-08   | P1  | 초대 코드 조회가 5xx로 실패                                                               | `/my/invite` 진입                       | 코드 카드에 "초대 코드를 불러오지 못했어요" + "다시 시도하기" 버튼(재시도 중 "다시 시도 중..."). 코드 입력 폼은 계속 사용 가능. 재시도 성공 시 코드 표시         | ✅ e2e `my/invite`                 | §3-1-7 이프·초대                       |
| MY-INVITE-09   | P2  | 조회 200이지만 응답에 `inviteCode` 없음                                                   | 진입                                    | MY-INVITE-08과 동일한 실패 안내 + 입력 폼 유지                                                                                                               | ✅ e2e `my/invite`                 | 구현(`invite-screen`)                  |
| MY-INVITE-10   | P2  | 코드 조회 성공 이력(캐시) 있음                                                            | 재진입 시 백그라운드 재조회가 실패      | 기존 코드·복사·공유 버튼 유지(실패 안내로 덮지 않음)                                                                                                         | ✅ e2e `my/invite`                 | 구현(`invite-screen`)                  |
| MY-INVITE-11   | P0  | 미사용 계정, 유효한 타인 코드                                                             | 소문자·공백 섞인 코드 입력 → "등록"     | 대문자 정규화된 코드로 제출. 성공 시 "친구 초대 보상으로 N 이프를 받았어요" 토스트(N은 `GET /credits/policies`의 `inviteReward`) + 입력 초기화 + 잔액 자동 갱신(me 무효화)                             | ✅ e2e `my/invite`                 | US-10-2, FE-SCREEN-008 코드 입력       |
| MY-INVITE-12   | P1  | 입력 비어 있음                                                                            | 등록 탭                                 | "코드를 입력해주세요" 인라인 오류(`aria-invalid`). API 요청 없음                                                                                             | ✅ e2e `my/invite`                 | FE-SCREEN-008 코드 입력                |
| MY-INVITE-13   | P0  | 각 오류 응답(400·404 / 409 `INVITE_SELF_CODE` / 409 `INVITE_ALREADY_REDEEMED` / 기타 5xx) | 코드 제출                               | 사유별 인라인 안내: "코드를 다시 확인해주세요" / "내 코드는 입력할 수 없어요" / "이미 초대 코드를 입력했어요" / "초대 코드 입력에 실패했어요". 입력값은 유지 | ✅ e2e `my/invite`                 | FE-SCREEN-008 코드 입력                |
| MY-INVITE-14   | P1  | 등록 요청 진행 중                                                                         | 폼 관찰                                 | 입력창·등록 버튼 비활성화 + 버튼 크기를 유지한 중앙 스피너("초대 코드 등록 중")                                                                              | ✅ e2e `my/invite`                 | FE-SCREEN-008 등록 중 상태             |
| MY-INVITE-15   | P2  | 응답 fixture의 월 보상 횟수·상한이 10/10회                                                         | 코드 카드 확인                          | 진행 표기만 10/10회로 바뀌고 코드 복사·공유는 계속 가능(상한은 보상 적립에만 적용)                                                                           | ✅ e2e `my/invite`                 | FE-SCREEN-008 이용 안내                |
| MY-INVITE-16   | P2  | 코드 입력창                                                                               | 공백 포함 문자열 붙여넣기·9자 이상 입력 | 공백 제거·대문자 변환 후 8자까지만 반영                                                                                                                      | ◐ e2e `my/invite`(대문자 표시만)   | 구현(`invite-code`)                    |
| MY-INVITE-17   | P2  | 임의 사용자                                                                               | 폐기된 초대 URL `/invite/{code}` 진입   | 404 표시. 초대 코드 쿠키 저장·로그인 리다이렉트 없음                                                                                                         | ✅ e2e `my/invite`                 | FE-SCREEN-008 결정 기록(초대 URL 폐기) |

## MY-ONBOARD — 신규 가입 초대 코드 모달 바텀 시트 (FE-SCREEN-008)

신규 가입 첫 로그인 직후의 초대 코드 바텀 시트 케이스는 [`onboarding.md`](onboarding.md)의 ONBD-INVITE 섹션이 소유합니다. 코드 입력의 사유별 오류 규칙은 이 문서의 MY-INVITE 섹션과 공유합니다.

<a id="my-info--서비스-안내-about-fe-screen-011-미배포"></a>

## MY-INFO — 서비스 안내 `/about` (FE-SCREEN-011)

기준: [계약·구조](../spec/3-1-client-spec.md#fe-screen-011-서비스-안내).

| ID          | P   | 사전조건                                               | 절차                                | 기대 결과                                                                                                                         | 자동화                                     | 근거                                      |
| ------------ | --- | --------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- | -------------------------------------- |
| MY-INFO-01 | P1 | 게스트/회원 | 마이 기타 섹션 "서비스 안내" 메뉴(피드백 위) 탭 | 메뉴 오른쪽에 새 창 아이콘 표시. 원래 `/my` 탭을 유지한 채 새 탭에서 `/about`을 열고, 뒤로가기 없는 마냑 로고 홈 링크 헤더 아래 본문 `h1` "서비스 안내"와 게스트 이용 안내·AI 콘텐츠 안내 등 섹션 표시 | ✅ e2e `my/service-info`·`visual/my-visual` | US-8-4, FE-SCREEN-011 진입점 |
| MY-INFO-02 | P1 | 페이지 표시됨 | 이프 안내 섹션이 없는지 확인 | "이프 안내" 제목과 이프 수치 고지 문구가 화면에 없어야 함. 수치는 각 사용 지점(STORY-INFO-10·CHAT-INPUT-20·MY-CREDITS-17·MY-MENU-22)이 서버 값으로 표시 | ✅ e2e `my/service-info` | FE-SCREEN-011 콘텐츠 규칙, §3-1-7 이프 정책 수치 표시, KNK-1095 |
| MY-INFO-03 | P1 | 페이지 표시됨 | 게스트 이용 안내 문구 확인 | FE-SCREEN-011의 게스트 동의 후 체험, 브라우저 저장 한계와 최초 로그인 1회 이관 안내를 표시하고 체험 한도 수치는 복제하지 않음 | ✅ e2e `my/service-info` | FE-SCREEN-011, 웹 사용자 모델 |
| MY-INFO-05 | P2 | 페이지 표시됨 | 문의 섹션 확인 | 회원 탈퇴 문구·탈퇴 문의 이메일은 표시되지 않고, "피드백" 링크가 `/my/feedback`으로 연결됨 | ✅ e2e `my/service-info` | FE-SCREEN-011, KNK-1068 |
| MY-INFO-06 | P2 | `/about` 직접 진입 | 헤더의 마냑 로고 탭 | 홈(`/`)으로 이동 | ✅ e2e `my/service-info` | 구현(`HomeLogoHeader`) |
| MY-INFO-07 | P2 | 게스트/회원 각각 | `/about` 직접 진입 | 라우트 가드 없이 양쪽 모두 동일한 본문 열람 가능 | ◐ e2e `my/service-info`(게스트만) | FE-SCREEN-011 검수 기준 |
| MY-INFO-08 | P1 | 페이지 표시됨 | 브라우저 탭 제목 확인 | "서비스 안내 - 마냑" 표시 | ✅ e2e `my/service-info` | FE-SCREEN-011, [웹 문서 제목](../spec/3-2-web-spec.md#문서-열람과-검색-노출) |

<a id="my-nav--하단-탭-네비게이션상단-헤더-3-2-3"></a>

## MY-NAV — 하단 탭 네비게이션·상단 헤더

기준: [계약·구조](../spec/3-2-web-spec.md#화면-전환-규칙).

| ID          | P   | 사전조건                                               | 절차                                | 기대 결과                                                                                                                         | 자동화                                     | 근거                                      |
| ----------- | --- | ------------------------------------------------------ | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | ----------------------------------------- |
| MY-NAV-01 | P0 | 임의 탭 화면 | 하단 탭 구성 확인 | 홈·채팅·제작·마이 순서의 4개 링크. 각 링크에 24px 아이콘과 보이는 라벨을 함께 표시 | ✅ e2e `my/my-page`·`smoke/navigation` | US-8-1, [웹 탭 이동](../design/1-1-web-design.md#히스토리-처리), KNK-988 |
| MY-NAV-02 | P0 | 홈에서 시작 | 탭으로 홈 → 채팅 → 제작 → 마이 → 홈 순회 | 각 경로(`/`·`/chats`·`/studio`·`/my`)로 이동. 홈은 로고만, 나머지는 섹션 라벨이 표시됨 | ✅ e2e `smoke/navigation` | US-8-1, [웹 라우팅](../spec/3-2-web-spec.md#3-2-4-라우팅레이아웃공통-셸), KNK-988·994·1012 |
| MY-NAV-03 | P1 | 임의 탭 화면 | 활성 탭 표시 확인 | 모든 아이콘·라벨에 같은 전경색을 적용. 현재 경로와 정확히 일치하는 탭에만 filled 아이콘·`aria-current="page"`를 적용하고 나머지는 outline 아이콘 | ✅ e2e `smoke/navigation` | [웹 라우팅](../spec/3-2-web-spec.md#3-2-4-라우팅레이아웃공통-셸), KNK-988 |
| MY-NAV-04 | P1 | 홈 → 채팅 → 제작 → 마이 순 탭 이동 | 브라우저 뒤로가기 | 탭 이동은 `replace`라 히스토리에 쌓이지 않음(탭 전환 이력을 되짚지 않고 탭 진입 이전 화면·이탈로 이동) | 수동 | [웹 화면 전환](../spec/3-2-web-spec.md#화면-전환-규칙) |
| MY-NAV-05 | P1 | 각 탭 화면 | 상단 헤더 확인 | 홈은 로고만 보이고 `h1` "홈"은 `sr-only`. 채팅·제작·마이는 20px semibold 섹션 라벨을 보더 없이 표시. 게스트의 홈·채팅·제작에는 오른쪽 secondary 로그인 버튼을 표시하고 마이에는 표시하지 않음 | ✅ e2e `smoke/navigation`·`stories/story-list` | [웹 헤더](../design/1-1-web-design.md#상단-헤더하단-네비게이션), KNK-988·1012 |
| MY-NAV-06 | P1 | `/my/feedback`·`/my/invite`·`/my/account-deletion`·`/login` | 각 화면 진입 | 상단 헤더·하단 탭 없이 뒤로가기 헤더만 표시 | 수동 | [웹 검수](../spec/3-2-web-spec.md#3-2-7-검수) |
| MY-NAV-07 | P2 | 하단 안전 영역이 있는 기기(iOS 등) | 하단 탭 확인 | 링크 상하 패딩 16px + `safe-area-inset-bottom` 추가 확보로 탭이 잘리지 않음 | ◐ e2e `smoke/navigation`(패딩만) | [웹 검수](../spec/3-2-web-spec.md#3-2-7-검수) |
| MY-NAV-08 | P2 | 구경로 `/more`·`/more/invite`·`/more/feedback` 진입 | 관찰 | 리다이렉트 없이 Not Found 표시(구경로 shim을 두지 않는 방침) | 수동 | [웹 화면 전환](../spec/3-2-web-spec.md#화면-전환-규칙) |

## ⚠️ 확인 필요

이 문서의 자동화 표시는 이번 실행·배포 완료를 뜻하지 않습니다.

통합한 ID(번호 재사용 금지):

- `MY-MENU-15` → auth.md의 AUTH-LOGOUT-01
- `MY-INFO-04` → legal.md의 LEGAL-ENTRY-08
