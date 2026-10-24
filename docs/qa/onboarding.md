# onboarding

## 문서 정보

| 항목 | 값 |
| --- | --- |
| 버전 | 미기재 |
| 작성일 | 미기재 |
| 수정일 | 2026-10-23 |
| 대상 | 마냑 웹 프론트엔드 |
| 작성 목적 | 신규 가입 초대 코드 온보딩과 앱 안내 배너의 수동 QA와 E2E 검수 기준을 정의합니다. 간편 제작 첫 진입 안내는 [STORY-TUTORIAL](stories.md#story-tutorial--간편-제작-첫-진입-안내)이 다룹니다. |
| 화면 | 신규 가입 초대 코드 모달 바텀 시트(FE-SCREEN-008, 루트 레이아웃 마운트) · 앱 안내 배너(루트 레이아웃, 모든 화면 최상단) |
| 기준 코드 | [manyak-web `9ab592f`](https://github.com/KIM-N-KANG/manyak-web/tree/9ab592f698d0baaf15d96c80161a5924e5c7f73c). 실행 결과·릴리스 포함 여부는 별도 기록 |
| 관련 스펙 | [웹 사용자 모델](../spec/3-2-web-spec.md#웹-사용자-모델), [앱 안내 배너](../spec/3-2-web-spec.md#앱-안내-배너) |
| 관련 E2E | `manyak-web/e2e/my/invite.spec.ts`(신규 가입 바텀 시트), `manyak-web/e2e/visual/onboarding-visual.spec.ts`, `manyak-web/e2e/smoke/app-banner.spec.ts`, `manyak-web/e2e/visual/app-banner-visual.spec.ts` |

## 읽는 순서

- [QA 공통 규칙](AGENTS.md)과 문서 정보의 관련 Spec·E2E를 먼저 확인합니다.
- 담당 화면의 케이스에서 사전 조건 → 절차 → 기대 결과를 확인하고 검수합니다.

## 목차

- [ONBD-INVITE — 신규 가입(회원) 초대 코드 온보딩](#onbd-invite--신규-가입회원-초대-코드-온보딩)
- [ONBD-BANNER — 앱 안내 배너](#onbd-banner--앱-안내-배너)
- [ONBD-APPLINK — 앱 공유 링크](#onbd-applink--앱-공유-링크)
- [⚠️ 확인 필요](#️-확인-필요)

---

컬럼 정의와 우선순위 기준은 [`AGENTS.md`](AGENTS.md)를 따릅니다.

## ONBD-INVITE — 신규 가입(회원) 초대 코드 온보딩

기준: [계약·구조](../spec/3-1-client-spec.md#fe-screen-008-로그인마이-페이지).

| ID             | P   | 사전조건                                                 | 절차                                  | 기대 결과                                                                                                                                                                                                                              | 자동화                                   | 근거                                                      |
| -------------- | --- | -------------------------------------------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | --------------------------------------------------------- |
| ONBD-INVITE-01 | P0  | 신규 가입 회원(`inviteOnboardingPending: true`)          | 첫 화면 진입                          | 모달 바텀 시트 표시: 제목 "초대 코드를 등록하면" / "N 이프를 받을 수 있어요"(N은 `GET /credits/policies`의 `inviteReward`), 설명 "지금은 건너뛰고 나중에 등록해도 돼요", 초대 코드 입력 + 세로 버튼 두 개("등록하기" 주 스타일, "닫기" 고스트 스타일, 웹은 xs·내용 너비·가운데 정렬, 등록 버튼과 8px 간격). 제목·설명 8px, 설명·폼 32px 간격. 닫기(X) 버튼 없음. 초점은 입력란이 아니라 시트에 있어 모바일 키보드가 자동으로 올라오지 않음. 게스트 온보딩과 동시 표시되지 않음 | ✅ e2e `my/invite` · visual `onboarding-visual` | FE-SCREEN-008, §3-1-7 이프 정책 수치 표시, 구현(`invite-onboarding-sheet`), KNK-1045·1095 |
| ONBD-INVITE-02 | P0  | ONBD-INVITE-01                                           | 배경 탭 또는 ESC 입력                 | 세션 플래그 소비(`inviteOnboardingPending: false` 저장) 후 닫힘. 새로고침·재방문에도 다시 뜨지 않음(단 ONBD-INVITE-05 재시도 화면에서는 닫기 재시도로 동작)                                                                             | ✅ e2e `my/invite`                       | FE-SCREEN-008, 구현(`invite-onboarding-sheet`)            |
| ONBD-INVITE-03 | P1  | 세션 갱신 API가 5xx로 실패                               | 배경 탭 또는 ESC 입력                 | 바텀 시트 유지 + "창을 닫지 못했어요" 토스트. 새로고침 시 다시 표시(플래그 미소비)                                                                                                                                                    | ✅ e2e `my/invite`                       | 구현(`invite-onboarding-sheet`)                           |
| ONBD-INVITE-04 | P0  | ONBD-INVITE-01                                           | 유효한 코드 입력 → "등록하기"         | "친구 초대 보상으로 N 이프를 받았어요" 토스트 + 바텀 시트 닫힘. 새로고침 후에도 다시 열리지 않음                                                                                                                                 | ✅ e2e `my/invite`                       | FE-SCREEN-008                                             |
| ONBD-INVITE-05 | P1  | 코드 적립 성공 + 세션 저장 실패                          | 등록 완료 관찰                        | 코드를 다시 청구하지 않고 입력 폼 대신 "N 이프는 정상 지급되었지만, 창을 닫는 데 실패했어요" 안내 + "닫기"(재시도) 버튼 표시(웹 xs·내용 너비·가운데 정렬)                                                                                                       | ✅ e2e `my/invite`                       | 구현(`invite-onboarding-sheet`)                           |
| ONBD-INVITE-07 | P2  | 등록 또는 닫기 처리 진행 중                              | 버튼·입력 상태 확인                   | 입력창과 "닫기"·"등록하기" 버튼이 모두 잠기고, 등록 버튼은 크기를 유지한 중앙 스피너 표시. 적립 후 저장 재시도 화면(ONBD-INVITE-05)의 "닫기" 버튼도 재시도 중 같은 방식의 스피너로 전환                                                                                                                                              | ◐ e2e `my/invite`(적립 후 저장 대기만)   | FE-SCREEN-008 등록 중 상태                                |
| ONBD-INVITE-08 | P2  | ONBD-INVITE-01, 잘못된 코드(예: 내 코드, 서버 모킹 필요) | 코드 입력 → "등록하기"                | 바텀 시트 유지 + `/my/invite`와 동일한 사유별 인라인 오류(`aria-invalid`·`role=alert`). 보상 미지급                                                                                                                                   | ✅ e2e `my/invite`                       | FE-SCREEN-008 코드 입력, 구현(`invite-onboarding-sheet`)  |
| ONBD-INVITE-09 | P0  | ONBD-INVITE-01                                           | "닫기" 탭                            | 배경 탭·ESC와 동일하게 세션 플래그 소비(`inviteOnboardingPending: false` 저장) 후 닫힘. 새로고침·재방문에도 다시 뜨지 않음. 코드 입력 자격(계정당 1회)은 남아 이후 `/my/invite`에서 등록 가능. 저장이 5xx로 실패하면 ONBD-INVITE-03과 동일하게 유지 + "창을 닫지 못했어요" 토스트 | ✅ e2e `my/invite`                       | FE-SCREEN-008, KNK-1045                                   |

## ONBD-BANNER — 앱 안내 배너

기준: [앱 안내 배너](../spec/3-2-web-spec.md#앱-안내-배너). Android 앱 진입은 앱 버전(KNK-1632 반영 여부)에 따라 다르므로 실기기 케이스에 앱 버전을 함께 기록합니다.

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
| --- | --- | --- | --- | --- | --- | --- |
| ONBD-BANNER-01 | P0 | Android Chrome, 첫 접속 | 홈 진입 | 헤더 위에 Android 배너(앱 아이콘, 앱 이름과 문구 두 줄, 앱 열기, 닫기) 표시 | ✅ e2e `smoke/app-banner` | [앱 안내 배너](../spec/3-2-web-spec.md#앱-안내-배너) |
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
| ONBD-BANNER-20 | P0 | Android 인스타그램 인앱, 앱 미설치 | 앱 열기 후 0.7초 대기 | 플레이스토어 앱의 마냑 페이지가 열림. 카카오톡, Chrome에서는 플레이스토어가 한 번만 열림 | ◐ e2e `smoke/app-banner`(이동과 취소만) | 같음, [W-041](../adr/1-2-web-adr.md#w-041) |

## ONBD-APPLINK — 앱 공유 링크

기준: [앱 공유 링크](../spec/3-2-web-spec.md#앱-공유-링크). Mobile Chrome 프로젝트는 Pixel 5라 Android UA이므로 데스크톱 케이스는 UA를 따로 지정합니다.

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
| --- | --- | --- | --- | --- | --- | --- |
| ONBD-APPLINK-01 | P1 | 데스크톱 또는 iOS 브라우저 | `/app` 열기 | 웹 홈(`/`)으로 교체 이동하고 뒤로가기가 `/app`으로 돌아오지 않음 | ✅ e2e `smoke/app-share` | [앱 공유 링크](../spec/3-2-web-spec.md#앱-공유-링크) |
| ONBD-APPLINK-02 | P0 | 카카오톡 스크래퍼 UA(`kakaotalk-scrap`) | `/app` 첫 HTML 요청 | `og:title`·`og:description`·`og:image`(절대 URL)·`og:url`(`/app`)·`twitter:card`가 들어 있고 `robots`는 `noindex, follow` | ✅ e2e `smoke/app-share` | 같음 |
| ONBD-APPLINK-03 | P0 | Android, 앱 미설치 | `/app` 열기 후 0.7초 대기 | 플레이스토어의 마냑 페이지가 열림(귀속값 `utm_medium=share_link`). 카카오톡 인앱은 외부 브라우저 열기를 거쳐 1.4초 안에 열림 | ◐ e2e `smoke/app-share`(카카오톡 UA의 이동만) | 같음 |
| ONBD-APPLINK-04 | P1 | Android, 앱 설치 | `/app` 열기 | 앱 홈이 열리고 플레이스토어는 열리지 않음. 앱에서 돌아오면 `/app`에 머물며 "Google Play에서 받기" 버튼이 보임 | ◐ e2e `smoke/app-share`(머무는 화면만) | 같음 |
| ONBD-APPLINK-05 | P2 | 실기기 카카오톡 대화방 | `https://manyak.app/app` 보내기 | 제목 "마냑", 홈 설명, 브랜드 이미지로 미리보기가 그려짐 | 수동 | 같음 |

## ⚠️ 확인 필요

이 문서의 자동화 표시는 이번 실행·배포 완료를 뜻하지 않습니다.

통합한 ID(번호 재사용 금지):

- `ONBD-GUEST-14` → ONBD-GUEST-01
- `ONBD-GUEST-24` → ONBD-GUEST-04

폐기한 ID(번호 재사용 금지):

- `ONBD-GUEST-27`: 온보딩 장면 카드 줄의 마우스 드래그. 스크롤 소개로 바뀌며 카드 줄이 사라짐(KNK-1644)
- `ONBD-GUEST` 전체: 게스트 온보딩 페이지와 서버 리다이렉트 제거(KNK-1804). 첫 사용 안내는 [STORY-TUTORIAL](stories.md#story-tutorial--간편-제작-첫-진입-안내)로 옮김
- `ONBD-INVITE-06`: 게스트 온보딩 페이지와 초대 코드 시트의 겹침. 온보딩 페이지 제거(KNK-1804). 간편 제작 첫 진입 안내와의 겹침은 STORY-TUTORIAL-08
- `ONBD-BANNER-21`: 온보딩 페이지의 배너 미노출과 접속 집계. 온보딩 페이지 제거(KNK-1804)
