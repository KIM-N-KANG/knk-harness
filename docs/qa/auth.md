# auth

이 문서의 케이스는 [ACCOUNT 웹 검증](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md)으로 옮겼다. 아래 절은 기존 링크의 진입점이다.

## 문서 정보

| 항목 | 값 |
| --- | --- |
| 버전 | 미기재 |
| 작성일 | 미기재 |
| 수정일 | 2026-10-19 |
| 대상 | 마냑 웹 프론트엔드 |
| 작성 목적 | 로그인·세션·계정 연동의 수동 QA와 E2E 검수 기준을 정의합니다. |
| 화면 | 로그인 `/login`(FE-SCREEN-008) + 로그인 필요 시트·필수 동의 시트(전역) + 계정 연동(마이 페이지 Chip 행·`/my/link/continue` 중계) + 전역 세션·이관 동작(루트 레이아웃 상주 컴포넌트) |
| 기준 코드 | [manyak-web `9ab592f`](https://github.com/KIM-N-KANG/manyak-web/tree/9ab592f698d0baaf15d96c80161a5924e5c7f73c). 실행 결과·릴리스 포함 여부는 별도 기록 |
| 관련 스펙 | [`3-1-client-spec.md FE-SCREEN-008(§3-1-3)·§3-1-7`](../spec/3-1-client-spec.md), [`3-2-web-spec.md §3-2-4·§3-2-5`](../spec/3-2-web-spec.md), [`4-backend-server-spec.md §4-3-5`](../spec/4-backend-server-spec.md)(인증), [`2-user-stories.md §2-8·§2-9`](../spec/2-user-stories.md) |
| 관련 E2E | `manyak-web/e2e/my/login-page.spec.ts`, `e2e/auth/consent.spec.ts`(필수 동의 게이트), `e2e/stories/story-login-gate.spec.ts`·`e2e/chats/chat-login-gate.spec.ts`(로그인 필요 시트), `e2e/my/session-expiry.spec.ts`, `e2e/auth/in-app-login.spec.ts`(팝업 로그인과 인앱 게스트 이용), `e2e/my/invite.spec.ts`(신규 가입 다이얼로그), `e2e/my/my-page.spec.ts`, `e2e/legal/legal.spec.ts`(로그인 화면 고지 없음), `manyak-web/e2e/visual/auth-visual.spec.ts` |

## 읽는 순서

- [QA 공통 규칙](AGENTS.md)과 문서 정보의 관련 Spec·E2E를 먼저 확인합니다.
- 담당 화면의 케이스에서 사전 조건 → 절차 → 기대 결과를 확인하고 검수합니다.

## 목차

- [AUTH-LOGIN — 로그인 페이지 `/login`](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-2-auth-login-로그인-페이지-login)
- [AUTH-CONSENT — 필수 동의 게이트(가입 대기와 로그인한 세션)](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-4-auth-consent-필수-동의-게이트가입-대기와-로그인한-세션)
- [AUTH-GUEST 게스트 이용 동의](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-3-auth-guest-게스트-이용-동의)
- [AUTH-LINK — 계정 연동 (마이 페이지, KNK-740)](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-5-auth-link-계정-연동-마이-페이지-knk-740)
- [AUTH-SESSION — BFF 토큰 세션·세션 만료](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-6-auth-session-bff-토큰-세션-세션-만료)
- [AUTH-MIGRATE — 게스트 데이터 자동 이관](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-7-auth-migrate-게스트-데이터-자동-이관)
- [AUTH-HANDOFF — 인앱 게스트 허용](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-8-auth-handoff-인앱-게스트-허용)
- [AUTH-POPUP — 인증 팝업](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-9-auth-popup-인증-팝업)
- [AUTH-LOGOUT — 로그아웃](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-10-auth-logout-로그아웃)
- [AUTH-ONBOARD — 신규 가입 온보딩(초대 코드 다이얼로그)](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#onbd-invite--신규-가입회원-초대-코드-온보딩)
- [⚠️ 확인 필요](#️-확인-필요)

---

컬럼 정의와 우선순위 기준은 [`AGENTS.md`](AGENTS.md)를 따릅니다.

범위: 인증·이관·연동·인앱 게스트 이용. 메뉴는 [마이 QA](my.md), 문서 내용은 [법적 QA](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md), 공통 화면 검수는 [QA 공통 항목](AGENTS.md#크로스커팅-항목)을 따릅니다. 외부 OAuth 서비스 화면 자체는 제외합니다.

## AUTH-LOGIN — 로그인 페이지 `/login`

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-2 AUTH-LOGIN: 로그인 페이지 `/login`](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-2-auth-login-로그인-페이지-login))

## AUTH-GUEST 게스트 이용 동의

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-3 AUTH-GUEST 게스트 이용 동의](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-3-auth-guest-게스트-이용-동의))

## AUTH-CONSENT — 필수 동의 게이트(가입 대기와 로그인한 세션)

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-4 AUTH-CONSENT: 필수 동의 게이트(가입 대기와 로그인한 세션)](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-4-auth-consent-필수-동의-게이트가입-대기와-로그인한-세션))

## AUTH-LINK — 계정 연동 (마이 페이지, KNK-740)

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-5 AUTH-LINK: 계정 연동 (마이 페이지, KNK-740)](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-5-auth-link-계정-연동-마이-페이지-knk-740))

## AUTH-SESSION — BFF 토큰 세션·세션 만료

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-6 AUTH-SESSION: BFF 토큰 세션, 세션 만료](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-6-auth-session-bff-토큰-세션-세션-만료))

## AUTH-MIGRATE — 게스트 데이터 자동 이관

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-7 AUTH-MIGRATE: 게스트 데이터 자동 이관](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-7-auth-migrate-게스트-데이터-자동-이관))

## AUTH-HANDOFF — 인앱 게스트 허용

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-8 AUTH-HANDOFF: 인앱 게스트 허용](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-8-auth-handoff-인앱-게스트-허용))

## AUTH-POPUP — 인증 팝업

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-9 AUTH-POPUP: 인증 팝업](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-9-auth-popup-인증-팝업))

## AUTH-LOGOUT — 로그아웃

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-10 AUTH-LOGOUT: 로그아웃](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-10-auth-logout-로그아웃))

## AUTH-ONBOARD — 신규 가입 온보딩(초대 코드 다이얼로그)

## ⚠️ 확인 필요

ACCOUNT 내용은 다음 문서에서 관리한다. ([5-1-19 ID 보존과 대체](../domain/ACCOUNT/CLIENT/WEB/5-1-VERIFICATION.md#5-1-19-id-보존과-대체))
